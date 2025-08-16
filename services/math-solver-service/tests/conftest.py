"""
Pytest configuration and fixtures for Math Solver Service tests.
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Any, AsyncGenerator, Dict, Generator, List
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest
import pytest_asyncio
import sympy as sp


# Test database and Redis fixtures
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mock_db_session() -> AsyncGenerator[AsyncMock, None]:
    """Mock database session for testing."""
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.delete = MagicMock()
    mock_session.execute = AsyncMock()
    mock_session.scalar = AsyncMock()
    mock_session.scalars = AsyncMock()
    yield mock_session


@pytest_asyncio.fixture
async def mock_redis() -> AsyncGenerator[AsyncMock, None]:
    """Mock Redis client for testing."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock()
    mock_redis.set = AsyncMock()
    mock_redis.delete = AsyncMock()
    mock_redis.exists = AsyncMock()
    mock_redis.expire = AsyncMock()
    mock_redis.hget = AsyncMock()
    mock_redis.hset = AsyncMock()
    mock_redis.hdel = AsyncMock()
    yield mock_redis


# Math problem fixtures
@pytest.fixture
def sample_algebra_problems():
    """Sample algebra problems for testing."""
    return [
        {
            "id": 1,
            "problem": "2x + 5 = 13",
            "type": "linear_equation",
            "expected_solution": "x = 4",
            "steps": ["2x + 5 = 13", "2x = 13 - 5", "2x = 8", "x = 8/2", "x = 4"],
            "difficulty": "easy",
        },
        {
            "id": 2,
            "problem": "x^2 - 5x + 6 = 0",
            "type": "quadratic_equation",
            "expected_solution": "x = 2, x = 3",
            "steps": [
                "x^2 - 5x + 6 = 0",
                "Using quadratic formula: x = (5 ± √(25-24))/2",
                "x = (5 ± √1)/2",
                "x = (5 ± 1)/2",
                "x = 3 or x = 2",
            ],
            "difficulty": "medium",
        },
        {
            "id": 3,
            "problem": "log(x) + log(x-3) = 1",
            "type": "logarithmic_equation",
            "expected_solution": "x = 5",
            "steps": [
                "log(x) + log(x-3) = 1",
                "log(x(x-3)) = 1",
                "x(x-3) = 10^1",
                "x^2 - 3x = 10",
                "x^2 - 3x - 10 = 0",
                "(x-5)(x+2) = 0",
                "x = 5 (x = -2 is extraneous)",
            ],
            "difficulty": "hard",
        },
    ]


@pytest.fixture
def sample_calculus_problems():
    """Sample calculus problems for testing."""
    return [
        {
            "id": 1,
            "problem": "d/dx(x^3 + 2x^2 - 5x + 1)",
            "type": "derivative",
            "expected_solution": "3x^2 + 4x - 5",
            "steps": [
                "d/dx(x^3 + 2x^2 - 5x + 1)",
                "d/dx(x^3) + d/dx(2x^2) + d/dx(-5x) + d/dx(1)",
                "3x^2 + 4x - 5 + 0",
                "3x^2 + 4x - 5",
            ],
            "difficulty": "easy",
        },
        {
            "id": 2,
            "problem": "∫(2x + 3)dx",
            "type": "integral",
            "expected_solution": "x^2 + 3x + C",
            "steps": [
                "∫(2x + 3)dx",
                "∫2x dx + ∫3 dx",
                "2∫x dx + 3∫dx",
                "2(x^2/2) + 3x + C",
                "x^2 + 3x + C",
            ],
            "difficulty": "easy",
        },
        {
            "id": 3,
            "problem": "lim(x→0) sin(x)/x",
            "type": "limit",
            "expected_solution": "1",
            "steps": [
                "lim(x→0) sin(x)/x",
                "This is a standard limit",
                "Using L'Hôpital's rule or squeeze theorem",
                "lim(x→0) sin(x)/x = 1",
            ],
            "difficulty": "medium",
        },
    ]


@pytest.fixture
def sample_geometry_problems():
    """Sample geometry problems for testing."""
    return [
        {
            "id": 1,
            "problem": "Find the area of a circle with radius 5",
            "type": "area_calculation",
            "expected_solution": "25π ≈ 78.54",
            "steps": [
                "Area of circle = πr^2",
                "r = 5",
                "Area = π × 5^2",
                "Area = 25π",
                "Area ≈ 78.54",
            ],
            "difficulty": "easy",
        },
        {
            "id": 2,
            "problem": "Find the distance between points (1,2) and (4,6)",
            "type": "distance_calculation",
            "expected_solution": "5",
            "steps": [
                "Distance formula: d = √[(x2-x1)^2 + (y2-y1)^2]",
                "Points: (1,2) and (4,6)",
                "d = √[(4-1)^2 + (6-2)^2]",
                "d = √[3^2 + 4^2]",
                "d = √[9 + 16]",
                "d = √25 = 5",
            ],
            "difficulty": "easy",
        },
    ]


@pytest.fixture
def sample_statistics_problems():
    """Sample statistics problems for testing."""
    return [
        {
            "id": 1,
            "problem": "Find mean, median, mode of [1,2,2,3,4,4,4,5]",
            "type": "descriptive_statistics",
            "data": [1, 2, 2, 3, 4, 4, 4, 5],
            "expected_solution": {"mean": 3.125, "median": 3.5, "mode": 4},
            "difficulty": "easy",
        },
        {
            "id": 2,
            "problem": "Calculate standard deviation of [10,12,14,16,18]",
            "type": "standard_deviation",
            "data": [10, 12, 14, 16, 18],
            "expected_solution": {"std_dev": 2.83, "variance": 8.0},
            "difficulty": "medium",
        },
    ]


# Math solution fixtures
@pytest.fixture
def sample_solution_data():
    """Sample solution data for testing."""
    return {
        "user_id": 1,
        "problem_text": "2x + 5 = 13",
        "problem_type": "linear_equation",
        "solution_steps": ["2x + 5 = 13", "2x = 13 - 5", "2x = 8", "x = 4"],
        "final_answer": "x = 4",
        "difficulty_level": "easy",
        "solving_time": 1.25,  # seconds
        "accuracy_score": 100.0,
        "created_at": datetime.utcnow(),
    }


# Math engine fixtures
@pytest.fixture
def mock_sympy_solver():
    """Mock SymPy solver for testing."""
    mock_solver = MagicMock()
    mock_solver.solve = MagicMock()
    mock_solver.diff = MagicMock()
    mock_solver.integrate = MagicMock()
    mock_solver.limit = MagicMock()
    mock_solver.simplify = MagicMock()
    mock_solver.expand = MagicMock()
    mock_solver.factor = MagicMock()
    return mock_solver


@pytest.fixture
def mock_numpy_calculator():
    """Mock NumPy calculator for testing."""
    mock_calc = MagicMock()
    mock_calc.array = MagicMock()
    mock_calc.mean = MagicMock()
    mock_calc.std = MagicMock()
    mock_calc.var = MagicMock()
    mock_calc.median = MagicMock()
    mock_calc.linalg = MagicMock()
    return mock_calc


@pytest.fixture
def mock_matplotlib_plotter():
    """Mock Matplotlib plotter for testing."""
    mock_plotter = MagicMock()
    mock_plotter.plot = MagicMock()
    mock_plotter.scatter = MagicMock()
    mock_plotter.bar = MagicMock()
    mock_plotter.hist = MagicMock()
    mock_plotter.savefig = MagicMock()
    mock_plotter.show = MagicMock()
    return mock_plotter


# Performance testing fixtures
@pytest.fixture
def performance_threshold():
    """Performance thresholds for math operations."""
    return {
        "simple_algebra": 0.1,  # seconds
        "complex_algebra": 1.0,  # seconds
        "calculus_derivative": 0.5,  # seconds
        "calculus_integral": 2.0,  # seconds
        "statistics_basic": 0.2,  # seconds
        "statistics_advanced": 1.5,  # seconds
        "geometry_basic": 0.1,  # seconds
        "graph_plotting": 3.0,  # seconds
    }


# Accuracy testing fixtures
@pytest.fixture
def accuracy_test_cases():
    """Test cases for accuracy validation."""
    return {
        "algebra": [
            {"input": "2*x + 5 = 13", "expected": [4], "tolerance": 1e-10},
            {"input": "x**2 - 5*x + 6 = 0", "expected": [2, 3], "tolerance": 1e-10},
            {"input": "3*x - 7 = 2*x + 1", "expected": [8], "tolerance": 1e-10},
        ],
        "calculus": [
            {
                "input": "diff(x**3 + 2*x**2 - 5*x + 1, x)",
                "expected": "3*x**2 + 4*x - 5",
                "tolerance": 1e-10,
            },
            {
                "input": "integrate(2*x + 3, x)",
                "expected": "x**2 + 3*x",
                "tolerance": 1e-10,
            },
        ],
        "trigonometry": [
            {"input": "sin(pi/2)", "expected": 1.0, "tolerance": 1e-10},
            {"input": "cos(0)", "expected": 1.0, "tolerance": 1e-10},
            {"input": "tan(pi/4)", "expected": 1.0, "tolerance": 1e-10},
        ],
    }


# Error handling fixtures
@pytest.fixture
def invalid_math_inputs():
    """Invalid math inputs for error testing."""
    return [
        "",  # Empty string
        "invalid equation",  # Invalid syntax
        "x + = 5",  # Malformed equation
        "1/0",  # Division by zero
        "log(-1)",  # Invalid logarithm
        "sqrt(-1)",  # Invalid square root (for real numbers)
        "x^x^x^x^x",  # Overly complex expression
        "solve(x**1000 = 1)",  # Computationally intensive
    ]


# Mock external services
@pytest.fixture
def mock_wolfram_alpha():
    """Mock Wolfram Alpha API for testing."""
    mock_service = MagicMock()
    mock_service.query = AsyncMock()
    mock_service.solve = AsyncMock()
    mock_service.is_available = MagicMock(return_value=True)
    return mock_service


@pytest.fixture
def mock_latex_renderer():
    """Mock LaTeX renderer for testing."""
    mock_renderer = MagicMock()
    mock_renderer.render_equation = MagicMock()
    mock_renderer.render_solution = MagicMock()
    mock_renderer.to_png = MagicMock()
    mock_renderer.to_svg = MagicMock()
    return mock_renderer


# Test client fixtures
@pytest_asyncio.fixture
async def test_client():
    """Test client for API testing."""
    from fastapi.testclient import TestClient
    from math_solver_service.main import app

    with TestClient(app) as client:
        yield client


# Environment fixtures
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("MATH_SOLVER_DB_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("WOLFRAM_ALPHA_API_KEY", "test-wolfram-key")
    monkeypatch.setenv("MAX_SOLVING_TIME", "30")  # seconds
    monkeypatch.setenv("ENABLE_ADVANCED_MATH", "true")
    monkeypatch.setenv("ENABLE_PLOTTING", "true")


# Math library fixtures
@pytest.fixture
def sympy_symbols():
    """Common SymPy symbols for testing."""
    return {
        "x": sp.Symbol("x"),
        "y": sp.Symbol("y"),
        "z": sp.Symbol("z"),
        "t": sp.Symbol("t"),
        "n": sp.Symbol("n", integer=True),
        "a": sp.Symbol("a", real=True),
        "b": sp.Symbol("b", real=True),
        "c": sp.Symbol("c", real=True),
    }


@pytest.fixture
def numpy_test_arrays():
    """Common NumPy arrays for testing."""
    return {
        "simple_array": np.array([1, 2, 3, 4, 5]),
        "matrix_2x2": np.array([[1, 2], [3, 4]]),
        "matrix_3x3": np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
        "random_data": np.random.rand(100),
        "normal_distribution": np.random.normal(0, 1, 1000),
    }


# Security testing fixtures
@pytest.fixture
def security_test_data():
    """Security test data for math solver."""
    return {
        "malicious_inputs": [
            "__import__('os').system('rm -rf /')",
            "eval('print(\"hacked\")')",
            'exec(\'import subprocess; subprocess.call(["ls", "/"])\')',
            "open('/etc/passwd').read()",
            "globals()",
            "locals()",
            "__builtins__",
        ],
        "resource_intensive": [
            "x**999999",
            "factorial(100000)",
            "sum(i for i in range(10**8))",
            "integrate(exp(x**2), (x, -oo, oo))",
        ],
    }


# Database cleanup fixtures
@pytest_asyncio.fixture(autouse=True)
async def cleanup_database():
    """Clean up database after each test."""
    yield
    # Cleanup logic would go here
    # For example: truncate tables, reset sequences, etc.
