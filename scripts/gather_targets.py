#!/usr/bin/env python3
"""
Fetch all Start9 marketplace packages from the official registry APIs
and generate assets/startos_targets.json for use by Tailrelay.

No external dependencies required — uses only the Python standard library.

Registries queried (in priority order for deduplication):
  1. start9    — https://registry.start9.com/package/v0/index
  2. beta      — https://beta-registry.start9.com/package/v0/index
  3. community — https://community-registry.start9.com/package/v0/index
"""

import json
import os
import sys
import urllib.error
import urllib.request

REGISTRIES = [
    ("start9", "https://registry.start9.com/package/v0/index"),
    ("beta", "https://beta-registry.start9.com/package/v0/index"),
    ("community", "https://community-registry.start9.com/package/v0/index"),
]

# Output path relative to this script's directory (i.e. <repo>/assets/startos_targets.json)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "..", "assets", "startos_targets.json")


def fetch_index(registry_name, url):
    """Fetch the package index from a Start9 registry API endpoint."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        print(
            f"  HTTP {e.code} fetching {registry_name} registry: {e.reason}",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"  Error fetching {registry_name} registry: {e}", file=sys.stderr)
    return []


def _make_target(
    app_id, host, title, iface_data, iface_id, internal_port, ssl, registry_name
):
    """Build a single target dict from resolved interface and port info."""
    protocols = iface_data.get("protocols", [])
    is_http = "http" in protocols or "https" in protocols
    target_type = "proxy" if is_http else "relay"

    if ssl:
        target_protocol = "https"
    elif is_http:
        target_protocol = "http"
    else:
        target_protocol = "tcp"

    iface_name = iface_data.get("name", iface_id)
    return {
        "app_id": app_id,
        "host": host,
        "port": int(internal_port),
        "type": target_type,
        "protocol": target_protocol,
        "target_name": f"{title} - {iface_name} (port {internal_port})",
        "registry": registry_name,
    }


def targets_from_manifest(manifest, registry_name):
    """
    Parse a StartOS manifest dict and return a list of Tailrelay target dicts.

    Port resolution strategy (in order of preference):
      1. lan-config  — explicit internal port + ssl flag; most accurate.
      2. tor-config  — port-mapping format is {"external": "internal"}; used when
                       lan-config is absent or null (covers TCP-only services such as
                       electrs, lnd, mastodon, dojo, etc.).

    Duplicate internal ports within the same interface are deduplicated.
    """
    app_id = manifest.get("id")
    title = manifest.get("title", app_id)
    host = f"{app_id}.embassy"
    interfaces = manifest.get("interfaces", {})
    targets = []

    for iface_id, iface_data in interfaces.items():
        if not isinstance(iface_data, dict):
            continue

        seen_ports = set()
        lan_config = iface_data.get("lan-config") or {}
        tor_config = iface_data.get("tor-config") or {}
        tor_port_mapping = tor_config.get("port-mapping") or {}

        # --- 1. LAN config (preferred) ---
        for _ext_port, port_config in lan_config.items():
            if not isinstance(port_config, dict):
                continue
            internal_port = int(port_config.get("internal", _ext_port))
            ssl = port_config.get("ssl", False)
            if internal_port in seen_ports:
                continue
            seen_ports.add(internal_port)
            targets.append(
                _make_target(
                    app_id,
                    host,
                    title,
                    iface_data,
                    iface_id,
                    internal_port,
                    ssl,
                    registry_name,
                )
            )

        # --- 2. Tor config fallback (for services with no LAN config) ---
        if not lan_config:
            for _ext_port, internal_port_str in tor_port_mapping.items():
                internal_port = int(internal_port_str)
                if internal_port in seen_ports:
                    continue
                seen_ports.add(internal_port)
                targets.append(
                    _make_target(
                        app_id,
                        host,
                        title,
                        iface_data,
                        iface_id,
                        internal_port,
                        False,
                        registry_name,
                    )
                )

    return targets


def main():
    # Collect manifests from all registries; deduplicate by app_id (first registry wins).
    seen_ids = set()
    all_targets = []

    for registry_name, url in REGISTRIES:
        print(f"Fetching {registry_name} registry...", file=sys.stderr)
        index = fetch_index(registry_name, url)
        new_count = 0

        for entry in index:
            manifest = entry.get("manifest")
            if not manifest:
                continue

            app_id = manifest.get("id")
            if not app_id:
                continue

            if app_id in seen_ids:
                print(
                    f"  Skipping {app_id} (already seen from higher-priority registry)",
                    file=sys.stderr,
                )
                continue

            seen_ids.add(app_id)
            targets = targets_from_manifest(manifest, registry_name)
            all_targets.extend(targets)
            new_count += 1
            print(f"  {app_id}: {len(targets)} target(s)", file=sys.stderr)

        print(f"  -> {new_count} new package(s) from {registry_name}", file=sys.stderr)

    # Sort for stable output: by app_id, then port
    all_targets.sort(key=lambda t: (t["app_id"], t["port"]))

    output_path = os.path.normpath(OUTPUT_FILE)
    with open(output_path, "w") as f:
        json.dump(all_targets, f, indent=2)
        f.write("\n")

    print(
        f"\nDiscovered {len(all_targets)} target(s) across {len(seen_ids)} package(s). "
        f"Saved to {output_path}.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
