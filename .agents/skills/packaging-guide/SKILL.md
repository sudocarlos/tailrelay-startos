---
name: startos-packaging-guide
description: Package services for StartOS using the Start SDK. Use when creating, building, or maintaining StartOS .s9pk packages, working with service manifests, configuring interfaces, actions, backups, dependencies, file models, container initialization, or version migrations.
---

# StartOS Packaging Guide

## Overview

StartOS packages (`.s9pk`) wrap Docker-based services with a TypeScript metadata layer (Start SDK) that enables GUI-driven install, configuration, networking, health checks, backups, and dependency management. The [Hello World template](https://github.com/Start9Labs/hello-world-startos) is the canonical starting point.

## Environment Prerequisites

- **StartOS device** – physical or VM ([flashing guide](../flashing-guides/))
- **Docker** – builds container images
- **Make** – orchestrates the build pipeline
- **Node.js v22 LTS** – compiles TypeScript
- **SquashFS** – `sudo apt install squashfs-tools squashfs-tools-ng` (Linux) or `brew install squashfs` (macOS)
- **start-cli** – `curl -fsSL https://start9labs.github.io/start-cli/install.sh | sh`

## Quick Start

```bash
# 1. Clone from the Hello World template
git clone <your-repo-url> && cd <repo-name>

# 2. Install dependencies
npm i

# 3. Build the .s9pk
make            # universal (all architectures)
make aarch64    # ARM64 only
make x86_64     # x86_64 only

# 4. Install to a StartOS device (requires ~/.startos/config.yaml)
make install
```

## Project Structure

```
/
├── assets/              # Optional extra files/scripts for your service
├── docs/                # Optional service documentation (instructions.md, etc.)
├── startos/             # Start SDK integration (see below)
│   ├── actions/         # Custom user-facing actions (buttons)
│   ├── fileModels/      # Typed file model definitions (.yaml, .toml, .json, etc.)
│   ├── init/            # Container initialization sequence
│   ├── install/         # Version graph + migrations
│   │   ├── versions/    # Per-version files with release notes & migrations
│   │   └── versionGraph.ts
│   ├── backups.ts       # Backup volume definitions & exclusions
│   ├── dependencies.ts  # Dependency declarations
│   ├── index.ts         # Export plumbing
│   ├── interfaces.ts    # Network interface definitions (LAN, Tor, clearnet)
│   ├── main.ts          # Daemon definitions + health checks
│   ├── manifest.ts      # Package metadata (ID, name, version, images, hw reqs)
│   ├── sdk.ts           # Package-typed SDK instance
│   └── utils.ts         # Package-specific constants/helpers
├── Dockerfile           # Optional custom image
├── icon.svg             # Package icon (≤ 40 KiB; .svg/.png/.jpg/.webp)
├── LICENSE
├── Makefile
├── package.json
└── tsconfig.json
```

## Key SDK Files

| File | Purpose |
|------|---------|
| `manifest.ts` | Static metadata: ID, name, description, release notes, volumes, images, hardware requirements, alerts, dependencies |
| `interfaces.ts` | Define service interfaces and exposure (LAN, Tor, clearnet). Runs on install, update, and config save |
| `main.ts` | Define daemons, runtime lifecycle, and health checks |
| `backups.ts` | Declare volumes to back up and exclusion patterns |
| `dependencies.ts` | Declare package dependencies, required versions, running state, and health check requirements |
| `actions/*.ts` | Custom actions displayed as buttons—accept input, return data (optionally masked or as QR) |
| `fileModels/*.ts` | Typed representations of config files with automatic parsing/serialization and reactive reads |
| `init/index.ts` | Container initialization order: `restoreInit` → `versionGraph` → `setInterfaces` → `setDependencies` → `actions` → custom |
| `install/versionGraph.ts` | Index versions, define `preInstall` logic for fresh installs |
| `install/versions/*.ts` | Per-version release notes and `up`/`down` migration functions |

## Container Initialization

Containers initialize on:
1. Fresh install, update, downgrade, or restore
2. Server (not service) restart
3. Manual "Container Rebuild" action

Starting/restarting a service does **not** trigger container init.

## File Models

Create typed file representations in `fileModels/`. Supported formats: `.json`, `.yaml`, `.toml`, `.ini`, `.env`, `.txt`. Use `raw` for custom formats with custom parser/serializer.

Reading patterns:
- `FileModel.read().once()` – one-time full read
- `FileModel.read(f => f.users).once()` – read a subset
- `FileModel.read().const(effects)` – reactive: re-runs context function on change
- `FileModel.read().onChange(effects)` – callback on change
- `FileModel.read().watch(effects)` – async iterator

## Build Commands

| Command | Description |
|---------|-------------|
| `make` / `make all` | Universal package (all platforms) |
| `make aarch64` | ARM64 only |
| `make x86_64` | x86_64 only |
| `make install` | Build + sideload to StartOS device |
| `make clean` | Remove build artifacts |

Commands can be chained: `make clean aarch64 install`

## Tips

- Hover over SDK functions in your editor for embedded documentation, type definitions, and examples
- Press `Ctrl+Space` inside objects for attribute auto-completion
- Use `store.json` file model to persist arbitrary data not managed by the upstream service
- Migrations (`up`/`down`) are only for data **not** migrated by the upstream service itself
- For detailed reference, see the individual guide files in [this directory](./README.md)
