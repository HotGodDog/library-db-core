.PHONY: install test build upload clean reset help

PYTHON := python

install:
	$(PYTHON) -m pip install -e ".[dev]"
	$(PYTHON) -m pip install build twine

test: clean
	set PYTHONPATH=src && $(PYTHON) -m pytest tests/ -v --tb=short --import-mode=importlib

build: clean
	$(PYTHON) -m build

upload: build
	$(PYTHON) -m twine upload --repository testpypi dist/*

clean:
	-find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	-find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	-find . -type f -name "*.pyc" -delete 2>/dev/null || true
	-rm -rf build/ dist/ *.egg-info

reset: clean
	-rm -f library.db

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install   Install dev dependencies"
	@echo "  test      Run tests"
	@echo "  build     Build package"
	@echo "  upload    Upload to TestPyPI"
	@echo "  clean     Remove cache and build artifacts"
	@echo "  reset     Clean + remove database"
	@echo "  help      Show this message"
