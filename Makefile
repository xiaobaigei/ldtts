.PHONY: help install test lint format reproduce clean

help:
	@echo "SQL-Pilot Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code with black"
	@echo "  make reproduce  - Reproduce full experiments"
	@echo "  make clean      - Clean generated files"

install:
	pip install -r requirements.txt
	pip install pytest pytest-cov flake8 black

test:
	pytest tests/ -v --cov=src/ --cov-report=html

test-unit:
	pytest tests/test_schema_linker.py tests/test_retriever.py tests/test_generator.py tests/test_evaluator.py tests/test_ensemble.py -v

test-e2e:
	pytest tests/test_e2e.py -v

test-ablation:
	pytest tests/test_ablation.py -v

lint:
	flake8 src/ tests/ --max-line-length=120 --ignore=E501,W503

format:
	black src/ tests/ --line-length=120

reproduce:
	@echo "Downloading Spider dataset..."
	@echo "(Please manually download from https://yale-lily.github.io/spider)"
	@echo ""
	@echo "Building FAISS index..."
	python -c "from src.retriever import ExampleRetriever; print('Index building would happen here')"
	@echo ""
	@echo "Running experiments..."
	@echo "Condition A: Pure LLM zero-shot"
	@echo "Condition B: LLM + few-shot"
	@echo "Condition C: SQL-Pilot (full pipeline)"
	@echo "Condition D: SQL-Pilot + self-correction"
	@echo "Condition E: SQL-Pilot + ensemble voting"
	@echo ""
	@echo "Results would be saved to results/"

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
