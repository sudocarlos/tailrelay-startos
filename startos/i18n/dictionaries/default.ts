export const DEFAULT_LANG = 'en_US'

const dict = {
    // manifest.ts
    'Tailrelay': 0,
    'Expose local services to your Tailscale network with automatic TLS, HTTP proxies, and TCP relays.': 1,
    'Tailrelay combines Tailscale VPN, Caddy reverse proxy, socat TCP relays, and a Web UI for browser-based management. Securely access self-hosted services like BTCPayServer, LND, electrs, and Mempool without Tor. Features automatic HTTPS certificates via Tailscale, protocol support for both HTTP/HTTPS proxies and raw TCP relays, and backup/restore functionality.': 2,
    'Tailrelay requires a Tailscale account with HTTPS certificates enabled. After installation, visit the Web UI to authenticate with Tailscale.': 3,

    // main.ts
    'Starting Tailrelay...': 4,
    'Web Interface': 5,
    'The Web UI is ready': 6,
    'The Web UI is not ready': 7,

    // interfaces.ts
    'Web UI': 8,
    'The Tailrelay management interface for configuring proxies, relays, and Tailscale connection.': 9,
} as const

/**
 * Plumbing. DO NOT EDIT.
 */
export type I18nKey = keyof typeof dict
export type LangDict = Record<(typeof dict)[I18nKey], string>
export default dict
