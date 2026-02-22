#!/bin/sh
set -e

# Read config if it exists (compat.setConfig writes YAML format)
CONFIG_FILE="/data/start9/config.yaml"
if [ -f "$CONFIG_FILE" ]; then
  # Parse the auth key from YAML config
  # YAML format: tailscale-auth-key: <value>
  TS_AUTHKEY=$(grep '^tailscale-auth-key:' "$CONFIG_FILE" | sed 's/^tailscale-auth-key:[[:space:]]*//' | tr -d '"' | tr -d "'")
  export TS_AUTHKEY
fi

# Ensure required directories exist
mkdir -p /var/lib/tailscale
mkdir -p /var/run/tailscale
mkdir -p /data/start9

# Start the upstream entrypoint
exec start.sh
