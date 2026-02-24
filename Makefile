PKG_ID := tailrelay
PKG_VERSION := $(shell yq e ".version" manifest.yaml)
TS_FILES := $(shell find . -name "*.ts" 2>/dev/null)
PLATFORM ?= linux/amd64

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

verify: $(PKG_ID).s9pk
	@start-sdk verify s9pk $(PKG_ID).s9pk
	@echo " Done!"
	@echo "   Filesize: $(shell du -h $(PKG_ID).s9pk) is ready"

install:
ifeq (,$(wildcard ~/.embassy/config.yaml))
	@echo; echo "You must define \"host: http://server-name.local\" in ~/.embassy/config.yaml config file first"; echo
else
	start-cli package install $(PKG_ID).s9pk
endif

scripts/embassy.js: $(TS_FILES)
	deno run --allow-read --allow-write --allow-env --allow-net scripts/bundle.ts

$(PKG_ID).s9pk: manifest.yaml instructions.md LICENSE icon.png scripts/embassy.js docker_entrypoint.sh Dockerfile image.tar
	start-sdk pack

image.tar: Dockerfile docker_entrypoint.sh
	docker buildx build --tag start9/$(PKG_ID)/main:$(PKG_VERSION) --platform=$(PLATFORM) -o type=docker,dest=image.tar .
