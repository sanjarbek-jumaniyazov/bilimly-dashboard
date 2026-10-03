#!/bin/bash
# One-glance health report for the pilot deployment.
cd "$(dirname "$0")/.."
url=$(grep '^MINI_APP_URL=' .env | cut -d= -f2-)
alive() { [ -f "run/$1.pid" ] && kill -0 "$(cat "run/$1.pid")" 2>/dev/null && echo "running (pid $(cat run/$1.pid))" || echo "NOT RUNNING"; }
echo "watchdog : $(alive watchdog)   launchd: $(launchctl print gui/$(id -u)/com.bilimly.watchdog 2>/dev/null | grep -oE 'state = [a-z]+' || echo 'not installed')"
echo "backend  : $(alive backend)   local /healthz -> $(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:8000/healthz)"
echo "tunnel   : $(alive tunnel)   $url -> $(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$url/healthz")"
echo "bot      : $(alive bot)"
echo "--- last watchdog events"; tail -5 logs/watchdog.log
