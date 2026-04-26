#!/usr/bin/env python3
"""LinkedIn OAuth 2.0 authorization flow."""

import json
import os
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests

TOKEN_PATH = os.path.expanduser("~/.config/linkedin-publisher/token.json")
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "openid profile w_member_social"

CLIENT_ID = os.environ["LINKEDIN_CLIENT_ID"]
CLIENT_SECRET = os.environ["LINKEDIN_CLIENT_SECRET"]

auth_code = None
state_token = secrets.token_urlsafe(16)


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = parse_qs(urlparse(self.path).query)
        if params.get("state", [None])[0] != state_token:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"State mismatch. Please try again.")
            return
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Authorization successful. You can close this tab.</h2>")

    def log_message(self, format, *args):
        pass


def run_server():
    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server.handle_request()


auth_url = "https://www.linkedin.com/oauth/v2/authorization?" + urlencode({
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "state": state_token,
})

print("Starting local callback server...")
t = threading.Thread(target=run_server)
t.start()

print(f"Opening browser for LinkedIn authorization...")
webbrowser.open(auth_url)

t.join(timeout=120)

if not auth_code:
    print("ERROR: No authorization code received. Did you authorize in the browser?")
    exit(1)

print("Exchanging code for token...")
resp = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
})
resp.raise_for_status()
token_data = resp.json()

os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
with open(TOKEN_PATH, "w") as f:
    json.dump(token_data, f, indent=2)

print(f"Token saved to {TOKEN_PATH}")
print(f"Access token expires in: {token_data.get('expires_in', 'unknown')} seconds")
