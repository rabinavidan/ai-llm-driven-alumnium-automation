.DEFAULT_GOAL := help
COMPOSE := docker compose

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

test: ## Run the full suite in Docker (Ollama + Selenium + runner)
	$(COMPOSE) up --build --abort-on-container-exit --exit-code-from tests tests

smoke: ## Run only the smoke subset in Docker
	$(COMPOSE) run --rm tests pytest -m smoke

report: ## Generate + open the Allure report locally (needs Allure CLI)
	allure serve allure-results

logs: ## Tail all container logs
	$(COMPOSE) logs -f

down: ## Stop and remove containers
	$(COMPOSE) down

clean: ## Stop containers and wipe results + model cache
	$(COMPOSE) down -v
	rm -rf allure-results allure-report

demo: ## Live headed demo against local Chrome (no Docker) — set env first
	HEADLESS=false pytest -m ai -k comparison

.PHONY: help test smoke report logs down clean demo
