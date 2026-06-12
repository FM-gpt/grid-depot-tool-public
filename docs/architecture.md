# Architecture

## Overview

GRID Depot uses a central server plus thin clients.

```text
Mac/Linux clients
  |
  | ssh/scp via private LAN, VPN, or overlay network
  v
Depot server
  /usr/local/bin/grid-depot
  $GRID_DEPOT_ROOT/manifest.json
  $GRID_DEPOT_ROOT/store/
  $GRID_DEPOT_ROOT/incoming/
```

The server owns durable storage and the artifact manifest. Clients never create independent depots. They only hash local files, check the server manifest, upload new artifacts, and optionally remove local copies after safe import.

## Server components

- `bin/grid-depot` / `/usr/local/bin/grid-depot`
  - server CLI
  - manages manifest and content-addressed store
  - imports server-local files
  - lists artifacts
  - downloads URLs server-side
  - scans server-side folders
  - groups by inferred family/version

- `$GRID_DEPOT_ROOT/manifest.json`
  - JSON source of truth for indexed artifacts

- `$GRID_DEPOT_ROOT/store/`
  - content-addressed file storage
  - path shape: `store/<sha-prefix>/<sha256>/<safe-name>`

- `$GRID_DEPOT_ROOT/by-type/`
  - symlink/copy convenience index by artifact type

- `$GRID_DEPOT_ROOT/incoming/`
  - staging area for client uploads

- `$GRID_DEPOT_ROOT/reports/`
  - audit reports

## Client components

- `client/grid-depot-client.py`
  - shared Python client helper
  - invoked via symlink names such as `grid-artifacts` and `grid-import`
  - uses SSH/SCP to call the server

- `bootstrap/macbook-grid-depot-client.sh`
  - generic macOS client bootstrap script
  - creates SSH alias
  - installs helper command symlinks

- `bootstrap/macbook-grid-dns-setup.sh`
  - optional macOS split-DNS resolver setup for private DNS zones

## Artifact identity

Primary identity is SHA-256. If two files have the same SHA-256 they are exact duplicates, regardless of name or location.

Secondary review metadata:

- `family`: inferred from filename, e.g. `obsidian`, `kali-linux`, `lm-studio`
- `version`: inferred from filename when possible, e.g. `1.12.7`, `2025.2`
- `type`: inferred from extension or provided by `--type`

Family/version inference is a review aid, not a package-manager-grade solver.

## Network model

Use a private access path. Examples:

- private LAN DNS name
- VPN-only DNS name
- Tailscale/MagicDNS/overlay-network name
- site-to-site routed private hostname

Do not expose the depot directly to the public internet.

## Boundaries

This tool is intentionally simple. It does not yet provide:

- web UI
- user/RBAC model beyond SSH access
- package proxy caching
- OCI registry semantics
- Munki catalogs
- garbage collection policy engine
- multi-server replication

Those are future layers, not blockers for the current depot use case.
