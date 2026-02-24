---
name: startos-packaging
description: Complete guide for packaging services for StartOS (.s9pk), including manifest, Dockerfile, scripting, config, dependencies, testing, and submission
metadata:
  version: "1.0.0"
  tags: ["startos", "packaging", "s9pk", "start-sdk", "docker"]
  source: "https://docs.start9.com/latest/developer-docs"
---

# StartOS Service Packaging Skill

You are a StartOS service packaging assistant. Help users create, build, test, and submit `.s9pk` packages for StartOS.

## Key Concepts

- **Service** — An application that runs on StartOS (server-side software)
- **Package (.s9pk)** — The bundled artifact installed on StartOS, containing a Docker image, manifest, instructions, icon, and license
- **Wrapper** — The repository that "wraps" an upstream project with the metadata files needed to build a `.s9pk`
- **start-sdk** — The CLI tool used to pack and verify services
- **start-cli** — The CLI tool for interacting with a running StartOS instance

## Software Compatibility

Suitable services should meet these criteria:

1. Has a web UI, REST API, or accepts TCP connections (no SSH/CLI-only tools)
2. Can compile for `arm64v8` (aarch64) and/or `amd64` (x86_64)
3. Can be served over Tor
4. Docker image optimized for size (under 1GB preferred)

---

## Development Environment

### Required Dependencies

- **Docker** + **Buildx** (cross-arch builds):
  ```bash
  curl -fsSL https://get.docker.com | bash
  sudo usermod -aG docker "$USER"
  exec sudo su -l $USER
  docker run --privileged --rm linuxkit/binfmt:v0.8  # ARM emulation (skip on ARM hosts)
  docker buildx install
  docker buildx create --use
  ```

- **Rust & Cargo**:
  ```bash
  curl https://sh.rustup.rs -sSf | sh
  source $HOME/.cargo/env
  ```

- **Start SDK**:
  ```bash
  git clone https://github.com/Start9Labs/start-os.git && \
    cd start-os && git submodule update --init --recursive && \
    make sdk
  start-sdk init
  start-sdk --version
  ```

- **Deno** (optional, for JS scripting):
  ```bash
  curl -fsSL https://deno.land/x/install/install.sh | sh
  ```

### Recommended Dependencies

- Build essentials: `sudo apt-get install -y build-essential openssl libssl-dev libc6-dev clang libclang-dev ca-certificates`
- Git: `sudo apt install git`
- yq: `sudo snap install yq`

---

## Wrapper Repository Structure

```
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── assets/
│   └── compat/
│       ├── config_rules.yaml
│       └── config_spec.yaml
├── docker_entrypoint.sh
├── <submodule-project>/
├── icon.png
├── instructions.md
├── manifest.yaml
└── scripts/
    └── procedures/
```

### Required Files

| File | Purpose |
|---|---|
| `manifest.yaml` | Package metadata, versions, ports, volumes, dependencies, health checks |
| `instructions.md` | User-facing instructions rendered in the StartOS UI |
| `LICENSE` | Open source license |
| `icon.png` | Service icon (< 100KB) |
| `Dockerfile` | Docker image build recipe |
| `docker_entrypoint.sh` | Container startup script, handles SIGTERMs gracefully |

### Optional Files

| File | Purpose |
|---|---|
| `Makefile` | Build automation: Docker build → `start-sdk pack` → `start-sdk verify` |
| `prepare.sh` | Sets up Debian build environment for Start9 reproducible builds |
| `scripts/` | TypeScript procedures for config, migrations, health checks |
| `assets/compat/` | Config spec and config rules files |

---

## Manifest Specification

The `manifest.yaml` (or `.toml`/`.json`) defines all service metadata. Key fields:

```yaml
id: my-service                  # Unique lowercase hyphenated identifier
title: My Service               # Human-readable title
version: 1.0.0                  # Semver (up to 4 digits)
release-notes: "Initial release"
license: mit
wrapper-repo: "https://github.com/user/my-service-wrapper"
upstream-repo: "https://github.com/upstream/project"
support-site: "https://github.com/user/my-service-wrapper/issues"
marketing-site: "https://example.com"
build: ["make"]
min-os-version: 0.3.0

description:
  short: "A brief description"
  long: "A detailed description for the marketplace page"

assets:
  license: LICENSE               # Default: LICENSE.md
  icon: icon.png                 # Default: icon.png
  instructions: instructions.md  # Default: INSTRUCTIONS.md
  docker-images: image.tar       # Default: image.tar

# Main service action (Docker container)
main:
  type: docker
  image: main
  entrypoint: "docker_entrypoint.sh"
  args: []
  mounts:
    main: /root                  # Persistence directory mount point
  io-format: yaml

# Health checks
health-checks:
  main:
    name: Web UI
    description: "Checks that the web UI is accessible"
    type: docker
    image: main
    entrypoint: "check-web.sh"
    args: []
    inject: true                 # Use main image (faster)
    io-format: yaml

# Volumes
volumes:
  main:
    type: data                   # Persists across updates
  compat:
    type: assets                 # Static assets (requires assets/compat/ folder)

# Network interfaces
interfaces:
  main:
    name: Web UI
    description: "The main web interface"
    tor-config:
      port-mapping:
        80: "80"
    lan-config:
      443:
        ssl: true
        internal: 80
    ui: true
    protocols:
      - tcp
      - http

# Dependencies (empty object if standalone)
dependencies: {}

# Alerts (all optional; defaults exist except start)
alerts:
  install-alert: "Custom install message"
  uninstall-alert: "Custom uninstall message"
  restore-alert: "Custom restore message"
  start-alert: "Custom start message"

# Backups using the compat/duplicity system
backup:
  create:
    type: docker
    image: compat
    system: true
    entrypoint: compat
    args:
      - duplicity
      - my-service
      - /mnt/backup
      - /root/data
    mounts:
      BACKUP: /mnt/backup
      main: /root/data
  restore:
    type: docker
    image: compat
    system: true
    entrypoint: compat
    args:
      - duplicity
      - my-service
      - /mnt/backup
      - /root/data
    mounts:
      BACKUP: /mnt/backup
      main: /root/data

# User-triggered actions (optional)
actions: {}
```

---

## Dockerfile Guidelines

- StartOS supports **one Dockerfile** per project (no Docker Compose)
- Prefer `alpine` base images for smallest size
- Build with buildx for cross-platform:
  ```bash
  docker buildx build \
    --tag start9/$(PKG_ID)/main:$(PKG_VERSION) \
    --platform linux/arm64 \
    -o type=docker,dest=image.tar .
  ```
- The resulting `image.tar` is included in the `.s9pk`
- Mount the service data at the path specified in `manifest.yaml` → `main.mounts.main`
- In StartOS, volumes bind to `/embassy-data/package-data/volumes/main/<service-id>`

### docker_entrypoint.sh

- Complete environment setup (create directories, set env vars)
- Execute the service run command
- Handle SIGTERMs for graceful shutdown
- Optionally generate `stats.yaml` for Properties display

---

## Config Specification

The config spec defines the UI-driven configuration form. ValueSpec types:

| Type | Description | UI Element |
|---|---|---|
| `boolean` | True/false toggle | Toggle switch |
| `enum` | Selection from a set | Dropdown |
| `list` | Array of values | List editor |
| `number` | Numeric value with optional range | Number input |
| `object` | Nested config group | Collapsible section |
| `string` | Text, optionally masked/copyable | Text input |
| `union` | Multiple variant configs | Variant selector |
| `pointer` | Reference to another service's config | Auto-linked |

Example config spec:
```yaml
enable-feature:
  type: boolean
  name: Enable Feature
  description: "Toggle this feature on or off"
  default: true

port:
  type: number
  name: Port
  description: "The port to listen on"
  nullable: false
  integral: true
  range: "[1024, 65535]"
  default: 8080

password:
  type: string
  name: Password
  description: "Service password"
  nullable: false
  copyable: true
  masked: true
  default:
    charset: "a-z,A-Z,0-9"
    len: 22
```

---

## JS Scripting API

For advanced features (config, migrations, health checks, properties, dependencies), create `scripts/embassy.ts`:

```typescript
import { types as T } from "https://deno.land/x/embassyd_sdk@v0.3.3.0.5/mod.ts";

export const getConfig: T.ExpectedExports.getConfig = /* ... */;
export const setConfig: T.ExpectedExports.setConfig = /* ... */;
export const properties: T.ExpectedExports.properties = /* ... */;
export const dependencies: T.ExpectedExports.dependencies = /* ... */;
export const health: T.ExpectedExports.health = /* ... */;
export const migration: T.ExpectedExports.migration = /* ... */;
```

Build step (must output to `scripts/embassy.js`):
```bash
deno bundle scripts/embassy.ts scripts/embassy.js
```

Set `type: script` in manifest config stanza to use JS procedures instead of Docker.

---

## Dependencies

Define in `manifest.yaml` under `dependencies`:

```yaml
dependencies:
  bitcoind:
    version: "^0.21.1.2"
    critical: false
    requirement:
      type: "opt-in"       # opt-in | opt-out | required
      how: "Can configure an external node instead"
    description: "Used to fetch validated blocks"
    config:                # Optional: advanced auto-configuration
      check:
        type: docker
        image: compat
        system: true
        entrypoint: compat
        args: [dependency, check, my-service, bitcoind, /datadir, /mnt/assets/bitcoind_config_rules.yaml]
        mounts:
          main: /datadir
          compat: /mnt/assets
        io-format: yaml
      auto-configure:
        type: docker
        image: compat
        system: true
        entrypoint: compat
        args: [dependency, auto-configure, my-service, bitcoind, /datadir, /mnt/assets/bitcoind_config_rules.yaml]
        mounts:
          main: /datadir
          compat: /mnt/assets
        io-format: yaml
```

Config rules file example:
```yaml
- rule: "advanced.peers.listen?"
  description: "Peer port must be listening"
  suggestions:
    - SET:
        var: advanced.peers.listen
        to-value: true
```

---

## Properties (stats.yaml)

Display runtime information in the service Properties panel:

```yaml
version: 2
data:
  "Admin URL":
    type: string
    value: "http://my-service.local:8080"
    description: "Web admin interface"
    copyable: true
    qr: false
    masked: false
```

---

## Build & Pack Commands

### Build the Docker image
```bash
docker buildx build --tag start9/$(PKG_ID)/main:$(PKG_VERSION) \
  --platform linux/arm64 -o type=docker,dest=image.tar .
```

### Pack into .s9pk
```bash
start-sdk pack
```

### Verify the package
```bash
start-sdk verify s9pk <package-id>.s9pk
```

### Inspect package contents
```bash
start-sdk inspect manifest <package-id>.s9pk
start-sdk inspect instructions <package-id>.s9pk
start-sdk inspect icon <package-id>.s9pk
start-sdk inspect docker-images <package-id>.s9pk
```

---

## Testing

1. Build: `make` (or run Docker build + `start-sdk pack` manually)
2. Sideload via UI: **System → Sideload Service** → drag and drop `.s9pk`
3. Or install via CLI:
   ```bash
   echo "host: <STARTOS_IP>" > /etc/embassy/config.yaml
   start-cli auth login
   start-cli package install <package-id>.s9pk
   ```
4. Verify:
   - Service starts and health checks pass
   - UI launches correctly (if applicable)
   - All Properties display accurate information
   - Config UI renders without errors
   - Service stops and restarts cleanly
   - Backup and restore work correctly

---

## Community Submission Checklist

1. Source code is public (wrapper + upstream)
2. `prepare.sh` produces a clean build on Debian
3. `make <package-id>.s9pk` builds without errors
4. Submit wrapper repo link to `submissions@start9.com`

### Start9 Review Criteria

- [ ] Marketplace listing has all required metadata and valid links
- [ ] Install/uninstall runs smoothly
- [ ] Instructions display correctly
- [ ] Properties display correctly
- [ ] Config functions without errors
- [ ] Dependencies use StartOS dependency management
- [ ] Actions run without errors
- [ ] Health checks display and run correctly
- [ ] At least one interface is defined
- [ ] Logs display correctly
- [ ] Runs alongside other services on low-resource devices (RPi 8GB)
- [ ] Backup and restore succeed

---

## Packaging Checklist (Quick Reference)

- [ ] Create or select project
- [ ] Build project
- [ ] Cross-compile for arm64/amd64 if necessary
- [ ] Create Dockerfile and docker_entrypoint.sh
- [ ] Create manifest.yaml
- [ ] Create instructions.md
- [ ] Create icon.png (< 100KB)
- [ ] Add LICENSE
- [ ] Package with `start-sdk pack`
- [ ] Verify with `start-sdk verify`
- [ ] Create wrapper repo on GitHub
- [ ] (Optional) Add Makefile for reproducible builds
- [ ] Test on StartOS device or VM

---

## Reference Examples

- [Hello World Wrapper](https://github.com/Start9Labs/hello-world-wrapper)
- [Filebrowser Wrapper](https://github.com/Start9Labs/filebrowser-wrapper)
- [BTCPay Server Wrapper](https://github.com/Start9Labs/btcpayserver-wrapper)
- [Synapse Wrapper](https://github.com/Start9Labs/synapse-wrapper)
- [LND Wrapper](https://github.com/Start9Labs/lnd-wrapper)
- [Photoview Wrapper](https://github.com/Start9Labs/photoview-wrapper)

## Support

- [Start9 Community](https://community.start9.com)
- [Matrix Dev Channel](https://matrix.to/#/#community-dev:matrix.start9labs.com)
- [Full Specification](https://start9.com/latest/developer-docs/specification)
