import { VersionInfo } from '@start9labs/start-sdk'

export const v_0_4_0_0_4_b0 = VersionInfo.of({
    version: '0.4.0:0.4-beta.0',
    releaseNotes: {
        en_US:
            'Initial StartOS package. Web UI for managing Tailscale, Caddy reverse proxies, and socat TCP relays.',
    },
    migrations: {
        up: async ({ effects }) => { },
        down: async ({ effects }) => { },
    },
})
