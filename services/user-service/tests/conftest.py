"""
Pytest configuration and fixtures for User Service tests.
"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio


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


# User fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "phone": "+84901234567",
        "date_of_birth": "1990-01-01",
        "is_active": True,
        "is_verified": False,
    }


@pytest.fixture
def sample_user_create_data():
    """Sample user creation data for testing."""
    return {
        "email": "newuser@example.com",
        "password": "NewPassword123!",
        "full_name": "New User",
        "phone": "+84987654321",
        "date_of_birth": "1995-05-15",
    }


@pytest.fixture
def sample_user_update_data():
    """Sample user update data for testing."""
    return {
        "full_name": "Updated User Name",
        "phone": "+84912345678",
        "date_of_birth": "1992-03-10",
    }


# Authentication fixtures
@pytest.fixture
def sample_login_data():
    """Sample login data for testing."""
    return {"email": "test@example.com", "password": "TestPassword123!"}


@pytest.fixture
def sample_jwt_payload():
    """Sample JWT payload for testing."""
    return {
        "user_id": 1,
        "email": "test@example.com",
        "role": "user",
        "exp": 1234567890,
        "iat": 1234567800,
    }


@pytest.fixture
def sample_refresh_token():
    """Sample refresh token for testing."""
    return "refresh_token_example_12345"


# Session fixtures
@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "user_id": 1,
        "device_info": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "ip_address": "192.168.1.100",
        "location": "Ho Chi Minh City, Vietnam",
        "is_active": True,
    }


# Balance fixtures
@pytest.fixture
def sample_balance_data():
    """Sample balance data for testing."""
    return {
        "user_id": 1,
        "current_balance": 100000,
        "total_deposited": 500000,
        "total_spent": 400000,
        "last_transaction_date": "2024-01-15T10:30:00",
    }


# Role fixtures
@pytest.fixture
def sample_role_data():
    """Sample role data for testing."""
    return {
        "name": "premium_user",
        "description": "Premium user with extended features",
        "permissions": ["solve_advanced_math", "unlimited_solutions"],
    }


# Mock external services
@pytest.fixture
def mock_email_service():
    """Mock email service for testing."""
    mock_service = MagicMock()
    mock_service.send_verification_email = AsyncMock(return_value=True)
    mock_service.send_password_reset_email = AsyncMock(return_value=True)
    mock_service.send_welcome_email = AsyncMock(return_value=True)
    return mock_service


@pytest.fixture
def mock_sms_service():
    """Mock SMS service for testing."""
    mock_service = MagicMock()
    mock_service.send_verification_sms = AsyncMock(return_value=True)
    mock_service.send_otp = AsyncMock(return_value="123456")
    return mock_service


# Test client fixtures
@pytest_asyncio.fixture
async def test_client():
    """Test client for API testing."""
    from fastapi.testclient import TestClient
    from user_service.main import app

    with TestClient(app) as client:
        yield client


# Environment fixtures
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("USER_SERVICE_DB_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-secret-key")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")


# Database cleanup fixtures
@pytest_asyncio.fixture(autouse=True)
async def cleanup_database():
    """Clean up database after each test."""
    yield
    # Cleanup logic would go here
    # For example: truncate tables, reset sequences, etc.


# Performance testing fixtures
@pytest.fixture
def performance_threshold():
    """Performance thresholds for testing."""
    return {
        "login_time": 1.0,  # seconds
        "registration_time": 2.0,  # seconds
        "profile_update_time": 0.5,  # seconds
        "password_change_time": 1.5,  # seconds
    }


# Security testing fixtures
@pytest.fixture
def security_test_data():
    """Security test data for testing."""
    return {
        "sql_injection_attempts": [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
        ],
        "xss_attempts": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
        ],
        "invalid_emails": [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
            "",
        ],
        "weak_passwords": ["123456", "password", "abc123", "12345678", "qwerty", ""],
    }


# Mock rate limiter
@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter for testing."""
    mock_limiter = MagicMock()
    mock_limiter.is_allowed = MagicMock(return_value=True)
    mock_limiter.increment = MagicMock()
    mock_limiter.reset = MagicMock()
    return mock_limiter
