#!/bin/bash
# Setup script for Notes to Blog Application
# This script sets up the environment, installs dependencies, and configures the application

set -e  # Exit on any error

echo "🚀 Setting up Notes to Blog Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if UV is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "UV is not installed. Please install UV first:"
        echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    print_success "UV is installed"
}

# Create virtual environment
setup_venv() {
    print_status "Creating virtual environment..."
    uv venv
    print_success "Virtual environment created"
}

# Install dependencies
install_deps() {
    print_status "Installing dependencies..."
    uv pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Create necessary directories
create_dirs() {
    print_status "Creating application directories..."
    mkdir -p inbox output images logs data
    print_success "Directories created"
}

# Setup environment file
setup_env() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        if [ -f example.env.txt ]; then
            cp example.env.txt .env
            print_warning "Please edit .env file with your API keys"
        else
            print_warning "No example.env.txt found. Please create .env file manually"
        fi
    else
        print_success ".env file already exists"
    fi
}

# Validate configuration
validate_config() {
    print_status "Validating configuration..."
    if [ -f .env ]; then
        uv run python -c "
from src.models.config_models import Config
try:
    config = Config.model_validate({})
    print('Configuration is valid')
except Exception as e:
    print(f'Configuration error: {e}')
    exit(1)
"
        print_success "Configuration validated"
    else
        print_warning "No .env file found. Skipping configuration validation"
    fi
}

# Run tests
run_tests() {
    print_status "Running tests..."
    uv run pytest tests/ -v --tb=short
    print_success "Tests completed"
}

# Show next steps
show_next_steps() {
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your API keys:"
    echo "   - OPENROUTER_API_KEY"
    echo "   - REPLICATE_API_TOKEN"
    echo "   - BRAVE_API_KEY"
    echo ""
    echo "2. Add note files to the inbox/ directory"
    echo ""
    echo "3. Run the application:"
    echo "   uv run python main.py --help"
    echo ""
    echo "4. Process a single file:"
    echo "   uv run python main.py process-file inbox/your-note.md"
    echo ""
    echo "5. Process all files in inbox:"
    echo "   uv run python main.py process-batch"
    echo ""
}

# Main setup function
main() {
    print_status "Starting setup..."
    
    check_uv
    setup_venv
    install_deps
    create_dirs
    setup_env
    validate_config
    
    # Ask if user wants to run tests
    read -p "Do you want to run tests? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    show_next_steps
}

# Run main function
main "$@" 