#!/usr/bin/env python3
"""
Fetch recent WeChat articles from wewe-rss Atom feed.
Reads WEWE_RSS_FEED_URL from environment.
Prints a JSON list of articles to stdout.
"""
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

FEED_URL = os.environ.get("WEWE_RSS_FEED_URL", "")
MAX_AGE_HOURS = 48
MAX_RESULTS = 10

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "": "http://www.w3.org/2005/Atom",
}


def parse_date(date_str: str):
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()[:300]


def main():
    if not FEED_URL:
        print("[]")
        return

    try:
        with urllib.request.urlopen(FEED_URL, timeout=10) as resp:
            content = resp.read()
    except Exception as e:
        print(f"ERROR fetching WeChat feed: {e}", file=sys.stderr)
        print("[]")
        return

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"ERROR parsing feed XML: {e}", file=sys.stderr)
        print("[]")
        return

    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    results = []

    # Handle both namespaced and plain Atom feeds
    entries = root.findall("{http://www.w3.org/2005/Atom}entry") or root.findall("entry")

    for entry in entries:
        def find_text(tag):
            el = entry.find(f"{{http://www.w3.org/2005/Atom}}{tag}") or entry.find(tag)
            return el.text.strip() if el is not None and el.text else ""

        title = find_text("title")
        link_el = entry.find("{http://www.w3.org/2005/Atom}link") or entry.find("link")
        url = link_el.get("href", "") if link_el is not None else ""
        author_el = entry.find("{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name") or entry.find("author/name")
        author = author_el.text.strip() if author_el is not None and author_el.text else "未知公众号"
        published = find_text("published") or find_text("updated")
        summary_raw = find_text("summary")
        summary = strip_html(summary_raw)

        pub_date = parse_date(published)
        if pub_date and pub_date < cutoff:
            continue

        if title:
            results.append({
                "source": "wechat",
                "title": title,
                "url": url,
                "account": author,
                "summary": summary,
            })
            if len(results) >= MAX_RESULTS:
                break

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
