# Fetches a Google SERP page via Crawlbase Smart AI Proxy.
# Requires: pip install requests
#
# Usage:
#   export CRAWLBASE_TOKEN=your_token
#   python google_serp_fetcher.py

import json
import os
import requests
from urllib.parse import quote_plus
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def fetch_google_serp(crawlbase_token: str, query: str) -> dict:
    """
    Fetch Google SERP for the given query using Crawlbase Smart AI Proxy.

    Uses autoparse=true; response is JSON. Returns the parsed dict as returned
    by Crawlbase (original_status, pc_status, url, body). For a normalized
    shape shared with Bing, use serp_fetcher.fetch_serp(..., engine="google").
    """
    proxy_https = f"https://{crawlbase_token}:@smartproxy.crawlbase.com:8013"
    proxies = {"http": proxy_https, "https": proxy_https}

    encoded_query = quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    params_header = "autoparse=true"
    headers = {"CrawlbaseAPI-Parameters": params_header}

    response = requests.get(
        url,
        headers=headers,
        proxies=proxies,
        verify=False,
        timeout=30,
    )
    response.raise_for_status()
    return json.loads(response.text)


if __name__ == "__main__":
    crawlbase_token = os.environ.get("CRAWLBASE_TOKEN", "YOUR_CRAWLBASE_TOKEN")
    data = fetch_google_serp(crawlbase_token, "best coffee shops Paris")
    keys = list(data.keys()) if isinstance(data, dict) else []
    print(f"Fetched keys: {keys}")
