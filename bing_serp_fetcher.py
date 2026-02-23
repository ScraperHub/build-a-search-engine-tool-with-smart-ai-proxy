# Fetches a Bing SERP page via Crawlbase Smart AI Proxy (no autoparse).
# Parses HTML into the same structure as the Google autoparse output.
# Requires: pip install requests beautifulsoup4
#
# Usage:
#   export CRAWLBASE_TOKEN=your_token
#   python bing_serp_fetcher.py

import os
import re
import requests
from urllib.parse import quote_plus
from urllib3.exceptions import InsecureRequestWarning

from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def _parse_bing_html(html: str, url: str) -> dict:
    """
    Parse Bing SERP HTML into the same shape as Google autoparse body:
    { "ads": [], "peopleAlsoAsk": [], "snackPack": {}, "searchResults": [...] }
    """
    soup = BeautifulSoup(html, "html.parser")

    # Organic results: Bing uses li.b_algo
    search_results = []
    for i, li in enumerate(soup.find_all("li", class_="b_algo"), start=1):
        h2 = li.find("h2")
        a = h2.find("a") if h2 else None
        # Description: first <p> in the result (Bing uses .b_caption p or just p)
        desc_el = li.find("p") or li.find("div", class_=re.compile(r"b_caption|b_snippet"))
        desc_text = (desc_el.get_text(strip=True) if desc_el else "") or ""
        # Destination: domain / display URL (from link or cite)
        cite = li.find("cite")
        destination = (cite.get_text(strip=True) if cite else "") or ""
        if a and a.get("href"):
            search_results.append({
                "position": i,
                "title": a.get_text(strip=True) if a else "",
                "postDate": "",
                "url": a.get("href", ""),
                "destination": destination,
                "description": desc_text,
                "additionalData": {"followers": ""},
            })

    # Ads: Bing often uses .b_ad or similar; same canonical keys as searchResults/ad shape
    ads = []
    for li in soup.find_all("li", class_=re.compile(r"b_ad|b_ans")):
        h2 = li.find("h2")
        a = h2.find("a") if h2 else None
        p = li.find("p")
        cite = li.find("cite")
        if a and a.get("href"):
            ads.append({
                "position": len(ads) + 1,
                "title": a.get_text(strip=True) if a else "",
                "url": a.get("href", ""),
                "destination": cite.get_text(strip=True) if cite else "",
                "description": p.get_text(strip=True) if p else "",
            })

    return {
        "ads": ads,
        "peopleAlsoAsk": [],
        "snackPack": {},
        "searchResults": search_results,
    }


def fetch_bing_serp(crawlbase_token: str, query: str) -> dict:
    """
    Fetch Bing SERP for the given query using Smart AI Proxy (no autoparse).
    Returns a dict in the same format as the Google fetcher's autoparse output:
    { "original_status", "pc_status", "url", "body": { "ads", "peopleAlsoAsk", "snackPack", "searchResults" } }

    Args:
        crawlbase_token: Crawlbase Smart AI Proxy token.
        query: Search query string.
    """
    proxy_https = f"https://{crawlbase_token}:@smartproxy.crawlbase.com:8013"
    proxies = {"http": proxy_https, "https": proxy_https}

    encoded_query = quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded_query}"
    # No autoparse: raw HTML is parsed locally. No country parameter (geo requires Premium).
    headers = {"CrawlbaseAPI-Parameters": ""}

    response = requests.get(
        url,
        headers=headers,
        proxies=proxies,
        verify=False,
        timeout=30,
    )
    response.raise_for_status()
    html = response.text
    body = _parse_bing_html(html, url)
    return {
        "original_status": response.status_code,
        "pc_status": response.status_code,
        "url": url,
        "body": body,
    }


if __name__ == "__main__":
    crawlbase_token = os.environ.get("CRAWLBASE_TOKEN", "YOUR_CRAWLBASE_TOKEN")
    data = fetch_bing_serp(crawlbase_token, "best coffee shops Paris")
    keys = list(data.keys()) if isinstance(data, dict) else []
    print(f"Fetched keys: {keys}")
