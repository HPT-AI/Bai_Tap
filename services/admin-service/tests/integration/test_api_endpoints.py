"""
Integration tests for Admin Service API endpoints.
"""

import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAdminServiceAPIEndpoints:
    """Integration tests for Admin Service API endpoints."""

    @pytest.fixture
    def mock_app(self):
        """Mock FastAPI application for testing."""
        from fastapi import Depends, FastAPI, HTTPException, Query
        from fastapi.security import HTTPBearer

        app = FastAPI(title="Admin Service", version="1.0.0")
        security = HTTPBearer()

        # Mock authentication dependency
        async def get_current_user(token: str = Depends(security)):
            if token.credentials == "admin_token":
                return {"user_id": 456, "email": "admin@example.com", "role": "admin"}
            elif token.credentials == "super_admin_token":
                return {
                    "user_id": 999,
                    "email": "superadmin@example.com",
                    "role": "super_admin",
                }
            elif token.credentials == "user_token":
                return {"user_id": 123, "email": "user@example.com", "role": "user"}
            else:
                raise HTTPException(status_code=401, detail="Invalid token")

        # System monitoring endpoints
        @app.get("/system/health")
        async def get_system_health():
            """Get overall system health status."""
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "user_service": {"status": "healthy", "response_time_ms": 45},
                    "payment_service": {"status": "healthy", "response_time_ms": 67},
                    "math_solver_service": {
                        "status": "healthy",
                        "response_time_ms": 123,
                    },
                    "content_service": {"status": "healthy", "response_time_ms": 89},
                    "admin_service": {"status": "healthy", "response_time_ms": 34},
                },
                "databases": {
                    "user_service_db": {
                        "status": "healthy",
                        "connections": 5,
                        "max_connections": 100,
                    },
                    "payment_service_db": {
                        "status": "healthy",
                        "connections": 3,
                        "max_connections": 100,
                    },
                    "math_solver_db": {
                        "status": "healthy",
                        "connections": 8,
                        "max_connections": 100,
                    },
                    "content_service_db": {
                        "status": "healthy",
                        "connections": 12,
                        "max_connections": 100,
                    },
                    "admin_service_db": {
                        "status": "healthy",
                        "connections": 2,
                        "max_connections": 100,
                    },
                },
                "redis": {
                    "status": "healthy",
                    "memory_usage": "45MB",
                    "connected_clients": 15,
                },
            }

            return {"success": True, "health": health_status}

        @app.get("/system/metrics")
        async def get_system_metrics(current_user: dict = Depends(get_current_user)):
            """Get detailed system metrics."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_usage_percent": 23.5,
                    "memory_usage_percent": 67.8,
                    "disk_usage_percent": 45.2,
                    "network_io": {"bytes_sent": 1024000, "bytes_received": 2048000},
                    "load_average": [0.8, 0.9, 1.1],
                },
                "application": {
                    "active_users": 145,
                    "requests_per_minute": 234,
                    "average_response_time_ms": 89,
                    "error_rate_percent": 0.2,
                },
                "database": {
                    "total_connections": 30,
                    "active_queries": 5,
                    "slow_queries": 0,
                    "cache_hit_rate_percent": 94.5,
                },
            }

            return {"success": True, "metrics": metrics}

        @app.get("/system/logs")
        async def get_system_logs(
            current_user: dict = Depends(get_current_user),
            level: str = Query("INFO"),
            service: str = Query(None),
            limit: int = Query(100, le=1000),
            page: int = Query(1, ge=1),
        ):
            """Get system logs with filtering."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            # Mock log entries
            all_logs = [
                {
                    "id": 1,
                    "timestamp": "2024-12-15T10:30:00",
                    "level": "INFO",
                    "service": "user_service",
                    "message": "User login successful",
                    "user_id": 123,
                    "ip_address": "192.168.1.100",
                },
                {
                    "id": 2,
                    "timestamp": "2024-12-15T10:25:00",
                    "level": "WARNING",
                    "service": "payment_service",
                    "message": "Payment gateway timeout, retrying",
                    "transaction_id": "txn_123456",
                },
                {
                    "id": 3,
                    "timestamp": "2024-12-15T10:20:00",
                    "level": "ERROR",
                    "service": "math_solver_service",
                    "message": "Failed to solve complex equation",
                    "equation": "x^5 + 2x^4 - 3x^3 + x^2 - 5x + 1 = 0",
                    "error": "Numerical instability",
                },
                {
                    "id": 4,
                    "timestamp": "2024-12-15T10:15:00",
                    "level": "INFO",
                    "service": "content_service",
                    "message": "Article published successfully",
                    "article_id": 15,
                    "author_id": 789,
                },
            ]

            # Apply filters
            filtered_logs = all_logs

            if level and level != "ALL":
                filtered_logs = [log for log in filtered_logs if log["level"] == level]

            if service:
                filtered_logs = [
                    log for log in filtered_logs if log["service"] == service
                ]

            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_logs = filtered_logs[start:end]

            return {
                "success": True,
                "logs": paginated_logs,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(filtered_logs),
                    "pages": (len(filtered_logs) + limit - 1) // limit,
                },
            }

        # User management endpoints
        @app.get("/users")
        async def get_users(
            current_user: dict = Depends(get_current_user),
            page: int = Query(1, ge=1),
            limit: int = Query(20, ge=1, le=100),
            role: str = Query(None),
            status: str = Query(None),
            search: str = Query(None),
        ):
            """Get users with filtering and pagination."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            # Mock users data
            all_users = [
                {
                    "id": 123,
                    "email": "user@example.com",
                    "full_name": "Regular User",
                    "role": "user",
                    "status": "active",
                    "email_verified": True,
                    "last_login": "2024-12-15T10:30:00",
                    "created_at": "2024-11-01T09:00:00",
                    "total_spent": 150.00,
                    "problems_solved": 45,
                },
                {
                    "id": 456,
                    "email": "admin@example.com",
                    "full_name": "Admin User",
                    "role": "admin",
                    "status": "active",
                    "email_verified": True,
                    "last_login": "2024-12-15T11:00:00",
                    "created_at": "2024-10-15T14:30:00",
                    "total_spent": 0.00,
                    "problems_solved": 0,
                },
                {
                    "id": 789,
                    "email": "author@example.com",
                    "full_name": "Content Author",
                    "role": "author",
                    "status": "active",
                    "email_verified": True,
                    "last_login": "2024-12-15T09:45:00",
                    "created_at": "2024-10-20T16:15:00",
                    "total_spent": 75.00,
                    "problems_solved": 23,
                },
                {
                    "id": 999,
                    "email": "premium@example.com",
                    "full_name": "Premium User",
                    "role": "premium_user",
                    "status": "active",
                    "email_verified": True,
                    "last_login": "2024-12-15T08:20:00",
                    "created_at": "2024-09-10T11:45:00",
                    "total_spent": 500.00,
                    "problems_solved": 156,
                },
                {
                    "id": 111,
                    "email": "suspended@example.com",
                    "full_name": "Suspended User",
                    "role": "user",
                    "status": "suspended",
                    "email_verified": True,
                    "last_login": "2024-12-10T15:30:00",
                    "created_at": "2024-11-15T10:00:00",
                    "total_spent": 25.00,
                    "problems_solved": 8,
                },
            ]

            # Apply filters
            filtered_users = all_users

            if role:
                filtered_users = [u for u in filtered_users if u["role"] == role]

            if status:
                filtered_users = [u for u in filtered_users if u["status"] == status]

            if search:
                search_lower = search.lower()
                filtered_users = [
                    u
                    for u in filtered_users
                    if search_lower in u["email"].lower()
                    or search_lower in u["full_name"].lower()
                ]

            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_users = filtered_users[start:end]

            return {
                "success": True,
                "users": paginated_users,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(filtered_users),
                    "pages": (len(filtered_users) + limit - 1) // limit,
                },
            }

        @app.get("/users/{user_id}")
        async def get_user_details(
            user_id: int, current_user: dict = Depends(get_current_user)
        ):
            """Get detailed user information."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            if user_id == 123:
                user_details = {
                    "id": 123,
                    "email": "user@example.com",
                    "full_name": "Regular User",
                    "role": "user",
                    "status": "active",
                    "email_verified": True,
                    "phone": "+1234567890",
                    "date_of_birth": "1995-05-15",
                    "country": "United States",
                    "timezone": "America/New_York",
                    "last_login": "2024-12-15T10:30:00",
                    "created_at": "2024-11-01T09:00:00",
                    "updated_at": "2024-12-14T16:20:00",
                    "subscription": {
                        "type": "basic",
                        "expires_at": None,
                        "auto_renew": False,
                    },
                    "statistics": {
                        "total_spent": 150.00,
                        "problems_solved": 45,
                        "articles_read": 23,
                        "login_count": 67,
                        "average_session_duration_minutes": 25,
                    },
                    "recent_activity": [
                        {
                            "action": "solved_problem",
                            "details": "Quadratic equation: x² + 5x + 6 = 0",
                            "timestamp": "2024-12-15T10:15:00",
                        },
                        {
                            "action": "read_article",
                            "details": "Introduction to Calculus",
                            "timestamp": "2024-12-15T09:45:00",
                        },
                    ],
                }

                return {"success": True, "user": user_details}
            else:
                raise HTTPException(status_code=404, detail="User not found")

        @app.put("/users/{user_id}/status")
        async def update_user_status(
            user_id: int,
            status_data: dict,
            current_user: dict = Depends(get_current_user),
        ):
            """Update user status (activate, suspend, ban)."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            new_status = status_data.get("status")
            reason = status_data.get("reason", "")

            if new_status not in ["active", "suspended", "banned"]:
                raise HTTPException(status_code=400, detail="Invalid status")

            if user_id == 123:
                return {
                    "success": True,
                    "message": f"User status updated to {new_status}",
                    "user": {
                        "id": user_id,
                        "status": new_status,
                        "status_reason": reason,
                        "updated_at": datetime.utcnow().isoformat(),
                        "updated_by": current_user["user_id"],
                    },
                }
            else:
                raise HTTPException(status_code=404, detail="User not found")

        # Analytics endpoints
        @app.get("/analytics/overview")
        async def get_analytics_overview(
            current_user: dict = Depends(get_current_user),
        ):
            """Get system analytics overview."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            overview = {
                "timestamp": datetime.utcnow().isoformat(),
                "users": {
                    "total": 1247,
                    "active_today": 89,
                    "new_this_month": 156,
                    "premium_users": 234,
                },
                "revenue": {
                    "total": 45678.90,
                    "this_month": 5432.10,
                    "average_per_user": 36.65,
                    "growth_rate_percent": 12.5,
                },
                "content": {
                    "total_articles": 89,
                    "published_articles": 76,
                    "total_views": 234567,
                    "average_engagement_rate": 8.9,
                },
                "math_solver": {
                    "problems_solved_today": 456,
                    "total_problems_solved": 123456,
                    "success_rate_percent": 94.2,
                    "average_solving_time_ms": 1250,
                },
                "system_performance": {
                    "uptime_percent": 99.8,
                    "average_response_time_ms": 89,
                    "error_rate_percent": 0.2,
                    "peak_concurrent_users": 234,
                },
            }

            return {"success": True, "analytics": overview}

        @app.get("/analytics/revenue")
        async def get_revenue_analytics(
            current_user: dict = Depends(get_current_user),
            period: str = Query("month"),
            start_date: str = Query(None),
            end_date: str = Query(None),
        ):
            """Get detailed revenue analytics."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            # Mock revenue data
            if period == "month":
                revenue_data = {
                    "period": "month",
                    "total_revenue": 5432.10,
                    "transaction_count": 234,
                    "average_transaction": 23.21,
                    "daily_breakdown": [
                        {"date": "2024-12-01", "revenue": 156.78, "transactions": 8},
                        {"date": "2024-12-02", "revenue": 234.56, "transactions": 12},
                        {"date": "2024-12-03", "revenue": 189.34, "transactions": 9},
                        {"date": "2024-12-04", "revenue": 298.45, "transactions": 15},
                        {"date": "2024-12-05", "revenue": 167.89, "transactions": 7},
                    ],
                    "payment_methods": {
                        "vnpay": {"revenue": 2456.78, "percentage": 45.2},
                        "momo": {"revenue": 1789.34, "percentage": 32.9},
                        "zalopay": {"revenue": 1185.98, "percentage": 21.9},
                    },
                    "subscription_types": {
                        "premium_monthly": {"revenue": 3456.78, "count": 156},
                        "premium_yearly": {"revenue": 1975.32, "count": 78},
                    },
                }
            else:
                revenue_data = {
                    "period": period,
                    "total_revenue": 0,
                    "transaction_count": 0,
                    "message": "No data available for this period",
                }

            return {"success": True, "revenue_analytics": revenue_data}

        # Audit log endpoints
        @app.get("/audit/logs")
        async def get_audit_logs(
            current_user: dict = Depends(get_current_user),
            page: int = Query(1, ge=1),
            limit: int = Query(50, ge=1, le=200),
            action: str = Query(None),
            user_id: int = Query(None),
            start_date: str = Query(None),
            end_date: str = Query(None),
        ):
            """Get audit logs with filtering."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            # Mock audit logs
            all_logs = [
                {
                    "id": 1,
                    "timestamp": "2024-12-15T11:30:00",
                    "user_id": 456,
                    "user_email": "admin@example.com",
                    "action": "user_status_updated",
                    "resource_type": "user",
                    "resource_id": 123,
                    "details": {
                        "old_status": "active",
                        "new_status": "suspended",
                        "reason": "Violation of terms",
                    },
                    "ip_address": "192.168.1.50",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                },
                {
                    "id": 2,
                    "timestamp": "2024-12-15T10:45:00",
                    "user_id": 789,
                    "user_email": "author@example.com",
                    "action": "article_published",
                    "resource_type": "article",
                    "resource_id": 15,
                    "details": {
                        "title": "Advanced Calculus Techniques",
                        "category": "calculus",
                    },
                    "ip_address": "192.168.1.75",
                    "user_agent": "Mozilla/5.0 (macOS; Intel Mac OS X 10_15_7)",
                },
                {
                    "id": 3,
                    "timestamp": "2024-12-15T09:20:00",
                    "user_id": 456,
                    "user_email": "admin@example.com",
                    "action": "system_backup_created",
                    "resource_type": "system",
                    "resource_id": None,
                    "details": {
                        "backup_type": "full",
                        "size_mb": 2048,
                        "duration_seconds": 145,
                    },
                    "ip_address": "192.168.1.50",
                    "user_agent": "Admin Dashboard",
                },
            ]

            # Apply filters
            filtered_logs = all_logs

            if action:
                filtered_logs = [
                    log for log in filtered_logs if log["action"] == action
                ]

            if user_id:
                filtered_logs = [
                    log for log in filtered_logs if log["user_id"] == user_id
                ]

            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_logs = filtered_logs[start:end]

            return {
                "success": True,
                "audit_logs": paginated_logs,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(filtered_logs),
                    "pages": (len(filtered_logs) + limit - 1) // limit,
                },
            }

        # Security endpoints
        @app.get("/security/events")
        async def get_security_events(
            current_user: dict = Depends(get_current_user),
            severity: str = Query("all"),
            limit: int = Query(100, le=500),
        ):
            """Get security events and alerts."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            # Mock security events
            all_events = [
                {
                    "id": 1,
                    "timestamp": "2024-12-15T11:45:00",
                    "severity": "high",
                    "event_type": "failed_login_attempts",
                    "description": "Multiple failed login attempts from IP 192.168.1.200",
                    "details": {
                        "ip_address": "192.168.1.200",
                        "attempts": 15,
                        "time_window_minutes": 10,
                        "targeted_emails": ["admin@example.com", "user@example.com"],
                    },
                    "status": "investigating",
                    "actions_taken": ["IP temporarily blocked", "Users notified"],
                },
                {
                    "id": 2,
                    "timestamp": "2024-12-15T10:30:00",
                    "severity": "medium",
                    "event_type": "suspicious_payment",
                    "description": "Unusual payment pattern detected",
                    "details": {
                        "user_id": 999,
                        "amount": 1000.00,
                        "payment_method": "vnpay",
                        "reason": "Amount significantly higher than user's typical transactions",
                    },
                    "status": "resolved",
                    "actions_taken": ["Payment verified manually", "User contacted"],
                },
                {
                    "id": 3,
                    "timestamp": "2024-12-15T09:15:00",
                    "severity": "low",
                    "event_type": "rate_limit_exceeded",
                    "description": "API rate limit exceeded by user",
                    "details": {
                        "user_id": 123,
                        "endpoint": "/math/solve",
                        "requests_per_minute": 150,
                        "limit": 100,
                    },
                    "status": "auto_resolved",
                    "actions_taken": ["Temporary rate limiting applied"],
                },
            ]

            # Apply severity filter
            if severity != "all":
                filtered_events = [e for e in all_events if e["severity"] == severity]
            else:
                filtered_events = all_events

            # Apply limit
            limited_events = filtered_events[:limit]

            return {
                "success": True,
                "security_events": limited_events,
                "summary": {
                    "total_events": len(filtered_events),
                    "high_severity": len(
                        [e for e in filtered_events if e["severity"] == "high"]
                    ),
                    "medium_severity": len(
                        [e for e in filtered_events if e["severity"] == "medium"]
                    ),
                    "low_severity": len(
                        [e for e in filtered_events if e["severity"] == "low"]
                    ),
                },
            }

        # Backup and maintenance endpoints
        @app.post("/system/backup")
        async def create_backup(
            backup_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Create system backup."""
            if current_user["role"] != "super_admin":
                raise HTTPException(
                    status_code=403, detail="Super admin access required"
                )

            backup_type = backup_data.get("type", "full")
            include_user_data = backup_data.get("include_user_data", True)

            if backup_type not in ["full", "database_only", "files_only"]:
                raise HTTPException(status_code=400, detail="Invalid backup type")

            # Mock backup creation
            backup_info = {
                "id": "backup_20241215_113000",
                "type": backup_type,
                "status": "in_progress",
                "started_at": datetime.utcnow().isoformat(),
                "estimated_completion": (
                    datetime.utcnow() + timedelta(minutes=30)
                ).isoformat(),
                "include_user_data": include_user_data,
                "estimated_size_mb": 2048 if backup_type == "full" else 1024,
            }

            return {
                "success": True,
                "message": "Backup started successfully",
                "backup": backup_info,
            }

        @app.get("/system/backups")
        async def get_backups(current_user: dict = Depends(get_current_user)):
            """Get list of available backups."""
            if current_user["role"] not in ["admin", "super_admin"]:
                raise HTTPException(status_code=403, detail="Admin access required")

            backups = [
                {
                    "id": "backup_20241215_113000",
                    "type": "full",
                    "status": "completed",
                    "created_at": "2024-12-15T11:30:00",
                    "completed_at": "2024-12-15T12:15:00",
                    "size_mb": 2048,
                    "retention_until": "2024-12-29T11:30:00",
                },
                {
                    "id": "backup_20241214_020000",
                    "type": "database_only",
                    "status": "completed",
                    "created_at": "2024-12-14T02:00:00",
                    "completed_at": "2024-12-14T02:45:00",
                    "size_mb": 1024,
                    "retention_until": "2024-12-28T02:00:00",
                },
            ]

            return {"success": True, "backups": backups}

        return app

    @pytest.fixture
    async def client(self, mock_app):
        """Create test client."""
        async with AsyncClient(app=mock_app, base_url="http://test") as ac:
            yield ac

    async def test_system_health(self, client):
        """Test system health endpoint."""
        response = await client.get("/system/health")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "health" in data

        health = data["health"]
        assert health["status"] == "healthy"
        assert "services" in health
        assert "databases" in health
        assert "redis" in health

        # Check services
        services = health["services"]
        assert len(services) == 5
        assert services["user_service"]["status"] == "healthy"
        assert services["payment_service"]["response_time_ms"] == 67

        # Check databases
        databases = health["databases"]
        assert len(databases) == 5
        assert databases["user_service_db"]["connections"] == 5
        assert databases["user_service_db"]["max_connections"] == 100

        # Check Redis
        redis = health["redis"]
        assert redis["status"] == "healthy"
        assert redis["connected_clients"] == 15

    async def test_system_metrics(self, client):
        """Test system metrics endpoint."""
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer user_token"}

        # Test successful metrics retrieval by admin
        response = await client.get("/system/metrics", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "metrics" in data

        metrics = data["metrics"]
        assert "system" in metrics
        assert "application" in metrics
        assert "database" in metrics

        # Check system metrics
        system = metrics["system"]
        assert system["cpu_usage_percent"] == 23.5
        assert system["memory_usage_percent"] == 67.8
        assert len(system["load_average"]) == 3

        # Check application metrics
        application = metrics["application"]
        assert application["active_users"] == 145
        assert application["error_rate_percent"] == 0.2

        # Test access denied for regular user
        response = await client.get("/system/metrics", headers=user_headers)
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    async def test_system_logs(self, client):
        """Test system logs endpoint."""
        admin_headers = {"Authorization": "Bearer admin_token"}

        # Test get all logs
        response = await client.get("/system/logs", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "logs" in data
        assert "pagination" in data

        logs = data["logs"]
        assert len(logs) == 4

        # Check first log
        first_log = logs[0]
        assert first_log["level"] == "INFO"
        assert first_log["service"] == "user_service"
        assert "timestamp" in first_log

        # Test level filter
        response = await client.get("/system/logs?level=ERROR", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        logs = data["logs"]
        assert len(logs) == 1
        assert logs[0]["level"] == "ERROR"

        # Test service filter
        response = await client.get(
            "/system/logs?service=payment_service", headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        logs = data["logs"]
        assert len(logs) == 1
        assert logs[0]["service"] == "payment_service"

        # Test pagination
        response = await client.get(
            "/system/logs?limit=2&page=1", headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        logs = data["logs"]
        assert len(logs) == 2

        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 2

    async def test_user_management(self, client):
        """Test user management endpoints."""
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer user_token"}

        # Test get users
        response = await client.get("/users", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "users" in data
        assert "pagination" in data

        users = data["users"]
        assert len(users) == 5

        # Check first user
        first_user = users[0]
        assert first_user["email"] == "user@example.com"
        assert first_user["role"] == "user"
        assert first_user["status"] == "active"

        # Test role filter
        response = await client.get("/users?role=admin", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        users = data["users"]
        assert len(users) == 1
        assert users[0]["role"] == "admin"

        # Test status filter
        response = await client.get("/users?status=suspended", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        users = data["users"]
        assert len(users) == 1
        assert users[0]["status"] == "suspended"

        # Test search
        response = await client.get("/users?search=premium", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        users = data["users"]
        assert len(users) == 1
        assert "premium" in users[0]["email"]

        # Test access denied for regular user
        response = await client.get("/users", headers=user_headers)
        assert response.status_code == 403

    async def test_user_details(self, client):
        """Test get user details endpoint."""
        admin_headers = {"Authorization": "Bearer admin_token"}

        # Test get existing user
        response = await client.get("/users/123", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "user" in data

        user = data["user"]
        assert user["id"] == 123
        assert user["email"] == "user@example.com"
        assert "subscription" in user
        assert "statistics" in user
        assert "recent_activity" in user

        # Check statistics
        stats = user["statistics"]
        assert stats["total_spent"] == 150.00
        assert stats["problems_solved"] == 45

        # Check recent activity
        activity = user["recent_activity"]
        assert len(activity) == 2
        assert activity[0]["action"] == "solved_problem"

        # Test get non-existent user
        response = await client.get("/users/999999", headers=admin_headers)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_update_user_status(self, client):
        """Test update user status endpoint."""
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer user_token"}

        # Test successful status update
        status_data = {"status": "suspended", "reason": "Violation of terms of service"}

        response = await client.put(
            "/users/123/status", json=status_data, headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "User status updated" in data["message"]
        assert data["user"]["status"] == "suspended"
        assert data["user"]["status_reason"] == "Violation of terms of service"

        # Test invalid status
        invalid_data = {"status": "invalid_status"}

        response = await client.put(
            "/users/123/status", json=invalid_data, headers=admin_headers
        )
        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]

        # Test access denied for regular user
        response = await client.put(
            "/users/123/status", json=status_data, headers=user_headers
        )
        assert response.status_code == 403

        # Test update non-existent user
        response = await client.put(
            "/users/999999/status", json=status_data, headers=admin_headers
        )
        assert response.status_code == 404

    async def test_analytics_overview(self, client):
        """Test analytics overview endpoint."""
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer user_token"}

        # Test successful analytics retrieval
        response = await client.get("/analytics/overview", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "analytics" in data

        analytics = data["analytics"]
        assert "users" in analytics
        assert "revenue" in analytics
        assert "content" in analytics
        assert "math_solver" in analytics
        assert "system_performance" in analytics

        # Check users analytics
        users = analytics["users"]
        assert users["total"] == 1247
        assert users["active_today"] == 89

        # Check revenue analytics
        revenue = analytics["revenue"]
        assert revenue["total"] == 45678.90
        assert revenue["growth_rate_percent"] == 12.5

        # Check system performance
        performance = analytics["system_performance"]
        assert performance["uptime_percent"] == 99.8
        assert performance["error_rate_percent"] == 0.2

        # Test access denied for regular user
        response = await client.get("/analytics/overview", headers=user_headers)
        assert response.status_code == 403

    async def test_revenue_analytics(self, client):
        """Test revenue analytics endpoint."""
        admin_headers = {"Authorization": "Bearer admin_token"}

        # Test monthly revenue analytics
        response = await client.get(
            "/analytics/revenue?period=month", headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "revenue_analytics" in data

        revenue = data["revenue_analytics"]
        assert revenue["period"] == "month"
        assert revenue["total_revenue"] == 5432.10
        assert revenue["transaction_count"] == 234

        # Check daily breakdown
        assert "daily_breakdown" in revenue
        daily = revenue["daily_breakdown"]
        assert len(daily) == 5
        assert daily[0]["date"] == "2024-12-01"

        # Check payment methods breakdown
        assert "payment_methods" in revenue
        payment_methods = revenue["payment_methods"]
        assert "vnpay" in payment_methods
        assert payment_methods["vnpay"]["percentage"] == 45.2

        # Test different period
        response = await client.get(
            "/analytics/revenue?period=week", headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        revenue = data["revenue_analytics"]
        assert revenue["period"] == "week"
        assert revenue["total_revenue"] == 0  # No data for this period

    async def test_audit_logs(self, client):
        """Test audit logs endpoint."""
        admin_headers = {"Authorization": "Bearer admin_token"}
        super_admin_headers = {"Authorization": "Bearer super_admin_token"}

        # Test get audit logs
        response = await client.get("/audit/logs", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "audit_logs" in data
        assert "pagination" in data

        logs = data["audit_logs"]
        assert len(logs) == 3

        # Check first log
        first_log = logs[0]
        assert first_log["action"] == "user_status_updated"
        assert first_log["resource_type"] == "user"
        assert "details" in first_log
        assert "ip_address" in first_log

        # Test action filter
        response = await client.get(
            "/audit/logs?action=article_published", headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        logs = data["audit_logs"]
        assert len(logs) == 1
        assert logs[0]["action"] == "article_published"

        # Test user filter
        response = await client.get("/audit/logs?user_id=456", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        logs = data["audit_logs"]
        assert len(logs) == 2  # Two logs from user 456

        # Test pagination
        response = await client.get("/audit/logs?limit=1&page=1", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        logs = data["audit_logs"]
        assert len(logs) == 1

    async def test_security_events(self, client):
        """Test security events endpoint."""
        admin_headers = {"Authorization": "Bearer admin_token"}

        # Test get all security events
        response = await client.get("/security/events", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "security_events" in data
        assert "summary" in data

        events = data["security_events"]
        assert len(events) == 3

        # Check first event
        first_event = events[0]
        assert first_event["severity"] == "high"
        assert first_event["event_type"] == "failed_login_attempts"
        assert "details" in first_event
        assert "actions_taken" in first_event

        # Check summary
        summary = data["summary"]
        assert summary["total_events"] == 3
        assert summary["high_severity"] == 1
        assert summary["medium_severity"] == 1
        assert summary["low_severity"] == 1

        # Test severity filter
        response = await client.get(
            "/security/events?severity=high", headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        events = data["security_events"]
        assert len(events) == 1
        assert events[0]["severity"] == "high"

        # Test limit
        response = await client.get("/security/events?limit=2", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        events = data["security_events"]
        assert len(events) == 2

    async def test_backup_management(self, client):
        """Test backup management endpoints."""
        super_admin_headers = {"Authorization": "Bearer super_admin_token"}
        admin_headers = {"Authorization": "Bearer admin_token"}

        # Test create backup by super admin
        backup_data = {"type": "full", "include_user_data": True}

        response = await client.post(
            "/system/backup", json=backup_data, headers=super_admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Backup started successfully" in data["message"]
        assert "backup" in data

        backup = data["backup"]
        assert backup["type"] == "full"
        assert backup["status"] == "in_progress"
        assert backup["include_user_data"] is True

        # Test create backup by regular admin (should fail)
        response = await client.post(
            "/system/backup", json=backup_data, headers=admin_headers
        )
        assert response.status_code == 403
        assert "Super admin access required" in response.json()["detail"]

        # Test invalid backup type
        invalid_data = {"type": "invalid_type"}

        response = await client.post(
            "/system/backup", json=invalid_data, headers=super_admin_headers
        )
        assert response.status_code == 400
        assert "Invalid backup type" in response.json()["detail"]

        # Test get backups
        response = await client.get("/system/backups", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "backups" in data

        backups = data["backups"]
        assert len(backups) == 2

        # Check first backup
        first_backup = backups[0]
        assert first_backup["type"] == "full"
        assert first_backup["status"] == "completed"
        assert first_backup["size_mb"] == 2048

    async def test_authentication_required(self, client):
        """Test endpoints require authentication."""
        endpoints_requiring_auth = [
            ("/system/metrics", "GET"),
            ("/system/logs", "GET"),
            ("/users", "GET"),
            ("/users/123", "GET"),
            ("/users/123/status", "PUT"),
            ("/analytics/overview", "GET"),
            ("/analytics/revenue", "GET"),
            ("/audit/logs", "GET"),
            ("/security/events", "GET"),
            ("/system/backup", "POST"),
            ("/system/backups", "GET"),
        ]

        for endpoint, method in endpoints_requiring_auth:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint, json={})
            elif method == "PUT":
                response = await client.put(endpoint, json={})

            assert response.status_code == 403  # FastAPI returns 403 for missing auth

    async def test_concurrent_operations(self, client):
        """Test concurrent admin operations."""
        admin_headers = {"Authorization": "Bearer admin_token"}

        async def get_system_metrics():
            response = await client.get("/system/metrics", headers=admin_headers)
            return response.status_code == 200

        async def get_users():
            response = await client.get("/users", headers=admin_headers)
            return response.status_code == 200

        async def get_analytics():
            response = await client.get("/analytics/overview", headers=admin_headers)
            return response.status_code == 200

        # Test 3 concurrent operations
        tasks = [get_system_metrics(), get_users(), get_analytics()]
        results = await asyncio.gather(*tasks)

        # All operations should succeed
        assert all(results)

    async def test_performance_thresholds(self, client):
        """Test API response time thresholds."""
        admin_headers = {"Authorization": "Bearer admin_token"}

        import time

        # Test system health endpoint (should be fast)
        start_time = time.time()
        response = await client.get("/system/health")
        end_time = time.time()

        assert response.status_code == 200
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 1000  # Should respond within 1 second

        # Test system metrics endpoint
        start_time = time.time()
        response = await client.get("/system/metrics", headers=admin_headers)
        end_time = time.time()

        assert response.status_code == 200
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 2000  # Should respond within 2 seconds
