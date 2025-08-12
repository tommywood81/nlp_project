.PHONY: help install test test-unit test-integration lint format clean build run deploy docker-build docker-run docker-stop docker-logs

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean up temporary files"
	@echo "  build        - Build Docker image"
	@echo "  run          - Run application locally"
	@echo "  deploy       - Deploy using deploy_local.py"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  docker-stop  - Stop Docker container"
	@echo "  docker-logs  - Show Docker logs"

# Install dependencies
install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

# Run all tests
test:
	pytest tests/ -v --tb=short

# Run unit tests only
test-unit:
	pytest tests/ -v -m "unit" --tb=short

# Run integration tests only
test-integration:
	pytest tests/ -v -m "integration" --tb=short

# Run linting
lint:
	flake8 app/ tests/ --max-line-length=88 --ignore=E203,W503
	mypy app/ --ignore-missing-imports

# Format code
format:
	black app/ tests/ --line-length=88
	isort app/ tests/

# Clean up temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Run application locally
run:
	uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Deploy using the deployment script
deploy:
	python deploy_local.py

# Docker commands
docker-build:
	docker build -t nlp-dashboard .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f nlp-dashboard

# Development setup
dev-setup: install
	@echo "Development environment setup complete!"
	@echo "Run 'make run' to start the application locally"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make deploy' to deploy with Docker"

# Production build
prod-build: clean
	docker build -t nlp-dashboard:latest .

# Quick test
quick-test:
	pytest tests/test_sentiment.py tests/test_ner.py -v
