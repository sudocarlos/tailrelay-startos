#!/bin/sh
set -e

# Ensure required directories exist
mkdir -p /var/lib/tailscale
mkdir -p /var/run/tailscale
mkdir -p /data/start9

# Start the upstream entrypoint
exec start.sh
