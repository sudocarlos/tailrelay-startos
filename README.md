# tailrelay-startos

StartOS wrapper for [Tailrelay](https://github.com/sudocarlos/tailrelay) — expose local services to your Tailscale network with automatic TLS, HTTP proxies, and TCP relays.

## Building

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (with [buildx](https://docs.docker.com/buildx/working-with-buildx/))
- [Node.js](https://nodejs.org/) and npm
- [Make](https://www.gnu.org/software/make/)
- [start-cli](https://docs.start9.com/latest/developer-guide/sdk/installing-the-sdk) — see [packaging docs](https://docs.start9.com/packaging/)

### Build

```bash
npm ci          # install dependencies (first time only)
make            # build both x86_64 and aarch64 packages
make x86        # build x86_64 only
make arm64      # build aarch64 only
```

### Install to StartOS Device

```bash
make install    # requires ~/.startos/config.yaml with host: http://your-server.local
```

## Sideloading

1. Clone this repo and run `npm ci && make`, or download the package from [the releases page](https://github.com/sudocarlos/tailrelay-startos/releases).
2. Install the package:
   - In the StartOS web UI menu, navigate to **System -> Sideload Service**.
   - Drag and drop or select the `<package>.s9pk` from your filesystem to install.
3. Once the service has installed, navigate to **Services -> Tailrelay** and click **Start**.

## License

MIT — see [LICENSE](LICENSE).
