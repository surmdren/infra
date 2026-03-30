#!/usr/bin/env python3
"""Publish a post to LinkedIn using the ugcPosts API."""

import argparse
import json
import os
import sys

import requests

TOKEN_PATH = os.path.expanduser("~/.config/linkedin-publisher/token.json")


def load_token():
    if not os.path.exists(TOKEN_PATH):
        print("ERROR: No token found. Run auth.py first.")
        sys.exit(1)
    with open(TOKEN_PATH) as f:
        return json.load(f)


def get_person_urn(access_token):
    resp = requests.get(
        "https://api.linkedin.com/v2/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    resp.raise_for_status()
    person_id = resp.json()["id"]
    return f"urn:li:person:{person_id}"


def publish_post(access_token, author_urn, text, url=None):
    content = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE" if not url else "ARTICLE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    if url:
        content["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
            {
                "status": "READY",
                "originalUrl": url,
            }
        ]
        content["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"

    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        json=content,
    )

    if not resp.ok:
        print(f"ERROR {resp.status_code}: {resp.text}")
        sys.exit(1)

    post_id = resp.headers.get("x-restli-id", "unknown")
    return post_id


def main():
    parser = argparse.ArgumentParser(description="Publish a LinkedIn post")
    parser.add_argument("--text", required=True, help="Post text content")
    parser.add_argument("--url", help="Optional YouTube URL to attach")
    args = parser.parse_args()

    token_data = load_token()
    access_token = token_data["access_token"]

    print("Fetching LinkedIn profile...")
    author_urn = get_person_urn(access_token)
    print(f"Posting as: {author_urn}")

    print("Publishing post...")
    post_id = publish_post(access_token, author_urn, args.text, args.url)

    # LinkedIn post URL format
    person_id = author_urn.split(":")[-1]
    post_url = f"https://www.linkedin.com/feed/update/urn:li:ugcPost:{post_id}/"
    print(f"\nPost published successfully!")
    print(f"Post ID: {post_id}")
    print(f"View at: {post_url}")


if __name__ == "__main__":
    main()
