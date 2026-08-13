#!/usr/bin/env python3
"""
Fetch all Start9 marketplace packages from the official registry APIs
and generate assets/startos_targets.json for use by Tailrelay.

No external dependencies required - uses only the Python standard library.

Registries queried (in priority order for deduplication):
  1. start9    - https://registry.start9.com/package/v0/index
  2. beta      - https://beta-registry.start9.com/package/v0/index
  3. community - https://community-registry.start9.com/package/v0/index

Manual overrides:
  Hand-curated entries in assets/manual_targets.json are merged over the
  generated output.  Each override is keyed by (app_id, host, port); it may
  patch any subset of fields on an existing generated target or introduce a
  wholly new one.
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
# Hand-curated entries that are merged over the generated output (see module
# docstring).  Optional: the file may be absent, in which case nothing is merged.
MANUAL_FILE = os.path.join(SCRIPT_DIR, "..", "assets", "manual_targets.json")


def fetch_index(registry_name, url):
    """Fetch all pages of the package index from a Start9 registry API endpoint.

    The registry defaults to 20 results per page.  We request 100 per page and
    iterate until an empty page is returned.
    """
    results = []
    page = 1
    per_page = 100
    while True:
        paged_url = f"{url}?per-page={per_page}&page={page}"
        try:
            req = urllib.request.Request(
                paged_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.load(response)
        except urllib.error.HTTPError as e:
            print(
                f"  HTTP {e.code} fetching {registry_name} registry (page {page}): {e.reason}",
                file=sys.stderr,
            )
            break
        except Exception as e:
            print(
                f"  Error fetching {registry_name} registry (page {page}): {e}",
                file=sys.stderr,
            )
            break

        if not data:
            break
        results.extend(data)
        if len(data) < per_page:
            # Last page - no more results
            break
        page += 1

    return results


def _make_target(
    app_id, host, title, iface_data, iface_id, internal_port, ssl, registry_name, icon
):
    """Build a single target dict from resolved interface and port info.

    The ``ssl`` flag indicates that the StartOS LAN proxy terminates TLS
    externally; it does NOT mean the internal service speaks HTTPS.  Protocol
    is therefore derived exclusively from the ``protocols`` list declared in
    the interface:

      - "https" listed  → target_protocol = "https"
      - "http" listed   → target_protocol = "http"
      - neither         → target_protocol = "tcp"
    """
    protocols = iface_data.get("protocols", [])
    is_http = "http" in protocols or "https" in protocols
    target_type = "proxy" if is_http else "relay"

    if "https" in protocols:
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
        "icon_url": icon,
    }


def targets_from_manifest(manifest, registry_name, icon):
    """
    Parse a StartOS manifest dict and return a list of Tailrelay target dicts.

    Port resolution strategy (in order of preference):
      1. lan-config  - explicit internal port + ssl flag; most accurate.
      2. tor-config  - port-mapping format is {"external": "internal"}; used when
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
                    icon,
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
                        icon,
                    )
                )

    return targets


def apply_manual_overrides(targets):
    """Merge hand-curated overrides from assets/manual_targets.json.

    Each manual entry is keyed by (app_id, host, port).  When the key matches a
    generated target, the manual fields are applied on top of it (so a manual
    entry may override as little as one field, e.g. ``protocol``); when there
    is no match the manual entry is appended as a brand new target.

    Returns the (possibly extended) target list plus counts of overrides and
    additions applied.  A missing manual file is a no-op.
    """
    if not os.path.exists(MANUAL_FILE):
        return targets, 0, 0

    with open(MANUAL_FILE) as f:
        manual = json.load(f)

    index = {(t["app_id"], t["host"], t["port"]): t for t in targets}
    overrides = 0
    additions = 0
    for entry in manual:
        key = (entry["app_id"], entry["host"], entry["port"])
        if key in index:
            index[key].update(entry)
            overrides += 1
        else:
            targets.append(entry)
            index[key] = entry
            additions += 1
    return targets, overrides, additions


def main():
    # Collect manifests from all registries; deduplicate by app_id (first registry wins).
    seen_ids = set()
    all_targets = []

    for registry_name, url in REGISTRIES:
        print(f"Fetching {registry_name} registry...", file=sys.stderr)
        index = fetch_index(registry_name, url)
        registry_base = url.rsplit("/package/v0/index", 1)[0]
        new_count = 0

        for entry in index:
            manifest = entry.get("manifest")
            if not manifest:
                continue

            app_id = manifest.get("id")
            if not app_id:
                continue

            icon = f"{registry_base}/package/v0/icon/{app_id}"

            if app_id in seen_ids:
                print(
                    f"  Skipping {app_id} (already seen from higher-priority registry)",
                    file=sys.stderr,
                )
                continue

            seen_ids.add(app_id)
            targets = targets_from_manifest(manifest, registry_name, icon)
            all_targets.extend(targets)
            new_count += 1
            print(f"  {app_id}: {len(targets)} target(s)", file=sys.stderr)

        print(f"  -> {new_count} new package(s) from {registry_name}", file=sys.stderr)

    # Merge hand-curated overrides last so they win over generated data.
    all_targets, overrides, additions = apply_manual_overrides(all_targets)
    if overrides or additions:
        print(
            f"Merged manual overrides: {overrides} patched, {additions} added",
            file=sys.stderr,
        )

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
