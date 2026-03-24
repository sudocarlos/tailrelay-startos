# Tailrelay Instructions

Tailrelay exposes your StartOS services to your Tailscale network via automatic HTTPS proxies and TCP relays.

## Getting Started

1. Install and start Tailrelay.
2. Click launch UI from the Tailrelay services page.
3. On first launch you will be prompted to **create an admin password**. Set a strong password and save it.
4. Once logged into Tailrelay, you must authenticate to Tailscale using either:
   - Login URL - click **Get Login URL** and open the generated link in a browser to authenticate
   - Auth Key - [generate a reusable auth key](https://login.tailscale.com/admin/machines/new-linux), paste it in, and click **Connect**.
5. Set your Tailrelay's hostname. 
6. After Tailscale connects, go to the **Dashboard** to add TCP and HTTPS relays.

## Tailscale Setup

1. Log into the [Tailscale Admin console](https://login.tailscale.com/admin/machines/new-linux) and click **DNS** to [enable MagicDNS](https://tailscale.com/kb/1081/magicdns).  
   _Tailnets created on or after October 20, 2022 have MagicDNS enabled by default._
2. Verify or set your [Tailnet name](https://login.tailscale.com/admin/dns).
3. Scroll down and enable **HTTPS** under [HTTPS Certificates](https://tailscale.com/kb/1153/enabling-https).
