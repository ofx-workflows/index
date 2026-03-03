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
private: false
```

2. Open a Pull Request against `main`.
3. CI will validate and rebuild `index.json` on merge.

## Automatic discovery

A nightly GitHub Action scans all repos in the `ofx-workflows` org and opens PRs for any new repos not yet in the index. It reads each repo's `collection.yaml` manifest and latest Git tag to populate the entry. When a PAT with `repo` scope is configured (see [Private Repos](#private-repos)), private repositories are discovered and indexed automatically.

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
| `private` | bool | Whether the collection is in a private repo (default: `false`) |

## Local development

```bash
pip install pyyaml
python scripts/build-index.py          # rebuild index.json
python scripts/build-index.py --check  # validate (CI mode)
```

## Private Repos

This index supports collections hosted in **private** GitHub repositories.

### How it works

1. The nightly scan action reads each repo's `private` flag from the GitHub API and records it in the collection entry.
2. OFX clients use this flag to know that authentication is required to clone.
3. When a user runs `ofx flow collection add <private-collection>`, OFX automatically injects a GitHub token into the clone URL.

### Setup (index repo)

The default `GITHUB_TOKEN` in Actions can only see **public** repos. To discover private repos:

1. Create a GitHub **Personal Access Token (PAT)** with `repo` scope (or a fine-grained token with read access to the org's repos).
2. Add it as a repository secret named `ORG_PAT` in this index repo.
3. The scan-org workflow automatically prefers `ORG_PAT` over `GITHUB_TOKEN`.

### Setup (OFX client)

OFX resolves a GitHub token using this precedence:

1. `OFX_GITHUB_TOKEN` environment variable
2. `gh auth token` — auto-detected if the [GitHub CLI](https://cli.github.com/) is installed and authenticated

No extra configuration is needed if you're already logged in with `gh auth login`.

```bash
# Option A: set the env var
export OFX_GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Option B: just use the gh CLI (auto-detected)
gh auth login

# Then install private collections as usual
ofx flow collection add my-private-collection
```

### Marking a collection as private

Set `private: true` in the collection entry:

```yaml
# collections/my-private-collection.yaml
name: my-private-collection
description: "Internal pentest workflows"
source: "https://github.com/ofx-workflows/my-private-collection"
latest: "1.0.0"
tags:
  - internal
author: security-team
private: true
```
