#!/usr/bin/env python3
"""
Fetch top Hacker News stories related to AI/Agent topics.
Prints a JSON list of relevant stories to stdout.
"""
import json
import re
import urllib.request

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

KEYWORDS = [
    "agent", "agentic", "llm", "claude", "openai", "anthropic",
    "ai", "automation", "workflow", "copilot", "gpt", "foundation model",
    "multi-agent", "rag", "tool use", "langchain", "langgraph", "autogen",
]

MAX_STORIES = 30
MAX_RESULTS = 10


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read())


def is_relevant(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in KEYWORDS)


def main():
    story_ids = fetch_json(HN_TOP_URL)[:MAX_STORIES]
    results = []

    for story_id in story_ids:
        try:
            item = fetch_json(HN_ITEM_URL.format(story_id))
            title = item.get("title", "")
            url = item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
            score = item.get("score", 0)

            if is_relevant(title):
                results.append({
                    "source": "hackernews",
                    "title": title,
                    "url": url,
                    "score": score,
                })
                if len(results) >= MAX_RESULTS:
                    break
        except Exception:
            continue

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
