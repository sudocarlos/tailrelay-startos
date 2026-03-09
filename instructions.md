# Tailrelay Instructions

Tailrelay exposes your StartOS services to your Tailscale network via automatic HTTPS proxies and TCP relays.

## Getting Started

1. Install and start Tailrelay.
2. Open the Web UI from the Interfaces tab.
3. On first launch you will be prompted to **create an admin password**. Set a strong password and save it.
4. Once logged in, go to the **Tailscale** section and click **Connect with Auth Key**.
5. Paste a reusable auth key from your [Tailscale admin console](https://login.tailscale.com/admin/settings/keys) and click **Connect**.
6. After Tailscale connects, use the Web UI to add HTTP/HTTPS reverse proxies and TCP relays.

## Notes

- The admin password is stored in the `tailscale` volume and survives restarts and upgrades.
- The Tailscale auth key is entered through the Web UI — there is no StartOS config form.
- Both the `main` and `tailscale` volumes are included in StartOS backups.
