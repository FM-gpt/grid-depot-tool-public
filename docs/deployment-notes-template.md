# Deployment Notes Template

This file is a template. Copy it into your private notes or a private repository before adding real deployment details.

Do not commit private IPs, internal DNS names, usernames, client names, or access paths to a public repository.

## Server

- Host label:
- Private DNS name:
- Private IP:
- Depot root:
- Server CLI path:
- Bootstrap path:

## DNS and network

- Private DNS zone:
- DNS server:
- VPN / overlay / LAN access method:
- Required routes:

## Current artifact count

- Artifact count:
- Approximate size:
- Notable categories:

## Client devices

- Client labels:
- Bootstrap status:
- Helper command status:

## Policy decisions

- Default scan extensions:
- Excluded extensions:
- Retention policy:
- Backup policy:

## Verification commands

```sh
grid-depot-auth-check
grid-artifacts
grid-artifacts auto-add --scan-downloads --dry-run
```
