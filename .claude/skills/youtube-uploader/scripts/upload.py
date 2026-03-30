#!/usr/bin/env python3
"""YouTube uploader — DreamWise AI"""

import argparse
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_SECRET = Path.home() / ".config/youtube-uploader/client_secret.json"
TOKEN_FILE    = Path.home() / ".config/youtube-uploader/token.pkl"
SCOPES        = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return creds

def upload(video_path, title, description, thumbnail_path=None, privacy="private", tags=None):
    creds   = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    snippet = {
        "title":       title,
        "description": description,
        "categoryId":  "28",   # Science & Technology
    }
    if tags:
        snippet["tags"] = tags

    body = {
        "snippet": snippet,
        "status":  {"privacyStatus": privacy},
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
    print(f"Uploading: {video_path}")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", end="\r")

    video_id = response["id"]
    print(f"\nDone! https://youtu.be/{video_id}")

    if thumbnail_path:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print("Thumbnail uploaded.")

    return video_id

def update(video_id, title=None, description=None, thumbnail_path=None, tags=None, privacy=None):
    """Update metadata of an already-uploaded video."""
    creds   = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    # Fetch current snippet to avoid wiping fields we're not changing
    current = youtube.videos().list(part="snippet,status", id=video_id).execute()
    if not current["items"]:
        print(f"Video {video_id} not found.")
        return

    snippet = current["items"][0]["snippet"]
    status  = current["items"][0]["status"]

    if title:       snippet["title"]       = title
    if description: snippet["description"] = description
    if tags:        snippet["tags"]        = tags

    if privacy:     status["privacyStatus"] = privacy

    youtube.videos().update(
        part="snippet,status",
        body={"id": video_id, "snippet": snippet, "status": status}
    ).execute()
    print(f"Updated! https://youtu.be/{video_id}")

    if thumbnail_path:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print("Thumbnail updated.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")

    # upload subcommand
    up = sub.add_parser("upload", help="Upload a new video")
    up.add_argument("video",       help="Path to video file")
    up.add_argument("--title",     required=True)
    up.add_argument("--desc",      required=True)
    up.add_argument("--thumbnail", help="Path to thumbnail PNG")
    up.add_argument("--privacy",   default="private", choices=["private","unlisted","public"])
    up.add_argument("--tags",      nargs="+", help="Space-separated tags")

    # update subcommand
    ud = sub.add_parser("update", help="Update an existing video's metadata")
    ud.add_argument("video_id",    help="YouTube video ID (e.g. t16T7konb9w)")
    ud.add_argument("--title",     help="New title")
    ud.add_argument("--desc",      help="New description")
    ud.add_argument("--thumbnail", help="New thumbnail PNG")
    ud.add_argument("--privacy",   choices=["private","unlisted","public"])
    ud.add_argument("--tags",      nargs="+", help="Space-separated tags")

    args = p.parse_args()

    if args.cmd == "upload":
        upload(args.video, args.title, args.desc, args.thumbnail, args.privacy, args.tags)
    elif args.cmd == "update":
        update(args.video_id, args.title, args.desc, args.thumbnail, args.tags, args.privacy)
    else:
        p.print_help()
