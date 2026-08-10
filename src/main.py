import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_DIR = Path("cache")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/alihassanwarsi/flyrank-polite-scraper)"
}


def fetch_page(url, cache_file):
    CACHE_DIR.mkdir(exist_ok=True)

    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")

        print(f"CACHE HIT: {url}")
        return html

    response = requests.get(url, headers=HEADERS, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch page: {response.status_code}")

    response.encoding = "utf-8"
    html = response.text

    cache_file.write_text(html, encoding="utf-8")

    print(f"FETCH: {url}")

    time.sleep(0.5)

    return html


def discover_books():
    current_url = PAGE_URL

    book_urls = []
    catalogue_pages = 0

    while catalogue_pages < 3:
        catalogue_pages += 1

        cache_file = CACHE_DIR / f"catalogue-page-{catalogue_pages}.html"

        html = fetch_page(current_url, cache_file)

        soup = BeautifulSoup(html, "html.parser")

        books = soup.select("article.product_pod h3 a")

        for book in books:
            relative_url = book.get("href")
            absolute_url = urljoin(current_url, relative_url)

            book_urls.append(absolute_url)

        if catalogue_pages == 3:
            break

        next_link = soup.select_one("li.next a")

        if next_link is None:
            break

        current_url = urljoin(current_url, next_link.get("href"))

    unique_urls = list(dict.fromkeys(book_urls))

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls


if __name__ == "__main__":
    discover_books()