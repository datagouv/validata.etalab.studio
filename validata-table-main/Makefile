.DEFAULT: help

DC_PROD := docker compose -f docker-compose.yml
DC_DEV := $(DC_PROD) -f docker-compose.dev.override.yml
DC_PREPROD := $(DC_PROD) -f docker-compose.preprod.override.yml

.PHONY: help
help:
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test
test: ## Run all the tests
	@ $(DC_DEV) run --rm ui pytest . tests

.PHONY: serve_dev
serve_dev: ## Serves application in a development environment
	@ $(DC_DEV) up --build

.PHONY: serve_preprod
serve_preprod: ## Serves application in a production environment (as a daemon)
	@ $(DC_PREPROD) up -d --build

.PHONY: serve_prod
serve_prod: ## Serves application in a production environment (as a daemon)
	@ $(DC_PROD) up -d --build
