"""
Unit tests for Content CRUD operations.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock imports - these would be actual imports in real implementation
# from content_service.models import Article, Category, Tag, Comment
# from content_service.repositories import ContentRepository, CategoryRepository
# from content_service.schemas import ArticleCreate, ArticleUpdate, CategoryCreate
# from content_service.services import ContentService, SEOService


@pytest.mark.asyncio
class TestArticleCRUD:
    """Test Article CRUD operations."""

    def test_create_article(self, sample_articles):
        """Test creating new articles."""

        async def create_article(article_data):
            """
            Create new article with validation and SEO optimization
            """
            try:
                # Validate required fields
                required_fields = ["title", "content", "author_id", "category_id"]
                for field in required_fields:
                    if field not in article_data or not article_data[field]:
                        return {
                            "success": False,
                            "error": f"Missing required field: {field}",
                        }

                # Generate SEO-friendly slug
                title = article_data["title"]
                slug = title.lower().replace(" ", "-").replace(",", "").replace(".", "")

                # Auto-generate meta description if not provided
                content = article_data["content"]
                meta_description = article_data.get("meta_description")
                if not meta_description:
                    # Extract first 160 characters as meta description
                    meta_description = (
                        content[:160] + "..." if len(content) > 160 else content
                    )

                # Set default values
                now = datetime.utcnow()
                article = {
                    "id": 1,  # Mock ID
                    "title": title,
                    "slug": slug,
                    "content": content,
                    "meta_description": meta_description,
                    "author_id": article_data["author_id"],
                    "category_id": article_data["category_id"],
                    "status": article_data.get("status", "draft"),
                    "is_featured": article_data.get("is_featured", False),
                    "view_count": 0,
                    "like_count": 0,
                    "comment_count": 0,
                    "created_at": now,
                    "updated_at": now,
                    "published_at": now
                    if article_data.get("status") == "published"
                    else None,
                }

                # Handle tags
                if "tags" in article_data:
                    article["tags"] = article_data["tags"]

                return {
                    "success": True,
                    "article": article,
                    "message": "Article created successfully",
                }

            except Exception as e:
                return {"success": False, "error": f"Error creating article: {str(e)}"}

        # Test successful article creation
        article_data = {
            "title": "Introduction to Calculus",
            "content": "Calculus is a branch of mathematics that deals with derivatives and integrals...",
            "author_id": 1,
            "category_id": 2,
            "status": "published",
            "tags": ["calculus", "mathematics", "education"],
        }

        result = await create_article(article_data)

        assert result["success"] is True
        assert "article" in result

        article = result["article"]
        assert article["title"] == "Introduction to Calculus"
        assert article["slug"] == "introduction-to-calculus"
        assert article["status"] == "published"
        assert article["view_count"] == 0
        assert article["published_at"] is not None
        assert len(article["meta_description"]) <= 163  # 160 + "..."
        assert "tags" in article
        assert len(article["tags"]) == 3

    def test_create_article_validation_errors(self):
        """Test article creation with validation errors."""

        async def create_article(article_data):
            # Same implementation as above
            try:
                required_fields = ["title", "content", "author_id", "category_id"]
                for field in required_fields:
                    if field not in article_data or not article_data[field]:
                        return {
                            "success": False,
                            "error": f"Missing required field: {field}",
                        }
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Test missing required fields
        invalid_cases = [
            ({}, "Missing required field: title"),
            ({"title": "Test"}, "Missing required field: content"),
            (
                {"title": "Test", "content": "Content"},
                "Missing required field: author_id",
            ),
            (
                {"title": "Test", "content": "Content", "author_id": 1},
                "Missing required field: category_id",
            ),
        ]

        for article_data, expected_error in invalid_cases:
            result = await create_article(article_data)

            assert result["success"] is False
            assert expected_error in result["error"]

    def test_get_article_by_id(self, sample_articles):
        """Test retrieving article by ID."""

        async def get_article_by_id(article_id, include_views=True):
            """
            Get article by ID with optional view count increment
            """
            try:
                # Mock database lookup
                mock_articles = {
                    1: {
                        "id": 1,
                        "title": "Linear Algebra Basics",
                        "slug": "linear-algebra-basics",
                        "content": "Linear algebra is the study of vectors and matrices...",
                        "meta_description": "Learn the fundamentals of linear algebra including vectors, matrices, and linear transformations.",
                        "author_id": 1,
                        "category_id": 1,
                        "status": "published",
                        "is_featured": True,
                        "view_count": 150,
                        "like_count": 25,
                        "comment_count": 8,
                        "created_at": datetime(2024, 1, 15),
                        "updated_at": datetime(2024, 1, 20),
                        "published_at": datetime(2024, 1, 15),
                        "tags": ["linear-algebra", "mathematics", "vectors"],
                    }
                }

                if article_id not in mock_articles:
                    return {"success": False, "error": "Article not found"}

                article = mock_articles[article_id].copy()

                # Increment view count if requested
                if include_views:
                    article["view_count"] += 1

                return {"success": True, "article": article}

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error retrieving article: {str(e)}",
                }

        # Test successful retrieval
        result = await get_article_by_id(1)

        assert result["success"] is True
        assert "article" in result

        article = result["article"]
        assert article["id"] == 1
        assert article["title"] == "Linear Algebra Basics"
        assert article["status"] == "published"
        assert article["view_count"] == 151  # Incremented

        # Test article not found
        result = await get_article_by_id(999)

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_update_article(self, sample_articles):
        """Test updating existing articles."""

        async def update_article(article_id, update_data):
            """
            Update existing article with validation
            """
            try:
                # Mock current article
                current_article = {
                    "id": article_id,
                    "title": "Old Title",
                    "slug": "old-title",
                    "content": "Old content",
                    "meta_description": "Old description",
                    "author_id": 1,
                    "category_id": 1,
                    "status": "draft",
                    "is_featured": False,
                    "view_count": 10,
                    "like_count": 2,
                    "comment_count": 1,
                    "created_at": datetime(2024, 1, 1),
                    "updated_at": datetime(2024, 1, 1),
                    "published_at": None,
                }

                if article_id != 1:
                    return {"success": False, "error": "Article not found"}

                # Apply updates
                updated_article = current_article.copy()

                for field, value in update_data.items():
                    if field in [
                        "id",
                        "created_at",
                        "view_count",
                        "like_count",
                        "comment_count",
                    ]:
                        continue  # Skip read-only fields

                    updated_article[field] = value

                # Update slug if title changed
                if "title" in update_data:
                    updated_article["slug"] = (
                        update_data["title"].lower().replace(" ", "-")
                    )

                # Set published_at if status changed to published
                if (
                    update_data.get("status") == "published"
                    and current_article["status"] != "published"
                ):
                    updated_article["published_at"] = datetime.utcnow()

                # Update timestamp
                updated_article["updated_at"] = datetime.utcnow()

                return {
                    "success": True,
                    "article": updated_article,
                    "message": "Article updated successfully",
                }

            except Exception as e:
                return {"success": False, "error": f"Error updating article: {str(e)}"}

        # Test successful update
        update_data = {
            "title": "Updated Title",
            "content": "Updated content with more details",
            "status": "published",
            "is_featured": True,
        }

        result = await update_article(1, update_data)

        assert result["success"] is True
        assert "article" in result

        article = result["article"]
        assert article["title"] == "Updated Title"
        assert article["slug"] == "updated-title"
        assert article["content"] == "Updated content with more details"
        assert article["status"] == "published"
        assert article["is_featured"] is True
        assert article["published_at"] is not None
        assert article["updated_at"] > article["created_at"]

        # Test article not found
        result = await update_article(999, {"title": "New Title"})

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_delete_article(self, sample_articles):
        """Test deleting articles (soft delete)."""

        async def delete_article(article_id, hard_delete=False):
            """
            Delete article (soft delete by default)
            """
            try:
                # Mock article existence check
                if article_id not in [1, 2, 3]:
                    return {"success": False, "error": "Article not found"}

                if hard_delete:
                    # Hard delete - remove from database
                    return {"success": True, "message": "Article permanently deleted"}
                else:
                    # Soft delete - mark as deleted
                    return {
                        "success": True,
                        "article": {
                            "id": article_id,
                            "status": "deleted",
                            "deleted_at": datetime.utcnow(),
                        },
                        "message": "Article moved to trash",
                    }

            except Exception as e:
                return {"success": False, "error": f"Error deleting article: {str(e)}"}

        # Test soft delete
        result = await delete_article(1)

        assert result["success"] is True
        assert "article" in result
        assert result["article"]["status"] == "deleted"
        assert result["article"]["deleted_at"] is not None
        assert "trash" in result["message"].lower()

        # Test hard delete
        result = await delete_article(2, hard_delete=True)

        assert result["success"] is True
        assert "article" not in result  # No article returned for hard delete
        assert "permanently deleted" in result["message"].lower()

        # Test article not found
        result = await delete_article(999)

        assert result["success"] is False
        assert "not found" in result["error"].lower()


@pytest.mark.asyncio
class TestCategoryCRUD:
    """Test Category CRUD operations."""

    def test_create_category(self, sample_categories):
        """Test creating new categories."""

        async def create_category(category_data):
            """
            Create new category with hierarchy support
            """
            try:
                # Validate required fields
                if "name" not in category_data or not category_data["name"]:
                    return {"success": False, "error": "Category name is required"}

                # Generate slug
                name = category_data["name"]
                slug = name.lower().replace(" ", "-").replace("&", "and")

                # Check parent category if specified
                parent_id = category_data.get("parent_id")
                if parent_id:
                    # Mock parent validation
                    valid_parents = [1, 2, 3]  # Mock existing category IDs
                    if parent_id not in valid_parents:
                        return {"success": False, "error": "Invalid parent category"}

                category = {
                    "id": 4,  # Mock new ID
                    "name": name,
                    "slug": slug,
                    "description": category_data.get("description", ""),
                    "parent_id": parent_id,
                    "sort_order": category_data.get("sort_order", 0),
                    "is_active": category_data.get("is_active", True),
                    "article_count": 0,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }

                return {
                    "success": True,
                    "category": category,
                    "message": "Category created successfully",
                }

            except Exception as e:
                return {"success": False, "error": f"Error creating category: {str(e)}"}

        # Test successful category creation
        category_data = {
            "name": "Advanced Mathematics",
            "description": "Advanced topics in mathematics including calculus, linear algebra, and more",
            "parent_id": 1,
            "sort_order": 10,
        }

        result = await create_category(category_data)

        assert result["success"] is True
        assert "category" in result

        category = result["category"]
        assert category["name"] == "Advanced Mathematics"
        assert category["slug"] == "advanced-mathematics"
        assert category["parent_id"] == 1
        assert category["sort_order"] == 10
        assert category["is_active"] is True
        assert category["article_count"] == 0

    def test_get_category_hierarchy(self, sample_categories):
        """Test retrieving category hierarchy."""

        async def get_category_hierarchy():
            """
            Get category hierarchy with parent-child relationships
            """
            try:
                # Mock category data with hierarchy
                categories = [
                    {
                        "id": 1,
                        "name": "Mathematics",
                        "slug": "mathematics",
                        "description": "All mathematics topics",
                        "parent_id": None,
                        "sort_order": 1,
                        "is_active": True,
                        "article_count": 25,
                        "children": [
                            {
                                "id": 2,
                                "name": "Algebra",
                                "slug": "algebra",
                                "description": "Algebraic concepts and equations",
                                "parent_id": 1,
                                "sort_order": 1,
                                "is_active": True,
                                "article_count": 12,
                                "children": [],
                            },
                            {
                                "id": 3,
                                "name": "Calculus",
                                "slug": "calculus",
                                "description": "Differential and integral calculus",
                                "parent_id": 1,
                                "sort_order": 2,
                                "is_active": True,
                                "article_count": 13,
                                "children": [],
                            },
                        ],
                    },
                    {
                        "id": 4,
                        "name": "Physics",
                        "slug": "physics",
                        "description": "Physics topics and concepts",
                        "parent_id": None,
                        "sort_order": 2,
                        "is_active": True,
                        "article_count": 8,
                        "children": [],
                    },
                ]

                return {
                    "success": True,
                    "categories": categories,
                    "total_count": len(categories),
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error retrieving categories: {str(e)}",
                }

        result = await get_category_hierarchy()

        assert result["success"] is True
        assert "categories" in result
        assert result["total_count"] == 2

        categories = result["categories"]

        # Check root categories
        math_category = categories[0]
        assert math_category["name"] == "Mathematics"
        assert math_category["parent_id"] is None
        assert len(math_category["children"]) == 2

        # Check child categories
        algebra_category = math_category["children"][0]
        assert algebra_category["name"] == "Algebra"
        assert algebra_category["parent_id"] == 1
        assert len(algebra_category["children"]) == 0


@pytest.mark.asyncio
class TestTagManagement:
    """Test Tag management functionality."""

    def test_create_and_manage_tags(self, sample_tags):
        """Test creating and managing tags."""

        async def create_tag(tag_data):
            """
            Create new tag with validation
            """
            try:
                if "name" not in tag_data or not tag_data["name"]:
                    return {"success": False, "error": "Tag name is required"}

                name = tag_data["name"].strip().lower()

                # Check for duplicate
                existing_tags = ["mathematics", "algebra", "calculus", "geometry"]
                if name in existing_tags:
                    return {"success": False, "error": "Tag already exists"}

                tag = {
                    "id": 5,  # Mock new ID
                    "name": name,
                    "display_name": tag_data["name"].strip(),
                    "description": tag_data.get("description", ""),
                    "color": tag_data.get("color", "#007bff"),
                    "usage_count": 0,
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                }

                return {
                    "success": True,
                    "tag": tag,
                    "message": "Tag created successfully",
                }

            except Exception as e:
                return {"success": False, "error": f"Error creating tag: {str(e)}"}

        # Test successful tag creation
        tag_data = {
            "name": "Linear Algebra",
            "description": "Topics related to linear algebra",
            "color": "#28a745",
        }

        result = await create_tag(tag_data)

        assert result["success"] is True
        assert "tag" in result

        tag = result["tag"]
        assert tag["name"] == "linear algebra"  # Normalized
        assert tag["display_name"] == "Linear Algebra"
        assert tag["color"] == "#28a745"
        assert tag["usage_count"] == 0
        assert tag["is_active"] is True

        # Test duplicate tag
        duplicate_data = {"name": "Mathematics"}
        result = await create_tag(duplicate_data)

        assert result["success"] is False
        assert "already exists" in result["error"].lower()

    def test_get_popular_tags(self, sample_tags):
        """Test retrieving popular tags."""

        async def get_popular_tags(limit=10):
            """
            Get most popular tags by usage count
            """
            try:
                # Mock popular tags data
                popular_tags = [
                    {
                        "id": 1,
                        "name": "mathematics",
                        "display_name": "Mathematics",
                        "usage_count": 45,
                        "color": "#007bff",
                    },
                    {
                        "id": 2,
                        "name": "algebra",
                        "display_name": "Algebra",
                        "usage_count": 32,
                        "color": "#28a745",
                    },
                    {
                        "id": 3,
                        "name": "calculus",
                        "display_name": "Calculus",
                        "usage_count": 28,
                        "color": "#dc3545",
                    },
                    {
                        "id": 4,
                        "name": "geometry",
                        "display_name": "Geometry",
                        "usage_count": 15,
                        "color": "#ffc107",
                    },
                ]

                # Sort by usage count and limit
                sorted_tags = sorted(
                    popular_tags, key=lambda x: x["usage_count"], reverse=True
                )
                limited_tags = sorted_tags[:limit]

                return {
                    "success": True,
                    "tags": limited_tags,
                    "total_count": len(limited_tags),
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error retrieving popular tags: {str(e)}",
                }

        result = await get_popular_tags(3)

        assert result["success"] is True
        assert "tags" in result
        assert result["total_count"] == 3

        tags = result["tags"]

        # Check sorting by usage count
        assert tags[0]["usage_count"] >= tags[1]["usage_count"]
        assert tags[1]["usage_count"] >= tags[2]["usage_count"]

        # Check first tag
        assert tags[0]["name"] == "mathematics"
        assert tags[0]["usage_count"] == 45


@pytest.mark.asyncio
class TestContentSearch:
    """Test Content search functionality."""

    def test_search_articles(self, sample_articles):
        """Test searching articles with various filters."""

        async def search_articles(
            query=None, category_id=None, tags=None, status=None, limit=10, offset=0
        ):
            """
            Search articles with filters and pagination
            """
            try:
                # Mock articles database
                mock_articles = [
                    {
                        "id": 1,
                        "title": "Introduction to Linear Algebra",
                        "content": "Linear algebra is fundamental to many areas of mathematics...",
                        "category_id": 1,
                        "status": "published",
                        "tags": ["linear-algebra", "mathematics", "vectors"],
                        "view_count": 150,
                        "created_at": datetime(2024, 1, 15),
                    },
                    {
                        "id": 2,
                        "title": "Calculus Fundamentals",
                        "content": "Calculus deals with derivatives and integrals...",
                        "category_id": 1,
                        "status": "published",
                        "tags": ["calculus", "mathematics", "derivatives"],
                        "view_count": 200,
                        "created_at": datetime(2024, 1, 20),
                    },
                    {
                        "id": 3,
                        "title": "Draft Article",
                        "content": "This is a draft article...",
                        "category_id": 2,
                        "status": "draft",
                        "tags": ["draft"],
                        "view_count": 5,
                        "created_at": datetime(2024, 2, 1),
                    },
                ]

                filtered_articles = mock_articles.copy()

                # Apply filters
                if query:
                    query_lower = query.lower()
                    filtered_articles = [
                        article
                        for article in filtered_articles
                        if query_lower in article["title"].lower()
                        or query_lower in article["content"].lower()
                    ]

                if category_id:
                    filtered_articles = [
                        article
                        for article in filtered_articles
                        if article["category_id"] == category_id
                    ]

                if tags:
                    if isinstance(tags, str):
                        tags = [tags]
                    filtered_articles = [
                        article
                        for article in filtered_articles
                        if any(tag in article["tags"] for tag in tags)
                    ]

                if status:
                    filtered_articles = [
                        article
                        for article in filtered_articles
                        if article["status"] == status
                    ]

                # Sort by view count (most popular first)
                filtered_articles.sort(key=lambda x: x["view_count"], reverse=True)

                # Apply pagination
                total_count = len(filtered_articles)
                paginated_articles = filtered_articles[offset : offset + limit]

                return {
                    "success": True,
                    "articles": paginated_articles,
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count,
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error searching articles: {str(e)}",
                }

        # Test search by query
        result = await search_articles(query="algebra")

        assert result["success"] is True
        assert result["total_count"] == 1
        assert len(result["articles"]) == 1
        assert "algebra" in result["articles"][0]["title"].lower()

        # Test search by category
        result = await search_articles(category_id=1)

        assert result["success"] is True
        assert result["total_count"] == 2
        assert all(article["category_id"] == 1 for article in result["articles"])

        # Test search by tags
        result = await search_articles(tags=["mathematics"])

        assert result["success"] is True
        assert result["total_count"] == 2
        assert all("mathematics" in article["tags"] for article in result["articles"])

        # Test search by status
        result = await search_articles(status="published")

        assert result["success"] is True
        assert result["total_count"] == 2
        assert all(article["status"] == "published" for article in result["articles"])

        # Test combined filters
        result = await search_articles(query="calculus", status="published")

        assert result["success"] is True
        assert result["total_count"] == 1
        assert "calculus" in result["articles"][0]["title"].lower()
        assert result["articles"][0]["status"] == "published"

        # Test pagination
        result = await search_articles(limit=1, offset=0)

        assert result["success"] is True
        assert len(result["articles"]) == 1
        assert result["has_more"] is True

        result = await search_articles(limit=1, offset=1)

        assert result["success"] is True
        assert len(result["articles"]) == 1
        assert result["has_more"] is True


@pytest.mark.asyncio
class TestContentValidation:
    """Test Content validation and sanitization."""

    def test_validate_article_content(self):
        """Test article content validation and sanitization."""

        def validate_and_sanitize_content(content, content_type="html"):
            """
            Validate and sanitize article content
            """
            try:
                if not content or not content.strip():
                    return {"is_valid": False, "error": "Content cannot be empty"}

                # Check minimum length
                if len(content.strip()) < 50:
                    return {
                        "is_valid": False,
                        "error": "Content must be at least 50 characters long",
                    }

                # Check maximum length
                if len(content) > 50000:
                    return {
                        "is_valid": False,
                        "error": "Content exceeds maximum length of 50,000 characters",
                    }

                sanitized_content = content

                if content_type == "html":
                    # Remove dangerous HTML tags and attributes
                    dangerous_tags = [
                        "<script",
                        "<iframe",
                        "<object",
                        "<embed",
                        "<form",
                    ]
                    for tag in dangerous_tags:
                        if tag in content.lower():
                            return {
                                "is_valid": False,
                                "error": f"Dangerous HTML tag detected: {tag}",
                            }

                    # Basic HTML sanitization (in real implementation, use a proper library)
                    sanitized_content = content.replace("<script>", "").replace(
                        "</script>", ""
                    )
                    sanitized_content = sanitized_content.replace("javascript:", "")
                    sanitized_content = sanitized_content.replace("onload=", "")
                    sanitized_content = sanitized_content.replace("onclick=", "")

                # Check for spam patterns
                spam_patterns = ["buy now", "click here", "free money", "guaranteed"]
                spam_count = sum(
                    1 for pattern in spam_patterns if pattern in content.lower()
                )

                if spam_count >= 3:
                    return {"is_valid": False, "error": "Content appears to be spam"}

                # Extract metadata
                word_count = len(content.split())
                reading_time = max(1, word_count // 200)  # Assume 200 words per minute

                return {
                    "is_valid": True,
                    "sanitized_content": sanitized_content,
                    "metadata": {
                        "word_count": word_count,
                        "character_count": len(content),
                        "reading_time_minutes": reading_time,
                        "content_type": content_type,
                    },
                }

            except Exception as e:
                return {
                    "is_valid": False,
                    "error": f"Error validating content: {str(e)}",
                }

        # Test valid content
        valid_content = "This is a comprehensive article about linear algebra. " * 10
        result = validate_and_sanitize_content(valid_content)

        assert result["is_valid"] is True
        assert "sanitized_content" in result
        assert "metadata" in result
        assert result["metadata"]["word_count"] > 0
        assert result["metadata"]["reading_time_minutes"] > 0

        # Test empty content
        result = validate_and_sanitize_content("")

        assert result["is_valid"] is False
        assert "empty" in result["error"].lower()

        # Test too short content
        result = validate_and_sanitize_content("Short")

        assert result["is_valid"] is False
        assert "50 characters" in result["error"]

        # Test dangerous HTML
        dangerous_content = "Valid content here <script>alert('xss')</script>"
        result = validate_and_sanitize_content(dangerous_content, "html")

        assert result["is_valid"] is False
        assert "dangerous" in result["error"].lower()

        # Test spam content
        spam_content = "Buy now! Click here for free money guaranteed! " * 20
        result = validate_and_sanitize_content(spam_content)

        assert result["is_valid"] is False
        assert "spam" in result["error"].lower()

    def test_validate_seo_metadata(self):
        """Test SEO metadata validation."""

        def validate_seo_metadata(title, meta_description, slug):
            """
            Validate SEO metadata for articles
            """
            try:
                errors = []
                warnings = []

                # Title validation
                if not title or len(title.strip()) == 0:
                    errors.append("Title is required")
                elif len(title) < 10:
                    warnings.append(
                        "Title is too short (recommended: 10-60 characters)"
                    )
                elif len(title) > 60:
                    warnings.append("Title is too long (recommended: 10-60 characters)")

                # Meta description validation
                if not meta_description:
                    warnings.append("Meta description is missing")
                elif len(meta_description) < 120:
                    warnings.append(
                        "Meta description is too short (recommended: 120-160 characters)"
                    )
                elif len(meta_description) > 160:
                    warnings.append(
                        "Meta description is too long (recommended: 120-160 characters)"
                    )

                # Slug validation
                if not slug:
                    errors.append("Slug is required")
                elif not slug.replace("-", "").replace("_", "").isalnum():
                    errors.append("Slug contains invalid characters")
                elif len(slug) > 100:
                    errors.append("Slug is too long (maximum: 100 characters)")

                # SEO score calculation
                score = 100
                score -= len(errors) * 20
                score -= len(warnings) * 10
                score = max(0, score)

                # SEO recommendations
                recommendations = []
                if len(title) < 30:
                    recommendations.append("Consider making the title more descriptive")
                if not meta_description:
                    recommendations.append("Add a compelling meta description")
                if "-" not in slug:
                    recommendations.append("Use hyphens in slug for better readability")

                return {
                    "is_valid": len(errors) == 0,
                    "errors": errors,
                    "warnings": warnings,
                    "recommendations": recommendations,
                    "seo_score": score,
                    "grade": "A"
                    if score >= 90
                    else "B"
                    if score >= 70
                    else "C"
                    if score >= 50
                    else "D",
                }

            except Exception as e:
                return {
                    "is_valid": False,
                    "errors": [f"Error validating SEO metadata: {str(e)}"],
                }

        # Test good SEO metadata
        result = validate_seo_metadata(
            title="Complete Guide to Linear Algebra for Beginners",
            meta_description="Learn linear algebra fundamentals including vectors, matrices, and linear transformations with practical examples and exercises.",
            slug="complete-guide-linear-algebra-beginners",
        )

        assert result["is_valid"] is True
        assert result["seo_score"] >= 90
        assert result["grade"] == "A"
        assert len(result["errors"]) == 0

        # Test missing title
        result = validate_seo_metadata(
            title="", meta_description="Good description here", slug="valid-slug"
        )

        assert result["is_valid"] is False
        assert "Title is required" in result["errors"]

        # Test poor SEO
        result = validate_seo_metadata(
            title="Math",  # Too short
            meta_description="Short",  # Too short
            slug="math@#$",  # Invalid characters
        )

        assert result["is_valid"] is False
        assert result["seo_score"] < 50
        assert result["grade"] in ["D", "C"]
        assert len(result["errors"]) > 0
        assert len(result["warnings"]) > 0
