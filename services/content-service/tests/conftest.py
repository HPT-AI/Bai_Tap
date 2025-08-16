"""
Pytest configuration and fixtures for Content Service tests.
"""

import asyncio
import json
from datetime import datetime, timedelta
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
    yield mock_redis


# Content fixtures
@pytest.fixture
def sample_article_data():
    """Sample article data for testing."""
    return {
        "title": "Giải phương trình bậc hai",
        "slug": "giai-phuong-trinh-bac-hai",
        "content": """
        <h2>Phương trình bậc hai</h2>
        <p>Phương trình bậc hai có dạng ax² + bx + c = 0 với a ≠ 0.</p>
        <h3>Công thức nghiệm</h3>
        <p>x = (-b ± √(b² - 4ac)) / 2a</p>
        <h3>Ví dụ</h3>
        <p>Giải phương trình x² - 5x + 6 = 0</p>
        <p>Ta có: a = 1, b = -5, c = 6</p>
        <p>Δ = b² - 4ac = 25 - 24 = 1</p>
        <p>x₁ = (5 + 1)/2 = 3</p>
        <p>x₂ = (5 - 1)/2 = 2</p>
        """,
        "excerpt": "Hướng dẫn chi tiết cách giải phương trình bậc hai với công thức nghiệm và ví dụ minh họa.",
        "author_id": 1,
        "category_id": 1,
        "tags": ["toán học", "phương trình", "bậc hai", "đại số"],
        "status": "published",
        "featured_image": "https://example.com/images/quadratic-equation.jpg",
        "meta_title": "Cách giải phương trình bậc hai - Công thức và ví dụ",
        "meta_description": "Học cách giải phương trình bậc hai với công thức nghiệm, delta và các ví dụ chi tiết.",
        "language": "vi",
        "reading_time": 5,
        "view_count": 0,
        "like_count": 0,
        "is_featured": False,
        "published_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        "name": "Đại số",
        "slug": "dai-so",
        "description": "Các bài viết về đại số, phương trình, bất phương trình",
        "parent_id": None,
        "sort_order": 1,
        "is_active": True,
        "meta_title": "Đại số - Toán học cơ bản",
        "meta_description": "Tổng hợp kiến thức đại số từ cơ bản đến nâng cao",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_tag_data():
    """Sample tag data for testing."""
    return [
        {
            "name": "toán học",
            "slug": "toan-hoc",
            "description": "Thẻ chung cho các bài viết toán học",
            "color": "#3498db",
            "is_active": True,
        },
        {
            "name": "phương trình",
            "slug": "phuong-trinh",
            "description": "Các bài viết về phương trình",
            "color": "#e74c3c",
            "is_active": True,
        },
        {
            "name": "bậc hai",
            "slug": "bac-hai",
            "description": "Phương trình bậc hai",
            "color": "#f39c12",
            "is_active": True,
        },
    ]


@pytest.fixture
def sample_comment_data():
    """Sample comment data for testing."""
    return {
        "article_id": 1,
        "user_id": 2,
        "parent_id": None,
        "content": "Bài viết rất hay và dễ hiểu. Cảm ơn tác giả!",
        "author_name": "Nguyễn Văn A",
        "author_email": "nguyenvana@example.com",
        "status": "approved",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_media_data():
    """Sample media data for testing."""
    return {
        "filename": "quadratic-equation-graph.jpg",
        "original_filename": "đồ thị phương trình bậc hai.jpg",
        "file_path": "/uploads/2024/01/quadratic-equation-graph.jpg",
        "file_size": 245760,  # bytes
        "mime_type": "image/jpeg",
        "width": 800,
        "height": 600,
        "alt_text": "Đồ thị hàm số bậc hai y = x² - 5x + 6",
        "caption": "Đồ thị minh họa nghiệm của phương trình x² - 5x + 6 = 0",
        "uploaded_by": 1,
        "is_public": True,
        "created_at": datetime.utcnow(),
    }


# SEO fixtures
@pytest.fixture
def sample_seo_data():
    """Sample SEO data for testing."""
    return {
        "url": "/bai-viet/giai-phuong-trinh-bac-hai",
        "title": "Cách giải phương trình bậc hai - Công thức và ví dụ",
        "description": "Học cách giải phương trình bậc hai với công thức nghiệm, delta và các ví dụ chi tiết.",
        "keywords": "phương trình bậc hai, công thức nghiệm, delta, toán học",
        "canonical_url": "https://mathservice.com/bai-viet/giai-phuong-trinh-bac-hai",
        "og_title": "Cách giải phương trình bậc hai",
        "og_description": "Hướng dẫn chi tiết cách giải phương trình bậc hai",
        "og_image": "https://mathservice.com/images/quadratic-equation-og.jpg",
        "og_type": "article",
        "twitter_card": "summary_large_image",
        "twitter_title": "Cách giải phương trình bậc hai",
        "twitter_description": "Hướng dẫn chi tiết cách giải phương trình bậc hai",
        "twitter_image": "https://mathservice.com/images/quadratic-equation-twitter.jpg",
        "robots": "index,follow",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Cách giải phương trình bậc hai",
            "author": {"@type": "Person", "name": "Giáo viên Toán"},
            "datePublished": "2024-01-15T10:00:00Z",
            "dateModified": "2024-01-15T10:00:00Z",
        },
    }


# Multi-language fixtures
@pytest.fixture
def sample_multilang_content():
    """Sample multi-language content for testing."""
    return {
        "vi": {
            "title": "Giải phương trình bậc hai",
            "content": "Phương trình bậc hai có dạng ax² + bx + c = 0",
            "excerpt": "Hướng dẫn giải phương trình bậc hai",
        },
        "en": {
            "title": "Solving Quadratic Equations",
            "content": "A quadratic equation has the form ax² + bx + c = 0",
            "excerpt": "Guide to solving quadratic equations",
        },
    }


# Content validation fixtures
@pytest.fixture
def content_validation_test_cases():
    """Test cases for content validation."""
    return {
        "valid_html": [
            "<p>This is a valid paragraph.</p>",
            "<h2>Valid heading</h2><p>With content</p>",
            "<ul><li>List item 1</li><li>List item 2</li></ul>",
            "<blockquote>This is a quote</blockquote>",
        ],
        "invalid_html": [
            "<script>alert('xss')</script>",
            "<iframe src='malicious.com'></iframe>",
            "<object data='malicious.swf'></object>",
            "<embed src='malicious.swf'></embed>",
            "<form><input type='text'></form>",
            "<style>body{display:none}</style>",
        ],
        "malicious_content": [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "vbscript:msgbox('xss')",
            "onload=alert('xss')",
            "onerror=alert('xss')",
        ],
    }


# Search fixtures
@pytest.fixture
def sample_search_data():
    """Sample search data for testing."""
    return {
        "query": "phương trình bậc hai",
        "filters": {
            "category": "dai-so",
            "tags": ["toán học", "phương trình"],
            "author": "giao-vien-toan",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
            "language": "vi",
        },
        "sort": "relevance",  # relevance, date, views, likes
        "page": 1,
        "per_page": 10,
    }


# Mock external services
@pytest.fixture
def mock_elasticsearch():
    """Mock Elasticsearch client for testing."""
    mock_es = MagicMock()
    mock_es.index = AsyncMock()
    mock_es.get = AsyncMock()
    mock_es.update = AsyncMock()
    mock_es.delete = AsyncMock()
    mock_es.search = AsyncMock()
    mock_es.bulk = AsyncMock()
    return mock_es


@pytest.fixture
def mock_image_processor():
    """Mock image processing service for testing."""
    mock_processor = MagicMock()
    mock_processor.resize = AsyncMock()
    mock_processor.crop = AsyncMock()
    mock_processor.optimize = AsyncMock()
    mock_processor.generate_thumbnails = AsyncMock()
    mock_processor.extract_metadata = AsyncMock()
    return mock_processor


@pytest.fixture
def mock_content_sanitizer():
    """Mock content sanitizer for testing."""
    mock_sanitizer = MagicMock()
    mock_sanitizer.sanitize_html = MagicMock()
    mock_sanitizer.validate_content = MagicMock()
    mock_sanitizer.extract_text = MagicMock()
    mock_sanitizer.detect_language = MagicMock()
    return mock_sanitizer


@pytest.fixture
def mock_seo_analyzer():
    """Mock SEO analyzer for testing."""
    mock_analyzer = MagicMock()
    mock_analyzer.analyze_content = AsyncMock()
    mock_analyzer.generate_meta_tags = AsyncMock()
    mock_analyzer.check_readability = AsyncMock()
    mock_analyzer.suggest_improvements = AsyncMock()
    return mock_analyzer


# Test client fixtures
@pytest_asyncio.fixture
async def test_client():
    """Test client for API testing."""
    from content_service.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        yield client


# Environment fixtures
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("CONTENT_SERVICE_DB_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ELASTICSEARCH_URL", "http://localhost:9200")
    monkeypatch.setenv("UPLOAD_PATH", "/tmp/test_uploads")
    monkeypatch.setenv("MAX_FILE_SIZE", "10485760")  # 10MB
    monkeypatch.setenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,pdf,doc,docx")
    monkeypatch.setenv("DEFAULT_LANGUAGE", "vi")
    monkeypatch.setenv("SUPPORTED_LANGUAGES", "vi,en")


# Performance testing fixtures
@pytest.fixture
def performance_threshold():
    """Performance thresholds for content operations."""
    return {
        "article_creation": 2.0,  # seconds
        "article_update": 1.5,  # seconds
        "article_search": 1.0,  # seconds
        "content_sanitization": 0.5,  # seconds
        "image_processing": 5.0,  # seconds
        "seo_analysis": 2.0,  # seconds
    }


# Security testing fixtures
@pytest.fixture
def security_test_data():
    """Security test data for content service."""
    return {
        "xss_payloads": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
        ],
        "sql_injection_payloads": [
            "'; DROP TABLE articles; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
            "1; DELETE FROM articles WHERE 1=1 --",
        ],
        "file_upload_attacks": [
            "malicious.php",
            "script.js",
            "virus.exe",
            "shell.sh",
            "backdoor.asp",
        ],
    }


# Database cleanup fixtures
@pytest_asyncio.fixture(autouse=True)
async def cleanup_database():
    """Clean up database after each test."""
    yield
    # Cleanup logic would go here
    # For example: truncate tables, reset sequences, etc.
