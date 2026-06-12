# Manifest Format

The depot manifest is stored at:

```text
$GRID_DEPOT_ROOT/manifest.json
```

Default schema version in the current pilot: `2`.

## Top-level shape

```json
{
  "schema": 2,
  "created_at": "2026-06-12T...",
  "artifacts": []
}
```

## Artifact fields

Each artifact contains fields like:

```json
{
  "id": "02774081e05c386f",
  "name": "example-installer.iso",
  "type": "iso",
  "family": "example-installer",
  "version": "1.0.0",
  "sha256": "02774081e05c386f...",
  "size_bytes": 3790000000,
  "human_size": "3.5 GiB",
  "mime_type": "application/x-iso9660-image",
  "store_path": "$GRID_DEPOT_ROOT/store/02/<sha>/example-installer.iso",
  "source_paths": [],
  "source_urls": [],
  "tags": ["current", "keep"],
  "created_at": "2026-06-12T...",
  "last_seen_at": "2026-06-12T..."
}
```

## Field meanings

- `id`: first 16 characters of SHA-256, used for human listing.
- `name`: original filename.
- `type`: artifact class, such as `dmg`, `iso`, `pkg`, `ai-model`, `archive`.
- `family`: inferred app/tool/model family from filename.
- `version`: inferred version from filename when present.
- `sha256`: full content hash and primary identity.
- `store_path`: canonical stored artifact path.
- `source_paths`: local/source paths observed during import.
- `source_urls`: original URLs when known.
- `tags`: operator-provided labels.

## Identity rules

- Exact duplicate: same SHA-256.
- Related artifact: same `family` and `type`, possibly different version/hash.
- Keep/retention signals: tags such as `current`, `previous`, `keep`.

## Known limitations

Filename family/version inference is intentionally simple. It is good enough for operational review but not a substitute for package metadata parsing.

Future versions should add optional sidecar metadata per artifact and parser plugins for known ecosystems.
