# PowerShell Setup script for Notes to Blog Application
# This script sets up the environment, installs dependencies, and configures the application

param(
    [switch]$SkipTests,
    [switch]$Force
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up Notes to Blog Application..." -ForegroundColor Green

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if UV is installed
function Test-UV {
    try {
        $null = Get-Command uv -ErrorAction Stop
        Write-Success "UV is installed"
        return $true
    }
    catch {
        Write-Error "UV is not installed. Please install UV first:"
        Write-Host "Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 | Invoke-Expression"
        return $false
    }
}

# Create virtual environment
function New-VirtualEnvironment {
    Write-Status "Creating virtual environment..."
    try {
        uv venv
        Write-Success "Virtual environment created"
    }
    catch {
        Write-Error "Failed to create virtual environment: $_"
        throw
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Status "Installing dependencies..."
    try {
        uv pip install -r requirements.txt
        Write-Success "Dependencies installed"
    }
    catch {
        Write-Error "Failed to install dependencies: $_"
        throw
    }
}

# Create necessary directories
function New-Directories {
    Write-Status "Creating application directories..."
    try {
        $directories = @("inbox", "output", "images", "logs", "data")
        foreach ($dir in $directories) {
            if (!(Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
            }
        }
        Write-Success "Directories created"
    }
    catch {
        Write-Error "Failed to create directories: $_"
        throw
    }
}

# Setup environment file
function Set-EnvironmentFile {
    if (!(Test-Path ".env")) {
        Write-Status "Creating .env file from template..."
        if (Test-Path "example.env.txt") {
            Copy-Item "example.env.txt" ".env"
            Write-Warning "Please edit .env file with your API keys"
        }
        else {
            Write-Warning "No example.env.txt found. Please create .env file manually"
        }
    }
    else {
        Write-Success ".env file already exists"
    }
}

# Validate configuration
function Test-Configuration {
    Write-Status "Validating configuration..."
    if (Test-Path ".env") {
        try {
            $result = uv run python -c "
from src.models.config_models import Config
try:
    config = Config.model_validate({})
    print('Configuration is valid')
except Exception as e:
    print(f'Configuration error: {e}')
    exit(1)
"
            Write-Success "Configuration validated"
        }
        catch {
            Write-Warning "Configuration validation failed: $_"
        }
    }
    else {
        Write-Warning "No .env file found. Skipping configuration validation"
    }
}

# Run tests
function Invoke-Tests {
    Write-Status "Running tests..."
    try {
        uv run pytest tests/ -v --tb=short
        Write-Success "Tests completed"
    }
    catch {
        Write-Warning "Tests failed: $_"
    }
}

# Show next steps
function Show-NextSteps {
    Write-Host ""
    Write-Success "Setup completed successfully!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Edit .env file with your API keys:"
    Write-Host "   - OPENROUTER_API_KEY"
    Write-Host "   - REPLICATE_API_TOKEN"
    Write-Host "   - BRAVE_API_KEY"
    Write-Host ""
    Write-Host "2. Add note files to the inbox/ directory"
    Write-Host ""
    Write-Host "3. Run the application:"
    Write-Host "   uv run python main.py --help"
    Write-Host ""
    Write-Host "4. Process a single file:"
    Write-Host "   uv run python main.py process-file inbox/your-note.md"
    Write-Host ""
    Write-Host "5. Process all files in inbox:"
    Write-Host "   uv run python main.py process-batch"
    Write-Host ""
}

# Main setup function
function Start-Setup {
    Write-Status "Starting setup..."
    
    # Check prerequisites
    if (!(Test-UV)) {
        exit 1
    }
    
    # Setup environment
    New-VirtualEnvironment
    Install-Dependencies
    New-Directories
    Set-EnvironmentFile
    Test-Configuration
    
    # Run tests if not skipped
    if (!$SkipTests) {
        $runTests = Read-Host "Do you want to run tests? (y/n)"
        if ($runTests -eq "y" -or $runTests -eq "Y") {
            Invoke-Tests
        }
    }
    
    Show-NextSteps
}

# Run main setup
try {
    Start-Setup
}
catch {
    Write-Error "Setup failed: $_"
    exit 1
} 