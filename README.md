# EventPics API

EventPics is the photo sharing app for weddings and parties. Guests scan a QR code, and all photos come together in one shared album in original quality. Free to use.

This repository documents the public API for uploading photos and videos into an EventPics event automatically, for example from a photo booth, a camera tethering tool or a photographer's workflow. Full guide: [event.pics/en/tutorial/api.html](https://event.pics/en/tutorial/api.html).

## How it works

1. **Get an API key** in the EventPics app or web app: open your event and go to the API key management.
2. **List your events and albums:** `GET https://api.event.pics/geteventsandalbums` with `Authorization: Bearer <API_KEY>`.
3. **Request an upload URL:** `POST https://api.event.pics/getuploadurl` with `apiKey`, the event's `linkId`, the `fileName` and optionally `albumId`, `fileSize` and `takenAt`.
4. **Upload the file:** `PUT` the bytes to the returned `uploadUrl` with a matching `Content-Type`. No auth header is needed. The URL is valid for 30 minutes.

The response also gives you `mediaUrl`, a short page for this one photo that fits in a QR code, so a guest can scan it at the photo booth and see their own picture, and `downloadUrl`, the file itself.

Maximum file size: 95 MB.

## Files

| File | Content |
|---|---|
| [`openapi.yaml`](openapi.yaml) | OpenAPI 3.1 description of both endpoints |
| [`examples/upload.sh`](examples/upload.sh) | curl and jq |
| [`examples/upload.py`](examples/upload.py) | Python 3, standard library only |
| [`examples/upload.mjs`](examples/upload.mjs) | Node.js 18 or newer, no dependencies |

All examples read the key from the environment variable `EVENTPICS_API_KEY`:

```bash
export EVENTPICS_API_KEY=your_key
python3 examples/upload.py --list
python3 examples/upload.py --event abcd1234 photo1.jpg photo2.jpg
```

## Related

- [EventPics for photographers and photo booth operators](https://event.pics/en/photographers.html), including the partner program
- [Folder Uploader and live preview for photo booths](https://event.pics/en/blog/photo-booth-folder-uploader-automatic-upload.html)

## Support

Open an issue in this repository. The examples are licensed under the MIT License, see [LICENSE](LICENSE).
