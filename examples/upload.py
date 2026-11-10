#!/usr/bin/env python3
"""Upload photos or videos into an EventPics event. Python 3, standard library only.

  export EVENTPICS_API_KEY=your_key
  python3 upload.py --list
  python3 upload.py --event LINK_ID [--album ALBUM_ID] FILE [FILE ...]
"""
import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request

API = "https://api.event.pics"
# Python's default "Python-urllib" user agent is refused by the API's edge protection.
USER_AGENT = "eventpics-api-example/1.0"


def request(method, url, data=None, headers=None):
    headers = dict(headers or {}, **{"User-Agent": USER_AGENT})
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as response:
        body = response.read()
        return json.loads(body) if body else None


def list_events(key):
    data = request("GET", API + "/geteventsandalbums", headers={"Authorization": "Bearer " + key})
    for event in data["events"]:
        print("%s  %s" % (event["linkId"], event["title"]))
        for album in event.get("albums", []):
            print("    album %s  %s" % (album["id"], album["title"]))


def upload(key, link_id, album_id, path):
    body = {
        "apiKey": key,
        "linkId": link_id,
        "fileName": os.path.basename(path),
        "fileSize": os.path.getsize(path),
        "takenAt": int(os.path.getmtime(path) * 1000),
    }
    if album_id:
        body["albumId"] = album_id
    urls = request("POST", API + "/getuploadurl", data=json.dumps(body).encode(),
                   headers={"Content-Type": "application/json"})
    content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as handle:
        request("PUT", urls["uploadUrl"], data=handle.read(), headers={"Content-Type": content_type})
    print("%s -> %s" % (path, urls["mediaUrl"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="list events and albums")
    parser.add_argument("--event", help="the event's linkId")
    parser.add_argument("--album", help="optional album id")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()
    key = os.environ.get("EVENTPICS_API_KEY")
    if not key:
        sys.exit("Set EVENTPICS_API_KEY first.")
    if args.list:
        list_events(key)
        return
    if not args.event or not args.files:
        sys.exit("Use --list, or --event LINK_ID with one or more files.")
    for path in args.files:
        upload(key, args.event, args.album, path)


def run():
    try:
        main()
    except urllib.error.HTTPError as error:
        sys.exit("HTTP %d: %s" % (error.code, error.read().decode("utf-8", "replace")[:200]))


if __name__ == "__main__":
    run()
