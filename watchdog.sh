#!/bin/bash
# Keeps Bilimly's backend, bot, and public tunnel alive unattended.
#
# Why this exists: the Mini App is served from this laptop through a free
# cloudflared "quick tunnel" (trycloudflare.com). That tunnel gets invalidated
# server-side every so often ("Unauthorized: Tunnel not found"), the laptop's
# network drops, and processes die on reboot. Any of those silently breaks
# the app for every student. This loop self-heals:
#
#   * backend  - restarted if the process is gone or /healthz stops answering
#   * tunnel   - restarted if the public URL stops answering; the new URL is
#                written into .env. The bot re-reads .env on its own and
#                re-points the menu button + already-sent buttons at the new
#                URL (bot/url_refresher.py), so the bot is NOT restarted.
#   * bot      - restarted if the process is gone
#
# Network outages on the laptop itself are detected separately so the tunnel
# isn't recycled (and the URL churned) while the laptop is simply offline.
#
# Run it via launchd (see scripts/install_service.sh) so it survives reboots
# and keeps the Mac awake; running it by hand still works.

set -u
cd "$(dirname "$0")/.."
PROJECT_DIR="$(pwd)"
RUN_DIR="$PROJECT_DIR/run"
LOG_DIR="$PROJECT_DIR/logs"
LOCK_FILE="$RUN_DIR/watchdog.pid"
ENV_FILE="$PROJECT_DIR/.env"
PYTHON="$PROJECT_DIR/.venv/bin/python"
UVICORN="$PROJECT_DIR/.venv/bin/uvicorn"
CLOUDFLARED="$PROJECT_DIR/bin/cloudflared"
BACKEND_PORT=8000

CHECK_INTERVAL=20          # seconds between health checks
TUNNEL_FAILS_BEFORE_CYCLE=2  # consecutive public-URL failures before recycling
MAX_LOG_BYTES=$((5 * 1024 * 1024))

mkdir -p "$RUN_DIR" "$LOG_DIR"

log() { echo "$(date -Iseconds) $*" >> "$LOG_DIR/watchdog.log"; }

if [ -f "$LOCK_FILE" ] && [ "$(cat "$LOCK_FILE")" != "$$" ] \
   && kill -0 "$(cat "$LOCK_FILE")" 2>/dev/null; then
  log "watchdog already running (pid $(cat "$LOCK_FILE")), exiting"
  exit 0
fi
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

is_alive() {
  local pidfile="$1"
  [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null
}

kill_pidfile() {
  local pidfile="$1"
  if [ -f "$pidfile" ]; then
    kill "$(cat "$pidfile")" 2>/dev/null
    sleep 1
    kill -9 "$(cat "$pidfile")" 2>/dev/null
    rm -f "$pidfile"
  fi
}

http_code() {  # $1=url $2=timeout
  curl -s -o /dev/null -w "%{http_code}" --max-time "$2" "$1" 2>/dev/null || echo 000
}

internet_up() {
  # The tunnel is useless without Cloudflare's edge; the bot without Telegram.
  # Either answering means the laptop is online.
  [ "$(http_code https://api.telegram.org/ 6)" != "000" ] \
    || [ "$(http_code https://www.cloudflare.com/cdn-cgi/trace 6)" != "000" ]
}

rotate_logs() {
  local f
  for f in backend.log bot.log cloudflared.log watchdog.log; do
    local path="$LOG_DIR/$f"
    [ -f "$path" ] || continue
    local size
    size=$(stat -f %z "$path" 2>/dev/null || echo 0)
    if [ "$size" -gt "$MAX_LOG_BYTES" ]; then
      tail -c $((MAX_LOG_BYTES / 2)) "$path" > "$path.tmp" && mv "$path.tmp" "$path"
    fi
  done
}

current_url() { grep '^MINI_APP_URL=' "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '[:space:]'; }

# --- processes ----------------------------------------------------------------

start_backend() {
  log "starting backend (uvicorn)"
  kill_pidfile "$RUN_DIR/backend.pid"
  pkill -f "uvicorn api.main:app" 2>/dev/null
  nohup "$UVICORN" api.main:app --host 127.0.0.1 --port "$BACKEND_PORT" \
    >> "$LOG_DIR/backend.log" 2>&1 &
  echo $! > "$RUN_DIR/backend.pid"
}

backend_healthy() {
  is_alive "$RUN_DIR/backend.pid" || return 1
  [ "$(http_code "http://127.0.0.1:$BACKEND_PORT/healthz" 5)" = "200" ]
}

start_bot() {
  log "starting bot (aiogram polling)"
  kill_pidfile "$RUN_DIR/bot.pid"
  pkill -f "bot.main" 2>/dev/null
  nohup "$PYTHON" -m bot.main >> "$LOG_DIR/bot.log" 2>&1 &
  echo $! > "$RUN_DIR/bot.pid"
}

start_tunnel() {
  log "starting new cloudflared quick tunnel"
  kill_pidfile "$RUN_DIR/tunnel.pid"
  pkill -f "cloudflared tunnel --url" 2>/dev/null
  : > "$LOG_DIR/cloudflared_latest.log"
  # cloudflared logs everything (including the assigned URL) to stderr.
  nohup "$CLOUDFLARED" tunnel --url "http://127.0.0.1:$BACKEND_PORT" \
    >> "$LOG_DIR/cloudflared_latest.log" 2>&1 &
  echo $! > "$RUN_DIR/tunnel.pid"

  local url=""
  for _ in $(seq 1 40); do
    sleep 1
    url=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" "$LOG_DIR/cloudflared_latest.log" 2>/dev/null | head -1)
    [ -n "$url" ] && break
  done
  cat "$LOG_DIR/cloudflared_latest.log" >> "$LOG_DIR/cloudflared.log" 2>/dev/null

  if [ -z "$url" ]; then
    log "ERROR: cloudflared did not report a URL within 40s"
    return 1
  fi

  # Wait until the edge actually routes the new hostname (takes a few seconds)
  # before publishing it; otherwise students get a Cloudflare error page.
  local ok=0
  for _ in $(seq 1 20); do
    sleep 2
    if [ "$(http_code "$url/healthz" 8)" = "200" ]; then ok=1; break; fi
  done
  [ "$ok" = 1 ] || log "warning: new tunnel URL not answering yet, publishing anyway"

  log "new tunnel URL: $url"
  if grep -q '^MINI_APP_URL=' "$ENV_FILE"; then
    sed -i '' "s#^MINI_APP_URL=.*#MINI_APP_URL=$url#" "$ENV_FILE"
  else
    echo "MINI_APP_URL=$url" >> "$ENV_FILE"
  fi
  return 0
}

tunnel_healthy() {
  is_alive "$RUN_DIR/tunnel.pid" || return 1
  local url
  url=$(current_url)
  [ -n "$url" ] || return 1
  [ "$(http_code "$url/healthz" 10)" = "200" ]
}

# --- main loop ----------------------------------------------------------------

log "watchdog loop starting (pid $$)"
tunnel_fail_count=0

while true; do
  rotate_logs

  if ! backend_healthy; then
    log "backend unhealthy, restarting"
    start_backend
    sleep 3
  fi

  if ! is_alive "$RUN_DIR/bot.pid"; then
    start_bot
  fi

  if tunnel_healthy; then
    tunnel_fail_count=0
  elif ! internet_up; then
    # Laptop offline (Wi-Fi drop, just woke from sleep). Recycling the tunnel
    # now would only churn the URL; wait for the network to come back.
    log "no internet connectivity, waiting"
    tunnel_fail_count=0
  else
    tunnel_fail_count=$((tunnel_fail_count + 1))
    if [ "$tunnel_fail_count" -ge "$TUNNEL_FAILS_BEFORE_CYCLE" ] || ! is_alive "$RUN_DIR/tunnel.pid"; then
      log "tunnel unhealthy ($tunnel_fail_count checks), recycling cloudflared"
      tunnel_fail_count=0
      start_tunnel || log "tunnel restart failed, will retry"
    else
      log "tunnel check failed ($tunnel_fail_count/$TUNNEL_FAILS_BEFORE_CYCLE), rechecking soon"
    fi
  fi

  sleep "$CHECK_INTERVAL"
done
