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
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    resp.raise_for_status()
    person_id = resp.json()["sub"]
    return f"urn:li:person:{person_id}"


def upload_image(access_token, author_urn, image_path):
    """Upload an image to LinkedIn and return the asset URN."""
    # Step 1: Register upload
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }
    resp = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json=register_payload,
    )
    if not resp.ok:
        print(f"ERROR registering image upload {resp.status_code}: {resp.text}")
        sys.exit(1)

    data = resp.json()
    upload_url = data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset_urn = data["value"]["asset"]

    # Step 2: Upload image binary
    with open(image_path, "rb") as f:
        image_data = f.read()

    put_resp = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {access_token}"},
        data=image_data,
    )
    if not put_resp.ok:
        print(f"ERROR uploading image {put_resp.status_code}: {put_resp.text}")
        sys.exit(1)

    print(f"Image uploaded: {asset_urn}")
    return asset_urn


def publish_post(access_token, author_urn, text, url=None, image_path=None, image_paths=None):
    media_list = []

    # Support multiple images (carousel) or single image
    all_images = image_paths or ([image_path] if image_path else [])

    for img in all_images:
        asset_urn = upload_image(access_token, author_urn, img)
        media_list.append({
            "status": "READY",
            "media": asset_urn,
        })

    if not all_images and url:
        media_list.append({
            "status": "READY",
            "originalUrl": url,
        })

    if all_images:
        category = "IMAGE"
    elif url:
        category = "ARTICLE"
    else:
        category = "NONE"

    share_content = {
        "shareCommentary": {"text": text},
        "shareMediaCategory": category,
    }
    if media_list:
        share_content["media"] = media_list

    content = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": share_content,
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

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
    parser.add_argument("--image", help="Single image path to attach")
    parser.add_argument("--images", nargs="+", help="Multiple image paths for carousel (e.g. --images p1.png p2.png p3.png)")
    args = parser.parse_args()

    token_data = load_token()
    access_token = token_data["access_token"]

    print("Fetching LinkedIn profile...")
    author_urn = get_person_urn(access_token)
    print(f"Posting as: {author_urn}")

    print("Publishing post...")
    post_id = publish_post(access_token, author_urn, args.text, args.url, args.image, args.images)

    # LinkedIn post URL format
    person_id = author_urn.split(":")[-1]
    post_url = f"https://www.linkedin.com/feed/update/urn:li:ugcPost:{post_id}/"
    print(f"\nPost published successfully!")
    print(f"Post ID: {post_id}")
    print(f"View at: {post_url}")


if __name__ == "__main__":
    main()
