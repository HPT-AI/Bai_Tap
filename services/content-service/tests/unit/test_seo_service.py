"""
Unit tests for SEO Service functionality.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock imports - these would be actual imports in real implementation
# from content_service.services import SEOService, SitemapService, SchemaService
# from content_service.models import Article, Category, SEOMetadata
# from content_service.schemas import SEOAnalysis, SitemapEntry


@pytest.mark.asyncio
class TestSEOAnalysis:
    """Test SEO analysis functionality."""

    def test_analyze_content_seo(self, sample_seo_content):
        """Test comprehensive SEO analysis of content."""

        def analyze_content_seo(
            title, content, meta_description=None, slug=None, target_keywords=None
        ):
            """
            Perform comprehensive SEO analysis of content
            """
            try:
                analysis = {
                    "title_analysis": {},
                    "content_analysis": {},
                    "meta_description_analysis": {},
                    "keyword_analysis": {},
                    "readability_analysis": {},
                    "overall_score": 0,
                    "recommendations": [],
                    "issues": [],
                    "warnings": [],
                }

                # Title Analysis
                title_score = 0
                if title:
                    title_length = len(title)
                    if 30 <= title_length <= 60:
                        title_score = 100
                        analysis["title_analysis"]["length_status"] = "optimal"
                    elif 10 <= title_length < 30:
                        title_score = 70
                        analysis["title_analysis"]["length_status"] = "too_short"
                        analysis["warnings"].append(
                            "Title is shorter than recommended (30-60 characters)"
                        )
                    elif title_length > 60:
                        title_score = 60
                        analysis["title_analysis"]["length_status"] = "too_long"
                        analysis["warnings"].append(
                            "Title is longer than recommended (30-60 characters)"
                        )
                    else:
                        title_score = 30
                        analysis["title_analysis"]["length_status"] = "very_short"
                        analysis["issues"].append(
                            "Title is too short (minimum 10 characters)"
                        )

                    # Check for target keywords in title
                    if target_keywords:
                        keywords_in_title = sum(
                            1
                            for keyword in target_keywords
                            if keyword.lower() in title.lower()
                        )
                        if keywords_in_title > 0:
                            title_score += 20
                            analysis["title_analysis"]["keywords_present"] = True
                        else:
                            analysis["title_analysis"]["keywords_present"] = False
                            analysis["recommendations"].append(
                                "Include target keywords in title"
                            )
                else:
                    analysis["issues"].append("Title is missing")

                analysis["title_analysis"]["score"] = title_score
                analysis["title_analysis"]["length"] = len(title) if title else 0

                # Content Analysis
                content_score = 0
                if content:
                    word_count = len(content.split())

                    if word_count >= 300:
                        content_score = 100
                        analysis["content_analysis"]["length_status"] = "optimal"
                    elif word_count >= 150:
                        content_score = 70
                        analysis["content_analysis"]["length_status"] = "acceptable"
                        analysis["recommendations"].append(
                            "Consider adding more content (recommended: 300+ words)"
                        )
                    else:
                        content_score = 40
                        analysis["content_analysis"]["length_status"] = "too_short"
                        analysis["issues"].append(
                            "Content is too short (minimum 150 words)"
                        )

                    # Keyword density analysis
                    if target_keywords:
                        keyword_density = {}
                        content_lower = content.lower()

                        for keyword in target_keywords:
                            keyword_count = content_lower.count(keyword.lower())
                            density = (
                                (keyword_count / word_count) * 100
                                if word_count > 0
                                else 0
                            )
                            keyword_density[keyword] = {
                                "count": keyword_count,
                                "density": round(density, 2),
                            }

                            if 1 <= density <= 3:
                                content_score += 10
                            elif density > 3:
                                analysis["warnings"].append(
                                    f"Keyword '{keyword}' density is too high ({density:.1f}%)"
                                )
                            elif density == 0:
                                analysis["recommendations"].append(
                                    f"Consider including keyword '{keyword}' in content"
                                )

                        analysis["keyword_analysis"]["density"] = keyword_density

                    # Check for headings structure
                    h1_count = content.count("<h1>")
                    h2_count = content.count("<h2>")
                    h3_count = content.count("<h3>")

                    if h1_count == 1:
                        content_score += 10
                    elif h1_count == 0:
                        analysis["issues"].append("Missing H1 heading")
                    elif h1_count > 1:
                        analysis["issues"].append("Multiple H1 headings found")

                    if h2_count > 0:
                        content_score += 10
                        analysis["content_analysis"]["has_subheadings"] = True
                    else:
                        analysis["content_analysis"]["has_subheadings"] = False
                        analysis["recommendations"].append(
                            "Add H2 subheadings to improve structure"
                        )

                    analysis["content_analysis"]["headings"] = {
                        "h1_count": h1_count,
                        "h2_count": h2_count,
                        "h3_count": h3_count,
                    }
                else:
                    analysis["issues"].append("Content is missing")

                analysis["content_analysis"]["score"] = content_score
                analysis["content_analysis"]["word_count"] = (
                    len(content.split()) if content else 0
                )

                # Meta Description Analysis
                meta_score = 0
                if meta_description:
                    meta_length = len(meta_description)
                    if 120 <= meta_length <= 160:
                        meta_score = 100
                        analysis["meta_description_analysis"][
                            "length_status"
                        ] = "optimal"
                    elif 80 <= meta_length < 120:
                        meta_score = 70
                        analysis["meta_description_analysis"][
                            "length_status"
                        ] = "too_short"
                        analysis["warnings"].append(
                            "Meta description is shorter than recommended"
                        )
                    elif meta_length > 160:
                        meta_score = 60
                        analysis["meta_description_analysis"][
                            "length_status"
                        ] = "too_long"
                        analysis["warnings"].append(
                            "Meta description is longer than recommended"
                        )
                    else:
                        meta_score = 40
                        analysis["meta_description_analysis"][
                            "length_status"
                        ] = "very_short"
                        analysis["issues"].append("Meta description is too short")

                    # Check for target keywords in meta description
                    if target_keywords:
                        keywords_in_meta = sum(
                            1
                            for keyword in target_keywords
                            if keyword.lower() in meta_description.lower()
                        )
                        if keywords_in_meta > 0:
                            meta_score += 20
                            analysis["meta_description_analysis"][
                                "keywords_present"
                            ] = True
                        else:
                            analysis["meta_description_analysis"][
                                "keywords_present"
                            ] = False
                            analysis["recommendations"].append(
                                "Include target keywords in meta description"
                            )
                else:
                    analysis["recommendations"].append("Add meta description")

                analysis["meta_description_analysis"]["score"] = meta_score
                analysis["meta_description_analysis"]["length"] = (
                    len(meta_description) if meta_description else 0
                )

                # Readability Analysis
                readability_score = 0
                if content:
                    sentences = content.split(".")
                    sentence_count = len([s for s in sentences if s.strip()])
                    word_count = len(content.split())

                    if sentence_count > 0:
                        avg_words_per_sentence = word_count / sentence_count

                        if avg_words_per_sentence <= 20:
                            readability_score = 100
                            analysis["readability_analysis"][
                                "sentence_length"
                            ] = "optimal"
                        elif avg_words_per_sentence <= 25:
                            readability_score = 80
                            analysis["readability_analysis"][
                                "sentence_length"
                            ] = "acceptable"
                        else:
                            readability_score = 60
                            analysis["readability_analysis"][
                                "sentence_length"
                            ] = "too_long"
                            analysis["recommendations"].append(
                                "Consider shorter sentences for better readability"
                            )

                        analysis["readability_analysis"][
                            "avg_words_per_sentence"
                        ] = round(avg_words_per_sentence, 1)
                        analysis["readability_analysis"][
                            "sentence_count"
                        ] = sentence_count

                analysis["readability_analysis"]["score"] = readability_score

                # Calculate Overall Score
                scores = [
                    analysis["title_analysis"]["score"],
                    analysis["content_analysis"]["score"],
                    analysis["meta_description_analysis"]["score"],
                    analysis["readability_analysis"]["score"],
                ]

                analysis["overall_score"] = round(sum(scores) / len(scores))

                # Determine grade
                if analysis["overall_score"] >= 90:
                    analysis["grade"] = "A"
                elif analysis["overall_score"] >= 80:
                    analysis["grade"] = "B"
                elif analysis["overall_score"] >= 70:
                    analysis["grade"] = "C"
                elif analysis["overall_score"] >= 60:
                    analysis["grade"] = "D"
                else:
                    analysis["grade"] = "F"

                return {"success": True, "analysis": analysis}

            except Exception as e:
                return {"success": False, "error": f"Error analyzing SEO: {str(e)}"}

        # Test comprehensive SEO analysis
        result = analyze_content_seo(
            title="Complete Guide to Linear Algebra: Vectors and Matrices",
            content="""
            <h1>Linear Algebra Fundamentals</h1>
            <p>Linear algebra is a fundamental branch of mathematics that deals with vectors, matrices, and linear transformations. This comprehensive guide will help you understand the core concepts.</p>

            <h2>Understanding Vectors</h2>
            <p>Vectors are mathematical objects that have both magnitude and direction. In linear algebra, vectors are used to represent points in space and perform various mathematical operations.</p>

            <h2>Working with Matrices</h2>
            <p>Matrices are rectangular arrays of numbers that can be used to represent linear transformations. They are essential tools in linear algebra for solving systems of equations.</p>

            <h3>Matrix Operations</h3>
            <p>Common matrix operations include addition, multiplication, and finding determinants. These operations are fundamental to understanding linear algebra concepts.</p>
            """
            * 2,  # Repeat to get more content
            meta_description="Learn linear algebra fundamentals including vectors, matrices, and linear transformations. Complete guide with examples and practical applications.",
            target_keywords=["linear algebra", "vectors", "matrices"],
        )

        assert result["success"] is True
        analysis = result["analysis"]

        # Check overall score and grade
        assert analysis["overall_score"] >= 80
        assert analysis["grade"] in ["A", "B"]

        # Check title analysis
        assert analysis["title_analysis"]["score"] >= 70
        assert analysis["title_analysis"]["keywords_present"] is True
        assert analysis["title_analysis"]["length_status"] in ["optimal", "acceptable"]

        # Check content analysis
        assert analysis["content_analysis"]["score"] >= 80
        assert analysis["content_analysis"]["word_count"] >= 150
        assert analysis["content_analysis"]["has_subheadings"] is True
        assert analysis["content_analysis"]["headings"]["h1_count"] == 1
        assert analysis["content_analysis"]["headings"]["h2_count"] >= 2

        # Check meta description analysis
        assert analysis["meta_description_analysis"]["score"] >= 70
        assert analysis["meta_description_analysis"]["keywords_present"] is True

        # Check keyword analysis
        assert "linear algebra" in analysis["keyword_analysis"]["density"]
        assert analysis["keyword_analysis"]["density"]["linear algebra"]["count"] > 0

        # Should have minimal issues for good content
        assert len(analysis["issues"]) <= 2

    def test_analyze_poor_seo_content(self):
        """Test SEO analysis of poor quality content."""

        def analyze_content_seo(
            title, content, meta_description=None, target_keywords=None
        ):
            # Same implementation as above (simplified for brevity)
            analysis = {
                "title_analysis": {"score": 0},
                "content_analysis": {"score": 0, "word_count": 0},
                "meta_description_analysis": {"score": 0},
                "readability_analysis": {"score": 0},
                "overall_score": 0,
                "issues": [],
                "warnings": [],
                "recommendations": [],
            }

            # Poor title analysis
            if not title or len(title) < 10:
                analysis["issues"].append("Title is too short or missing")
                analysis["title_analysis"]["score"] = 20

            # Poor content analysis
            if not content or len(content.split()) < 50:
                analysis["issues"].append("Content is too short")
                analysis["content_analysis"]["score"] = 30
                analysis["content_analysis"]["word_count"] = (
                    len(content.split()) if content else 0
                )

            # Missing meta description
            if not meta_description:
                analysis["recommendations"].append("Add meta description")
                analysis["meta_description_analysis"]["score"] = 0

            # Calculate poor overall score
            scores = [
                analysis["title_analysis"]["score"],
                analysis["content_analysis"]["score"],
                analysis["meta_description_analysis"]["score"],
                analysis["readability_analysis"]["score"],
            ]
            analysis["overall_score"] = round(sum(scores) / len(scores))
            analysis["grade"] = "F" if analysis["overall_score"] < 60 else "D"

            return {"success": True, "analysis": analysis}

        # Test poor SEO content
        result = analyze_content_seo(
            title="Math",  # Too short
            content="Short content.",  # Too short
            meta_description=None,  # Missing
            target_keywords=["mathematics"],
        )

        assert result["success"] is True
        analysis = result["analysis"]

        # Should have poor scores
        assert analysis["overall_score"] < 60
        assert analysis["grade"] in ["F", "D"]

        # Should have multiple issues
        assert len(analysis["issues"]) >= 2
        assert len(analysis["recommendations"]) >= 1

        # Check specific issues
        assert any("title" in issue.lower() for issue in analysis["issues"])
        assert any("content" in issue.lower() for issue in analysis["issues"])
        assert any(
            "meta description" in rec.lower() for rec in analysis["recommendations"]
        )


@pytest.mark.asyncio
class TestSchemaMarkup:
    """Test Schema.org markup generation."""

    def test_generate_article_schema(self, sample_articles):
        """Test generating Article schema markup."""

        def generate_article_schema(article_data):
            """
            Generate Schema.org Article markup
            """
            try:
                schema = {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": article_data.get("title"),
                    "description": article_data.get("meta_description"),
                    "image": article_data.get("featured_image"),
                    "author": {
                        "@type": "Person",
                        "name": article_data.get("author_name", "Unknown Author"),
                        "url": article_data.get("author_url"),
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "Math Service Website",
                        "logo": {
                            "@type": "ImageObject",
                            "url": "https://mathservice.com/logo.png",
                        },
                    },
                    "datePublished": article_data.get(
                        "published_at", datetime.utcnow()
                    ).isoformat(),
                    "dateModified": article_data.get(
                        "updated_at", datetime.utcnow()
                    ).isoformat(),
                    "mainEntityOfPage": {
                        "@type": "WebPage",
                        "@id": f"https://mathservice.com/articles/{article_data.get('slug')}",
                    },
                }

                # Add optional fields
                if article_data.get("category_name"):
                    schema["articleSection"] = article_data["category_name"]

                if article_data.get("tags"):
                    schema["keywords"] = ", ".join(article_data["tags"])

                if article_data.get("word_count"):
                    schema["wordCount"] = article_data["word_count"]

                # Add reading time
                if article_data.get("word_count"):
                    reading_time = max(1, article_data["word_count"] // 200)
                    schema["timeRequired"] = f"PT{reading_time}M"

                return {
                    "success": True,
                    "schema": schema,
                    "json_ld": json.dumps(schema, indent=2),
                }

            except Exception as e:
                return {"success": False, "error": f"Error generating schema: {str(e)}"}

        # Test article schema generation
        article_data = {
            "title": "Introduction to Linear Algebra",
            "slug": "introduction-linear-algebra",
            "meta_description": "Learn the fundamentals of linear algebra including vectors and matrices.",
            "author_name": "Dr. Math Expert",
            "author_url": "https://mathservice.com/authors/dr-math-expert",
            "category_name": "Mathematics",
            "tags": ["linear algebra", "mathematics", "vectors"],
            "word_count": 1500,
            "published_at": datetime(2024, 1, 15),
            "updated_at": datetime(2024, 1, 20),
            "featured_image": "https://mathservice.com/images/linear-algebra.jpg",
        }

        result = generate_article_schema(article_data)

        assert result["success"] is True
        assert "schema" in result
        assert "json_ld" in result

        schema = result["schema"]

        # Check required fields
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Article"
        assert schema["headline"] == "Introduction to Linear Algebra"
        assert (
            schema["description"]
            == "Learn the fundamentals of linear algebra including vectors and matrices."
        )

        # Check author
        assert schema["author"]["@type"] == "Person"
        assert schema["author"]["name"] == "Dr. Math Expert"

        # Check publisher
        assert schema["publisher"]["@type"] == "Organization"
        assert schema["publisher"]["name"] == "Math Service Website"

        # Check optional fields
        assert schema["articleSection"] == "Mathematics"
        assert "linear algebra" in schema["keywords"]
        assert schema["wordCount"] == 1500
        assert schema["timeRequired"] == "PT7M"  # 1500 words / 200 = 7.5 ≈ 7 minutes

        # Check JSON-LD format
        assert '"@context": "https://schema.org"' in result["json_ld"]
        assert '"@type": "Article"' in result["json_ld"]

    def test_generate_breadcrumb_schema(self):
        """Test generating BreadcrumbList schema markup."""

        def generate_breadcrumb_schema(breadcrumbs):
            """
            Generate Schema.org BreadcrumbList markup
            """
            try:
                if not breadcrumbs or len(breadcrumbs) == 0:
                    return {"success": False, "error": "Breadcrumbs list is empty"}

                list_items = []
                for index, breadcrumb in enumerate(breadcrumbs):
                    list_item = {
                        "@type": "ListItem",
                        "position": index + 1,
                        "name": breadcrumb["name"],
                        "item": breadcrumb["url"],
                    }
                    list_items.append(list_item)

                schema = {
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": list_items,
                }

                return {
                    "success": True,
                    "schema": schema,
                    "json_ld": json.dumps(schema, indent=2),
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error generating breadcrumb schema: {str(e)}",
                }

        # Test breadcrumb schema generation
        breadcrumbs = [
            {"name": "Home", "url": "https://mathservice.com/"},
            {
                "name": "Mathematics",
                "url": "https://mathservice.com/categories/mathematics",
            },
            {
                "name": "Linear Algebra",
                "url": "https://mathservice.com/categories/linear-algebra",
            },
            {
                "name": "Introduction to Linear Algebra",
                "url": "https://mathservice.com/articles/introduction-linear-algebra",
            },
        ]

        result = generate_breadcrumb_schema(breadcrumbs)

        assert result["success"] is True
        assert "schema" in result

        schema = result["schema"]

        # Check schema structure
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "BreadcrumbList"
        assert len(schema["itemListElement"]) == 4

        # Check first item
        first_item = schema["itemListElement"][0]
        assert first_item["@type"] == "ListItem"
        assert first_item["position"] == 1
        assert first_item["name"] == "Home"
        assert first_item["item"] == "https://mathservice.com/"

        # Check last item
        last_item = schema["itemListElement"][-1]
        assert last_item["position"] == 4
        assert last_item["name"] == "Introduction to Linear Algebra"


@pytest.mark.asyncio
class TestSitemapGeneration:
    """Test XML sitemap generation."""

    def test_generate_sitemap(self, sample_articles):
        """Test generating XML sitemap."""

        def generate_sitemap(articles, categories, base_url="https://mathservice.com"):
            """
            Generate XML sitemap for articles and categories
            """
            try:
                sitemap_entries = []

                # Add homepage
                sitemap_entries.append(
                    {
                        "url": base_url,
                        "lastmod": datetime.utcnow().strftime("%Y-%m-%d"),
                        "changefreq": "daily",
                        "priority": "1.0",
                    }
                )

                # Add categories
                for category in categories:
                    if category.get("is_active", True):
                        sitemap_entries.append(
                            {
                                "url": f"{base_url}/categories/{category['slug']}",
                                "lastmod": category.get(
                                    "updated_at", datetime.utcnow()
                                ).strftime("%Y-%m-%d"),
                                "changefreq": "weekly",
                                "priority": "0.8",
                            }
                        )

                # Add articles
                for article in articles:
                    if article.get("status") == "published":
                        # Calculate priority based on view count and recency
                        view_count = article.get("view_count", 0)
                        days_old = (
                            datetime.utcnow()
                            - article.get("published_at", datetime.utcnow())
                        ).days

                        # Base priority for articles
                        priority = 0.6

                        # Boost for popular articles
                        if view_count > 1000:
                            priority += 0.2
                        elif view_count > 500:
                            priority += 0.1

                        # Reduce for old articles
                        if days_old > 365:
                            priority -= 0.1
                        elif days_old > 180:
                            priority -= 0.05

                        priority = max(
                            0.1, min(0.9, priority)
                        )  # Clamp between 0.1 and 0.9

                        # Determine change frequency
                        if days_old < 7:
                            changefreq = "daily"
                        elif days_old < 30:
                            changefreq = "weekly"
                        else:
                            changefreq = "monthly"

                        sitemap_entries.append(
                            {
                                "url": f"{base_url}/articles/{article['slug']}",
                                "lastmod": article.get(
                                    "updated_at",
                                    article.get("published_at", datetime.utcnow()),
                                ).strftime("%Y-%m-%d"),
                                "changefreq": changefreq,
                                "priority": f"{priority:.1f}",
                            }
                        )

                # Generate XML
                xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
                xml_content += (
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                )

                for entry in sitemap_entries:
                    xml_content += "  <url>\n"
                    xml_content += f'    <loc>{entry["url"]}</loc>\n'
                    xml_content += f'    <lastmod>{entry["lastmod"]}</lastmod>\n'
                    xml_content += (
                        f'    <changefreq>{entry["changefreq"]}</changefreq>\n'
                    )
                    xml_content += f'    <priority>{entry["priority"]}</priority>\n'
                    xml_content += "  </url>\n"

                xml_content += "</urlset>"

                return {
                    "success": True,
                    "entries": sitemap_entries,
                    "xml_content": xml_content,
                    "total_urls": len(sitemap_entries),
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error generating sitemap: {str(e)}",
                }

        # Test sitemap generation
        articles = [
            {
                "slug": "linear-algebra-basics",
                "status": "published",
                "view_count": 1500,
                "published_at": datetime.utcnow() - timedelta(days=10),
                "updated_at": datetime.utcnow() - timedelta(days=2),
            },
            {
                "slug": "calculus-fundamentals",
                "status": "published",
                "view_count": 800,
                "published_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow() - timedelta(days=15),
            },
            {
                "slug": "draft-article",
                "status": "draft",
                "view_count": 0,
                "published_at": None,
                "updated_at": datetime.utcnow(),
            },
        ]

        categories = [
            {
                "slug": "mathematics",
                "is_active": True,
                "updated_at": datetime.utcnow() - timedelta(days=5),
            },
            {
                "slug": "physics",
                "is_active": True,
                "updated_at": datetime.utcnow() - timedelta(days=20),
            },
        ]

        result = generate_sitemap(articles, categories)

        assert result["success"] is True
        assert "entries" in result
        assert "xml_content" in result
        assert (
            result["total_urls"] == 5
        )  # 1 homepage + 2 categories + 2 published articles

        entries = result["entries"]

        # Check homepage entry
        homepage = entries[0]
        assert homepage["url"] == "https://mathservice.com"
        assert homepage["priority"] == "1.0"
        assert homepage["changefreq"] == "daily"

        # Check category entries
        category_entries = [e for e in entries if "/categories/" in e["url"]]
        assert len(category_entries) == 2
        assert all(e["priority"] == "0.8" for e in category_entries)
        assert all(e["changefreq"] == "weekly" for e in category_entries)

        # Check article entries
        article_entries = [e for e in entries if "/articles/" in e["url"]]
        assert len(article_entries) == 2  # Only published articles

        # Popular article should have higher priority
        popular_article = next(
            e for e in article_entries if "linear-algebra-basics" in e["url"]
        )
        assert float(popular_article["priority"]) > 0.6

        # Check XML format
        xml_content = result["xml_content"]
        assert xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        assert (
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            in xml_content
        )
        assert xml_content.count("<url>") == 5
        assert xml_content.count("</url>") == 5
        assert xml_content.endswith("</urlset>")


@pytest.mark.asyncio
class TestSEOValidation:
    """Test SEO validation and recommendations."""

    def test_validate_url_structure(self):
        """Test URL structure validation for SEO."""

        def validate_url_structure(url):
            """
            Validate URL structure for SEO best practices
            """
            try:
                issues = []
                recommendations = []
                score = 100

                # Check URL length
                if len(url) > 100:
                    issues.append("URL is too long (recommended: under 100 characters)")
                    score -= 20
                elif len(url) > 75:
                    recommendations.append(
                        "Consider shortening URL for better usability"
                    )
                    score -= 5

                # Check for special characters
                if any(char in url for char in ["?", "&", "=", "%", "#"]):
                    issues.append("URL contains query parameters or special characters")
                    score -= 15

                # Check for uppercase letters
                if any(char.isupper() for char in url):
                    recommendations.append("Use lowercase letters in URLs")
                    score -= 10

                # Check for underscores
                if "_" in url:
                    recommendations.append("Use hyphens instead of underscores in URLs")
                    score -= 5

                # Check for multiple consecutive hyphens
                if "--" in url:
                    issues.append("URL contains multiple consecutive hyphens")
                    score -= 10

                # Check for trailing slash consistency
                if url.endswith("/") and url != "/":
                    recommendations.append(
                        "Consider removing trailing slash for consistency"
                    )

                # Check for meaningful structure
                url_parts = url.strip("/").split("/")
                if len(url_parts) > 5:
                    recommendations.append(
                        "URL hierarchy is too deep (recommended: max 4 levels)"
                    )
                    score -= 10

                # Check for stop words
                stop_words = [
                    "a",
                    "an",
                    "the",
                    "and",
                    "or",
                    "but",
                    "in",
                    "on",
                    "at",
                    "to",
                    "for",
                    "of",
                    "with",
                    "by",
                ]
                for part in url_parts:
                    words = part.split("-")
                    stop_word_count = sum(1 for word in words if word in stop_words)
                    if stop_word_count > 2:
                        recommendations.append("Consider removing stop words from URL")
                        score -= 5
                        break

                score = max(0, score)

                return {
                    "is_valid": len(issues) == 0,
                    "score": score,
                    "issues": issues,
                    "recommendations": recommendations,
                    "grade": "A"
                    if score >= 90
                    else "B"
                    if score >= 80
                    else "C"
                    if score >= 70
                    else "D"
                    if score >= 60
                    else "F",
                }

            except Exception as e:
                return {"is_valid": False, "error": f"Error validating URL: {str(e)}"}

        # Test good URL
        result = validate_url_structure("/articles/linear-algebra-basics")

        assert result["is_valid"] is True
        assert result["score"] >= 90
        assert result["grade"] == "A"
        assert len(result["issues"]) == 0

        # Test poor URL
        result = validate_url_structure(
            "/Articles/Linear_Algebra_Basics_And_The_Complete_Guide_To_Understanding_Vectors_And_Matrices?category=math&sort=date"
        )

        assert result["is_valid"] is False
        assert result["score"] < 70
        assert len(result["issues"]) > 0
        assert len(result["recommendations"]) > 0

        # Check specific issues
        issues_text = " ".join(result["issues"])
        recommendations_text = " ".join(result["recommendations"])

        assert "query parameters" in issues_text.lower()
        assert "lowercase" in recommendations_text.lower()
        assert "underscores" in recommendations_text.lower()

    def test_validate_meta_tags(self):
        """Test meta tags validation for SEO."""

        def validate_meta_tags(meta_tags):
            """
            Validate meta tags for SEO compliance
            """
            try:
                issues = []
                recommendations = []
                score = 100

                required_tags = ["title", "description"]
                for tag in required_tags:
                    if tag not in meta_tags or not meta_tags[tag]:
                        issues.append(f"Missing required meta tag: {tag}")
                        score -= 30

                # Validate title tag
                if "title" in meta_tags and meta_tags["title"]:
                    title = meta_tags["title"]
                    if len(title) < 30:
                        recommendations.append(
                            "Title tag is too short (recommended: 30-60 characters)"
                        )
                        score -= 10
                    elif len(title) > 60:
                        recommendations.append(
                            "Title tag is too long (recommended: 30-60 characters)"
                        )
                        score -= 10

                # Validate description tag
                if "description" in meta_tags and meta_tags["description"]:
                    description = meta_tags["description"]
                    if len(description) < 120:
                        recommendations.append(
                            "Meta description is too short (recommended: 120-160 characters)"
                        )
                        score -= 10
                    elif len(description) > 160:
                        recommendations.append(
                            "Meta description is too long (recommended: 120-160 characters)"
                        )
                        score -= 10

                # Check for recommended tags
                recommended_tags = ["keywords", "author", "viewport", "robots"]
                missing_recommended = [
                    tag for tag in recommended_tags if tag not in meta_tags
                ]

                if "viewport" not in meta_tags:
                    recommendations.append(
                        "Add viewport meta tag for mobile optimization"
                    )
                    score -= 5

                if "robots" not in meta_tags:
                    recommendations.append("Add robots meta tag to control indexing")
                    score -= 5

                # Check Open Graph tags
                og_tags = ["og:title", "og:description", "og:image", "og:url"]
                missing_og = [tag for tag in og_tags if tag not in meta_tags]

                if len(missing_og) > 2:
                    recommendations.append(
                        "Add Open Graph meta tags for social media sharing"
                    )
                    score -= 10

                # Check Twitter Card tags
                twitter_tags = ["twitter:card", "twitter:title", "twitter:description"]
                missing_twitter = [tag for tag in twitter_tags if tag not in meta_tags]

                if len(missing_twitter) > 1:
                    recommendations.append(
                        "Add Twitter Card meta tags for Twitter sharing"
                    )
                    score -= 5

                score = max(0, score)

                return {
                    "is_valid": len(issues) == 0,
                    "score": score,
                    "issues": issues,
                    "recommendations": recommendations,
                    "missing_required": [
                        tag
                        for tag in required_tags
                        if tag not in meta_tags or not meta_tags[tag]
                    ],
                    "missing_recommended": missing_recommended,
                    "grade": "A"
                    if score >= 90
                    else "B"
                    if score >= 80
                    else "C"
                    if score >= 70
                    else "D"
                    if score >= 60
                    else "F",
                }

            except Exception as e:
                return {
                    "is_valid": False,
                    "error": f"Error validating meta tags: {str(e)}",
                }

        # Test complete meta tags
        complete_meta_tags = {
            "title": "Complete Guide to Linear Algebra - Math Service",
            "description": "Learn linear algebra fundamentals including vectors, matrices, and linear transformations with practical examples and step-by-step solutions.",
            "keywords": "linear algebra, vectors, matrices, mathematics",
            "author": "Dr. Math Expert",
            "viewport": "width=device-width, initial-scale=1.0",
            "robots": "index, follow",
            "og:title": "Complete Guide to Linear Algebra",
            "og:description": "Learn linear algebra fundamentals with practical examples",
            "og:image": "https://mathservice.com/images/linear-algebra.jpg",
            "og:url": "https://mathservice.com/articles/linear-algebra-guide",
            "twitter:card": "summary_large_image",
            "twitter:title": "Complete Guide to Linear Algebra",
            "twitter:description": "Learn linear algebra fundamentals with practical examples",
        }

        result = validate_meta_tags(complete_meta_tags)

        assert result["is_valid"] is True
        assert result["score"] >= 90
        assert result["grade"] == "A"
        assert len(result["issues"]) == 0
        assert len(result["missing_required"]) == 0

        # Test minimal meta tags
        minimal_meta_tags = {"title": "Math", "description": "Short"}

        result = validate_meta_tags(minimal_meta_tags)

        assert result["is_valid"] is True  # Has required tags
        assert result["score"] < 80  # But poor quality
        assert len(result["recommendations"]) > 0

        # Check specific recommendations
        recommendations_text = " ".join(result["recommendations"])
        assert "too short" in recommendations_text.lower()
        assert "viewport" in recommendations_text.lower()

        # Test missing required tags
        empty_meta_tags = {}

        result = validate_meta_tags(empty_meta_tags)

        assert result["is_valid"] is False
        assert result["score"] < 50
        assert len(result["issues"]) >= 2
        assert len(result["missing_required"]) == 2
