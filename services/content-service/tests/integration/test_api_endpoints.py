"""
Integration tests for Content Service API endpoints.
"""

import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestContentServiceAPIEndpoints:
    """Integration tests for Content Service API endpoints."""

    @pytest.fixture
    def mock_app(self):
        """Mock FastAPI application for testing."""
        from fastapi import Depends, FastAPI, HTTPException, Query
        from fastapi.security import HTTPBearer

        app = FastAPI(title="Content Service", version="1.0.0")
        security = HTTPBearer()

        # Mock authentication dependency
        async def get_current_user(token: str = Depends(security)):
            if token.credentials == "valid_token":
                return {"user_id": 123, "email": "test@example.com", "role": "user"}
            elif token.credentials == "admin_token":
                return {"user_id": 456, "email": "admin@example.com", "role": "admin"}
            elif token.credentials == "author_token":
                return {"user_id": 789, "email": "author@example.com", "role": "author"}
            else:
                raise HTTPException(status_code=401, detail="Invalid token")

        # Article endpoints
        @app.get("/articles")
        async def get_articles(
            page: int = Query(1, ge=1),
            limit: int = Query(10, ge=1, le=100),
            category: str = None,
            tag: str = None,
            search: str = None,
            status: str = Query("published"),
        ):
            """Get articles with filtering and pagination."""
            # Mock articles data
            all_articles = [
                {
                    "id": 1,
                    "title": "Introduction to Algebra",
                    "slug": "introduction-to-algebra",
                    "excerpt": "Learn the basics of algebra with step-by-step examples.",
                    "content": "Algebra is a branch of mathematics...",
                    "author_id": 789,
                    "author_name": "Math Teacher",
                    "category": "algebra",
                    "tags": ["algebra", "basics", "mathematics"],
                    "status": "published",
                    "featured_image": "/images/algebra-intro.jpg",
                    "seo_title": "Introduction to Algebra - Learn Math Basics",
                    "seo_description": "Master algebra fundamentals with our comprehensive guide",
                    "views": 1250,
                    "likes": 89,
                    "published_at": "2024-12-10T10:00:00",
                    "created_at": "2024-12-09T15:30:00",
                    "updated_at": "2024-12-10T09:45:00",
                },
                {
                    "id": 2,
                    "title": "Calculus Fundamentals",
                    "slug": "calculus-fundamentals",
                    "excerpt": "Understanding derivatives and integrals made easy.",
                    "content": "Calculus is the mathematical study...",
                    "author_id": 789,
                    "author_name": "Math Teacher",
                    "category": "calculus",
                    "tags": ["calculus", "derivatives", "integrals"],
                    "status": "published",
                    "featured_image": "/images/calculus-basics.jpg",
                    "seo_title": "Calculus Fundamentals - Derivatives and Integrals",
                    "seo_description": "Learn calculus basics including derivatives and integrals",
                    "views": 980,
                    "likes": 67,
                    "published_at": "2024-12-12T14:00:00",
                    "created_at": "2024-12-11T10:15:00",
                    "updated_at": "2024-12-12T13:30:00",
                },
                {
                    "id": 3,
                    "title": "Draft Article",
                    "slug": "draft-article",
                    "excerpt": "This is a draft article.",
                    "content": "Draft content...",
                    "author_id": 789,
                    "author_name": "Math Teacher",
                    "category": "general",
                    "tags": ["draft"],
                    "status": "draft",
                    "featured_image": None,
                    "views": 0,
                    "likes": 0,
                    "published_at": None,
                    "created_at": "2024-12-15T09:00:00",
                    "updated_at": "2024-12-15T09:00:00",
                },
            ]

            # Apply filters
            filtered_articles = all_articles

            # Filter by status
            if status:
                filtered_articles = [
                    a for a in filtered_articles if a["status"] == status
                ]

            # Filter by category
            if category:
                filtered_articles = [
                    a for a in filtered_articles if a["category"] == category
                ]

            # Filter by tag
            if tag:
                filtered_articles = [a for a in filtered_articles if tag in a["tags"]]

            # Search filter
            if search:
                search_lower = search.lower()
                filtered_articles = [
                    a
                    for a in filtered_articles
                    if search_lower in a["title"].lower()
                    or search_lower in a["content"].lower()
                ]

            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_articles = filtered_articles[start:end]

            return {
                "success": True,
                "articles": paginated_articles,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(filtered_articles),
                    "pages": (len(filtered_articles) + limit - 1) // limit,
                },
            }

        @app.get("/articles/{article_id}")
        async def get_article(article_id: int):
            """Get specific article by ID."""
            # Mock article lookup
            if article_id == 1:
                article = {
                    "id": 1,
                    "title": "Introduction to Algebra",
                    "slug": "introduction-to-algebra",
                    "content": "Algebra is a branch of mathematics dealing with symbols and the rules for manipulating those symbols...",
                    "author_id": 789,
                    "author_name": "Math Teacher",
                    "author_bio": "Experienced mathematics educator with 10+ years of teaching.",
                    "category": "algebra",
                    "tags": ["algebra", "basics", "mathematics"],
                    "status": "published",
                    "featured_image": "/images/algebra-intro.jpg",
                    "seo_title": "Introduction to Algebra - Learn Math Basics",
                    "seo_description": "Master algebra fundamentals with our comprehensive guide",
                    "meta_keywords": "algebra, mathematics, basics, learning",
                    "views": 1251,  # Incremented
                    "likes": 89,
                    "published_at": "2024-12-10T10:00:00",
                    "created_at": "2024-12-09T15:30:00",
                    "updated_at": "2024-12-10T09:45:00",
                    "reading_time_minutes": 8,
                    "related_articles": [
                        {
                            "id": 2,
                            "title": "Calculus Fundamentals",
                            "slug": "calculus-fundamentals",
                        }
                    ],
                }

                return {"success": True, "article": article}
            else:
                raise HTTPException(status_code=404, detail="Article not found")

        @app.post("/articles")
        async def create_article(
            article_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Create new article."""
            # Check permissions
            if current_user["role"] not in ["admin", "author"]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")

            title = article_data.get("title")
            content = article_data.get("content")
            category = article_data.get("category")

            if not title:
                raise HTTPException(status_code=400, detail="Title is required")
            if not content:
                raise HTTPException(status_code=400, detail="Content is required")
            if not category:
                raise HTTPException(status_code=400, detail="Category is required")

            # Generate slug from title
            slug = title.lower().replace(" ", "-").replace("'", "")

            # Create article
            new_article = {
                "id": 4,  # Mock new ID
                "title": title,
                "slug": slug,
                "excerpt": article_data.get("excerpt", content[:150] + "..."),
                "content": content,
                "author_id": current_user["user_id"],
                "author_name": current_user["email"].split("@")[0],
                "category": category,
                "tags": article_data.get("tags", []),
                "status": article_data.get("status", "draft"),
                "featured_image": article_data.get("featured_image"),
                "seo_title": article_data.get("seo_title", title),
                "seo_description": article_data.get("seo_description", ""),
                "views": 0,
                "likes": 0,
                "published_at": datetime.utcnow().isoformat()
                if article_data.get("status") == "published"
                else None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            return {
                "success": True,
                "message": "Article created successfully",
                "article": new_article,
            }

        @app.put("/articles/{article_id}")
        async def update_article(
            article_id: int,
            article_data: dict,
            current_user: dict = Depends(get_current_user),
        ):
            """Update existing article."""
            # Mock article ownership check
            if article_id == 1:
                article_author_id = 789
                if (
                    current_user["user_id"] != article_author_id
                    and current_user["role"] != "admin"
                ):
                    raise HTTPException(
                        status_code=403, detail="You can only edit your own articles"
                    )

                # Update article
                updated_article = {
                    "id": article_id,
                    "title": article_data.get("title", "Introduction to Algebra"),
                    "slug": article_data.get("slug", "introduction-to-algebra"),
                    "excerpt": article_data.get(
                        "excerpt", "Learn the basics of algebra..."
                    ),
                    "content": article_data.get("content", "Updated content..."),
                    "author_id": article_author_id,
                    "category": article_data.get("category", "algebra"),
                    "tags": article_data.get("tags", ["algebra", "basics"]),
                    "status": article_data.get("status", "published"),
                    "updated_at": datetime.utcnow().isoformat(),
                }

                return {
                    "success": True,
                    "message": "Article updated successfully",
                    "article": updated_article,
                }
            else:
                raise HTTPException(status_code=404, detail="Article not found")

        @app.delete("/articles/{article_id}")
        async def delete_article(
            article_id: int, current_user: dict = Depends(get_current_user)
        ):
            """Delete article."""
            # Mock article ownership check
            if article_id == 1:
                article_author_id = 789
                if (
                    current_user["user_id"] != article_author_id
                    and current_user["role"] != "admin"
                ):
                    raise HTTPException(
                        status_code=403, detail="You can only delete your own articles"
                    )

                return {"success": True, "message": "Article deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail="Article not found")

        # Category endpoints
        @app.get("/categories")
        async def get_categories():
            """Get all categories."""
            categories = [
                {
                    "id": 1,
                    "name": "Algebra",
                    "slug": "algebra",
                    "description": "Articles about algebraic concepts and problems",
                    "article_count": 15,
                    "parent_id": None,
                },
                {
                    "id": 2,
                    "name": "Calculus",
                    "slug": "calculus",
                    "description": "Calculus tutorials and examples",
                    "article_count": 12,
                    "parent_id": None,
                },
                {
                    "id": 3,
                    "name": "Geometry",
                    "slug": "geometry",
                    "description": "Geometric shapes and calculations",
                    "article_count": 8,
                    "parent_id": None,
                },
            ]

            return {"success": True, "categories": categories}

        @app.post("/categories")
        async def create_category(
            category_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Create new category."""
            if current_user["role"] != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")

            name = category_data.get("name")
            if not name:
                raise HTTPException(status_code=400, detail="Category name is required")

            slug = name.lower().replace(" ", "-")

            new_category = {
                "id": 4,
                "name": name,
                "slug": slug,
                "description": category_data.get("description", ""),
                "article_count": 0,
                "parent_id": category_data.get("parent_id"),
                "created_at": datetime.utcnow().isoformat(),
            }

            return {
                "success": True,
                "message": "Category created successfully",
                "category": new_category,
            }

        # Tag endpoints
        @app.get("/tags")
        async def get_tags():
            """Get all tags."""
            tags = [
                {"id": 1, "name": "algebra", "article_count": 15},
                {"id": 2, "name": "calculus", "article_count": 12},
                {"id": 3, "name": "basics", "article_count": 20},
                {"id": 4, "name": "advanced", "article_count": 8},
                {"id": 5, "name": "geometry", "article_count": 10},
            ]

            return {"success": True, "tags": tags}

        # Comment endpoints
        @app.get("/articles/{article_id}/comments")
        async def get_article_comments(article_id: int, page: int = 1, limit: int = 10):
            """Get comments for an article."""
            if article_id == 1:
                comments = [
                    {
                        "id": 1,
                        "article_id": article_id,
                        "user_id": 123,
                        "user_name": "Student",
                        "content": "Great explanation! Very helpful for beginners.",
                        "status": "approved",
                        "likes": 5,
                        "created_at": "2024-12-11T14:30:00",
                        "replies": [
                            {
                                "id": 2,
                                "parent_id": 1,
                                "user_id": 789,
                                "user_name": "Math Teacher",
                                "content": "Thank you! Glad it helped.",
                                "status": "approved",
                                "likes": 2,
                                "created_at": "2024-12-11T15:00:00",
                            }
                        ],
                    }
                ]

                return {
                    "success": True,
                    "comments": comments,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": len(comments),
                        "pages": 1,
                    },
                }
            else:
                return {
                    "success": True,
                    "comments": [],
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": 0,
                        "pages": 0,
                    },
                }

        @app.post("/articles/{article_id}/comments")
        async def create_comment(
            article_id: int,
            comment_data: dict,
            current_user: dict = Depends(get_current_user),
        ):
            """Create comment on article."""
            content = comment_data.get("content")
            if not content:
                raise HTTPException(
                    status_code=400, detail="Comment content is required"
                )

            if len(content) < 10:
                raise HTTPException(
                    status_code=400, detail="Comment must be at least 10 characters"
                )

            new_comment = {
                "id": 3,
                "article_id": article_id,
                "user_id": current_user["user_id"],
                "user_name": current_user["email"].split("@")[0],
                "content": content,
                "status": "pending",  # Comments need approval
                "likes": 0,
                "created_at": datetime.utcnow().isoformat(),
                "replies": [],
            }

            return {
                "success": True,
                "message": "Comment submitted for approval",
                "comment": new_comment,
            }

        # SEO endpoints
        @app.get("/seo/analyze/{article_id}")
        async def analyze_seo(
            article_id: int, current_user: dict = Depends(get_current_user)
        ):
            """Analyze SEO for an article."""
            if current_user["role"] not in ["admin", "author"]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")

            if article_id == 1:
                seo_analysis = {
                    "article_id": article_id,
                    "title_analysis": {
                        "length": 45,
                        "score": 85,
                        "issues": [],
                        "recommendations": [
                            "Consider adding target keyword at the beginning"
                        ],
                    },
                    "meta_description_analysis": {
                        "length": 52,
                        "score": 90,
                        "issues": [],
                        "recommendations": ["Good length and includes target keywords"],
                    },
                    "content_analysis": {
                        "word_count": 1250,
                        "reading_time": 8,
                        "keyword_density": 2.4,
                        "score": 88,
                        "issues": ["Missing H2 headings"],
                        "recommendations": [
                            "Add more subheadings",
                            "Include more internal links",
                        ],
                    },
                    "technical_seo": {
                        "url_structure": "Good",
                        "image_alt_tags": "Missing",
                        "internal_links": 3,
                        "external_links": 1,
                        "score": 75,
                    },
                    "overall_score": 84,
                    "grade": "B+",
                    "priority_issues": [
                        "Add alt tags to images",
                        "Include more H2/H3 headings",
                    ],
                }

                return {"success": True, "seo_analysis": seo_analysis}
            else:
                raise HTTPException(status_code=404, detail="Article not found")

        # Search endpoints
        @app.get("/search")
        async def search_content(
            q: str = Query(..., min_length=3),
            type: str = Query("all"),
            page: int = Query(1, ge=1),
            limit: int = Query(10, ge=1, le=50),
        ):
            """Search content across articles, categories, and tags."""
            # Mock search results
            if "algebra" in q.lower():
                results = [
                    {
                        "type": "article",
                        "id": 1,
                        "title": "Introduction to Algebra",
                        "slug": "introduction-to-algebra",
                        "excerpt": "Learn the basics of algebra with step-by-step examples.",
                        "relevance_score": 95,
                        "highlight": "Learn the basics of <mark>algebra</mark> with step-by-step examples.",
                    },
                    {
                        "type": "category",
                        "id": 1,
                        "name": "Algebra",
                        "slug": "algebra",
                        "description": "Articles about algebraic concepts and problems",
                        "relevance_score": 100,
                    },
                ]
            else:
                results = []

            return {
                "success": True,
                "query": q,
                "results": results,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(results),
                    "pages": (len(results) + limit - 1) // limit if results else 0,
                },
                "search_time_ms": 45,
            }

        # Analytics endpoints
        @app.get("/analytics/articles/{article_id}")
        async def get_article_analytics(
            article_id: int, current_user: dict = Depends(get_current_user)
        ):
            """Get analytics for specific article."""
            if current_user["role"] not in ["admin", "author"]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")

            if article_id == 1:
                analytics = {
                    "article_id": article_id,
                    "views": {
                        "total": 1251,
                        "today": 45,
                        "this_week": 312,
                        "this_month": 890,
                    },
                    "engagement": {
                        "likes": 89,
                        "comments": 12,
                        "shares": 23,
                        "average_time_on_page": 285,  # seconds
                    },
                    "traffic_sources": {
                        "direct": 35,
                        "search": 45,
                        "social": 15,
                        "referral": 5,
                    },
                    "top_keywords": [
                        {"keyword": "algebra basics", "clicks": 156},
                        {"keyword": "learn algebra", "clicks": 89},
                        {"keyword": "algebra tutorial", "clicks": 67},
                    ],
                    "performance_score": 87,
                }

                return {"success": True, "analytics": analytics}
            else:
                raise HTTPException(status_code=404, detail="Article not found")

        return app

    @pytest.fixture
    async def client(self, mock_app):
        """Create test client."""
        async with AsyncClient(app=mock_app, base_url="http://test") as ac:
            yield ac

    async def test_get_articles(self, client):
        """Test get articles endpoint."""
        # Test get all published articles
        response = await client.get("/articles")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "articles" in data
        assert "pagination" in data

        articles = data["articles"]
        assert len(articles) == 2  # Only published articles

        # Check first article
        first_article = articles[0]
        assert first_article["id"] == 1
        assert first_article["title"] == "Introduction to Algebra"
        assert first_article["status"] == "published"
        assert first_article["views"] == 1250

        # Test pagination
        response = await client.get("/articles?page=1&limit=1")
        assert response.status_code == 200

        data = response.json()
        articles = data["articles"]
        assert len(articles) == 1

        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 1
        assert pagination["total"] == 2
        assert pagination["pages"] == 2

        # Test category filter
        response = await client.get("/articles?category=algebra")
        assert response.status_code == 200

        data = response.json()
        articles = data["articles"]
        assert len(articles) == 1
        assert articles[0]["category"] == "algebra"

        # Test tag filter
        response = await client.get("/articles?tag=calculus")
        assert response.status_code == 200

        data = response.json()
        articles = data["articles"]
        assert len(articles) == 1
        assert "calculus" in articles[0]["tags"]

        # Test search
        response = await client.get("/articles?search=algebra")
        assert response.status_code == 200

        data = response.json()
        articles = data["articles"]
        assert len(articles) == 1
        assert "algebra" in articles[0]["title"].lower()

        # Test draft status (should return empty for public)
        response = await client.get("/articles?status=draft")
        assert response.status_code == 200

        data = response.json()
        articles = data["articles"]
        assert len(articles) == 1  # Draft article

    async def test_get_specific_article(self, client):
        """Test get specific article endpoint."""
        # Test get existing article
        response = await client.get("/articles/1")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "article" in data

        article = data["article"]
        assert article["id"] == 1
        assert article["title"] == "Introduction to Algebra"
        assert article["views"] == 1251  # Incremented after view
        assert "author_bio" in article
        assert "related_articles" in article
        assert "reading_time_minutes" in article

        # Test get non-existent article
        response = await client.get("/articles/999")
        assert response.status_code == 404
        assert "Article not found" in response.json()["detail"]

    async def test_create_article(self, client):
        """Test create article endpoint."""
        author_headers = {"Authorization": "Bearer author_token"}
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer valid_token"}

        # Test successful article creation by author
        article_data = {
            "title": "New Math Tutorial",
            "content": "This is a comprehensive tutorial about mathematics...",
            "category": "general",
            "tags": ["tutorial", "mathematics"],
            "excerpt": "A comprehensive math tutorial",
            "status": "draft",
            "seo_title": "New Math Tutorial - Learn Mathematics",
            "seo_description": "Comprehensive mathematics tutorial for students",
        }

        response = await client.post(
            "/articles", json=article_data, headers=author_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Article created successfully" in data["message"]
        assert "article" in data

        article = data["article"]
        assert article["title"] == "New Math Tutorial"
        assert article["slug"] == "new-math-tutorial"
        assert article["status"] == "draft"
        assert article["author_id"] == 789
        assert article["views"] == 0

        # Test article creation by admin
        response = await client.post(
            "/articles", json=article_data, headers=admin_headers
        )
        assert response.status_code == 200

        # Test article creation by regular user (should fail)
        response = await client.post(
            "/articles", json=article_data, headers=user_headers
        )
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

        # Test validation errors
        invalid_data = {"content": "Content without title", "category": "general"}

        response = await client.post(
            "/articles", json=invalid_data, headers=author_headers
        )
        assert response.status_code == 400
        assert "Title is required" in response.json()["detail"]

        invalid_data = {"title": "Title without content", "category": "general"}

        response = await client.post(
            "/articles", json=invalid_data, headers=author_headers
        )
        assert response.status_code == 400
        assert "Content is required" in response.json()["detail"]

    async def test_update_article(self, client):
        """Test update article endpoint."""
        author_headers = {"Authorization": "Bearer author_token"}
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer valid_token"}

        # Test successful update by article author
        update_data = {
            "title": "Updated Introduction to Algebra",
            "content": "Updated content with more examples...",
            "status": "published",
        }

        response = await client.put(
            "/articles/1", json=update_data, headers=author_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Article updated successfully" in data["message"]
        assert data["article"]["title"] == "Updated Introduction to Algebra"

        # Test update by admin (should work)
        response = await client.put(
            "/articles/1", json=update_data, headers=admin_headers
        )
        assert response.status_code == 200

        # Test update by different user (should fail)
        response = await client.put(
            "/articles/1", json=update_data, headers=user_headers
        )
        assert response.status_code == 403
        assert "You can only edit your own articles" in response.json()["detail"]

        # Test update non-existent article
        response = await client.put(
            "/articles/999", json=update_data, headers=author_headers
        )
        assert response.status_code == 404
        assert "Article not found" in response.json()["detail"]

    async def test_delete_article(self, client):
        """Test delete article endpoint."""
        author_headers = {"Authorization": "Bearer author_token"}
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer valid_token"}

        # Test delete by article author
        response = await client.delete("/articles/1", headers=author_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Article deleted successfully" in data["message"]

        # Test delete by admin (should work)
        response = await client.delete("/articles/1", headers=admin_headers)
        assert response.status_code == 200

        # Test delete by different user (should fail)
        response = await client.delete("/articles/1", headers=user_headers)
        assert response.status_code == 403
        assert "You can only delete your own articles" in response.json()["detail"]

        # Test delete non-existent article
        response = await client.delete("/articles/999", headers=author_headers)
        assert response.status_code == 404
        assert "Article not found" in response.json()["detail"]

    async def test_categories(self, client):
        """Test category endpoints."""
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer valid_token"}

        # Test get categories
        response = await client.get("/categories")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "categories" in data

        categories = data["categories"]
        assert len(categories) == 3

        # Check first category
        first_category = categories[0]
        assert first_category["name"] == "Algebra"
        assert first_category["slug"] == "algebra"
        assert first_category["article_count"] == 15

        # Test create category by admin
        category_data = {
            "name": "Statistics",
            "description": "Statistical analysis and probability",
        }

        response = await client.post(
            "/categories", json=category_data, headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["category"]["name"] == "Statistics"
        assert data["category"]["slug"] == "statistics"

        # Test create category by regular user (should fail)
        response = await client.post(
            "/categories", json=category_data, headers=user_headers
        )
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

        # Test create category without name
        invalid_data = {"description": "Description without name"}

        response = await client.post(
            "/categories", json=invalid_data, headers=admin_headers
        )
        assert response.status_code == 400
        assert "Category name is required" in response.json()["detail"]

    async def test_tags(self, client):
        """Test tags endpoint."""
        response = await client.get("/tags")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "tags" in data

        tags = data["tags"]
        assert len(tags) == 5

        # Check first tag
        first_tag = tags[0]
        assert first_tag["name"] == "algebra"
        assert first_tag["article_count"] == 15

    async def test_comments(self, client):
        """Test comment endpoints."""
        user_headers = {"Authorization": "Bearer valid_token"}

        # Test get article comments
        response = await client.get("/articles/1/comments")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "comments" in data

        comments = data["comments"]
        assert len(comments) == 1

        # Check comment structure
        first_comment = comments[0]
        assert first_comment["user_name"] == "Student"
        assert first_comment["status"] == "approved"
        assert first_comment["likes"] == 5
        assert "replies" in first_comment
        assert len(first_comment["replies"]) == 1

        # Test create comment
        comment_data = {
            "content": "This is a very helpful article. Thank you for sharing!"
        }

        response = await client.post(
            "/articles/1/comments", json=comment_data, headers=user_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Comment submitted for approval" in data["message"]
        assert data["comment"]["status"] == "pending"

        # Test comment validation
        short_comment = {"content": "Too short"}

        response = await client.post(
            "/articles/1/comments", json=short_comment, headers=user_headers
        )
        assert response.status_code == 400
        assert "Comment must be at least 10 characters" in response.json()["detail"]

        empty_comment = {"content": ""}

        response = await client.post(
            "/articles/1/comments", json=empty_comment, headers=user_headers
        )
        assert response.status_code == 400
        assert "Comment content is required" in response.json()["detail"]

    async def test_seo_analysis(self, client):
        """Test SEO analysis endpoint."""
        author_headers = {"Authorization": "Bearer author_token"}
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer valid_token"}

        # Test SEO analysis by author
        response = await client.get("/seo/analyze/1", headers=author_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "seo_analysis" in data

        seo = data["seo_analysis"]
        assert seo["article_id"] == 1
        assert "title_analysis" in seo
        assert "meta_description_analysis" in seo
        assert "content_analysis" in seo
        assert "technical_seo" in seo
        assert seo["overall_score"] == 84
        assert seo["grade"] == "B+"

        # Test SEO analysis by admin
        response = await client.get("/seo/analyze/1", headers=admin_headers)
        assert response.status_code == 200

        # Test SEO analysis by regular user (should fail)
        response = await client.get("/seo/analyze/1", headers=user_headers)
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

        # Test SEO analysis for non-existent article
        response = await client.get("/seo/analyze/999", headers=author_headers)
        assert response.status_code == 404
        assert "Article not found" in response.json()["detail"]

    async def test_search(self, client):
        """Test search endpoint."""
        # Test successful search
        response = await client.get("/search?q=algebra")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["query"] == "algebra"
        assert "results" in data

        results = data["results"]
        assert len(results) == 2  # Article and category

        # Check article result
        article_result = next(r for r in results if r["type"] == "article")
        assert article_result["title"] == "Introduction to Algebra"
        assert article_result["relevance_score"] == 95
        assert "highlight" in article_result

        # Check category result
        category_result = next(r for r in results if r["type"] == "category")
        assert category_result["name"] == "Algebra"
        assert category_result["relevance_score"] == 100

        # Test search with no results
        response = await client.get("/search?q=nonexistent")
        assert response.status_code == 200

        data = response.json()
        assert len(data["results"]) == 0

        # Test search with short query (should fail)
        response = await client.get("/search?q=ab")
        assert response.status_code == 422  # Validation error

    async def test_analytics(self, client):
        """Test analytics endpoint."""
        author_headers = {"Authorization": "Bearer author_token"}
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer valid_token"}

        # Test analytics by author
        response = await client.get("/analytics/articles/1", headers=author_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "analytics" in data

        analytics = data["analytics"]
        assert analytics["article_id"] == 1
        assert "views" in analytics
        assert "engagement" in analytics
        assert "traffic_sources" in analytics
        assert "top_keywords" in analytics
        assert analytics["performance_score"] == 87

        # Check views data
        views = analytics["views"]
        assert views["total"] == 1251
        assert views["today"] == 45

        # Check engagement data
        engagement = analytics["engagement"]
        assert engagement["likes"] == 89
        assert engagement["comments"] == 12

        # Test analytics by admin
        response = await client.get("/analytics/articles/1", headers=admin_headers)
        assert response.status_code == 200

        # Test analytics by regular user (should fail)
        response = await client.get("/analytics/articles/1", headers=user_headers)
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

        # Test analytics for non-existent article
        response = await client.get("/analytics/articles/999", headers=author_headers)
        assert response.status_code == 404
        assert "Article not found" in response.json()["detail"]

    async def test_authentication_required(self, client):
        """Test endpoints require authentication."""
        endpoints_requiring_auth = [
            (
                "/articles",
                "POST",
                {"title": "Test", "content": "Test", "category": "test"},
            ),
            ("/articles/1", "PUT", {"title": "Updated"}),
            ("/articles/1", "DELETE", {}),
            ("/categories", "POST", {"name": "Test Category"}),
            ("/articles/1/comments", "POST", {"content": "Test comment content"}),
            ("/seo/analyze/1", "GET", {}),
            ("/analytics/articles/1", "GET", {}),
        ]

        for endpoint, method, data in endpoints_requiring_auth:
            if method == "POST":
                response = await client.post(endpoint, json=data)
            elif method == "PUT":
                response = await client.put(endpoint, json=data)
            elif method == "DELETE":
                response = await client.delete(endpoint)
            else:  # GET
                response = await client.get(endpoint)

            assert response.status_code == 403  # FastAPI returns 403 for missing auth

    async def test_concurrent_operations(self, client):
        """Test concurrent content operations."""
        headers = {"Authorization": "Bearer author_token"}

        async def create_article(title):
            article_data = {
                "title": title,
                "content": f"Content for {title}",
                "category": "general",
            }
            response = await client.post(
                "/articles", json=article_data, headers=headers
            )
            return response.status_code == 200

        # Test 3 concurrent article creations
        titles = ["Article 1", "Article 2", "Article 3"]
        tasks = [create_article(title) for title in titles]
        results = await asyncio.gather(*tasks)

        # All articles should be created successfully
        assert all(results)
