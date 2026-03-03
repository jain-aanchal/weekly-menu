#!/usr/bin/env python3
"""
Weekly Menu Generator
=====================
Generates a random Mon–Fri menu and emails it every Friday.

Usage:
  python3 generate_menu.py            # generate + send email
  python3 generate_menu.py --preview  # print menu only, no email, no rotation save
"""

import json
import random
import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# ── Dish Data ──────────────────────────────────────────────────────────────────

# Monday breakfast is always Oatmeal (see generate_menu below)
MONDAY_BREAKFAST = "Oatmeal"

# Rotation pool for Tue–Fri (Oatmeal excluded since it's fixed to Monday)
BREAKFASTS = [
    "Cheese Dosa",
    "Avocado Sandwich",
    "Yogurt Sandwich",
    "Smoothie",
    "Nutella Sandwich",
    "Toast and Boiled Egg",
    "Egg Sandwich",
    "Milk Cereal",
]

DINNERS = [
    "Chola, Shahi Paneer & Green Chutney",
    "Chola & Shahi Paneer",
    "Taco Night or Ravioli",
    "Pau Bhaji",
    "Rajma & Paneer",
    "Thai Curry",
    "Baked Vegetables",
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# ── File Paths ─────────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "email_config.json")
USED_FILE   = os.path.join(SCRIPT_DIR, "used_dishes.json")

# ── Rotation Logic ─────────────────────────────────────────────────────────────

def load_used():
    if os.path.exists(USED_FILE):
        with open(USED_FILE) as f:
            return json.load(f)
    return {"breakfasts": [], "dinners": []}

def save_used(used):
    with open(USED_FILE, "w") as f:
        json.dump(used, f, indent=2)

def pick_dishes(all_dishes, used_recent, count):
    """Pick `count` dishes avoiding recently used ones where possible."""
    available = [d for d in all_dishes if d not in used_recent]
    if len(available) < count:
        # Not enough fresh options — reset rotation and use full list
        available = list(all_dishes)
        used_recent.clear()
    return random.sample(available, count)

def generate_menu(save_rotation=True):
    used = load_used()

    # Rolling window: ~2 weeks of breakfast history, ~2 weeks of dinner history
    recent_breakfasts = used["breakfasts"][-8:]
    recent_dinners    = used["dinners"][-8:]

    # Monday is always Oatmeal; pick 4 random breakfasts for Tue–Fri
    breakfasts = pick_dishes(BREAKFASTS, recent_breakfasts, 4)
    dinners    = pick_dishes(DINNERS,    recent_dinners,    4)

    menu = {}
    for i, day in enumerate(DAYS):
        if day == "Monday":
            menu[day] = {"breakfast": MONDAY_BREAKFAST}
        else:
            menu[day] = {"breakfast": breakfasts[i - 1]}
        if day != "Friday":
            menu[day]["dinner"] = dinners[i]

    if save_rotation:
        used["breakfasts"] = recent_breakfasts + breakfasts
        used["dinners"]    = recent_dinners    + dinners
        save_used(used)

    return menu

# ── Date Helpers ───────────────────────────────────────────────────────────────

def next_week_range():
    """Return (next_monday, next_friday) as datetime objects."""
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    next_monday = today + timedelta(days=days_until_monday)
    next_friday = next_monday + timedelta(days=4)
    return next_monday, next_friday

# ── Formatting ─────────────────────────────────────────────────────────────────

def format_menu_text(menu):
    mon, fri = next_week_range()
    week_label = f"{mon.strftime('%b %d')} – {fri.strftime('%b %d, %Y')}"

    lines = [
        f"🍽️  Weekly Family Menu — {week_label}",
        "=" * 50,
    ]
    for day in DAYS:
        lines.append(f"\n{day}")
        lines.append(f"  🌅 Breakfast : {menu[day]['breakfast']}  (1 person)")
        if day != "Friday":
            lines.append(f"  🌙 Dinner    : {menu[day]['dinner']}  (family of 3)")
        else:
            lines.append(  "  🌙 Dinner    : Free night — enjoy! 🎉")
    lines += ["", "=" * 50, "Have a delicious week! 🤗"]
    return "\n".join(lines)

def format_menu_html(menu):
    mon, fri = next_week_range()
    week_label = f"{mon.strftime('%b %d')} – {fri.strftime('%b %d, %Y')}"

    rows = ""
    for day in DAYS:
        breakfast = menu[day]["breakfast"]
        if day != "Friday":
            dinner_cell = f"""{menu[day]['dinner']}
                <br><span style="color:#aaa;font-size:11px;">family of 3</span>"""
        else:
            dinner_cell = "<span style='color:#bbb;font-style:italic;'>Free night 🎉</span>"

        bg = "#fafafa" if DAYS.index(day) % 2 == 0 else "#ffffff"
        rows += f"""
        <tr style="background:{bg};">
          <td style="padding:14px 18px;font-weight:700;color:#444;white-space:nowrap;
                     border-bottom:1px solid #f0f0f0;width:110px;">{day}</td>
          <td style="padding:14px 18px;color:#333;border-bottom:1px solid #f0f0f0;">
            {breakfast}
            <br><span style="color:#aaa;font-size:11px;">1 person</span>
          </td>
          <td style="padding:14px 18px;color:#333;border-bottom:1px solid #f0f0f0;">
            {dinner_cell}
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f2f2f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f2f2f7;padding:32px 16px;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0"
           style="background:#fff;border-radius:16px;overflow:hidden;
                  box-shadow:0 4px 24px rgba(0,0,0,0.09);max-width:600px;">

      <!-- Header -->
      <tr>
        <td colspan="3"
            style="background:linear-gradient(135deg,#ff6b6b 0%,#ff9a3c 100%);
                   padding:32px 24px 28px;text-align:center;">
          <div style="font-size:40px;line-height:1;margin-bottom:8px;">🍽️</div>
          <h1 style="margin:0;color:#fff;font-size:24px;font-weight:700;
                     letter-spacing:-0.3px;">Weekly Family Menu</h1>
          <p style="margin:8px 0 0;color:rgba(255,255,255,0.88);font-size:15px;">
            {week_label}
          </p>
        </td>
      </tr>

      <!-- Column headers -->
      <tr style="background:#f8f8f8;">
        <td style="padding:11px 18px;font-size:11px;font-weight:700;color:#999;
                   text-transform:uppercase;letter-spacing:0.8px;
                   border-bottom:2px solid #ebebeb;">Day</td>
        <td style="padding:11px 18px;font-size:11px;font-weight:700;color:#999;
                   text-transform:uppercase;letter-spacing:0.8px;
                   border-bottom:2px solid #ebebeb;">🌅 Breakfast</td>
        <td style="padding:11px 18px;font-size:11px;font-weight:700;color:#999;
                   text-transform:uppercase;letter-spacing:0.8px;
                   border-bottom:2px solid #ebebeb;">🌙 Dinner</td>
      </tr>

      {rows}

      <!-- Footer -->
      <tr>
        <td colspan="3"
            style="padding:20px 24px;text-align:center;background:#f8f8f8;">
          <p style="margin:0;color:#bbb;font-size:12px;">
            Generated by your Weekly Menu Agent 🤖 • Have a delicious week!
          </p>
        </td>
      </tr>
    </table>
  </td></tr>
</table>
</body>
</html>"""

# ── Email ──────────────────────────────────────────────────────────────────────

def send_email(menu):
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"email_config.json not found at {CONFIG_FILE}\n"
            "Please fill in your Gmail settings (see README.md)."
        )

    with open(CONFIG_FILE) as f:
        config = json.load(f)

    sender   = config["sender_email"]
    password = config["sender_app_password"]

    # Support both "recipient_emails" (list) and legacy "recipient_email" (string)
    recipients = config.get("recipient_emails") or [config.get("recipient_email", sender)]
    if isinstance(recipients, str):
        recipients = [recipients]

    mon, _ = next_week_range()
    subject = f"🍽️ Weekly Menu — Week of {mon.strftime('%b %d, %Y')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Menu Agent 🍽️ <{sender}>"
    msg["To"]      = ", ".join(recipients)

    msg.attach(MIMEText(format_menu_text(menu), "plain"))
    msg.attach(MIMEText(format_menu_html(menu), "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, msg.as_string())

    print(f"✅ Email sent to: {', '.join(recipients)}")

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    preview_mode = "--preview" in sys.argv

    print("🍽️  Generating weekly menu…\n")
    menu = generate_menu(save_rotation=not preview_mode)

    print(format_menu_text(menu))
    print()

    if preview_mode:
        print("ℹ️  Preview mode — no email sent, rotation not updated.")
        return

    try:
        send_email(menu)
    except FileNotFoundError as e:
        print(f"⚠️  Email not sent: {e}")
    except KeyError as e:
        print(f"⚠️  Email not sent: Missing config key {e} in email_config.json")
    except smtplib.SMTPAuthenticationError:
        print("⚠️  Email not sent: Gmail authentication failed.\n"
              "    Make sure you're using an App Password (not your regular password).\n"
              "    See README.md for setup instructions.")
    except Exception as e:
        print(f"⚠️  Email not sent: {e}")

if __name__ == "__main__":
    main()
