#!/usr/bin/env python3
"""Scan the ofx-workflows GitHub org for repos not yet in collections/.

For each new repo found, creates a collections/<name>.yaml stub.
Intended to be run by the scan-org.yml GitHub Action.
"""

from __future__ import annotations

import os
from pathlib import Path

import requests
import yaml

ORG = "ofx-workflows"
API = f"https://api.github.com/orgs/{ORG}/repos"
COLLECTIONS_DIR = Path(__file__).resolve().parent.parent / "collections"

SKIP_REPOS = {"index", ".github"}  # repos that are not collections


def _headers() -> dict[str, str]:
    """Build request headers with optional auth token.

    Works with both public and private orgs/repos.
    """
    token = os.environ.get("GH_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_org_repos() -> list[dict]:
    """Fetch all repos in the org (paginated). Includes private repos when GH_TOKEN is set."""
    repos: list[dict] = []
    page = 1
    while True:
        resp = requests.get(
            API,
            headers=_headers(),
            params={"per_page": 100, "page": page, "type": "all"},
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


def existing_names() -> set[str]:
    """Return names already registered in collections/."""
    COLLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    names: set[str] = set()
    for p in COLLECTIONS_DIR.glob("*.yaml"):
        try:
            d = yaml.safe_load(p.read_text()) or {}
            names.add(d.get("name", p.stem))
        except Exception:
            names.add(p.stem)
    return names


def fetch_manifest(repo_name: str, default_branch: str) -> dict | None:
    """Try to fetch collection.yaml from the repo root via the API.

    Uses the contents API which works for both public and private repos
    when a token is provided.
    """
    url = (
        f"https://api.github.com/repos/{ORG}/{repo_name}"
        f"/contents/collection.yaml?ref={default_branch}"
    )
    resp = requests.get(url, headers=_headers(), timeout=10)
    if resp.status_code == 200:
        import base64

        data = resp.json()
        if "content" in data:
            raw = base64.b64decode(data["content"]).decode()
            return yaml.safe_load(raw) or {}
    return None


def get_latest_tag(repo_name: str) -> str:
    """Return the latest tag name, or '' if none."""
    resp = requests.get(
        f"https://api.github.com/repos/{ORG}/{repo_name}/tags",
        headers=_headers(),
        params={"per_page": 1},
    )
    if resp.status_code == 200:
        tags = resp.json()
        if tags:
            return tags[0]["name"].lstrip("v")
    return ""


def main() -> None:
    repos = get_org_repos()
    known = existing_names()
    created = 0

    for repo in repos:
        name = repo["name"]
        if name in SKIP_REPOS or name in known:
            continue

        default_branch = repo.get("default_branch", "main")
        manifest = fetch_manifest(name, default_branch)
        latest = get_latest_tag(name)

        entry = {
            "name": name,
            "description": (manifest or {}).get("description", repo.get("description", "") or ""),
            "source": f"https://github.com/{ORG}/{name}",
            "latest": (manifest or {}).get("version", latest or "0.0.0"),
            "tags": (manifest or {}).get("tags", []),
            "author": (manifest or {}).get("author", "ofx-community"),
            "private": repo.get("private", False),
        }

        out = COLLECTIONS_DIR / f"{name}.yaml"
        out.write_text(yaml.dump(entry, default_flow_style=False, sort_keys=False))
        print(f"✓ Created {out.name}")
        created += 1

    print(f"\nDone — {created} new collection(s) discovered.")


if __name__ == "__main__":
    main()
