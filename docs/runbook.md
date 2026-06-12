# Runbook

## Install server CLI

```sh
sudo mkdir -p /var/lib/grid-depot
sudo install -m 0755 bin/grid-depot /usr/local/bin/grid-depot
GRID_DEPOT_ROOT=/var/lib/grid-depot /usr/local/bin/grid-depot where
```

Expected:

```text
/var/lib/grid-depot
```

For a different storage path, set `GRID_DEPOT_ROOT` in the server environment.

## Install Mac client helpers

Create SSH key if needed:

```sh
ssh-keygen -t ed25519 -f ~/.ssh/grid_depot_server -C "grid-depot-client"
```

Authorize the public key on your depot server according to your server user policy.

Run bootstrap with your private server hostname:

```sh
GRID_DEPOT_REMOTE_HOST=depot.example.internal \
GRID_DEPOT_REMOTE_USER=grid-depot \
sh bootstrap/macbook-grid-depot-client.sh
```

Verify:

```sh
grid-depot-auth-check
grid-artifacts
```

## Optional DNS setup on macOS

If your depot hostname lives in a private DNS zone and macOS is not resolving it, configure a resolver for that private zone:

```sh
GRID_DEPOT_DNS_SERVER=10.0.0.53 \
GRID_DEPOT_DNS_ZONE=internal \
GRID_DEPOT_TEST_HOST=depot.example.internal \
sh bootstrap/macbook-grid-dns-setup.sh
```

Verify:

```sh
dscacheutil -q host -a name depot.example.internal
nc -vz depot.example.internal 22
```

## Safe import workflow

Always dry-run first when scanning broad folders:

```sh
grid-artifacts auto-add --scan-downloads --dry-run
```

Then import:

```sh
grid-artifacts auto-add --scan-downloads --tag macbook
```

For explicit files:

```sh
grid-import ~/Downloads/App.dmg --type dmg --tag macbook
```

After successful import or duplicate detection, the client asks whether to remove the local file.

Use safety flags:

```sh
--keep-local    # never ask/remove local files
--yes-remove    # remove local copies automatically after safe import/duplicate detection
--dry-run       # no upload, no delete
```

## Default scan extensions

Included:

- `.iso`
- `.dmg`
- `.pkg`
- `.img`
- `.qcow2`
- `.vmdk`
- `.gguf`
- `.safetensors`

Excluded by default:

- `.zip`

Intentional ZIP import:

```sh
grid-import ~/Downloads/file.zip --type archive
```

## Review related versions

```sh
grid-artifacts families --multiple
```

Use this to identify multiple versions of the same app/tool/model before deciding retention.

## Server-side commands

```sh
grid-depot list
grid-depot list --json
grid-depot import /path/to/file --type dmg --tag imported
grid-depot get https://example.com/file.iso --type iso --tag keep
grid-depot audit --dir /tmp --hash
grid-depot auto-add --dir /tmp --ext dmg
grid-depot families --multiple
grid-depot where
```

## Backup notes

Protect the depot root with your server backup system. For ZFS-backed storage, use:

- ZFS snapshots
- offsite replication where available
- manifest + representative blob restore drills

Minimum restore drill:

1. Copy `manifest.json` and one stored artifact to a temp restore path.
2. Verify SHA-256 of the restored artifact matches the manifest.
3. Run `grid-depot list --json` against a temporary `GRID_DEPOT_ROOT`.

## Failure handling

DNS failure:

```sh
dig @<private-dns-server> depot.example.internal
nc -vz depot.example.internal 22
```

SSH failure:

```sh
ssh -v grid-depot-server /usr/local/bin/grid-depot where
```

Manifest failure:

```sh
python3 -m json.tool "$GRID_DEPOT_ROOT/manifest.json" >/dev/null
```

Client helper failure:

```sh
which grid-artifacts
ls -l ~/.local/bin/grid-artifacts ~/.local/bin/grid-depot-client
python3 -m py_compile ~/.local/bin/grid-depot-client
```
