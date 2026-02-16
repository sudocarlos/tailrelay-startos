# AGENTS.md - Tailrelay StartOS Package

This document provides guidance for AI coding agents working on this codebase.

## Project Overview

This is a **StartOS package wrapper** for [Tailrelay](https://github.com/sudocarlos/tailrelay) using the **Start SDK** (`@start9labs/start-sdk`). The package wraps a Docker image and provides StartOS integration (interfaces, backups, health checks, etc.).

**Tech Stack:**

- Language: TypeScript (strict mode)
- Runtime: Node.js v22 LTS
- Build: Vercel ncc (bundler)
- Package Format: `.s9pk` (StartOS package)

## Build Commands

```bash
npm ci                       # Install dependencies
npm run check                # Type check (no emit)
npm run build                # Build JavaScript bundle
npm run prettier             # Format code with Prettier
```

## Make Commands (Package Building)

```bash
make                         # Build for all architectures (default)
make x86                     # Build x86_64 package (alias: x86_64)
make arm                     # Build ARM64 package (alias: aarch64, arm64)
make install                 # Build and sideload to StartOS device
make clean                   # Clean build artifacts
```

## Testing

No test suite. Validation:

1. `npm run check` - TypeScript type checking
2. `make` - Full package build
3. `make install` - Install on StartOS device for integration testing

## Code Style

### Formatting (Prettier in `package.json`)

- 2-space indentation, no semicolons, single quotes, trailing commas

### TypeScript (`tsconfig.json`)

- Target: ES2018, Module: CommonJS, Strict mode, esModuleInterop

### Naming Conventions

| Type                 | Convention         | Example                         |
| -------------------- | ------------------ | ------------------------------- |
| Files                | camelCase.ts       | `versionGraph.ts`, `backups.ts` |
| Directory entry      | index.ts           | `actions/index.ts`              |
| Version files        | v_X_Y_Z_W_label.ts | `v_0_4_0_0_4_b0.ts`             |
| Variables/Functions  | camelCase          | `uiPort`, `setInterfaces`       |
| Constants            | SCREAMING_SNAKE    | `DEFAULT_LANG`                  |
| Types                | PascalCase         | `I18nKey`, `LangDict`           |
| Package IDs          | kebab-case         | `'tailrelay'`                   |
| Volume/Interface IDs | kebab-case         | `'main'`, `'ui-multi'`          |

### Import Order

1. External packages (`@start9labs/start-sdk`)
2. Local SDK instance (`./sdk`)
3. Other local modules (by dependency order)

```typescript
import { VersionInfo } from '@start9labs/start-sdk'
import { sdk } from './sdk'
import { uiPort } from './utils'
```

### Export Patterns

- Named exports for functions and constants
- Re-exports in index.ts files
- Version aliasing: `export { v_0_4_0_0_4_b0 as current }`
- Default exports only for dictionary objects

## Directory Structure

Key files in `startos/`:

- `manifest.ts` - Package metadata
- `main.ts` - Daemon definitions + health checks
- `interfaces.ts` - Network interface definitions
- `backups.ts` - Backup volume definitions
- `dependencies.ts` - Package dependencies
- `utils.ts` - Shared constants
- `actions/index.ts` - Custom user actions
- `init/index.ts` - Container initialization
- `install/versions/` - Version migration files
- `install/versionGraph.ts` - Version graph builder
- `i18n/dictionaries/` - Internationalization strings
- `index.ts`, `sdk.ts` - Export plumbing (DO NOT EDIT)

## SDK Patterns

### Setup Functions

All SDK setup functions follow this pattern:

```typescript
export const mySetup = sdk.setupX(async ({ effects }) => {
  // Implementation
})
```

### Factory Methods

- `sdk.Daemons.of(effects)` - Create daemon manager
- `sdk.Actions.of()` - Create actions container
- `sdk.Mounts.of()` - Create mount configuration
- `sdk.MultiHost.of(effects, 'id')` - Create multi-host binding
- `sdk.SubContainer.of(effects, ...)` - Create subcontainer
- `sdk.Backups.ofVolumes('volumeId')` - Define backup volumes

### Static Builders

- `VersionGraph.of({ current, other, preInstall })` - Build version graph
- `VersionInfo.of({ version, releaseNotes, migrations })` - Define version

## Error Handling

The codebase relies on SDK-provided error handling:

- Async/await with implicit promise rejection
- Health checks for runtime error detection
- No try/catch blocks in typical wrapper code

## Adding New Versions

1. Create `startos/install/versions/v_X_Y_Z_W_label.ts`:

```typescript
import { VersionInfo } from '@start9labs/start-sdk'

export const v_X_Y_Z_W_label = VersionInfo.of({
  version: 'X.Y.Z:W-label',
  releaseNotes: { en_US: 'Release notes here.' },
  migrations: {
    up: async ({ effects }) => {},
    down: async ({ effects }) => {},
  },
})
```

2. Update `startos/install/versions/index.ts`:

```typescript
export { v_X_Y_Z_W_label as current } from './v_X_Y_Z_W_label'
export const other = [v_previous] // Add old version to array
```

## Files Marked "DO NOT EDIT"

These files contain SDK plumbing and should not be modified:

- `startos/index.ts` - Export plumbing
- `startos/sdk.ts` - SDK instance creation

## Skill Reference

For comprehensive StartOS packaging guidance, load the skill:

```
skill: startos-packaging-guide
```

This provides detailed documentation on manifests, interfaces, actions, backups, dependencies, file models, container initialization, and version migrations.
