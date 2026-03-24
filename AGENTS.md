# AGENTS.md - Tailrelay StartOS Package

This document provides guidance for AI coding agents working on this codebase.

## Project Overview

This is a **StartOS package wrapper** for [Tailrelay](https://github.com/sudocarlos/tailrelay) using the **Embassy SDK** (`embassyd_sdk` v0.3.3). The package builds a Docker image from the `tailrelay` submodule and provides StartOS integration (interfaces, health checks, backups, migrations).

**Tech Stack:**

- Language: TypeScript (Deno)
- Runtime: [Deno](https://deno.land/) (scripts compiled via `deno.land/x/emit`)
- Package Format: `.s9pk` (StartOS package)
- Container: Docker (buildx, multi-platform)

## Build Commands

```bash
make                         # Build Docker image, pack .s9pk, and verify (default platform: linux/amd64)
make x86                     # Build x86_64 package
make arm                     # Build ARM64 package
make install                 # Build and sideload to StartOS device
make clean                   # Clean build artifacts (scripts/*.js, docker-images/, *.s9pk)
```

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with [buildx](https://docs.docker.com/buildx/working-with-buildx/)
- [Deno](https://deno.land/) (for bundling TypeScript scripts)
- [Make](https://www.gnu.org/software/make/)
- [yq](https://github.com/mikefarah/yq) (YAML processor, used by Makefile)
- [start-sdk](https://github.com/Start9Labs/start-os) (for `start-sdk pack` and `start-sdk verify`)

## Testing

No test suite. Validation:

1. `make` - Full package build + verification (`start-sdk verify`)
2. `make install` - Install on StartOS device for integration testing

## Code Style

### TypeScript (Deno)

- Double quotes for strings
- Semicolons at end of statements
- 2-space indentation

### Naming Conventions

| Type                 | Convention         | Example                                  |
| -------------------- | ------------------ | ---------------------------------------- |
| Files                | camelCase.ts       | `getConfig.ts`, `healthChecks.ts`        |
| Entry point          | embassy.ts         | `scripts/embassy.ts`                     |
| Variables/Functions  | camelCase          | `setConfig`, `healthUtil`                |
| Package IDs          | kebab-case         | `'tailrelay'`                            |
| Volume IDs           | kebab-case         | `'main'`, `'tailscale'`                  |

### Import Pattern

All procedure files import from a shared `deps.ts` barrel:

```typescript
import { compat, types as T } from "../deps.ts";
```

The `deps.ts` file re-exports from the Embassy SDK:

```typescript
export * from "https://deno.land/x/embassyd_sdk@v0.3.3.0.11/mod.ts";
```

## Directory Structure

```
/
├── .agents/                 # Agent skills and configuration
│   └── skills/
│       ├── git-workflow/       # Git commit/branch/PR conventions
│       ├── startos-packaging/  # Complete StartOS service packaging guide (.s9pk)
│       └── create-release/     # Release process for tailrelay-startos
├── assets/                  # Extra files (currently just README.md)
├── scripts/                 # Deno TypeScript source
│   ├── bundle.ts            # Deno bundler script (compiles embassy.ts → embassy.js)
│   ├── deps.ts              # Barrel file re-exporting Embassy SDK
│   ├── embassy.ts           # Entry point — re-exports all procedures
│   ├── embassy.js           # Compiled output (generated, do not edit)
│   └── procedures/          # StartOS integration procedures
│       ├── healthChecks.ts  # Web UI health check (HTTP check on port 8021)
│       ├── migrations.ts    # Version migrations
│       └── properties.ts   # Service properties display
├── Dockerfile               # Extends sudocarlos/tailrelay:latest with entrypoint
├── docker_entrypoint.sh     # Ensures required directories exist, execs start.sh
├── manifest.yaml            # Package metadata, volumes, interfaces, backup config
├── instructions.md          # User-facing instructions (shown in StartOS UI)
├── icon.png                 # Package icon
├── Makefile                 # Build orchestration
├── LICENSE                  # MIT
└── README.md                # Project overview
```

## Key Files

| File | Purpose |
|------|---------|
| `manifest.yaml` | Package metadata: ID, version, volumes, interfaces, backup/restore, migrations, health checks |
| `scripts/embassy.ts` | Entry point that re-exports all procedure functions |
| `scripts/procedures/healthChecks.ts` | HTTP health check against `http://tailrelay.embassy:8021` |
| `scripts/procedures/migrations.ts` | Version migration mappings |
| `scripts/procedures/properties.ts` | Exports `compat.properties` for the properties display |
| `docker_entrypoint.sh` | Ensures required directories exist, execs `start.sh` |
| `Dockerfile` | Built from `tailrelay` submodule + StarOS layer; copies entrypoint |

## Embassy SDK Patterns

### Procedure Exports

All procedures follow the `compat` helper pattern from the Embassy SDK:

```typescript
import { compat, types as T } from "../deps.ts";

export const getConfig: T.ExpectedExports.getConfig = compat.getConfig({
  // config field definitions
});
```

### Health Checks

Health checks use `healthUtil.checkWebUrl` to verify HTTP endpoints:

```typescript
import { types as T, healthUtil } from "../deps.ts";

export const health: T.ExpectedExports.health = {
  async "web-ui"(effects, duration) {
    return healthUtil
      .checkWebUrl("http://tailrelay.embassy:8021")(effects, duration)
      .catch(healthUtil.catchError(effects));
  },
};
```

### Migrations

Migrations use `compat.migrations.fromMapping` with version keys:

```typescript
export const migration: T.ExpectedExports.migration = compat.migrations
  .fromMapping({
    "0.4.2": {
      up: compat.migrations.updateConfig((config: any) => config, true, { version: "0.4.2", type: "script" }),
      down: compat.migrations.updateConfig((config: any) => config, true, { version: "0.4.3", type: "script" }),
    },
  }, "0.4.3");
```

## Adding New Versions

1. Update `manifest.yaml` — bump `version` and update `release-notes`
2. Rebuild: `make clean && make`

## Volumes

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `main` | `/data` | Persistent data (config, relay definitions) |
| `tailscale` | `/var/lib/tailscale` | Tailscale state (keys, node identity) |

Both volumes are included in backups via `duplicity`.

## Interfaces

| Interface | Port (External → Internal) | Description |
|-----------|---------------------------|-------------|
| `main` | LAN 443 (SSL) → 8021, Tor 80 → 8021 | Tailrelay Web UI |

## Skill Reference

For Git workflow guidance (commits, branches, PRs):

```
skill: git-workflow
```

For StartOS service packaging reference (manifest, Dockerfile, config spec, testing, submission):

```
skill: startos-packaging
```

For creating a new release (version bump, tags, pipelines):

```
skill: create-release
```
