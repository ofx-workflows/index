# OFX Workflow Collection Index

Community index of installable workflow collections for [OFX](https://github.com/anhhung04/ofx).

## How it works

OFX clients fetch `index.json` from this repository to power `ofx flow collection search`.

The index is **auto-generated** from the YAML files in `collections/`. Do not edit `index.json` by hand.

## Adding a collection

1. Create a file `collections/<name>.yaml`:

```yaml
name: my-collection
description: "Short description of your collection"
source: "https://github.com/ofx-workflows/my-collection"
latest: "1.0.0"
tags:
  - recon
  - scanning
author: your-name
```

2. Open a Pull Request against `main`.
3. CI will validate and rebuild `index.json` on merge.

## Automatic discovery

A nightly GitHub Action scans all repos in the `ofx-workflows` org and opens PRs for any new repos not yet in the index. It reads each repo's `collection.yaml` manifest and latest Git tag to populate the entry.

## Schema

Each entry in `index.json` has these fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Collection name (must match the YAML filename) |
| `description` | string | Human-readable description |
| `source` | string | Git clone URL |
| `latest` | string | Latest semver version |
| `tags` | list[string] | Tags for search/discovery |
| `author` | string | Author or team name |

## Local development

```bash
pip install pyyaml
python scripts/build-index.py          # rebuild index.json
python scripts/build-index.py --check  # validate (CI mode)
```
