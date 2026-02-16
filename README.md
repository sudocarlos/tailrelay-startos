# tailrelay-startos

StartOS wrapper for [Tailrelay](https://github.com/sudocarlos/tailscale-socaddy-proxy) — expose local services to your Tailscale network with automatic TLS, HTTP proxies, and TCP relays.

## Building

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Make](https://www.gnu.org/software/make/)
- [Node.js v22 LTS](https://nodejs.org/)
- [SquashFS tools](https://github.com/plougher/squashfs-tools) — `sudo apt install squashfs-tools squashfs-tools-ng`
- [start-cli](https://github.com/Start9Labs/start-cli/) — `curl -fsSL https://start9labs.github.io/start-cli/install.sh | sh`

### Build

```bash
npm i
make            # universal (all architectures)
make aarch64    # ARM64 only
make x86_64     # x86_64 only
```

### Install to StartOS Device

```bash
make install    # requires ~/.startos/config.yaml
```

## License

MIT — see [LICENSE](LICENSE).
