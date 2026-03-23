PKG_ID := tailrelay
PKG_VERSION := $(shell yq e ".version" manifest.yaml)
TS_FILES := $(shell find . -name "*.ts" 2>/dev/null)
PLATFORM ?= linux/amd64

# Path to the tailrelay source tree. Override to use a local sibling repo:
#   make TAILRELAY_DIR=../tailrelay
TAILRELAY_DIR ?= tailrelay

# Build metadata derived from the tailrelay source tree
UPSTREAM_VERSION := $(shell git -C $(TAILRELAY_DIR) describe --tags --exact-match 2>/dev/null || git -C $(TAILRELAY_DIR) describe --tags 2>/dev/null || echo "dev")
UPSTREAM_COMMIT  := $(shell git -C $(TAILRELAY_DIR) rev-parse --short HEAD 2>/dev/null || echo "none")
UPSTREAM_DATE    := $(shell git -C $(TAILRELAY_DIR) log -1 --format=%cI 2>/dev/null || echo "unknown")
UPSTREAM_BRANCH  := $(shell git -C $(TAILRELAY_DIR) symbolic-ref --short HEAD 2>/dev/null || git -C $(TAILRELAY_DIR) describe --tags --exact-match 2>/dev/null || echo "unknown")

.DELETE_ON_ERROR:

all: verify

arm:
	@$(MAKE) PLATFORM=linux/arm64

x86:
	@$(MAKE) PLATFORM=linux/amd64

clean:
	rm -f $(PKG_ID).s9pk
	rm -f scripts/*.js
	rm -rf docker-images/
	rm -f image.tar

verify: $(PKG_ID).s9pk
	@start-sdk verify s9pk $(PKG_ID).s9pk
	@echo " Done!"
	@echo "   Filesize: $(shell du -h $(PKG_ID).s9pk) is ready"

install:
ifeq (,$(wildcard ~/.embassy/config.yaml))
	@echo; echo "You must define \"host: http://server-name.local\" in ~/.embassy/config.yaml config file first"; echo
else
	start-cli package install --sideload $(PKG_ID).s9pk
endif

scripts/embassy.js: $(TS_FILES)
	deno run --allow-read --allow-write --allow-env --allow-net scripts/bundle.ts

Dockerfile: $(TAILRELAY_DIR)/Dockerfile Dockerfile.startos
	@# The upstream Dockerfile starts with '# syntax=docker/dockerfile:1' which must
	@# remain on line 1 for BuildKit. We prepend our notice as inline comments after it.
	@head -1 $(TAILRELAY_DIR)/Dockerfile > Dockerfile
	@echo "# Generated — do not edit directly. Edit Dockerfile.startos and run: make Dockerfile" >> Dockerfile
	@tail -n +2 $(TAILRELAY_DIR)/Dockerfile >> Dockerfile
	@cat Dockerfile.startos >> Dockerfile

$(PKG_ID).s9pk: manifest.yaml instructions.md LICENSE icon.png scripts/embassy.js docker_entrypoint.sh Dockerfile image.tar
	start-sdk pack

# Sentinel file that changes whenever the tailrelay source tree's HEAD changes.
# For the default submodule, the real HEAD lives in .git/modules/tailrelay/HEAD.
# For a sibling repo (e.g. TAILRELAY_DIR=../tailrelay) it lives at $(TAILRELAY_DIR)/.git/HEAD.
ifeq ($(TAILRELAY_DIR),tailrelay)
TAILRELAY_HEAD := .git/modules/tailrelay/HEAD
else
TAILRELAY_HEAD := $(TAILRELAY_DIR)/.git/HEAD
endif

image.tar: Dockerfile docker_entrypoint.sh assets/startos_targets.json $(TAILRELAY_HEAD)
	docker buildx build \
		--tag start9/$(PKG_ID)/main:$(PKG_VERSION) \
		--platform=$(PLATFORM) \
		--build-arg VERSION=$(UPSTREAM_VERSION) \
		--build-arg COMMIT=$(UPSTREAM_COMMIT) \
		--build-arg DATE=$(UPSTREAM_DATE) \
		--build-arg BRANCH=$(UPSTREAM_BRANCH) \
		--build-arg BUILDER=start-sdk \
		--build-context startos=. \
		--file Dockerfile \
		-o type=docker,dest=image.tar \
		$(TAILRELAY_DIR)
