# Build both x86_64 and aarch64 by default.
# Use `make x86` or `make arm64` for a single architecture.
ARCHES := x86 arm

# Path to the tailrelay source tree. Override to use a local sibling repo:
#   make TAILRELAY_DIR=../tailrelay
TAILRELAY_DIR ?= tailrelay

# Build metadata derived from the tailrelay source tree
UPSTREAM_VERSION := $(shell git -C $(TAILRELAY_DIR) describe --tags --exact-match 2>/dev/null || git -C $(TAILRELAY_DIR) describe --tags 2>/dev/null || echo "dev")
UPSTREAM_COMMIT  := $(shell git -C $(TAILRELAY_DIR) rev-parse --short HEAD 2>/dev/null || echo "none")
UPSTREAM_DATE    := $(shell git -C $(TAILRELAY_DIR) log -1 --format=%cI 2>/dev/null || echo "unknown")
UPSTREAM_BRANCH  := $(shell git -C $(TAILRELAY_DIR) symbolic-ref --short HEAD 2>/dev/null || git -C $(TAILRELAY_DIR) describe --tags --exact-match 2>/dev/null || echo "unknown")

# Sentinel file that changes whenever the tailrelay source tree's HEAD changes.
# For the default submodule, the real HEAD lives in .git/modules/tailrelay/HEAD.
# For a sibling repo (e.g. TAILRELAY_DIR=../tailrelay) it lives at $(TAILRELAY_DIR)/.git/HEAD.
ifeq ($(TAILRELAY_DIR),tailrelay)
TAILRELAY_HEAD := .git/modules/tailrelay/HEAD
else
TAILRELAY_HEAD := $(TAILRELAY_DIR)/.git/HEAD
endif

# Generate the combined Dockerfile from the upstream Dockerfile + StartOS layer.
# The upstream Dockerfile starts with '# syntax=docker/dockerfile:1' which must
# remain on line 1 for BuildKit. We prepend our notice as inline comments after it.
Dockerfile: $(TAILRELAY_DIR)/Dockerfile Dockerfile.startos $(TAILRELAY_HEAD)
	@head -1 $(TAILRELAY_DIR)/Dockerfile > Dockerfile
	@echo "# Generated — do not edit directly. Edit Dockerfile.startos and run: make Dockerfile" >> Dockerfile
	@tail -n +2 $(TAILRELAY_DIR)/Dockerfile >> Dockerfile
	@cat Dockerfile.startos >> Dockerfile

include s9pk.mk
