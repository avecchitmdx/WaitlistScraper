import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timezone

URL = "https://unos.org/transplant/frequently-asked-questions/"
OUTPUT = "waitlist.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def scrape():
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    # Extract total waitlist number
    count_match = re.search(
        r"([\d,]+)\s+people need a lifesaving organ transplant",
        text
    )
    if not count_match:
        raise ValueError("Could not find waitlist number on page")

    raw = count_match.group(1)
    total = int(raw.replace(",", ""))

    # Extract timestamp shown on UNOS page e.g. "9:44pm EDT"
    time_match = re.search(
        r"Totals as of today\s+([\d]+:[\d]+(?:am|pm)\s+[A-Z]+)",
        text,
        re.IGNORECASE
    )
    unos_time = time_match.group(1).strip() if time_match else None

    # Build display string: "May 20, 2026 at 9:44pm EDT"
    today = datetime.now(timezone.utc).strftime("%B %-d, %Y")
    as_of = today

    data = {
        "total": total,
        "total_formatted": raw,
        "as_of": as_of,
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": URL
    }

    with open(OUTPUT, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Wrote {raw} (as of {as_of}) to {OUTPUT}")

if __name__ == "__main__":
    scrape()
