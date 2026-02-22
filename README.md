# tailrelay-startos

StartOS wrapper for [Tailrelay](https://github.com/sudocarlos/tailrelay) — expose local services to your Tailscale network with automatic TLS, HTTP proxies, and TCP relays.

## Building

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (with [buildx](https://docs.docker.com/buildx/working-with-buildx/))
- [Make](https://www.gnu.org/software/make/)
- [yq](https://github.com/mikefarah/yq) — YAML processor
- [start-sdk](https://github.com/Start9Labs/start-os) — see [packaging docs](https://docs.start9.com/0.3.5.x/developer-docs/packaging)

### Build

```bash
make            # build Docker image, pack, and verify
```

### Install to StartOS Device

```bash
make install    # requires ~/.embassy/config.yaml
```

## License

MIT — see [LICENSE](LICENSE).
