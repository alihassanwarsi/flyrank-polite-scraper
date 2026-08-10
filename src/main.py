import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, ValidationError



PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_DIR = Path("cache")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/alihassanwarsi/flyrank-polite-scraper)"
}

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: str
    fetched_at: str

def fetch_page(url, cache_file):
    cache_file.parent.mkdir(parents=True, exist_ok=True)

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

            book_urls.append({
                "product_url": absolute_url,
                "source_page": current_url
            })

        if catalogue_pages == 3:
            break

        next_link = soup.select_one("li.next a")

        if next_link is None:
            break

        current_url = urljoin(current_url,next_link.get("href"))

    unique_books = {}

    for book in book_urls:
        unique_books[book["product_url"]] = book

    unique_books = list(unique_books.values())

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(unique_books)}")

    return unique_books


def get_detail_cache_file(url):
    path = urlparse(url).path
    slug = path.strip("/").split("/")[-2]

    return CACHE_DIR / "books" / f"{slug}.html"


def extract_book(product_url, source_page):
    cache_file = get_detail_cache_file(product_url)

    html = fetch_page(product_url, cache_file)

    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("div.product_main h1").get_text(strip=True)

    price_text = soup.select_one("div.product_main p.price_color").get_text(strip=True)

    availability_text = soup.select_one("div.product_main p.instock.availability").get_text(" ", strip=True)

    rating_element = soup.select_one("div.product_main p.star-rating")

    rating_text = rating_element.get("class")[1]

    description_element = soup.select_one("#product_description + p")

    if description_element:
        description = description_element.get_text(strip=True)
    else:
        description = None

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

def normalize_book(raw_record):
    price_text = raw_record["price_text"]

    price_gbp = float(
        price_text.replace("£", "").strip()
    )

    normalized_record = {
        "title": raw_record["title"],
        "product_url": raw_record["product_url"],
        "price_text": raw_record["price_text"],
        "price_gbp": price_gbp,
        "availability_text": raw_record["availability_text"],
        "rating_text": raw_record["rating_text"],
        "description": raw_record["description"],
        "source_page": raw_record["source_page"],
        "fetched_at": raw_record["fetched_at"]
    }

    return normalized_record


def validate_book(raw_record):
    normalized_record = normalize_book(raw_record)

    if not normalized_record["product_url"].startswith("https://"):
        raise ValueError("product_url must start with https://")

    if not normalized_record["source_page"].startswith("https://"):
        raise ValueError("source_page must start with https://")

    book = BookRecord(**normalized_record)

    return book




def save_records(raw_records):
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    valid_records = []
    errors = []

    for raw_record in raw_records:
        try:
            book = validate_book(raw_record)

            valid_records.append(
                book.model_dump()
            )

        except (ValidationError, ValueError) as error:
            errors.append({
                "record": raw_record,
                "reason": str(error)
            })

    unique_records = {}

    for record in valid_records:
        unique_records[record["product_url"]] = record

    valid_records = list(unique_records.values())

    books_file = output_dir / "books.json"
    errors_file = output_dir / "errors.json"

    books_file.write_text(
        json.dumps(
            valid_records,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    errors_file.write_text(
        json.dumps(
            errors,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")

if __name__ == "__main__":
    books = discover_books()

    raw_records = []

    for book in books:
        record = extract_book(
            book["product_url"],
            book["source_page"]
        )

        raw_records.append(record)

    print(raw_records[0])
    print(f"detail_pages={len(raw_records)}")

    save_records(raw_records)