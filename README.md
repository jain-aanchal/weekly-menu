# 🍽️ Weekly Menu Agent

Automatically generates a Mon–Fri family menu every **Friday at 8 PM** and emails it to you.

---

## What it generates

| | Details |
|---|---|
| **Breakfast** | Mon–Fri · 1 person · randomly selected |
| **Dinner** | Mon–Thu · family of 3 · randomly selected |
| **Friday dinner** | Free night 🎉 |

Dishes **rotate automatically** — you won't see the same meal repeated for at least 2 weeks.

---

## Quick start

### Step 1 — Set up Gmail App Password

The script sends email via Gmail SMTP. You need a **Google App Password** (16-char code just for this app):

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Ensure **2-Step Verification** is ON
3. Search for **"App passwords"** in the Google account search bar
4. Click **Create** → name it "Menu Agent" → copy the 16-character password
5. Open `email_config.json` and replace `YOUR_APP_PASSWORD_HERE`:

```json
{
  "sender_email": "jain.aanchal@gmail.com",
  "sender_app_password": "abcd efgh ijkl mnop",
  "recipient_email": "jain.aanchal@gmail.com"
}
```

### Step 2 — Schedule auto-run (Friday 8 PM)

Open **Terminal**, navigate to this folder, and run:

```bash
cd "/path/to/weekly-menu"
chmod +x setup_schedule.sh
./setup_schedule.sh
```

That's it! The script installs a macOS LaunchAgent that fires every Friday at 8 PM.

---

## Manual run

```bash
# Generate menu + send email
python3 "/path/to/weekly-menu/generate_menu.py"

# Preview only (no email sent, rotation not updated)
python3 "/path/to/weekly-menu/generate_menu.py" --preview
```

Or just ask Claude: **"Run my weekly menu generator"**

---

## Uninstall auto-schedule

```bash
launchctl unload ~/Library/LaunchAgents/com.menuagent.weekly-menu.plist
rm ~/Library/LaunchAgents/com.menuagent.weekly-menu.plist
```

---

## Adding or changing dishes

Open `generate_menu.py` and edit the lists near the top:

```python
BREAKFASTS = [
    "Cheese Dosa",
    "Your New Breakfast",   # ← add here
    ...
]

DINNERS = [
    "Thai Curry",
    "Your New Dinner",      # ← add here
    ...
]
```

---

## Files

| File | Purpose |
|---|---|
| `generate_menu.py` | Main script |
| `email_config.json` | Gmail credentials (**keep private!**) |
| `setup_schedule.sh` | One-time macOS scheduler setup |
| `used_dishes.json` | Auto-created; tracks rotation history |
| `logs/` | Auto-created; run logs from scheduled jobs |
| `README.md` | This file |
