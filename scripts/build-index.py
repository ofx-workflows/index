#!/usr/bin/env python3
"""Build index.json from collections/*.yaml source files.

Usage:
    python scripts/build-index.py            # writes index.json
    python scripts/build-index.py --check    # dry-run: exit 1 if index.json is stale
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml  # pip install pyyaml

COLLECTIONS_DIR = Path(__file__).resolve().parent.parent / "collections"
INDEX_FILE = Path(__file__).resolve().parent.parent / "index.json"

REQUIRED_FIELDS = {"name"}


def load_entries() -> dict[str, dict]:
    entries: dict[str, dict] = {}

    if not COLLECTIONS_DIR.exists():
        print(f"⚠  No collections/ directory found at {COLLECTIONS_DIR}", file=sys.stderr)
        return entries

    for path in sorted(COLLECTIONS_DIR.glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f) or {}

        missing = REQUIRED_FIELDS - data.keys()
        if missing:
            print(f"⚠  Skipping {path.name}: missing {missing}", file=sys.stderr)
            continue

        name = data["name"]
        entries[name] = {
            "name": name,
            "description": data.get("description", ""),
            "source": data.get("source", f"https://github.com/ofx-workflows/{name}"),
            "latest": data.get("latest", "0.0.0"),
            "tags": data.get("tags", []),
            "author": data.get("author", ""),
            "private": data.get("private", False),
        }

    return entries


def build_index(entries: dict[str, dict]) -> dict:
    return {"collections": entries}


def main() -> None:
    check_mode = "--check" in sys.argv

    entries = load_entries()
    index = build_index(entries)
    new_content = json.dumps(index, indent=2, sort_keys=False) + "\n"

    if check_mode:
        if INDEX_FILE.exists() and INDEX_FILE.read_text() == new_content:
            print("✓ index.json is up to date")
            sys.exit(0)
        else:
            print("✗ index.json is stale — run: python scripts/build-index.py")
            sys.exit(1)

    INDEX_FILE.write_text(new_content)
    print(f"✓ Wrote {len(entries)} collection(s) to {INDEX_FILE}")


if __name__ == "__main__":
    main()
