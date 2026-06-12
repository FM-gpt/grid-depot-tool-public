# Security Notes

## Exposure policy

Do not expose the depot directly to the public internet.

Preferred access paths:

- LAN
- VPN
- Tailscale
- site-to-site private routing

## Authentication model

Current pilot uses SSH authentication.

Recommended:

- per-client SSH keys
- least-privilege server account in future versions
- no shared passwords
- no secrets in documentation

Use a non-root `grid-depot` server user where possible. Avoid documenting real usernames, hostnames, or internal addresses in public repositories.

## Local deletion safety

The client only offers local deletion after:

1. an exact SHA-256 duplicate already exists on the server, or
2. a new upload/import completed successfully.

Safety controls:

- `--dry-run`: no upload/delete
- `--keep-local`: never prompt/delete
- `--yes-remove`: automatic local cleanup after safe state

## Supply-chain caution

The depot stores files. It does not prove the files are safe.

Future hardening should include:

- checksums from upstream sources
- detached signatures where available
- malware scanning for generic files
- provenance/source URL tracking
- allowlisted source repositories for auto-downloads
- manual approval/promote workflow for production artifacts

## Secrets policy

Do not store:

- private SSH keys
- API keys
- passwords
- Tailscale auth keys
- GitHub tokens
- vendor credentials

Documentation may mention credential file paths or setup commands, but never credential values.
