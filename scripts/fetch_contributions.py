#!/usr/bin/env python3
from pathlib import Path
import datetime as dt
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
profile = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
username = os.getenv("GH_PROFILE_USER", profile["username"])
url = f"https://github.com/users/{username}/contributions"
out = ROOT / "data" / "contributions.json"


def parse_count(text):
    if not text or re.search(r"no contributions", text, re.I):
        return 0
    match = re.search(r"([0-9][0-9,]*)\s+contribution", text, re.I)
    return int(match.group(1).replace(",", "")) if match else 0


def fetch_html():
    last_error = None
    for attempt in range(3):
        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": "m-zia-rasa-profile/2.0",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last_error


def fetch_days():
    soup = BeautifulSoup(fetch_html(), "html.parser")
    cells = (
        soup.select("td.ContributionCalendar-day[data-date], rect.ContributionCalendar-day[data-date]")
        or soup.select("[data-date][data-level]")
    )
    days = {}

    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue

        level = int(cell.get("data-level") or 0)
        text = ""
        cell_id = cell.get("id")

        if cell_id:
            tip = soup.find("tool-tip", attrs={"for": cell_id})
            if tip:
                text = tip.get_text(" ", strip=True)

        if not text:
            text = cell.get("aria-label", "")

        days[date] = {
            "date": date,
            "count": parse_count(text),
            "level": level,
        }

    if not days:
        raise RuntimeError("GitHub contribution markup changed: no dated cells found.")

    return [days[key] for key in sorted(days)]


def calc(days):
    total = sum(day["count"] for day in days)
    active = sum(day["count"] > 0 for day in days)
    best = max(days, key=lambda day: day["count"]) if days else {"date": None, "count": 0}

    index = len(days) - 1
    streak = 0
    if index >= 0 and days[index]["count"] == 0:
        index -= 1
    while index >= 0 and days[index]["count"] > 0:
        streak += 1
        index -= 1

    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] > 0 else 0
        longest = max(longest, run)

    return {
        "total": total,
        "active_days": active,
        "current_streak": streak,
        "longest_streak": longest,
        "best_day": best,
    }


try:
    days = fetch_days()
except Exception as exc:
    print(f"Contribution refresh failed: {exc}", file=sys.stderr)
    raise SystemExit(1)

payload = {
    "username": username,
    "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "days": days,
    "stats": calc(days),
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"Fetched {len(days)} contribution days for {username}")
