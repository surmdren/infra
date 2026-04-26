#!/usr/bin/env python3
"""
Fetch latest AI/Agent papers from arXiv cs.AI and cs.MA.
Prints a JSON list of papers to stdout.
"""
import json
import urllib.request
import xml.etree.ElementTree as ET

ARXIV_API = "https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.MA&sortBy=submittedDate&sortOrder=descending&max_results=10"

NS = {"atom": "http://www.w3.org/2005/Atom"}

AGENT_KEYWORDS = [
    "agent", "agentic", "multi-agent", "tool use", "tool-use",
    "autonomous", "workflow", "orchestrat", "llm", "foundation model",
    "rag", "retrieval", "planning", "reasoning",
]


def is_agent_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(kw in text for kw in AGENT_KEYWORDS)


def main():
    req = urllib.request.Request(ARXIV_API, headers={"User-Agent": "linkedin-hot-topics/1.0 (mailto:rick@dreamwiseai.com)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read()

    root = ET.fromstring(content)
    results = []

    for entry in root.findall("atom:entry", NS):
        title = entry.findtext("atom:title", "", NS).strip().replace("\n", " ")
        summary = entry.findtext("atom:summary", "", NS).strip().replace("\n", " ")[:300]
        link_el = entry.find("atom:id", NS)
        url = link_el.text.strip() if link_el is not None else ""

        if is_agent_relevant(title, summary):
            results.append({
                "source": "arxiv",
                "title": title,
                "url": url,
                "summary": summary,
            })

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
