# AGENTS.md - Tailrelay StartOS Package

This document provides guidance for AI coding agents working on this codebase.

## Project Overview

This is a **StartOS 0.4.0 package wrapper** for [Tailrelay](https://github.com/sudocarlos/tailrelay) using the **Start SDK** (`@start9labs/start-sdk` v1.0.0). The package builds a Docker image from the `tailrelay` submodule and provides StartOS integration (interfaces, health checks, backups, migrations).

**Tech Stack:**

- Language: TypeScript (Node.js)
- Runtime: Node.js (compiled via `@vercel/ncc` → `javascript/index.js`)
- Package Format: `.s9pk` (StartOS 0.4.0 package)
- Container: Docker (buildx, multi-platform: x86_64 + aarch64)

## Build Commands

```bash
npm ci                       # Install dependencies (first time)
make                         # Build both x86_64 and aarch64 packages (default)
make x86                     # Build x86_64 package only
make arm64                   # Build aarch64 package only
make install                 # Build and sideload to StartOS device
make clean                   # Clean build artifacts (javascript/, node_modules/, *.s9pk)
make Dockerfile              # Regenerate Dockerfile from tailrelay/Dockerfile + Dockerfile.startos
```

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with [buildx](https://docs.docker.com/buildx/working-with-buildx/)
- [Node.js](https://nodejs.org/) and npm
- [Make](https://www.gnu.org/software/make/)
- [start-cli](https://docs.start9.com/latest/developer-guide/sdk/installing-the-sdk) (for `start-cli s9pk pack`)
- `~/.startos/config.yaml` with `host: http://your-server.local` (for `make install`)

## Testing

No test suite. Validation:

1. `npm run check` — TypeScript type-check without emitting
2. `make x86` — Full package build for x86_64
3. `make install` — Install on StartOS 0.4.0 device for integration testing

## Code Style

### TypeScript (Node.js)

- Single quotes for strings
- No semicolons
- 2-space indentation
- Trailing commas

(Enforced by Prettier — run `npm run prettier` to format.)

### Naming Conventions

| Type                | Convention   | Example                                     |
| ------------------- | ------------ | ------------------------------------------- |
| Files               | camelCase.ts | `main.ts`, `interfaces.ts`                  |
| Entry point         | index.ts     | `startos/index.ts`                          |
| Variables/Functions | camelCase    | `setInterfaces`, `uiPort`                   |
| Package IDs         | kebab-case   | `'tailrelay'`                               |
| Volume IDs          | kebab-case   | `'main'`, `'tailscale'`                     |

## Directory Structure

```
/
├── .agents/                 # Agent skills and configuration
│   └── skills/
│       ├── git-workflow/       # Git commit/branch/PR conventions
│       ├── startos-packaging/  # Complete StartOS service packaging guide (.s9pk)
│       └── create-release/     # Release process for tailrelay-startos
├── assets/                  # Extra files (startos_targets.json, etc.)
├── startos/                 # Primary development directory (StartOS SDK integration)
│   ├── actions/
│   │   └── index.ts         # sdk.Actions.of() — no custom actions yet
│   ├── i18n/
│   │   ├── index.ts         # setupI18n() boilerplate
│   │   └── dictionaries/
│   │       ├── default.ts   # English strings keyed by index
│   │       └── translations.ts  # Translations for other locales
│   ├── init/
│   │   └── index.ts         # sdk.setupInit() + sdk.setupUninit()
│   ├── manifest/
│   │   ├── index.ts         # setupManifest() — id, volumes, images, alerts
│   │   └── i18n.ts          # Locale objects for description short/long
│   ├── versions/
│   │   ├── index.ts         # VersionGraph.of() — current + history
│   │   └── v0.8.6.0.a0.ts  # VersionInfo for 0.8.6:0-alpha.0
│   ├── backups.ts           # sdk.setupBackups() — main + tailscale volumes
│   ├── dependencies.ts      # sdk.setupDependencies() — empty
│   ├── index.ts             # Module exports (plumbing, do not edit)
│   ├── interfaces.ts        # sdk.setupInterfaces() — HTTP on port 8021
│   ├── main.ts              # sdk.setupMain() — primary daemon + health check
│   ├── sdk.ts               # SDK initialization (plumbing, do not edit)
│   └── utils.ts             # uiPort = 8021
├── Dockerfile               # Generated — do not edit directly (run: make Dockerfile)
├── Dockerfile.startos        # StartOS layer appended to upstream Dockerfile
├── docker_entrypoint.sh     # Ensures required directories exist, execs start.sh
├── icon.png                 # Package icon
├── instructions.md          # User-facing instructions (shown in StartOS UI)
├── LICENSE                  # MIT
├── Makefile                 # Build orchestration (ARCHES, Dockerfile gen, include s9pk.mk)
├── s9pk.mk                  # Shared build logic (plumbing, do not edit)
├── package.json             # Node.js dependencies (@start9labs/start-sdk, ncc, etc.)
├── tsconfig.json            # TypeScript compiler config
└── README.md                # Project overview
```

## Key Files

| File | Purpose |
|------|---------|
| `startos/manifest/index.ts` | Package metadata: ID, version, volumes, images, alerts |
| `startos/versions/index.ts` | Version graph: current and historical versions with migrations |
| `startos/main.ts` | Daemon runtime: subcontainer, exec, health check, volume mounts |
| `startos/interfaces.ts` | Network interface: HTTP on port 8021 exposed as `ui` type |
| `startos/backups.ts` | Backup: `main` + `tailscale` volumes |
| `startos/init/index.ts` | Init sequence: restoreInit, versionGraph, setInterfaces, setDependencies, actions |
| `Dockerfile.startos` | StartOS layer: copies entrypoint, sets CMD to docker_entrypoint.sh |
| `docker_entrypoint.sh` | Ensures `/var/lib/tailscale`, `/var/run/tailscale`, `/data/start9` exist; execs start.sh |
| `Makefile` | Custom targets: Dockerfile generation; delegates all s9pk targets to s9pk.mk |

## Start SDK Patterns

### Manifest

```typescript
import { setupManifest } from '@start9labs/start-sdk'

export const manifest = setupManifest({
  id: 'tailrelay',
  volumes: ['main', 'tailscale'],
  images: {
    main: {
      source: { dockerBuild: {} },
      arch: ['x86_64', 'aarch64'],
    },
  },
  // ...
})
```

### Main / Daemons

```typescript
export const main = sdk.setupMain(async ({ effects }) => {
  const mounts = sdk.Mounts.of()
    .mountVolume({ volumeId: 'main', subpath: null, mountpoint: '/data', readonly: false })
    .mountVolume({ volumeId: 'tailscale', subpath: null, mountpoint: '/var/lib/tailscale', readonly: false })

  const mainSub = await sdk.SubContainer.of(effects, { imageId: 'main' }, mounts, 'tailrelay-sub')

  return sdk.Daemons.of(effects).addDaemon('primary', {
    subcontainer: mainSub,
    exec: { command: sdk.useEntrypoint() },
    ready: {
      display: i18n('Web UI'),
      fn: () => sdk.healthCheck.checkPortListening(effects, uiPort, { ... }),
    },
    requires: [],
  })
})
```

### Interfaces

```typescript
export const setInterfaces = sdk.setupInterfaces(async ({ effects }) => {
  const multi = sdk.MultiHost.of(effects, 'ui-multi')
  const origin = await multi.bindPort(uiPort, { protocol: 'http' })
  const ui = sdk.createInterface(effects, { name: i18n('Tailrelay Web UI'), id: 'ui', type: 'ui', ... })
  return [await origin.export([ui])]
})
```

### Versions & Migrations

```typescript
// startos/versions/v0.8.6.0.a0.ts
export const v_0_8_6_0_a0 = VersionInfo.of({
  version: '0.8.6:0-alpha.0',
  releaseNotes: { en_US: '...', ... },
  migrations: {
    up: async ({ effects }) => {},
    down: IMPOSSIBLE,  // initial v0.4 release
  },
})

// startos/versions/index.ts
export const versionGraph = VersionGraph.of({
  current: v_0_8_6_0_a0,
  other: [],  // add previous versions here when releasing new ones
})
```

## Adding New Versions

1. Create `startos/versions/vX.Y.Z.N.ts` with the new `VersionInfo`
2. Update `startos/versions/index.ts` — set the new version as `current`, move old to `other`
3. Rebuild: `make clean && make`

## Volumes

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `main` | `/data` | Persistent data (config, relay definitions) |
| `tailscale` | `/var/lib/tailscale` | Tailscale state (keys, node identity) |

Both volumes are included in backups via `sdk.setupBackups()`.

## Interfaces

| Interface | Internal Port | Description |
|-----------|--------------|-------------|
| `ui` | 8021 (HTTP) | Tailrelay Web UI |

## Skill Reference

For Git workflow guidance (commits, branches, PRs):

```
skill: git-workflow
```

For StartOS service packaging reference (manifest, main.ts, interfaces, versions, testing):

```
skill: startos-packaging
```

For creating a new release (version bump, tags, pipelines):

```
skill: create-release
```
