@echo off
REM =============================================================================
REM Math Service Website - Development Environment Setup Script (Windows)
REM =============================================================================
REM This script automates the setup of development environment on Windows
REM =============================================================================

echo.
echo ============================================================
echo 🚀 Math Service Website Development Setup (Windows)
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found:
python --version

REM Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not installed
    pause
    exit /b 1
)

echo ✅ pip found

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
)

echo ✅ Git found

echo.
echo 📦 Setting up Python virtual environment...

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo 📦 Installing dependencies...

REM Install production dependencies
echo Installing production dependencies...
pip install -r requirements.txt

REM Install development dependencies
if exist "requirements-dev.txt" (
    echo Installing development dependencies...
    pip install -r requirements-dev.txt
) else (
    echo Installing pre-commit...
    pip install "pre-commit>=3.0.0"
)

echo.
echo 🔧 Setting up pre-commit hooks...

REM Install pre-commit hooks
if exist ".pre-commit-config.yaml" (
    echo Installing pre-commit hooks...
    pre-commit install

    echo Running pre-commit on all files...
    pre-commit run --all-files

    echo ✅ Pre-commit hooks setup completed
) else (
    echo ❌ .pre-commit-config.yaml not found
    pause
    exit /b 1
)

echo.
echo ✅ Verifying installation...

REM Check tools
black --version
flake8 --version
mypy --version
pre-commit --version

echo.
echo ============================================================
echo 🎉 Development environment setup completed!
echo ============================================================
echo.
echo 📋 What's been set up:
echo   ✅ Python virtual environment (venv\)
echo   ✅ Production dependencies (requirements.txt)
echo   ✅ Development dependencies (requirements-dev.txt)
echo   ✅ Pre-commit hooks (.pre-commit-config.yaml)
echo   ✅ Code quality tools (Black, Flake8, MyPy, isort)
echo.
echo 🚀 Next steps:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Start development: docker-compose up -d
echo   3. Run tests: pytest
echo.
echo 📚 Useful commands:
echo   • Format code: black .
echo   • Lint code: flake8 .
echo   • Type check: mypy .
echo   • Run tests: pytest
echo.
echo Happy coding! 🚀
echo.
pause
