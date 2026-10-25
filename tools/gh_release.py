#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create a GitHub release for a tag and upload assets (token from env GITHUB_TOKEN, never printed).

usage: GITHUB_TOKEN=... gh_release.py OWNER/REPO TAG TITLE NOTES.md ASSET...
"""
import json, os, sys, urllib.parse, urllib.request
from pathlib import Path

repo, tag, title, notes, *assets = sys.argv[1:]
tok = os.environ["GITHUB_TOKEN"]
H = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


def call(method, url, data=None, ctype="application/json"):
    req = urllib.request.Request(url, data=data, method=method, headers={**H, "Content-Type": ctype})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read() or b"{}")


api = f"https://api.github.com/repos/{repo}"
try:
    rel = call("GET", f"{api}/releases/tags/{tag}")
    print("release exists:", rel["html_url"])
except urllib.error.HTTPError as e:
    if e.code != 404:
        raise
    body = json.dumps({"tag_name": tag, "name": title, "body": Path(notes).read_text(), "draft": False,
                       "prerelease": False}).encode()
    rel = call("POST", f"{api}/releases", body)
    print("created:", rel["html_url"])
have = {a["name"] for a in rel.get("assets", [])}
upload = rel["upload_url"].split("{")[0]
for a in map(Path, assets):
    if a.name in have:
        print("asset exists:", a.name)
        continue
    res = call("POST", f"{upload}?name={urllib.parse.quote(a.name)}", a.read_bytes(), "application/x-7z-compressed")
    print("uploaded:", res["name"], res["size"], res["browser_download_url"])
