# FlyRank Polite Scraper

A polite web scraping pipeline built for the FlyRank AI Backend Internship.

The scraper collects book data from the first 3 catalogue pages of Books to Scrape, validates the records, stores them as JSON, survives a broken page, and creates a report at the end of every run.

## Target Classification

**Target:** Books to Scrape

**Purpose:** Books to Scrape is a public practice sandbox created for learning and testing web scraping.

**Scope:** Only the first 3 catalogue pages are scraped, covering 60 books.

**Data collected:**

- Title
- Product URL
- Price
- Availability
- Rating
- Description
- Source page
- Fetch time

**robots.txt result:** No robots file found (404 Not Found).

This target is appropriate because it is specifically designed as a scraping sandbox, and this project uses a limited scope with polite fetching and caching.

I will not reuse this code on another site without checking its rules and terms first.

## Tech Stack

- Python
- Requests
- Beautiful Soup
- Pydantic

## How It Works

The scraper follows this pipeline:

**Fetch → Extract → Normalize → Validate → Store → Report**

It first discovers the 60 books from the first 3 catalogue pages.

Each book page is then fetched and cached locally.

The required information is extracted from the HTML, cleaned, validated using Pydantic, and stored in JSON format.

A run report is generated at the end showing what happened during the run.

## Installation

Clone the repository:

```bash
git clone https://github.com/alihassanwarsi/flyrank-polite-scraper.git
cd flyrank-polite-scraper
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Run

Run the scraper with:

```bash
python src/main.py
```

After the run, the project creates:

```text
output/
├── books.json
├── errors.json
└── run-report.json
```

## Record Schema

Each validated book record contains:

```json
{
    "title": "A Light in the Attic",
    "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "price_text": "£51.77",
    "price_gbp": 51.77,
    "availability_text": "In stock (22 available)",
    "rating_text": "Three",
    "description": "...",
    "source_page": "https://books.toscrape.com/catalogue/page-1.html",
    "fetched_at": "2026-08-10T20:50:55.362809+00:00"
}
```

The original price text is kept while `price_gbp` stores the cleaned numeric value.

The product URL is used as the unique identity of each record so rerunning the scraper does not create duplicate books.

## Politeness Rules

The scraper follows these rules to avoid making unnecessary requests:

- Every real request sends an identifying User-Agent.
- Every request has a timeout.
- The response status code is checked before processing HTML.
- The scraper waits at least 0.5 seconds between real requests.
- Downloaded HTML pages are cached locally and reused during development.
- Cached pages do not create another request to the website.
- 404 and 403 responses are not repeatedly retried.
- Temporary server errors and network failures are retried once.

The `cache/` directory is ignored by Git and is not included in the repository.

## Failure Handling

The scraper handles each book page separately so one broken page does not crash the whole run.

For testing, one deliberately fake book URL was added.

The fake page returns a 404 response and is skipped, while all 60 valid book records are still processed and stored successfully.

The failure is recorded inside `run-report.json`.

## Example Run Report

```json
{
    "start_time": "2026-08-10T21:17:56.030869+00:00",
    "duration_seconds": 2.433593,
    "pages_fetched": 0,
    "cache_hits": 63,
    "valid_records": 60,
    "invalid_records": 0,
    "failed_pages": 1,
    "failures": [
        {
            "url": "https://books.toscrape.com/catalogue/fake-book-does-not-exist/index.html",
            "reason": "Failed to fetch page: 404"
        }
    ]
}
```

This report came from a cached rerun, which is why `pages_fetched` is `0` and `cache_hits` is `63`.

The 63 cache hits come from:

- 3 catalogue pages
- 60 book detail pages

The deliberately broken URL was not cached and was recorded as one failed page.

## Output

### books.json

Contains the 60 cleaned and validated book records.

### errors.json

Contains records that failed schema validation together with the reason they failed.

### run-report.json

Contains information about the scraper run, including:

- Start time
- Duration
- Pages fetched
- Cache hits
- Valid records
- Invalid records
- Failed pages

## Why No Browser Was Needed

This assignment did not require Selenium, Playwright, or another browser automation tool because the book data is already present in the HTML returned by the server.

A normal HTTP request using Requests is enough to access the required data.

Using a browser would only add unnecessary cost and complexity for this target.

## Limitation

The scraper depends on the current HTML structure of Books to Scrape.

If the website changes its HTML structure or CSS classes, some selectors may need to be updated.

## Ethics

Web scraping should be done responsibly.

I would use an official API when one exists, never bypass logins, paywalls, blocks, or access restrictions, and only collect the data needed for the task.