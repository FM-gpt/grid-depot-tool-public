# Roadmap and Future Scope

This project started as the GRID local artifact depot pilot. The next goal is to make it useful for other homelab, small-business, and office-server owners.

## Near-term improvements

### Packaging

- install script for Linux server
- install script for macOS clients
- uninstall script
- Homebrew tap/cask for client helper
- Debian package for server CLI

### Configuration

- `/etc/grid-depot/config.toml`
- client config at `~/.config/grid-depot/client.toml`
- configurable server root, SSH alias, default extensions, and cleanup behavior
- named profiles for LAN vs Tailscale access

### Safer permissions

- dedicated `grid-depot` Unix user
- group-based write access
- restricted SSH command for import-only clients
- per-client key registration/removal

### Better metadata

- operator notes per artifact
- source URL/source project fields
- license field
- checksum-source field
- architecture/platform tags
- searchable tool categories, such as `installer`, `developer-tool`, `server-image`, `ai-model`, `firmware`, `utility`, `backup-tool`, `network-tool`
- short human descriptions for each artifact so the depot can answer "what is this for?"
- search tags/keywords for later database search, filtering, and dashboard discovery
- artifact status: `candidate`, `current`, `previous`, `keep`, `retired`
- machine-readable sidecar metadata

### Retention and cleanup

- policy: keep current + previous + keep-tagged
- stale duplicate review command
- safe garbage collection for unreferenced incoming files
- dry-run-first cleanup reports

### Mac app management integration

- AutoPkg import mode
- Munki repository output
- appcast/version awareness
- quarantine/xattr reporting
- signed/notarized status capture

### Package/cache integrations

- Nexus raw repository sync
- Harbor/ORAS model package export
- apt-cacher-ng or Pulp integration notes
- npm/PyPI proxy documentation

### Model depot improvements

- GGUF metadata parsing
- Hugging Face repo/source capture
- quantization tags
- context-length/runtime notes
- model card import
- local benchmark metadata

### Web UI

- basic web dashboard as a near-term product milestone
- read-only artifact browser
- searchable/filterable table by name, type, category, tags, platform, size, status, and date added
- artifact detail page showing short description, source URL, checksum, tags, related versions, and install/retrieval notes
- upload workflow with duplicate warnings
- version-family view
- disk usage dashboard
- retention review queue

### CLI progress and run summaries

- end-of-run summary table showing files scanned, new imports, duplicates skipped, failures, local files removed, total bytes uploaded, total bytes avoided via duplicate detection, and total run time
- per-type/category breakdown in the summary, for example ISO, DMG, PKG, disk image, AI model
- optional machine-readable JSON run report for later dashboards and logs
- live progress box for long runs with current file, item counter, uploaded bytes, transfer rate, elapsed time, ETA, and success/failure counters
- progress bar/status line that updates without requiring a web UI, with a plain-output fallback for cron/log mode

### API

- local HTTP API behind LAN/VPN only
- token-based client auth
- JSON import/list/status endpoints
- webhook hooks for completed imports

### Monitoring

- Prometheus textfile exporter
- disk usage alerts
- import counts
- duplicate avoidance totals
- last backup/snapshot status

### Backup and replication

- documented ZFS snapshot policy
- `zfs send`/`recv` offsite replica pattern
- restore drill script
- manifest/blob consistency checker

### Multi-user support

- per-user tags
- uploader identity
- approval workflows
- team/project ownership
- audit history

## Productization questions

- Should this remain SSH-only or grow a small server daemon?
- Should it manage only curated artifacts or also act as a cache?
- Should ZIP support stay manual-only by default?
- Should the tool integrate with existing package managers or stay generic?
- Should metadata live only in one JSON manifest or move to SQLite?

## Generalized positioning

Potential public-facing description:

> A small self-hosted artifact depot for homelabs and small offices. Keep ISOs, installers, packages, disk images, and local AI model files on one server, avoid duplicate downloads, and clean up laptop Downloads folders safely.

## Acceptance criteria for first public release

- clean install instructions for a non-GRID server
- non-root server account support
- client install script
- tested import/list/auto-add workflows
- documented backup/restore process
- no hardcoded GRID paths in generic scripts
- example config files
- shellcheck/py_compile/JSON validation in CI
- GitHub release with checksums
