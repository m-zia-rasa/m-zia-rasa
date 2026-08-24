#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sys

import cv2
import numpy as np
import requests

ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = ROOT / "profile.json"
AVATAR_PATH = ROOT / "assets" / "source-avatar.webp"

HEADERS = {
    "User-Agent": "m-zia-rasa-profile-sync/2.0",
    "Accept": "application/vnd.github+json",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_existing_avatar_hash() -> str | None:
    if not AVATAR_PATH.exists():
        return None
    return sha256_bytes(AVATAR_PATH.read_bytes())


def download_avatar(url: str) -> bytes:
    response = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=30)
    response.raise_for_status()
    raw = np.frombuffer(response.content, dtype=np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("Downloaded GitHub avatar could not be decoded.")
    ok, encoded = cv2.imencode(".webp", image, [cv2.IMWRITE_WEBP_QUALITY, 92])
    if not ok:
        raise RuntimeError("GitHub avatar could not be encoded as WebP.")
    return encoded.tobytes()


def main() -> int:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    username = profile["username"]
    sync = profile.setdefault(
        "github_sync",
        {"name": True, "bio": True, "avatar": True},
    )

    response = requests.get(
        f"https://api.github.com/users/{username}",
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    public = response.json()

    changed = False

    if sync.get("name", True) and public.get("name"):
        if profile.get("name") != public["name"]:
            profile["name"] = public["name"]
            changed = True

    if sync.get("bio", True):
        bio = (public.get("bio") or "").strip()
        if profile.get("github_bio", "") != bio:
            profile["github_bio"] = bio
            changed = True

    avatar_changed = False
    avatar_url = public.get("avatar_url")
    if sync.get("avatar", True) and avatar_url:
        avatar_bytes = download_avatar(avatar_url)
        new_hash = sha256_bytes(avatar_bytes)
        if new_hash != read_existing_avatar_hash():
            AVATAR_PATH.parent.mkdir(parents=True, exist_ok=True)
            AVATAR_PATH.write_bytes(avatar_bytes)
            avatar_changed = True
        if profile.get("github_avatar_url") != avatar_url:
            profile["github_avatar_url"] = avatar_url
            changed = True

    if changed:
        PROFILE_PATH.write_text(
            json.dumps(profile, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(
        "GitHub profile sync:",
        f"metadata_changed={changed}",
        f"avatar_changed={avatar_changed}",
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"GitHub profile sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
