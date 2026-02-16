export const manifest = {
    id: 'tailrelay',
    title: 'Tailrelay',
    license: 'mit',
    wrapperRepo: 'https://github.com/sudocarlos/tailrelay-startos',
    upstreamRepo: 'https://github.com/sudocarlos/tailscale-socaddy-proxy',
    supportSite: 'https://github.com/sudocarlos/tailscale-socaddy-proxy/issues',
    marketingSite: 'https://github.com/sudocarlos/tailscale-socaddy-proxy',
    donationUrl: null,
    docsUrl: 'https://github.com/sudocarlos/tailrelay-startos/blob/master/docs',
    description: {
        short: {
            en_US:
                'Expose local services to your Tailscale network with automatic TLS, HTTP proxies, and TCP relays.',
        },
        long: {
            en_US:
                'Tailrelay combines Tailscale VPN, Caddy reverse proxy, socat TCP relays, and a Web UI for browser-based management. Securely access self-hosted services like BTCPayServer, LND, electrs, and Mempool without Tor. Features automatic HTTPS certificates via Tailscale, protocol support for both HTTP/HTTPS proxies and raw TCP relays, and backup/restore functionality.',
        },
    },
    assets: [],
    volumes: ['main'],
    images: {
        main: {
            source: {
                dockerBuild: {
                    dockerfile: 'Dockerfile',
                },
            },
        },
    },
    alerts: {
        install: {
            en_US:
                'Tailrelay requires a Tailscale account with HTTPS certificates enabled. After installation, visit the Web UI to authenticate with Tailscale.',
        },
        update: null,
        uninstall: null,
        restore: null,
        start: null,
        stop: null,
    },
    dependencies: {},
}
