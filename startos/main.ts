import { sdk } from './sdk'
import { uiPort } from './utils'

export const main = sdk.setupMain(async ({ effects }) => {
    console.info('Starting Tailrelay...')

    return sdk.Daemons.of(effects).addDaemon('primary', {
        subcontainer: await sdk.SubContainer.of(
            effects,
            { imageId: 'main' },
            sdk.Mounts.of().mountVolume({
                volumeId: 'main',
                subpath: null,
                mountpoint: '/var/lib/tailscale',
                readonly: false,
            }),
            'tailrelay',
        ),
        exec: { command: ['start.sh'] },
        ready: {
            display: 'Web Interface',
            fn: () =>
                sdk.healthCheck.checkPortListening(effects, uiPort, {
                    successMessage: 'The Web UI is ready',
                    errorMessage: 'The Web UI is not ready',
                }),
        },
        requires: [],
    })
})
