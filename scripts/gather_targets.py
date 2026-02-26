#!/usr/bin/env python3

import urllib.request
import urllib.error
import json
import yaml
import sys

# Requirements: pip install pyyaml

REPOS = [
    "Start9Labs/bisq-startos",
    "Start9Labs/bitcoin-core-startos",
    "Start9Labs/bitcoin-explorer-startos",
    "Start9Labs/btc-rpc-proxy-startos",
    "Start9Labs/btcpayserver-startos",
    "Start9Labs/cln-startos",
    "Start9Labs/cryptpad-startos",
    "Start9Labs/cups-startos",
    "Start9Labs/cwtch-startos",
    "Start9Labs/deluge-startos",
    "Start9Labs/docuseal-startos",
    "Start9Labs/element-web-startos",
    "Start9Labs/filebrowser-startos",
    "Start9Labs/ghost-startos",
    "Start9Labs/hello-world-startos",
    "Start9Labs/holesail-startos",
    "Start9Labs/home-assistant-startos",
    "Start9Labs/iris-startos",
    "Start9Labs/jam-startos",
    "Start9Labs/jellyfin-startos",
    "Start9Labs/lightning-terminal-startos",
    "Start9Labs/lnbits-startos",
    "Start9Labs/lnd-startos",
    "Start9Labs/lndboss-startos",
    "Start9Labs/mastodon-startos",
    "Start9Labs/mempool-startos",
    "Start9Labs/myspeed-startos",
    "Start9Labs/nextcloud-startos",
    "Start9Labs/nostr-rs-relay-startos",
    "Start9Labs/ollama-startos",
    "Start9Labs/open-webui-startos",
    "Start9Labs/openclaw-startos",
    "Start9Labs/phoenixd-dashboard-startos",
    "Start9Labs/phoenixd-startos",
    "Start9Labs/ride-the-lightning-startos",
    "Start9Labs/searxng-startos",
    "Start9Labs/serge-startos",
    "Start9Labs/spark-wallet-startos",
    "Start9Labs/sphinx-relay-startos",
    "Start9Labs/start9-pages-startos",
    "Start9Labs/synapse-startos",
    "Start9Labs/syncthing-startos",
    "Start9Labs/thunderhub-startos",
    "Start9Labs/tor-startos",
    "Start9Labs/vaultwarden-startos"
]

def fetch_manifest(repo):
    branches = ["master", "main"]
    extensions = ["yaml", "yml"]
    
    for branch in branches:
        for ext in extensions:
            url = f"https://raw.githubusercontent.com/{repo}/{branch}/manifest.{ext}"
            try:
                # Add headers to avoid basic scraping blocks
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    content = response.read()
                    return yaml.safe_load(content)
            except urllib.error.HTTPError as e:
                # 404 means try the next URL combination
                if e.code == 404:
                    continue
                else:
                    print(f"HTTP Error {e.code} for {url}: {e.reason}", file=sys.stderr)
            except Exception as e:
                print(f"Error fetching {url}: {e}", file=sys.stderr)
    return None

def main():
    targets = []
    
    for repo in REPOS:
        print(f"Processing {repo}...", file=sys.stderr)
        manifest = fetch_manifest(repo)
        
        if not manifest:
            print(f"  -> Warning: No manifest found.", file=sys.stderr)
            continue
            
        app_id = manifest.get('id')
        if not app_id:
            print(f"  -> Warning: Manifest missing 'id' field.", file=sys.stderr)
            continue
            
        host = f"{app_id}.embassy"
        interfaces = manifest.get('interfaces', {})
        
        for iface_id, iface_data in interfaces.items():
            protocols = iface_data.get('protocols', [])
            lan_config = iface_data.get('lan-config', {})
            
            # Prioritize LAN config since it specifies internal ports and ssl context
            for external_port, port_config in lan_config.items():
                if not isinstance(port_config, dict):
                    # Sometimes config is simplified
                    continue
                
                internal_port = port_config.get('internal', external_port)
                ssl = port_config.get('ssl', False)
                
                is_http = 'http' in protocols or 'https' in protocols
                
                # Determine Tailrelay type and protocol
                target_type = "proxy" if is_http else "relay"
                target_protocol = "https" if ssl else ("http" if is_http else "tcp")
                
                target = {
                    "app_id": app_id,
                    "host": host,
                    "port": int(internal_port),
                    "type": target_type,
                    "protocol": target_protocol,
                    "target_name": iface_data.get('name', iface_id)
                }
                targets.append(target)
                
    output_file = "startos_targets.json"
    with open(output_file, 'w') as f:
        json.dump(targets, f, indent=2)
        
    print(f"\nDiscovered {len(targets)} targets. Saved to {output_file}.", file=sys.stderr)

if __name__ == "__main__":
    main()
