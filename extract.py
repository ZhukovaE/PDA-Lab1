import os
import re
import time
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NASA_API_KEY")
BASE_URL = "https://api.nasa.gov/neo/rest/v1/feed"
START = date(2024, 1, 1)
END = date(2026, 9, 30)
OUT_DIR = Path("data")
SLEEP_SECONDS = 0.5

OUT_DIR.mkdir(exist_ok=True)


def fetch_window(start, end):
    fname = OUT_DIR / f"feed_{start}_{end}.json"
    if fname.exists():
        print(f"[skip] {fname.name}")
        return
    params = {
        "start_date": str(start),
        "end_date": str(end),
        "api_key": API_KEY,
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    if r.status_code != 200:
        print("[ERR]", start, end, r.status_code)
        return
    safe_text = re.sub(r"api_key=[A-Za-z0-9]+", "api_key=***", r.text)
    fname.write_text(safe_text, encoding="utf-8")
    print(f"[ok] {start}..{end} remaining={r.headers.get('X-RateLimit-Remaining')}")

def main():
    cur = START
    while cur < END:
        window_end = min(cur + timedelta(days=6), END)
        fetch_window(cur, window_end)
        time.sleep(SLEEP_SECONDS)
        cur = window_end + timedelta(days=1)
    print("Готово")
if __name__ == "__main__":
    main()