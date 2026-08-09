from pathlib import Path

import requests


PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/alihassanwarsi/flyrank-polite-scraper)"
}


def fetch_page():
    CACHE_DIR.mkdir(exist_ok=True)

    if CACHE_FILE.exists():
        html = CACHE_FILE.read_text(encoding="utf-8")

        print("CACHE HIT")
        print(f"response_size={len(html.encode('utf-8'))} bytes")

        return html

    response = requests.get(PAGE_URL, headers=HEADERS, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch page: {response.status_code}")

    html = response.text

    CACHE_FILE.write_text(html, encoding="utf-8")

    print("FETCH")
    print(f"response_size={len(html.encode('utf-8'))} bytes")

    return html


if __name__ == "__main__":
    fetch_page()