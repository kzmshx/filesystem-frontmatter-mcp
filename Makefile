.PHONY: help
help: ## ヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: lint
lint: ## 静的解析を実行
	uv run ruff check src tests
	uv run ruff format --check src tests

.PHONY: fix
fix: ## 自動修正を実行
	uv run ruff check --fix src tests
	uv run ruff format src tests

.PHONY: test
test: ## 自動テストを実行
	uv run pytest tests -v
