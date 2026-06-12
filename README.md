# GRID Depot Tool

GRID Depot Tool is a lightweight SSH-first artifact depot for homelab, office, and small-business servers.

It keeps installers, ISOs, packages, disk images, and curated model files on one central server instead of scattering duplicate downloads across laptops and workstations.

## Why this exists

Common home/office lab problem:

- the same DMGs, ISOs, PKGs, model files, and VM images get downloaded repeatedly
- laptop Downloads folders become messy
- server recovery media and installers are not indexed
- there is no simple way to know whether a file is already stored centrally
- a full package registry stack can be overkill for an early depot

GRID Depot solves the first version of that problem with:

- content-addressed storage by SHA-256
- a JSON manifest
- duplicate detection before upload
- related version/family hints from filenames
- SSH/SCP client wrappers
- optional prompt to remove local copies after safe import
- simple documentation and runbooks

## What it is not yet

This is not a full replacement for Harbor, Nexus, Munki, Pulp, or a Hugging Face registry. It is a pragmatic central depot layer that can later grow into or sit beside those systems.

## Quick start: server

Install the server CLI on a Linux server with a durable storage path:

```sh
sudo mkdir -p /var/lib/grid-depot
sudo install -m 0755 bin/grid-depot /usr/local/bin/grid-depot
GRID_DEPOT_ROOT=/var/lib/grid-depot grid-depot where
```

The default root is `/var/lib/grid-depot`. Override with:

```sh
export GRID_DEPOT_ROOT=/path/to/depot
```

## Quick start: Mac client

Recommended client access is via SSH alias:

```sshconfig
Host grid-depot-server
  HostName depot.example.internal
  User grid-depot
  IdentityFile ~/.ssh/grid_depot_server
  IdentitiesOnly yes
```

Install helper symlinks pointing to `client/grid-depot-client.py`, or run the bootstrap script adapted for your environment.

```sh
GRID_DEPOT_REMOTE_HOST=depot.example.internal \
GRID_DEPOT_REMOTE_USER=grid-depot \
sh bootstrap/macbook-grid-depot-client.sh
```

## Main commands

List server artifacts:

```sh
grid-artifacts
```

Dry-run scan/import of local Downloads:

```sh
grid-artifacts auto-add --scan-downloads --dry-run
```

Import after reviewing dry run:

```sh
grid-artifacts auto-add --scan-downloads --tag macbook
```

Import explicit files:

```sh
grid-import ~/Downloads/App.dmg --type dmg --tag macbook
grid-import ~/Downloads/model.gguf --type ai-model --tag gguf --tag keep
```

Download centrally on the server:

```sh
grid-get https://example.com/file.iso --type iso --tag keep
```

Show duplicate/version groups:

```sh
grid-artifacts families --multiple
```

## Default scan policy

Default auto-add/audit scans include:

- `.iso`
- `.dmg`
- `.pkg`
- `.img`
- `.qcow2`
- `.vmdk`
- `.gguf`
- `.safetensors`

`.zip` is intentionally excluded from default scans because Downloads folders contain many unrelated ZIP archives.

ZIP files can still be imported deliberately:

```sh
grid-import ~/Downloads/file.zip --type archive
```

Or included in a one-off scan:

```sh
grid-artifacts auto-add --scan-downloads --ext zip
```

## Help

Every command exposes help:

```sh
grid-artifacts --help
grid-import --help
grid-get --help
grid-depot-audit --help
grid-depot-auth-check --help
grid-depot --help
```

Server subcommands also expose help:

```sh
grid-depot import --help
grid-depot get --help
grid-depot list --help
grid-depot audit --help
grid-depot auto-add --help
grid-depot families --help
grid-depot where --help
```

## Documentation

See:

- `docs/architecture.md`
- `docs/runbook.md`
- `docs/manifest-format.md`
- `docs/security.md`
- `docs/roadmap.md`

## Current status

This repository was extracted from a private server pilot and sanitized for future generalization. Deployment-specific addresses, hostnames, and paths should live outside this public template in local/private notes.
