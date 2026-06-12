#!/bin/sh
# Configure macOS split DNS for a private depot zone.
#
# Required:
#   GRID_DEPOT_DNS_SERVER  DNS server IP for the private zone
# Optional:
#   GRID_DEPOT_DNS_ZONE    private DNS zone, default internal
#   GRID_DEPOT_TEST_HOST   hostname to test after setup
#
# Example:
#   GRID_DEPOT_DNS_SERVER=10.0.0.53 GRID_DEPOT_DNS_ZONE=internal GRID_DEPOT_TEST_HOST=depot.example.internal sh bootstrap/macbook-grid-dns-setup.sh
set -eu
DNS_SERVER="${GRID_DEPOT_DNS_SERVER:-}"
DNS_ZONE="${GRID_DEPOT_DNS_ZONE:-internal}"
TEST_HOST="${GRID_DEPOT_TEST_HOST:-}"

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This script is for macOS clients." >&2
  exit 2
fi
if [ -z "$DNS_SERVER" ]; then
  echo "Set GRID_DEPOT_DNS_SERVER to your private DNS server IP." >&2
  exit 2
fi

sudo mkdir -p /etc/resolver
printf 'nameserver %s\nsearch_order 1\ntimeout 2\n' "$DNS_SERVER" | sudo tee "/etc/resolver/$DNS_ZONE" >/dev/null

sudo dscacheutil -flushcache || true
sudo killall -HUP mDNSResponder 2>/dev/null || true

echo "Installed macOS resolver file: /etc/resolver/$DNS_ZONE"

if [ -n "$TEST_HOST" ]; then
  if command -v dig >/dev/null 2>&1; then
    echo "Direct DNS test:"
    dig +short @"$DNS_SERVER" "$TEST_HOST" A || true
  fi
  echo "macOS resolver test:"
  dscacheutil -q host -a name "$TEST_HOST" || true
fi
