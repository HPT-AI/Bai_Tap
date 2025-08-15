# Scripts Directory

This directory contains automation scripts for the Math Service Website project.

## Development Setup Scripts

### `setup-dev.sh` (Linux/macOS)
Automated development environment setup script for Unix-based systems.

**Features:**
- ✅ Prerequisites checking (Python, pip, Git, Docker)
- ✅ Python virtual environment creation
- ✅ Dependencies installation (production + development)
- ✅ Pre-commit hooks setup and installation
- ✅ Database initialization (if Docker available)
- ✅ Installation verification
- ✅ Colored output and progress tracking

**Usage:**
```bash
# Make executable (if needed)
chmod +x scripts/setup-dev.sh

# Run setup
./scripts/setup-dev.sh
```

### `setup-dev.bat` (Windows)
Automated development environment setup script for Windows systems.

**Features:**
- ✅ Prerequisites checking (Python, pip, Git)
- ✅ Python virtual environment creation
- ✅ Dependencies installation
- ✅ Pre-commit hooks setup
- ✅ Installation verification

**Usage:**
```cmd
# Run from project root
scripts\setup-dev.bat
```

## Database Scripts

### `init-databases.sql`
Master database initialization script that creates all required databases.

### Service-specific initialization scripts:
- `user-service/init.sql` - User Service database schema
- `payment-service/init.sql` - Payment Service database schema
- `math-solver-service/init.sql` - Math Solver Service database schema
- `content-service/init.sql` - Content Service database schema
- `admin-service/init.sql` - Admin Service database schema

## Usage Examples

### Quick Development Setup
```bash
# Clone repository
git clone <repository-url>
cd math-service-website

# Run automated setup
./scripts/setup-dev.sh

# Start development
source venv/bin/activate
docker-compose up -d
```

### Manual Setup (if scripts fail)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit
pre-commit install
pre-commit run --all-files
```

### Database Setup
```bash
# Start database services
docker-compose up -d postgres redis

# Initialize databases
docker-compose exec postgres psql -U postgres -f /docker-entrypoint-initdb.d/init-databases.sql
```

## Script Features

### Error Handling
- ✅ Exit on any error (`set -e`)
- ✅ Prerequisite validation
- ✅ Graceful error messages
- ✅ Cleanup on interruption

### Cross-Platform Support
- ✅ Linux/macOS (Bash script)
- ✅ Windows (Batch script)
- ✅ Consistent functionality across platforms

### Developer Experience
- ✅ Colored output for better readability
- ✅ Progress indicators
- ✅ Detailed success/error messages
- ✅ Next steps guidance
- ✅ Useful commands reference

## Troubleshooting

### Common Issues

**Permission denied:**
```bash
chmod +x scripts/setup-dev.sh
```

**Python not found:**
- Install Python 3.11+ from https://python.org
- Ensure Python is in PATH

**Docker not available:**
- Scripts will skip database setup
- Install Docker Desktop for full functionality

**Pre-commit hooks fail:**
- This is normal on first run
- Hooks will auto-fix issues and work on subsequent commits

### Getting Help

1. Check the main [README.md](../README.md)
2. Review [docs/development-setup.md](../docs/development-setup.md)
3. Check [docs/troubleshooting.md](../docs/troubleshooting.md) (if available)

## Contributing

When adding new scripts:

1. **Follow naming convention**: `action-target.sh` (e.g., `setup-dev.sh`)
2. **Add documentation**: Update this README
3. **Include error handling**: Use `set -e` and proper error messages
4. **Test cross-platform**: Ensure compatibility
5. **Add to .gitignore**: If scripts generate temporary files

## Script Maintenance

### Regular Updates
- Keep dependency versions current
- Update Python version requirements
- Test scripts with new OS versions
- Update documentation

### Version Compatibility
- Python 3.11+ required
- Docker Compose v2+ recommended
- Git 2.0+ required

---

**Last Updated:** 2024-08-15
**Maintainer:** Development Team

