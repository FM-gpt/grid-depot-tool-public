#!/bin/sh
# Generic macOS client bootstrap for GRID Depot Tool.
#
# Required environment variables for your deployment:
#   GRID_DEPOT_REMOTE_HOST   server DNS name or IP, e.g. depot.example.internal
# Optional:
#   GRID_DEPOT_REMOTE_ALIAS  SSH alias to create, default grid-depot-server
#   GRID_DEPOT_REMOTE_USER   SSH user, default grid-depot
#   GRID_DEPOT_IDENTITY_FILE SSH key path, default ~/.ssh/grid_depot_server
#
# Example:
#   GRID_DEPOT_REMOTE_HOST=depot.example.internal sh bootstrap/macbook-grid-depot-client.sh
set -eu
REMOTE_ALIAS="${GRID_DEPOT_REMOTE_ALIAS:-grid-depot-server}"
REMOTE_HOST="${GRID_DEPOT_REMOTE_HOST:-}"
REMOTE_USER="${GRID_DEPOT_REMOTE_USER:-grid-depot}"
IDENTITY_FILE="${GRID_DEPOT_IDENTITY_FILE:-$HOME/.ssh/grid_depot_server}"
LOCAL_BIN="$HOME/.local/bin"

if [ -z "$REMOTE_HOST" ]; then
  echo "Set GRID_DEPOT_REMOTE_HOST to your depot server DNS name or IP." >&2
  echo "Example: GRID_DEPOT_REMOTE_HOST=depot.example.internal sh $0" >&2
  exit 2
fi

mkdir -p "$LOCAL_BIN" "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

touch "$HOME/.ssh/config"
chmod 600 "$HOME/.ssh/config"
TMP_CONFIG="$HOME/.ssh/config.grid-depot.$$.tmp"
awk -v a1="$REMOTE_ALIAS" '
  /^Host[[:space:]]+/ {
    skip = 0
    for (i = 2; i <= NF; i++) if ($i == a1) skip = 1
  }
  !skip { print }
' "$HOME/.ssh/config" > "$TMP_CONFIG"
mv "$TMP_CONFIG" "$HOME/.ssh/config"
cat >> "$HOME/.ssh/config" <<EOF

Host $REMOTE_ALIAS
  HostName $REMOTE_HOST
  User $REMOTE_USER
  IdentityFile $IDENTITY_FILE
  IdentitiesOnly yes
EOF

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
install -m 0755 "$REPO_ROOT/client/grid-depot-client.py" "$LOCAL_BIN/grid-depot-client"
for c in grid-depot grid-artifacts grid-import grid-get grid-depot-audit grid-depot-auth-check; do
  rm -f "$LOCAL_BIN/$c"
  ln -s "$LOCAL_BIN/grid-depot-client" "$LOCAL_BIN/$c"
done

case ":$PATH:" in
  *":$LOCAL_BIN:"*) ;;
  *)
    SHELL_RC="$HOME/.zshrc"
    touch "$SHELL_RC"
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_RC"; then
      printf '\n# GRID Depot Tool client helpers\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$SHELL_RC"
    fi
    ;;
esac

echo "Installed GRID Depot Tool client helpers in $LOCAL_BIN"
echo "Server target: $REMOTE_USER@$REMOTE_HOST"
echo "Try: grid-depot-auth-check && grid-artifacts --help"
