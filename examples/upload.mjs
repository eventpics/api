// Upload photos or videos into an EventPics event. Node.js 18 or newer, no dependencies.
//
//   export EVENTPICS_API_KEY=your_key
//   node upload.mjs --list
//   node upload.mjs --event LINK_ID [--album ALBUM_ID] FILE [FILE ...]

import { readFile, stat } from 'node:fs/promises';
import { basename, extname } from 'node:path';

const API = 'https://api.event.pics';
const TYPES = { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.heic': 'image/heic',
  '.webp': 'image/webp', '.mp4': 'video/mp4', '.mov': 'video/quicktime' };

const key = process.env.EVENTPICS_API_KEY;
if (!key) { console.error('Set EVENTPICS_API_KEY first.'); process.exit(1); }

const args = process.argv.slice(2);
const option = (name) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : undefined; };

async function listEvents() {
  const res = await fetch(`${API}/geteventsandalbums`, { headers: { Authorization: `Bearer ${key}` } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  for (const event of (await res.json()).events) {
    console.log(`${event.linkId}  ${event.title}`);
    for (const album of event.albums ?? []) console.log(`    album ${album.id}  ${album.title}`);
  }
}

async function upload(linkId, albumId, path) {
  const info = await stat(path);
  const body = { apiKey: key, linkId, fileName: basename(path), fileSize: info.size, takenAt: Math.round(info.mtimeMs) };
  if (albumId) body.albumId = albumId;
  const res = await fetch(`${API}/getuploadurl`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const { uploadUrl, mediaUrl } = await res.json();
  const type = TYPES[extname(path).toLowerCase()] ?? 'application/octet-stream';
  const put = await fetch(uploadUrl, { method: 'PUT', headers: { 'Content-Type': type }, body: await readFile(path) });
  if (!put.ok) throw new Error(`Upload failed: HTTP ${put.status}`);
  console.log(`${path} -> ${mediaUrl}`);
}

if (args.includes('--list')) {
  await listEvents();
} else {
  const linkId = option('--event');
  const albumId = option('--album');
  if (!linkId || args.length === 0) { console.error('Use --list, or --event LINK_ID with one or more files.'); process.exit(1); }
  for (const path of args) await upload(linkId, albumId, path);
}
