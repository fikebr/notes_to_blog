# Makefile for Notes to Blog Application
# Common development and deployment tasks

.PHONY: help install test lint clean setup deploy docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  clean       - Clean up generated files"
	@echo "  setup       - Initial setup"
	@echo "  deploy      - Deploy application"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run with Docker Compose"
	@echo "  help        - Show this help"

# Install dependencies
install:
	@echo "Installing dependencies..."
	uv pip install -r requirements.txt
	@echo "Dependencies installed successfully"

# Run tests
test:
	@echo "Running tests..."
	uv run pytest tests/ -v --cov=src --cov-report=term-missing
	@echo "Tests completed"

# Run tests with coverage report
test-coverage:
	@echo "Running tests with coverage..."
	uv run pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

# Run linting
lint:
	@echo "Running linting..."
	uv run flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	uv run black --check src/ tests/
	@echo "Linting completed"

# Format code
format:
	@echo "Formatting code..."
	uv run black src/ tests/
	@echo "Code formatting completed"

# Clean up generated files
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/
	@echo "Cleanup completed"

# Initial setup
setup:
	@echo "Setting up Notes to Blog Application..."
	@if [ -f "scripts/setup.sh" ]; then \
		chmod +x scripts/setup.sh && ./scripts/setup.sh; \
	else \
		echo "Setup script not found. Running manual setup..."; \
		uv venv; \
		uv pip install -r requirements.txt; \
		mkdir -p inbox output images logs data; \
		echo "Manual setup completed"; \
	fi

# Deploy application
deploy:
	@echo "Deploying application..."
	@if [ -f "scripts/deploy.sh" ]; then \
		chmod +x scripts/deploy.sh && ./scripts/deploy.sh start; \
	else \
		echo "Deploy script not found. Starting manually..."; \
		uv run python main.py process-batch; \
	fi

# Build Docker image
docker-build:
	@echo "Building Docker image..."
	docker build -t notes-to-blog .
	@echo "Docker image built successfully"

# Run with Docker Compose
docker-run:
	@echo "Starting with Docker Compose..."
	docker-compose up -d
	@echo "Application started with Docker Compose"

# Stop Docker Compose
docker-stop:
	@echo "Stopping Docker Compose..."
	docker-compose down
	@echo "Docker Compose stopped"

# Show Docker logs
docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

# Backup data
backup:
	@echo "Creating backup..."
	@if [ -f "scripts/deploy.sh" ]; then \
		chmod +x scripts/deploy.sh && ./scripts/deploy.sh backup; \
	else \
		echo "Backup script not found. Creating manual backup..."; \
		timestamp=$$(date +%Y%m%d_%H%M%S); \
		backup_dir="backups/backup_$$timestamp"; \
		mkdir -p "$$backup_dir"; \
		cp -r output "$$backup_dir/" 2>/dev/null || true; \
		cp -r images "$$backup_dir/" 2>/dev/null || true; \
		cp -r data "$$backup_dir/" 2>/dev/null || true; \
		cp .env "$$backup_dir/" 2>/dev/null || true; \
		echo "Backup created: $$backup_dir"; \
	fi

# Show application status
status:
	@echo "Application status:"
	@if [ -f "scripts/deploy.sh" ]; then \
		chmod +x scripts/deploy.sh && ./scripts/deploy.sh status; \
	else \
		echo "Status script not found. Checking manually..."; \
		echo "Checking if application is running..."; \
		ps aux | grep "python main.py" | grep -v grep || echo "Application not running"; \
	fi

# Process a single file
process-file:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make process-file FILE=path/to/file.md"; \
		exit 1; \
	fi
	@echo "Processing file: $(FILE)"
	uv run python main.py process-file "$(FILE)"

# Process all files in inbox
process-batch:
	@echo "Processing all files in inbox..."
	uv run python main.py process-batch

# Show configuration
config:
	@echo "Showing configuration..."
	uv run python main.py config --show

# Validate configuration
validate:
	@echo "Validating configuration..."
	uv run python main.py config --validate

# Development server (for testing)
dev:
	@echo "Starting development server..."
	export DEBUG=true && uv run python main.py process-batch

# Security scan
security:
	@echo "Running security scan..."
	uv pip install bandit safety
	uv run bandit -r src/ -f json -o bandit-report.json || true
	uv run safety check --json --output safety-report.json || true
	@echo "Security scan completed"

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	uv pip install --upgrade -r requirements.txt
	@echo "Dependencies updated"

# Create new note template
new-note:
	@echo "Creating new note template..."
	@read -p "Enter note title: " title; \
	read -p "Enter note filename (without extension): " filename; \
	if [ -z "$$filename" ]; then \
		filename="new_note"; \
	fi; \
	cat > "inbox/$$filename.md" << EOF; \
# $$title

## Key Points
- Point 1: Important information
- Point 2: More details
- Point 3: Additional context

## Ideas
Some ideas for the blog post:
- Idea 1
- Idea 2
- Idea 3

## Notes
Additional notes and thoughts.

EOF
	@echo "Note template created: inbox/$$filename.md"

# Show help for specific command
help-%:
	@echo "Help for command: $*"
	@case "$*" in \
		install) echo "Installs all Python dependencies using UV";; \
		test) echo "Runs the test suite with pytest";; \
		lint) echo "Runs code linting with flake8 and black";; \
		clean) echo "Removes generated files and caches";; \
		setup) echo "Performs initial application setup";; \
		deploy) echo "Deploys the application";; \
		docker-build) echo "Builds the Docker image";; \
		docker-run) echo "Starts the application with Docker Compose";; \
		*) echo "No help available for command: $*";; \
	esac 