# Unified SERP fetcher: Google or Bing via Crawlbase Smart AI Proxy.
# Requires: pip install requests beautifulsoup4
#
# Usage:
#   export CRAWLBASE_TOKEN=your_token
#   python serp_fetcher.py

import json
import os

# Engine-specific fetchers: (crawlbase_token, query). No country parameter.
from google_serp_fetcher import fetch_google_serp
from bing_serp_fetcher import fetch_bing_serp

CRAWLBASE_TOKEN = os.environ.get("CRAWLBASE_TOKEN", "YOUR_CRAWLBASE_TOKEN")


def _normalize_search_result(item: dict) -> dict:
    """Ensure each search result has the same keys; fill missing with defaults."""
    if not isinstance(item, dict):
        return {
            "position": 0,
            "title": "",
            "postDate": "",
            "url": "",
            "destination": "",
            "description": "",
            "additionalData": {"followers": ""},
        }
    additional = item.get("additionalData")
    if not isinstance(additional, dict):
        additional = {}
    followers = str(additional.get("followers", "") or "")
    return {
        "position": int(item.get("position", 0)) if item.get("position") is not None else 0,
        "title": str(item.get("title", "") or ""),
        "postDate": str(item.get("postDate", "") or ""),
        "url": str(item.get("url", "") or ""),
        "destination": str(item.get("destination", "") or ""),
        "description": str(item.get("description", "") or ""),
        "additionalData": {"followers": followers},
    }


def _normalize_ad(item: dict) -> dict:
    """Ensure each ad has the same keys; fill missing with defaults."""
    if not isinstance(item, dict):
        return {"position": 0, "title": "", "url": "", "destination": "", "description": ""}
    return {
        "position": int(item.get("position", 0)) if item.get("position") is not None else 0,
        "title": str(item.get("title", "") or ""),
        "url": str(item.get("url", "") or ""),
        "destination": str(item.get("destination", "") or ""),
        "description": str(item.get("description", "") or ""),
    }


def _normalize_serp_response(raw: dict) -> dict:
    """
    Normalize engine response to a single uniform shape.

    Raises RuntimeError if original_status or pc_status is not 200.
    Ensures body has ads, peopleAlsoAsk, snackPack, searchResults with canonical keys per item.
    """
    orig = int(raw.get("original_status", 0))
    pc = int(raw.get("pc_status", 0))
    if orig != 200 or pc != 200:
        raise RuntimeError(
            f"SERP request failed: original_status={orig}, pc_status={pc} (expected 200). url={raw.get('url', '')}"
        )
    body = raw.get("body")
    if not isinstance(body, dict):
        body = {}
    ads = list(body.get("ads") or [])
    people_also_ask = list(body.get("peopleAlsoAsk") or [])
    snack_pack = body.get("snackPack") if isinstance(body.get("snackPack"), dict) else {}
    search_results = list(body.get("searchResults") or [])
    return {
        "original_status": 200,
        "pc_status": 200,
        "url": str(raw.get("url", "") or ""),
        "body": {
            "ads": [_normalize_ad(a) for a in ads],
            "peopleAlsoAsk": people_also_ask,
            "snackPack": snack_pack,
            "searchResults": [_normalize_search_result(r) for r in search_results],
        },
    }


def fetch_serp(query: str, engine: str = "google") -> dict:
    """
    Fetch SERP from the given search engine using Crawlbase Smart AI Proxy.

    Returns a normalized dict: original_status=200, pc_status=200, url, and body with
    ads, peopleAlsoAsk, snackPack, searchResults (each item has uniform keys).
    Raises RuntimeError if original_status or pc_status is not 200.

    Args:
        query: Search query string.
        engine: Search engine to use: "google" (JSON via autoparse) or "bing" (HTML parsed to same format).

    Returns:
        Dict with original_status=200, pc_status=200, url, and body (searchResults, ads, etc.).
    """
    engine = (engine or "google").strip().lower()
    if engine not in ("google", "bing"):
        raise ValueError(f"engine must be 'google' or 'bing', got: {engine!r}")

    if engine == "google":
        raw = fetch_google_serp(CRAWLBASE_TOKEN, query)
    else:
        raw = fetch_bing_serp(CRAWLBASE_TOKEN, query)
    return _normalize_serp_response(raw)


if __name__ == "__main__":
    import sys
    engine = sys.argv[1] if len(sys.argv) > 1 else "google"
    data = fetch_serp("best coffee shops Paris", engine=engine)
    print(f"Engine: {engine}")
    print(f"Status: {data.get('original_status')}, URL: {data.get('url')}")
    results = data.get("body", {}).get("searchResults", [])
    print(f"Search results count: {len(results)}")
    if results:
        print("First result:", json.dumps(results[0], indent=2))
