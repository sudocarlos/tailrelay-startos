import { setupManifest } from '@start9labs/start-sdk'
import { short, long } from './i18n'

export const manifest = setupManifest({
  id: 'tailrelay',
  title: 'Tailrelay',
  license: 'MIT',
  packageRepo: 'https://github.com/sudocarlos/tailrelay-startos',
  upstreamRepo: 'https://github.com/sudocarlos/tailrelay',
  marketingUrl: 'https://github.com/sudocarlos/tailrelay',
  donationUrl: null,
  docsUrls: ['https://github.com/sudocarlos/tailrelay/blob/main/README.md'],
  description: { short, long },
  volumes: ['main', 'tailscale'],
  images: {
    main: {
      source: {
        dockerBuild: {},
      },
      arch: ['x86_64', 'aarch64'],
    },
  },
  alerts: {
    install: null,
    update: null,
    uninstall: null,
    restore: null,
    start: null,
    stop: null,
  },
  dependencies: {},
})
