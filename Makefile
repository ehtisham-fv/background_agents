# Makefile for Purchase Price Analysis Project

.PHONY: help install test test-unit test-integration test-coverage test-html clean lint format

help:  ## Show this help message
	@echo "Purchase Price Analysis - Available Commands:"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install project dependencies
	pip install -r requirements.txt

test:  ## Run all tests with coverage
	python3 run_tests.py --coverage --html-report

test-unit:  ## Run only unit tests
	python3 run_tests.py --unit --verbose

test-integration:  ## Run only integration tests
	python3 run_tests.py --integration --verbose

test-coverage:  ## Run tests with detailed coverage report
	python3 run_tests.py --coverage --verbose

test-html:  ## Run tests and generate HTML coverage report
	python3 run_tests.py --html-report --verbose

test-fast:  ## Run tests excluding slow ones
	python3 run_tests.py --fast --verbose

test-file:  ## Run tests in specific file (usage: make test-file FILE=test_price_analyzer.py)
	python3 run_tests.py --file $(FILE) --verbose

clean:  ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf src/__pycache__/
	rm -f .coverage
	rm -f price_analysis.log
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

lint:  ## Run code linting (if flake8 is installed)
	@if command -v flake8 >/dev/null 2>&1; then \
		echo "Running flake8 linting..."; \
		flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503; \
	else \
		echo "flake8 not installed. Install with: pip install flake8"; \
	fi

format:  ## Format code (if black is installed)
	@if command -v black >/dev/null 2>&1; then \
		echo "Formatting code with black..."; \
		black src/ tests/ --line-length=100; \
	else \
		echo "black not installed. Install with: pip install black"; \
	fi

run:  ## Run the price analysis
	python3 run_analysis.py

# Default target
all: install test