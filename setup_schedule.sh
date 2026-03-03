#!/bin/bash
# ============================================================
# Weekly Menu Agent — macOS Auto-Schedule Setup
# Run this ONCE from Terminal to schedule the Friday 8 PM email
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/generate_menu.py"
PLIST_LABEL="com.menuagent.weekly-menu"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"
LOG_DIR="$SCRIPT_DIR/logs"

# ── Sanity checks ─────────────────────────────────────────────────────────────
if [ ! -f "$PYTHON_SCRIPT" ]; then
  echo "❌  Could not find generate_menu.py at: $PYTHON_SCRIPT"
  echo "    Make sure you run this script from the weekly-menu folder."
  exit 1
fi

PYTHON_BIN=$(which python3 2>/dev/null || echo "")
if [ -z "$PYTHON_BIN" ]; then
  echo "❌  python3 not found. Please install Python 3 from https://python.org"
  exit 1
fi

# ── Create logs directory ─────────────────────────────────────────────────────
mkdir -p "$LOG_DIR"

# ── Write launchd plist ───────────────────────────────────────────────────────
# Runs every Friday at 20:00 (8 PM) in the user's local time
cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$PLIST_LABEL</string>

  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON_BIN</string>
    <string>$PYTHON_SCRIPT</string>
  </array>

  <key>StartCalendarInterval</key>
  <dict>
    <!-- Friday = Weekday 5, at 20:00 (8 PM local time) -->
    <key>Weekday</key>
    <integer>5</integer>
    <key>Hour</key>
    <integer>20</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>

  <key>StandardOutPath</key>
  <string>$LOG_DIR/menu-agent.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/menu-agent-error.log</string>

  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
PLIST

# ── Load (or reload) the plist ────────────────────────────────────────────────
# Unload first if it was already loaded
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo ""
echo "✅  Weekly Menu Agent scheduled successfully!"
echo ""
echo "   📅  Runs every Friday at 8:00 PM (your local time)"
echo "   📧  Email will be sent to the address in email_config.json"
echo "   📄  Logs saved to: $LOG_DIR/"
echo ""
echo "   To run NOW (manual):   python3 \"$PYTHON_SCRIPT\""
echo "   To preview (no email): python3 \"$PYTHON_SCRIPT\" --preview"
echo "   To uninstall:          launchctl unload \"$PLIST_PATH\" && rm \"$PLIST_PATH\""
echo ""
echo "   ⚠️   Reminder: fill in your Gmail App Password in email_config.json"
echo "        before the first Friday run!"
echo ""
