#!/usr/bin/env bash
# Upload one file into an EventPics event with curl and jq.
#
#   export EVENTPICS_API_KEY=your_key
#   ./upload.sh --list
#   ./upload.sh LINK_ID photo.jpg [ALBUM_ID]
set -euo pipefail

API="https://api.event.pics"
: "${EVENTPICS_API_KEY:?Set EVENTPICS_API_KEY first.}"

if [ "${1:-}" = "--list" ]; then
  curl -fsS -H "Authorization: Bearer $EVENTPICS_API_KEY" "$API/geteventsandalbums" | jq .
  exit 0
fi

LINK_ID="${1:?Usage: ./upload.sh LINK_ID FILE [ALBUM_ID]}"
FILE="${2:?Usage: ./upload.sh LINK_ID FILE [ALBUM_ID]}"
ALBUM_ID="${3:-}"
TYPE="$(file --brief --mime-type "$FILE")"

BODY="$(jq -n --arg key "$EVENTPICS_API_KEY" --arg link "$LINK_ID" --arg name "$(basename "$FILE")" \
  --arg album "$ALBUM_ID" --argjson size "$(wc -c < "$FILE" | tr -d ' ')" \
  '{apiKey: $key, linkId: $link, fileName: $name, fileSize: $size} + (if $album == "" then {} else {albumId: $album} end)')"

RESPONSE="$(curl -fsS -X POST -H "Content-Type: application/json" -d "$BODY" "$API/getuploadurl")"
UPLOAD_URL="$(echo "$RESPONSE" | jq -r .uploadUrl)"

curl -fsS -X PUT -H "Content-Type: $TYPE" --data-binary "@$FILE" "$UPLOAD_URL"
echo "$FILE -> $(echo "$RESPONSE" | jq -r .mediaUrl)"
