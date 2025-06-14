lint:
	ruff check .
	mypy . --config-file pyproject.toml --ignore-missing-imports --no-namespace-packages


format:
	ruff format .
	ruff check --fix --select I .
