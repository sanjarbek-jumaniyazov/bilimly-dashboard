#!/bin/bash
# Installs (or reinstalls) the watchdog as a macOS launchd user agent so it:
#   * starts automatically when you log in,
#   * is restarted by launchd if it ever exits, and
#   * keeps the Mac from idle-sleeping (caffeinate) while it runs.
#
# Usage:  ./scripts/install_service.sh          # install + start
#         ./scripts/install_service.sh remove   # stop + uninstall
set -eu
cd "$(dirname "$0")/.."
PROJECT_DIR="$(pwd)"
LABEL="com.bilimly.watchdog"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

if [ "${1:-}" = "remove" ]; then
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "removed $LABEL"
  exit 0
fi

mkdir -p "$HOME/Library/LaunchAgents" "$PROJECT_DIR/logs"
cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <!-- -i: no idle sleep, -s: no system sleep while on AC power. -->
    <string>/usr/bin/caffeinate</string>
    <string>-i</string>
    <string>-s</string>
    <string>/bin/bash</string>
    <string>$PROJECT_DIR/scripts/watchdog.sh</string>
  </array>
  <key>WorkingDirectory</key><string>$PROJECT_DIR</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>10</integer>
  <key>StandardOutPath</key><string>$PROJECT_DIR/logs/launchd.log</string>
  <key>StandardErrorPath</key><string>$PROJECT_DIR/logs/launchd.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>HOME</key><string>$HOME</string>
  </dict>
</dict>
</plist>
PLIST

# A watchdog started by hand would block the launchd one (pid lock), so stop it.
if [ -f "$PROJECT_DIR/run/watchdog.pid" ]; then
  kill "$(cat "$PROJECT_DIR/run/watchdog.pid")" 2>/dev/null || true
  rm -f "$PROJECT_DIR/run/watchdog.pid"
fi
pkill -f "scripts/watchdog.sh" 2>/dev/null || true

launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
launchctl bootstrap "$DOMAIN" "$PLIST"
launchctl kickstart -k "$DOMAIN/$LABEL"
echo "installed and started $LABEL"
echo "status: launchctl print $DOMAIN/$LABEL | grep -E 'state|pid'"
