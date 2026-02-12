"""
GitHub + jsDelivr 上传封装（免费但适合低频更新）
"""
from __future__ import annotations

import base64
import os
import uuid
from pathlib import Path
from fastapi import UploadFile
import requests


def github_enabled() -> bool:
    return bool(os.getenv("GITHUB_TOKEN")) and bool(os.getenv("GITHUB_REPO"))


def _build_public_url(path: str) -> str:
    base_url = os.getenv("GITHUB_PUBLIC_BASE_URL", "").strip()
    if base_url:
        return f"{base_url.rstrip('/')}/{path}"
    repo = os.getenv("GITHUB_REPO", "").strip()
    branch = os.getenv("GITHUB_BRANCH", "main").strip() or "main"
    return f"https://cdn.jsdelivr.net/gh/{repo}@{branch}/{path}"


def upload_to_github(upload: UploadFile, folder: str = "news") -> str:
    repo = os.getenv("GITHUB_REPO", "").strip()
    token = os.getenv("GITHUB_TOKEN", "").strip()
    branch = os.getenv("GITHUB_BRANCH", "main").strip() or "main"
    prefix = os.getenv("GITHUB_UPLOAD_PREFIX", "uploads").strip().strip("/")
    ext = Path(upload.filename).suffix if upload.filename else ""
    key = f"{prefix}/{folder}/{uuid.uuid4().hex}{ext}"

    content = upload.file.read()
    upload.file.seek(0)
    encoded = base64.b64encode(content).decode("utf-8")

    url = f"https://api.github.com/repos/{repo}/contents/{key}"
    payload = {
        "message": f"Upload {upload.filename or 'file'}",
        "content": encoded,
        "branch": branch,
    }
    headers = {"Authorization": f"token {token}"}
    resp = requests.put(url, json=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    return _build_public_url(key)
