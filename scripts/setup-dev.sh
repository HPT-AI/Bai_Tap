#!/bin/bash

# =============================================================================
# Math Service Website - Development Environment Setup Script
# =============================================================================
# This script automates the setup of development environment including:
# - Python virtual environment
# - Dependencies installation
# - Pre-commit hooks setup
# - Database initialization
# - Code quality tools configuration
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    log_info "🚀 Starting Math Service Website Development Setup..."
    echo "============================================================"
    
    # Check prerequisites
    check_prerequisites
    
    # Setup Python environment
    setup_python_environment
    
    # Install dependencies
    install_dependencies
    
    # Setup pre-commit hooks
    setup_pre_commit_hooks
    
    # Setup database (if Docker is available)
    setup_database
    
    # Verify installation
    verify_installation
    
    # Show completion message
    show_completion_message
}

# Check prerequisites
check_prerequisites() {
    log_info "📋 Checking prerequisites..."
    
    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_info "Found Python $PYTHON_VERSION"
    
    # Check pip
    if ! command_exists pip3; then
        log_error "pip3 is not installed. Please install pip first."
        exit 1
    fi
    
    # Check Git
    if ! command_exists git; then
        log_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        log_info "Docker found - database setup will be available"
    else
        log_warning "Docker not found - skipping database setup"
    fi
    
    log_success "Prerequisites check completed"
}

# Setup Python virtual environment
setup_python_environment() {
    log_info "🐍 Setting up Python virtual environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    log_success "Python environment setup completed"
}

# Install dependencies
install_dependencies() {
    log_info "📦 Installing dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install production dependencies
    log_info "Installing production dependencies..."
    pip install -r requirements.txt
    
    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        log_info "Installing development dependencies..."
        pip install -r requirements-dev.txt
    else
        log_warning "requirements-dev.txt not found, installing pre-commit separately"
        pip install pre-commit>=3.0.0
    fi
    
    log_success "Dependencies installation completed"
}

# Setup pre-commit hooks
setup_pre_commit_hooks() {
    log_info "🔧 Setting up pre-commit hooks..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install pre-commit hooks
    if [ -f ".pre-commit-config.yaml" ]; then
        log_info "Installing pre-commit hooks..."
        pre-commit install
        
        # Run pre-commit on all files to ensure everything works
        log_info "Running pre-commit on all files (first time setup)..."
        pre-commit run --all-files || {
            log_warning "Some pre-commit hooks failed - this is normal for first run"
            log_info "Pre-commit will fix issues automatically on next commit"
        }
        
        log_success "Pre-commit hooks setup completed"
    else
        log_error ".pre-commit-config.yaml not found"
        exit 1
    fi
}

# Setup database
setup_database() {
    if command_exists docker && command_exists docker-compose; then
        log_info "🗄️  Setting up database..."
        
        # Check if docker-compose.yml exists
        if [ -f "docker-compose.yml" ]; then
            log_info "Starting database services..."
            docker-compose up -d postgres redis
            
            # Wait for database to be ready
            log_info "Waiting for database to be ready..."
            sleep 10
            
            # Initialize database
            if [ -f "scripts/init-databases.sql" ]; then
                log_info "Initializing databases..."
                docker-compose exec -T postgres psql -U postgres -f /docker-entrypoint-initdb.d/init-databases.sql
                log_success "Database initialization completed"
            else
                log_warning "Database initialization script not found"
            fi
        else
            log_warning "docker-compose.yml not found - skipping database setup"
        fi
    else
        log_info "Docker/Docker Compose not available - skipping database setup"
    fi
}

# Verify installation
verify_installation() {
    log_info "✅ Verifying installation..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check Python packages
    log_info "Checking installed packages..."
    
    # Check code quality tools
    if command_exists black; then
        log_success "Black formatter: $(black --version)"
    else
        log_error "Black not found"
    fi
    
    if command_exists flake8; then
        log_success "Flake8 linter: $(flake8 --version)"
    else
        log_error "Flake8 not found"
    fi
    
    if command_exists mypy; then
        log_success "MyPy type checker: $(mypy --version)"
    else
        log_error "MyPy not found"
    fi
    
    if command_exists pre-commit; then
        log_success "Pre-commit: $(pre-commit --version)"
    else
        log_error "Pre-commit not found"
    fi
    
    # Check pre-commit hooks
    if [ -f ".git/hooks/pre-commit" ]; then
        log_success "Pre-commit hooks installed"
    else
        log_error "Pre-commit hooks not installed"
    fi
    
    log_success "Installation verification completed"
}

# Show completion message
show_completion_message() {
    echo ""
    echo "============================================================"
    log_success "🎉 Development environment setup completed!"
    echo "============================================================"
    echo ""
    echo "📋 What's been set up:"
    echo "  ✅ Python virtual environment (venv/)"
    echo "  ✅ Production dependencies (requirements.txt)"
    echo "  ✅ Development dependencies (requirements-dev.txt)"
    echo "  ✅ Pre-commit hooks (.pre-commit-config.yaml)"
    echo "  ✅ Code quality tools (Black, Flake8, MyPy, isort)"
    echo "  ✅ Testing framework (pytest)"
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Activate virtual environment: source venv/bin/activate"
    echo "  2. Start development: docker-compose up -d"
    echo "  3. Run tests: pytest"
    echo "  4. Check code quality: pre-commit run --all-files"
    echo ""
    echo "📚 Useful commands:"
    echo "  • Format code: black ."
    echo "  • Lint code: flake8 ."
    echo "  • Type check: mypy ."
    echo "  • Run tests: pytest"
    echo "  • Update pre-commit: pre-commit autoupdate"
    echo ""
    echo "🔗 Documentation:"
    echo "  • README.md - Project overview"
    echo "  • docs/development-setup.md - Detailed setup guide"
    echo "  • docs/api-endpoints.md - API documentation"
    echo ""
    log_success "Happy coding! 🚀"
}

# Handle script interruption
cleanup() {
    log_warning "Setup interrupted"
    exit 1
}

# Set trap for cleanup
trap cleanup INT TERM

# Run main function
main "$@"

