import { i18n } from './i18n'
import { sdk } from './sdk'
import { uiPort } from './utils'

export const main = sdk.setupMain(async ({ effects }) => {
  console.info(i18n('Starting Tailrelay!'))

  const mounts = sdk.Mounts.of()
    .mountVolume({
      volumeId: 'main',
      subpath: null,
      mountpoint: '/data',
      readonly: false,
    })
    .mountVolume({
      volumeId: 'tailscale',
      subpath: null,
      mountpoint: '/var/lib/tailscale',
      readonly: false,
    })

  const mainSub = await sdk.SubContainer.of(
    effects,
    { imageId: 'main' },
    mounts,
    'tailrelay-sub',
  )

  return sdk.Daemons.of(effects).addDaemon('primary', {
    subcontainer: mainSub,
    exec: { command: sdk.useEntrypoint() },
    ready: {
      display: i18n('Web UI'),
      fn: () =>
        sdk.healthCheck.checkPortListening(effects, uiPort, {
          successMessage: i18n('The web interface is ready'),
          errorMessage: i18n('The web interface is not ready'),
        }),
    },
    requires: [],
  })
})
