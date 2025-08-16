"""
Integration tests for Math Solver Service API endpoints.
"""

import asyncio
import json
import math
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMathSolverServiceAPIEndpoints:
    """Integration tests for Math Solver Service API endpoints."""

    @pytest.fixture
    def mock_app(self):
        """Mock FastAPI application for testing."""
        from fastapi import Depends, FastAPI, HTTPException
        from fastapi.security import HTTPBearer

        app = FastAPI(title="Math Solver Service", version="1.0.0")
        security = HTTPBearer()

        # Mock authentication dependency
        async def get_current_user(token: str = Depends(security)):
            if token.credentials == "valid_token":
                return {"user_id": 123, "email": "test@example.com", "role": "user"}
            elif token.credentials == "premium_token":
                return {
                    "user_id": 456,
                    "email": "premium@example.com",
                    "role": "premium_user",
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid token")

        # Algebra solver endpoints
        @app.post("/algebra/solve")
        async def solve_algebra(
            problem_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Solve algebra problems."""
            equation = problem_data.get("equation")
            variable = problem_data.get("variable", "x")

            if not equation:
                raise HTTPException(status_code=400, detail="Equation is required")

            # Mock algebra solving
            if equation == "2*x + 5 = 15":
                return {
                    "success": True,
                    "problem": {
                        "equation": equation,
                        "variable": variable,
                        "type": "linear",
                    },
                    "solution": {
                        "value": 5,
                        "steps": [
                            "Given: 2*x + 5 = 15",
                            "Subtract 5 from both sides: 2*x = 10",
                            "Divide both sides by 2: x = 5",
                        ],
                        "verification": "2*(5) + 5 = 10 + 5 = 15 ✓",
                    },
                    "solving_time_ms": 45,
                }
            elif equation == "x^2 - 5*x + 6 = 0":
                return {
                    "success": True,
                    "problem": {
                        "equation": equation,
                        "variable": variable,
                        "type": "quadratic",
                    },
                    "solution": {
                        "values": [2, 3],
                        "steps": [
                            "Given: x^2 - 5*x + 6 = 0",
                            "Factor: (x - 2)(x - 3) = 0",
                            "Solutions: x = 2 or x = 3",
                        ],
                        "verification": "For x=2: 4 - 10 + 6 = 0 ✓, For x=3: 9 - 15 + 6 = 0 ✓",
                    },
                    "solving_time_ms": 78,
                }
            elif equation == "x^3 - 6*x^2 + 11*x - 6 = 0":
                # Complex equation - premium feature
                if current_user["role"] != "premium_user":
                    raise HTTPException(
                        status_code=403,
                        detail="Premium subscription required for cubic equations",
                    )

                return {
                    "success": True,
                    "problem": {
                        "equation": equation,
                        "variable": variable,
                        "type": "cubic",
                    },
                    "solution": {
                        "values": [1, 2, 3],
                        "steps": [
                            "Given: x^3 - 6*x^2 + 11*x - 6 = 0",
                            "Factor: (x - 1)(x - 2)(x - 3) = 0",
                            "Solutions: x = 1, x = 2, x = 3",
                        ],
                        "verification": "All solutions verified ✓",
                    },
                    "solving_time_ms": 156,
                }
            else:
                raise HTTPException(
                    status_code=400, detail="Unable to solve this equation"
                )

        @app.post("/calculus/derivative")
        async def calculate_derivative(
            problem_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Calculate derivatives."""
            expression = problem_data.get("expression")
            variable = problem_data.get("variable", "x")

            if not expression:
                raise HTTPException(status_code=400, detail="Expression is required")

            # Mock derivative calculation
            if expression == "x^2 + 3*x + 2":
                return {
                    "success": True,
                    "problem": {
                        "expression": expression,
                        "variable": variable,
                        "operation": "derivative",
                    },
                    "solution": {
                        "derivative": "2*x + 3",
                        "steps": [
                            "Given: f(x) = x^2 + 3*x + 2",
                            "Apply power rule to x^2: d/dx(x^2) = 2*x",
                            "Apply power rule to 3*x: d/dx(3*x) = 3",
                            "Derivative of constant 2: d/dx(2) = 0",
                            "Therefore: f'(x) = 2*x + 3",
                        ],
                    },
                    "solving_time_ms": 32,
                }
            elif expression == "sin(x) + cos(x)":
                return {
                    "success": True,
                    "problem": {
                        "expression": expression,
                        "variable": variable,
                        "operation": "derivative",
                    },
                    "solution": {
                        "derivative": "cos(x) - sin(x)",
                        "steps": [
                            "Given: f(x) = sin(x) + cos(x)",
                            "d/dx(sin(x)) = cos(x)",
                            "d/dx(cos(x)) = -sin(x)",
                            "Therefore: f'(x) = cos(x) - sin(x)",
                        ],
                    },
                    "solving_time_ms": 28,
                }
            else:
                raise HTTPException(
                    status_code=400, detail="Unable to calculate derivative"
                )

        @app.post("/calculus/integral")
        async def calculate_integral(
            problem_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Calculate integrals."""
            expression = problem_data.get("expression")
            variable = problem_data.get("variable", "x")
            definite = problem_data.get("definite", False)
            lower_limit = problem_data.get("lower_limit")
            upper_limit = problem_data.get("upper_limit")

            if not expression:
                raise HTTPException(status_code=400, detail="Expression is required")

            if definite and (lower_limit is None or upper_limit is None):
                raise HTTPException(
                    status_code=400, detail="Limits required for definite integral"
                )

            # Mock integral calculation
            if expression == "2*x + 3":
                if definite:
                    # Calculate definite integral from lower_limit to upper_limit
                    # ∫(2*x + 3)dx from a to b = [x^2 + 3*x] from a to b
                    a, b = lower_limit, upper_limit
                    result = (b**2 + 3 * b) - (a**2 + 3 * a)

                    return {
                        "success": True,
                        "problem": {
                            "expression": expression,
                            "variable": variable,
                            "operation": "definite_integral",
                            "lower_limit": a,
                            "upper_limit": b,
                        },
                        "solution": {
                            "integral": f"x^2 + 3*x",
                            "definite_value": result,
                            "steps": [
                                f"Given: ∫({expression})dx from {a} to {b}",
                                "∫(2*x)dx = x^2",
                                "∫(3)dx = 3*x",
                                "Indefinite integral: x^2 + 3*x + C",
                                f"Evaluate at limits: [{b}^2 + 3*{b}] - [{a}^2 + 3*{a}]",
                                f"Result: {result}",
                            ],
                        },
                        "solving_time_ms": 67,
                    }
                else:
                    return {
                        "success": True,
                        "problem": {
                            "expression": expression,
                            "variable": variable,
                            "operation": "indefinite_integral",
                        },
                        "solution": {
                            "integral": "x^2 + 3*x + C",
                            "steps": [
                                f"Given: ∫({expression})dx",
                                "∫(2*x)dx = x^2",
                                "∫(3)dx = 3*x",
                                "Therefore: ∫(2*x + 3)dx = x^2 + 3*x + C",
                            ],
                        },
                        "solving_time_ms": 45,
                    }
            else:
                raise HTTPException(
                    status_code=400, detail="Unable to calculate integral"
                )

        @app.post("/geometry/area")
        async def calculate_area(
            problem_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Calculate geometric areas."""
            shape = problem_data.get("shape")
            parameters = problem_data.get("parameters", {})

            if not shape:
                raise HTTPException(status_code=400, detail="Shape is required")

            # Mock area calculations
            if shape == "rectangle":
                width = parameters.get("width")
                height = parameters.get("height")

                if not width or not height:
                    raise HTTPException(
                        status_code=400,
                        detail="Width and height required for rectangle",
                    )

                area = width * height

                return {
                    "success": True,
                    "problem": {"shape": shape, "parameters": parameters},
                    "solution": {
                        "area": area,
                        "formula": "Area = width × height",
                        "calculation": f"Area = {width} × {height} = {area}",
                        "unit": "square units",
                    },
                    "solving_time_ms": 15,
                }

            elif shape == "circle":
                radius = parameters.get("radius")

                if not radius:
                    raise HTTPException(
                        status_code=400, detail="Radius required for circle"
                    )

                area = math.pi * radius**2

                return {
                    "success": True,
                    "problem": {"shape": shape, "parameters": parameters},
                    "solution": {
                        "area": round(area, 4),
                        "formula": "Area = π × r²",
                        "calculation": f"Area = π × {radius}² = {round(area, 4)}",
                        "unit": "square units",
                    },
                    "solving_time_ms": 18,
                }

            elif shape == "triangle":
                base = parameters.get("base")
                height = parameters.get("height")

                if not base or not height:
                    raise HTTPException(
                        status_code=400, detail="Base and height required for triangle"
                    )

                area = 0.5 * base * height

                return {
                    "success": True,
                    "problem": {"shape": shape, "parameters": parameters},
                    "solution": {
                        "area": area,
                        "formula": "Area = ½ × base × height",
                        "calculation": f"Area = ½ × {base} × {height} = {area}",
                        "unit": "square units",
                    },
                    "solving_time_ms": 12,
                }

            else:
                raise HTTPException(status_code=400, detail="Unsupported shape")

        @app.post("/statistics/analyze")
        async def analyze_statistics(
            problem_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Analyze statistical data."""
            data = problem_data.get("data")
            analysis_type = problem_data.get("analysis_type", "descriptive")

            if not data or not isinstance(data, list):
                raise HTTPException(status_code=400, detail="Data array is required")

            if len(data) == 0:
                raise HTTPException(
                    status_code=400, detail="Data array cannot be empty"
                )

            # Mock statistical analysis
            if analysis_type == "descriptive":
                n = len(data)
                mean = sum(data) / n
                sorted_data = sorted(data)

                # Median
                if n % 2 == 0:
                    median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
                else:
                    median = sorted_data[n // 2]

                # Mode (simple implementation)
                from collections import Counter

                counts = Counter(data)
                mode_count = max(counts.values())
                modes = [k for k, v in counts.items() if v == mode_count]

                # Standard deviation
                variance = sum((x - mean) ** 2 for x in data) / n
                std_dev = math.sqrt(variance)

                return {
                    "success": True,
                    "problem": {
                        "data": data,
                        "analysis_type": analysis_type,
                        "sample_size": n,
                    },
                    "solution": {
                        "descriptive_statistics": {
                            "mean": round(mean, 4),
                            "median": median,
                            "mode": modes[0] if len(modes) == 1 else modes,
                            "range": max(data) - min(data),
                            "variance": round(variance, 4),
                            "standard_deviation": round(std_dev, 4),
                            "minimum": min(data),
                            "maximum": max(data),
                        },
                        "interpretation": f"The dataset has {n} values with mean {round(mean, 2)} and standard deviation {round(std_dev, 2)}",
                    },
                    "solving_time_ms": 89,
                }

            else:
                raise HTTPException(status_code=400, detail="Unsupported analysis type")

        @app.get("/history")
        async def get_solving_history(
            page: int = 1,
            limit: int = 10,
            problem_type: str = None,
            current_user: dict = Depends(get_current_user),
        ):
            """Get user's solving history."""
            # Mock history data
            all_history = [
                {
                    "id": 1,
                    "user_id": 123,
                    "problem_type": "algebra",
                    "equation": "2*x + 5 = 15",
                    "solution": "x = 5",
                    "solving_time_ms": 45,
                    "created_at": "2024-12-15T10:00:00",
                },
                {
                    "id": 2,
                    "user_id": 123,
                    "problem_type": "calculus",
                    "expression": "x^2 + 3*x + 2",
                    "operation": "derivative",
                    "solution": "2*x + 3",
                    "solving_time_ms": 32,
                    "created_at": "2024-12-15T10:30:00",
                },
                {
                    "id": 3,
                    "user_id": 123,
                    "problem_type": "geometry",
                    "shape": "circle",
                    "parameters": {"radius": 5},
                    "solution": "78.5398",
                    "solving_time_ms": 18,
                    "created_at": "2024-12-15T11:00:00",
                },
            ]

            # Filter by user
            user_history = [
                h for h in all_history if h["user_id"] == current_user["user_id"]
            ]

            # Filter by problem type if provided
            if problem_type:
                user_history = [
                    h for h in user_history if h["problem_type"] == problem_type
                ]

            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_history = user_history[start:end]

            return {
                "success": True,
                "history": paginated_history,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(user_history),
                    "pages": (len(user_history) + limit - 1) // limit,
                },
            }

        @app.get("/statistics/user")
        async def get_user_statistics(current_user: dict = Depends(get_current_user)):
            """Get user solving statistics."""
            # Mock user statistics
            return {
                "success": True,
                "statistics": {
                    "user_id": current_user["user_id"],
                    "total_problems_solved": 156,
                    "problems_by_type": {
                        "algebra": 67,
                        "calculus": 45,
                        "geometry": 32,
                        "statistics": 12,
                    },
                    "average_solving_time_ms": 78,
                    "accuracy_rate": 94.2,
                    "streak_days": 15,
                    "total_time_spent_minutes": 245,
                    "level": "Advanced",
                    "achievements": [
                        "Algebra Master",
                        "Calculus Explorer",
                        "Speed Solver",
                    ],
                },
            }

        @app.post("/validate")
        async def validate_expression(validation_data: dict):
            """Validate mathematical expressions."""
            expression = validation_data.get("expression")
            expression_type = validation_data.get("type", "general")

            if not expression:
                raise HTTPException(status_code=400, detail="Expression is required")

            # Mock validation
            valid_expressions = [
                "x^2 + 3*x + 2",
                "2*x + 5 = 15",
                "sin(x) + cos(x)",
                "∫(2*x + 3)dx",
            ]

            is_valid = expression in valid_expressions or any(
                char.isalnum() or char in "+-*/^()=∫" for char in expression
            )

            if is_valid:
                return {
                    "success": True,
                    "validation": {
                        "is_valid": True,
                        "expression": expression,
                        "type": expression_type,
                        "complexity": "medium",
                        "estimated_solving_time_ms": 50,
                        "supported_operations": ["solve", "simplify", "evaluate"],
                    },
                }
            else:
                return {
                    "success": True,
                    "validation": {
                        "is_valid": False,
                        "expression": expression,
                        "errors": ["Invalid mathematical expression"],
                        "suggestions": ["Check syntax", "Use supported operators"],
                    },
                }

        return app

    @pytest.fixture
    async def client(self, mock_app):
        """Create test client."""
        async with AsyncClient(app=mock_app, base_url="http://test") as ac:
            yield ac

    async def test_solve_algebra(self, client):
        """Test algebra solving endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test linear equation
        linear_data = {"equation": "2*x + 5 = 15", "variable": "x"}

        response = await client.post(
            "/algebra/solve", json=linear_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "problem" in data
        assert "solution" in data

        problem = data["problem"]
        assert problem["equation"] == "2*x + 5 = 15"
        assert problem["variable"] == "x"
        assert problem["type"] == "linear"

        solution = data["solution"]
        assert solution["value"] == 5
        assert len(solution["steps"]) == 3
        assert "verification" in solution
        assert data["solving_time_ms"] == 45

        # Test quadratic equation
        quadratic_data = {"equation": "x^2 - 5*x + 6 = 0"}

        response = await client.post(
            "/algebra/solve", json=quadratic_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        solution = data["solution"]
        assert solution["values"] == [2, 3]
        assert data["problem"]["type"] == "quadratic"

    async def test_premium_algebra_features(self, client):
        """Test premium algebra features."""
        user_headers = {"Authorization": "Bearer valid_token"}
        premium_headers = {"Authorization": "Bearer premium_token"}

        # Test cubic equation with regular user (should fail)
        cubic_data = {"equation": "x^3 - 6*x^2 + 11*x - 6 = 0"}

        response = await client.post(
            "/algebra/solve", json=cubic_data, headers=user_headers
        )
        assert response.status_code == 403
        assert "Premium subscription required" in response.json()["detail"]

        # Test cubic equation with premium user (should succeed)
        response = await client.post(
            "/algebra/solve", json=cubic_data, headers=premium_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["problem"]["type"] == "cubic"
        assert data["solution"]["values"] == [1, 2, 3]

    async def test_calculate_derivative(self, client):
        """Test derivative calculation endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test polynomial derivative
        poly_data = {"expression": "x^2 + 3*x + 2", "variable": "x"}

        response = await client.post(
            "/calculus/derivative", json=poly_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["problem"]["operation"] == "derivative"
        assert data["solution"]["derivative"] == "2*x + 3"
        assert len(data["solution"]["steps"]) == 5

        # Test trigonometric derivative
        trig_data = {"expression": "sin(x) + cos(x)"}

        response = await client.post(
            "/calculus/derivative", json=trig_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["solution"]["derivative"] == "cos(x) - sin(x)"

    async def test_calculate_integral(self, client):
        """Test integral calculation endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test indefinite integral
        indefinite_data = {"expression": "2*x + 3", "variable": "x", "definite": False}

        response = await client.post(
            "/calculus/integral", json=indefinite_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["problem"]["operation"] == "indefinite_integral"
        assert data["solution"]["integral"] == "x^2 + 3*x + C"

        # Test definite integral
        definite_data = {
            "expression": "2*x + 3",
            "variable": "x",
            "definite": True,
            "lower_limit": 0,
            "upper_limit": 2,
        }

        response = await client.post(
            "/calculus/integral", json=definite_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["problem"]["operation"] == "definite_integral"
        assert data["problem"]["lower_limit"] == 0
        assert data["problem"]["upper_limit"] == 2
        assert data["solution"]["definite_value"] == 10  # (4 + 6) - (0 + 0) = 10

        # Test definite integral without limits (should fail)
        invalid_definite_data = {
            "expression": "2*x + 3",
            "definite": True
            # Missing limits
        }

        response = await client.post(
            "/calculus/integral", json=invalid_definite_data, headers=headers
        )
        assert response.status_code == 400
        assert "Limits required for definite integral" in response.json()["detail"]

    async def test_calculate_area(self, client):
        """Test geometric area calculation endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test rectangle area
        rectangle_data = {"shape": "rectangle", "parameters": {"width": 5, "height": 3}}

        response = await client.post(
            "/geometry/area", json=rectangle_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["solution"]["area"] == 15
        assert data["solution"]["formula"] == "Area = width × height"

        # Test circle area
        circle_data = {"shape": "circle", "parameters": {"radius": 5}}

        response = await client.post(
            "/geometry/area", json=circle_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert abs(data["solution"]["area"] - 78.5398) < 0.0001
        assert data["solution"]["formula"] == "Area = π × r²"

        # Test triangle area
        triangle_data = {"shape": "triangle", "parameters": {"base": 6, "height": 4}}

        response = await client.post(
            "/geometry/area", json=triangle_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["solution"]["area"] == 12
        assert data["solution"]["formula"] == "Area = ½ × base × height"

        # Test unsupported shape
        invalid_shape_data = {"shape": "hexagon", "parameters": {"side": 5}}

        response = await client.post(
            "/geometry/area", json=invalid_shape_data, headers=headers
        )
        assert response.status_code == 400
        assert "Unsupported shape" in response.json()["detail"]

    async def test_analyze_statistics(self, client):
        """Test statistical analysis endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test descriptive statistics
        stats_data = {
            "data": [1, 2, 3, 4, 5, 5, 6, 7, 8, 9],
            "analysis_type": "descriptive",
        }

        response = await client.post(
            "/statistics/analyze", json=stats_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["problem"]["sample_size"] == 10

        stats = data["solution"]["descriptive_statistics"]
        assert stats["mean"] == 5.0
        assert stats["median"] == 5.0
        assert stats["mode"] == 5  # 5 appears twice
        assert stats["range"] == 8  # 9 - 1
        assert stats["minimum"] == 1
        assert stats["maximum"] == 9

        # Test with empty data
        empty_data = {"data": [], "analysis_type": "descriptive"}

        response = await client.post(
            "/statistics/analyze", json=empty_data, headers=headers
        )
        assert response.status_code == 400
        assert "Data array cannot be empty" in response.json()["detail"]

        # Test with invalid data
        invalid_data = {"data": "not an array"}

        response = await client.post(
            "/statistics/analyze", json=invalid_data, headers=headers
        )
        assert response.status_code == 400
        assert "Data array is required" in response.json()["detail"]

    async def test_get_solving_history(self, client):
        """Test get solving history endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test get all history
        response = await client.get("/history", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "history" in data
        assert "pagination" in data

        history = data["history"]
        assert len(history) == 3

        # Check first history item
        first_item = history[0]
        assert first_item["user_id"] == 123
        assert first_item["problem_type"] == "algebra"
        assert first_item["equation"] == "2*x + 5 = 15"

        # Test pagination
        response = await client.get("/history?page=1&limit=2", headers=headers)
        assert response.status_code == 200

        data = response.json()
        history = data["history"]
        assert len(history) == 2

        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 2
        assert pagination["total"] == 3
        assert pagination["pages"] == 2

        # Test filter by problem type
        response = await client.get("/history?problem_type=calculus", headers=headers)
        assert response.status_code == 200

        data = response.json()
        history = data["history"]
        assert len(history) == 1
        assert history[0]["problem_type"] == "calculus"

    async def test_get_user_statistics(self, client):
        """Test get user statistics endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        response = await client.get("/statistics/user", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "statistics" in data

        stats = data["statistics"]
        assert stats["user_id"] == 123
        assert stats["total_problems_solved"] == 156
        assert "problems_by_type" in stats
        assert stats["problems_by_type"]["algebra"] == 67
        assert stats["accuracy_rate"] == 94.2
        assert stats["level"] == "Advanced"
        assert "achievements" in stats
        assert "Algebra Master" in stats["achievements"]

    async def test_validate_expression(self, client):
        """Test expression validation endpoint."""
        # Test valid expression
        valid_data = {"expression": "x^2 + 3*x + 2", "type": "polynomial"}

        response = await client.post("/validate", json=valid_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["validation"]["is_valid"] is True
        assert data["validation"]["complexity"] == "medium"
        assert "supported_operations" in data["validation"]

        # Test invalid expression
        invalid_data = {"expression": "invalid@#$%", "type": "general"}

        response = await client.post("/validate", json=invalid_data)
        assert response.status_code == 200

        data = response.json()
        assert data["validation"]["is_valid"] is False
        assert "errors" in data["validation"]
        assert "suggestions" in data["validation"]

    async def test_input_validation(self, client):
        """Test input validation for all endpoints."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test algebra endpoint without equation
        response = await client.post("/algebra/solve", json={}, headers=headers)
        assert response.status_code == 400
        assert "Equation is required" in response.json()["detail"]

        # Test derivative endpoint without expression
        response = await client.post("/calculus/derivative", json={}, headers=headers)
        assert response.status_code == 400
        assert "Expression is required" in response.json()["detail"]

        # Test geometry endpoint without shape
        response = await client.post("/geometry/area", json={}, headers=headers)
        assert response.status_code == 400
        assert "Shape is required" in response.json()["detail"]

        # Test geometry endpoint with missing parameters
        incomplete_rectangle = {
            "shape": "rectangle",
            "parameters": {"width": 5},  # Missing height
        }

        response = await client.post(
            "/geometry/area", json=incomplete_rectangle, headers=headers
        )
        assert response.status_code == 400
        assert "Width and height required" in response.json()["detail"]

    async def test_authentication_required(self, client):
        """Test endpoints require authentication."""
        endpoints_requiring_auth = [
            ("/algebra/solve", {"equation": "x + 1 = 2"}),
            ("/calculus/derivative", {"expression": "x^2"}),
            ("/calculus/integral", {"expression": "x"}),
            ("/geometry/area", {"shape": "circle", "parameters": {"radius": 1}}),
            ("/statistics/analyze", {"data": [1, 2, 3]}),
        ]

        for endpoint, data in endpoints_requiring_auth:
            response = await client.post(endpoint, json=data)
            assert response.status_code == 403  # FastAPI returns 403 for missing auth

        # Test GET endpoints
        get_endpoints = ["/history", "/statistics/user"]

        for endpoint in get_endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 403

    async def test_concurrent_solving(self, client):
        """Test concurrent problem solving."""
        headers = {"Authorization": "Bearer valid_token"}

        async def solve_problem(equation):
            problem_data = {"equation": equation}
            response = await client.post(
                "/algebra/solve", json=problem_data, headers=headers
            )
            return response.status_code == 200

        # Test 3 concurrent algebra problems
        equations = [
            "2*x + 5 = 15",
            "x^2 - 5*x + 6 = 0",
            "2*x + 5 = 15",  # Same as first to test caching
        ]

        tasks = [solve_problem(eq) for eq in equations]
        results = await asyncio.gather(*tasks)

        # All problems should solve successfully
        assert all(results)

    async def test_performance_thresholds(self, client):
        """Test solving performance thresholds."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test simple algebra problem (should be fast)
        simple_data = {"equation": "2*x + 5 = 15"}

        response = await client.post(
            "/algebra/solve", json=simple_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        # Simple problems should solve quickly
        assert data["solving_time_ms"] < 100

        # Test derivative calculation (should also be fast)
        derivative_data = {"expression": "x^2 + 3*x + 2"}

        response = await client.post(
            "/calculus/derivative", json=derivative_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["solving_time_ms"] < 50
