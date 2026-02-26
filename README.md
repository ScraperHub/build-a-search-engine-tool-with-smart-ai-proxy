<a href="https://crawlbase.com/signup?utm_source=github&utm_medium=readme&utm_campaign=crawling_api_banner" target="_blank">
  <img src="https://github.com/user-attachments/assets/afa4f6e7-25fb-442c-af2f-b4ddcfd62ab2" 
       alt="crawling-api-cta" 
       style="max-width: 100%; border: 0;">
</a>

We invite you to explore our [blog](https://crawlbase.com/blog/how-to-build-search-engine-tool/?utm_source=github&utm_medium=referral&utm_campaign=scraperhub&ref=gh_scraperhub) for more details.

# SERP Fetcher Example (Crawlbase Smart AI Proxy)

Minimal Python example that fetches a Google SERP using **Crawlbase Smart AI Proxy** as the data collection layer. Used in the blog: [Build a Search Engine Tool with Smart AI Proxy](../draft/build-a-search-engine-tool-with-smart-ai-proxy.md).

## Prerequisites

- A [Crawlbase](https://crawlbase.com) account and **Smart AI Proxy** token.
- Set `CRAWLBASE_TOKEN` to your token (or replace `YOUR_CRAWLBASE_TOKEN` in code; not recommended for production).

## Run

**Google (JSON via autoparse):**
```bash
pip install requests
export CRAWLBASE_TOKEN=your_token
python google_serp_fetcher.py
```

**Bing (HTML parsed to same format):**
```bash
pip install requests beautifulsoup4
export CRAWLBASE_TOKEN=your_token
python bing_serp_fetcher.py
```

**Unified (Google or Bing by `engine`):**
```bash
pip install requests beautifulsoup4
export CRAWLBASE_TOKEN=your_token
python serp_fetcher.py              # default: google
python serp_fetcher.py bing         # Bing
```

## What it does

- Builds a search URL for the query (e.g. Google or Bing).
- Sends a GET request through Smart AI Proxy. Google uses `CrawlbaseAPI-Parameters: autoparse=true`; no country parameter (geo requires Crawlbase Premium).
- Returns structured SERP data (dict): organic results, ads, and snippets. Use `serp_fetcher.fetch_serp` for a normalized shape and status checks.

### `bing_serp_fetcher.py`

- Fetches **Bing** SERP via Smart AI Proxy **without** `autoparse=true` (raw HTML).
- Parses the HTML with BeautifulSoup and returns a dict in the **same shape** as the Google autoparse output: `body.searchResults`, `body.ads`, `body.peopleAlsoAsk`, `body.snackPack`, so you can use one unified format across engines.

### `serp_fetcher.py` (unified)

- Single entry point: **`fetch_serp(query, engine="google")`**.
- **Parameters:** `query`, `engine` (`"google"` or `"bing"`). No country parameter (geo not allowed on free tier).
- Returns a **normalized dict** with `original_status=200`, `pc_status=200`, `url`, and `body` (`searchResults`, `ads`, `peopleAlsoAsk`, `snackPack`) so both engines share the same property names. **Raises `RuntimeError`** if the request returns a non-200 status.

## Docs

- [Smart AI Proxy](https://crawlbase.com/docs/smart-proxy/)
- [Smart Proxy Parameters](https://crawlbase.com/docs/smart-proxy/parameters/)
