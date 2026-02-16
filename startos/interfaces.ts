import { sdk } from './sdk'
import { uiPort } from './utils'

export const setInterfaces = sdk.setupInterfaces(async ({ effects }) => {
    const uiMulti = sdk.MultiHost.of(effects, 'ui-multi')
    const uiMultiOrigin = await uiMulti.bindPort(uiPort, {
        protocol: 'http',
    })
    const ui = sdk.createInterface(effects, {
        name: 'Web UI',
        id: 'ui',
        description:
            'The Tailrelay management interface for configuring proxies, relays, and Tailscale connection.',
        type: 'ui',
        masked: false,
        schemeOverride: null,
        username: null,
        path: '',
        query: {},
    })

    const uiReceipt = await uiMultiOrigin.export([ui])

    return [uiReceipt]
})
