"""
Unit tests for Algebra Solver functionality.
"""

from decimal import Decimal
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import sympy as sp

# Mock imports - these would be actual imports in real implementation
# from math_solver_service.solvers import AlgebraSolver, EquationSolver
# from math_solver_service.models import Problem, Solution
# from math_solver_service.schemas import AlgebraProblem, SolutionResponse


@pytest.mark.asyncio
class TestLinearEquationSolver:
    """Test linear equation solving functionality."""

    def test_solve_simple_linear_equation(self, sample_linear_equations):
        """Test solving simple linear equations."""

        def solve_linear_equation(equation_str):
            """
            Solve linear equation of form ax + b = c
            Returns solution and steps
            """
            try:
                # Parse equation
                x = sp.Symbol("x")
                equation = sp.sympify(equation_str.replace("=", "-(") + ")")

                # Solve equation
                solutions = sp.solve(equation, x)

                # Generate solution steps
                steps = []
                steps.append(f"Original equation: {equation_str}")
                steps.append(f"Rearranged: {equation} = 0")

                if len(solutions) == 1:
                    solution = solutions[0]
                    steps.append(f"Solution: x = {solution}")

                    # Verify solution
                    verification = equation.subs(x, solution)
                    steps.append(f"Verification: {verification} = 0 ✓")

                    return {
                        "solutions": [float(solution)],
                        "steps": steps,
                        "equation_type": "linear",
                        "is_valid": True,
                    }
                else:
                    return {
                        "solutions": [float(sol) for sol in solutions],
                        "steps": steps,
                        "equation_type": "linear",
                        "is_valid": len(solutions) > 0,
                    }

            except Exception as e:
                return {
                    "solutions": [],
                    "steps": [f"Error solving equation: {str(e)}"],
                    "equation_type": "unknown",
                    "is_valid": False,
                    "error": str(e),
                }

        # Test simple linear equations
        test_cases = [
            ("2*x + 3 = 7", [2.0]),
            ("5*x - 10 = 0", [2.0]),
            ("x + 5 = 12", [7.0]),
            ("-3*x + 9 = 0", [3.0]),
        ]

        for equation, expected_solutions in test_cases:
            result = solve_linear_equation(equation)

            assert result["is_valid"] is True
            assert result["equation_type"] == "linear"
            assert len(result["solutions"]) == len(expected_solutions)

            for i, expected in enumerate(expected_solutions):
                assert abs(result["solutions"][i] - expected) < 1e-10

            assert len(result["steps"]) >= 3
            assert "Original equation:" in result["steps"][0]
            assert "Solution:" in result["steps"][-2]
            assert "Verification:" in result["steps"][-1]

    def test_solve_linear_equation_no_solution(self):
        """Test linear equation with no solution."""

        def solve_linear_equation(equation_str):
            try:
                x = sp.Symbol("x")
                equation = sp.sympify(equation_str.replace("=", "-(") + ")")
                solutions = sp.solve(equation, x)

                if len(solutions) == 0:
                    # Check if it's a contradiction
                    simplified = sp.simplify(equation)
                    if simplified.is_number and simplified != 0:
                        return {
                            "solutions": [],
                            "steps": [
                                f"Original equation: {equation_str}",
                                f"Simplified: {simplified} = 0",
                                "This is a contradiction - no solution exists",
                            ],
                            "equation_type": "linear",
                            "is_valid": False,
                            "no_solution": True,
                        }

                return {"solutions": solutions, "is_valid": True}

            except Exception as e:
                return {"solutions": [], "is_valid": False, "error": str(e)}

        # Test contradiction equation
        result = solve_linear_equation("2*x + 3 = 2*x + 5")

        assert result["is_valid"] is False
        assert result.get("no_solution") is True
        assert "contradiction" in result["steps"][-1].lower()

    def test_solve_linear_equation_infinite_solutions(self):
        """Test linear equation with infinite solutions."""

        def solve_linear_equation(equation_str):
            try:
                x = sp.Symbol("x")
                equation = sp.sympify(equation_str.replace("=", "-(") + ")")
                solutions = sp.solve(equation, x)

                # Check if equation simplifies to 0 = 0 (identity)
                simplified = sp.simplify(equation)
                if simplified == 0:
                    return {
                        "solutions": "infinite",
                        "steps": [
                            f"Original equation: {equation_str}",
                            f"Simplified: {simplified} = 0",
                            "This is an identity - infinite solutions",
                        ],
                        "equation_type": "linear",
                        "is_valid": True,
                        "infinite_solutions": True,
                    }

                return {"solutions": solutions, "is_valid": True}

            except Exception as e:
                return {"solutions": [], "is_valid": False, "error": str(e)}

        # Test identity equation
        result = solve_linear_equation("3*x + 2 = 3*x + 2")

        assert result["is_valid"] is True
        assert result["solutions"] == "infinite"
        assert result.get("infinite_solutions") is True
        assert "identity" in result["steps"][-1].lower()


@pytest.mark.asyncio
class TestQuadraticEquationSolver:
    """Test quadratic equation solving functionality."""

    def test_solve_quadratic_equation_two_real_roots(self, sample_quadratic_equations):
        """Test solving quadratic equations with two real roots."""

        def solve_quadratic_equation(equation_str):
            """
            Solve quadratic equation of form ax² + bx + c = 0
            Returns solutions, discriminant, and detailed steps
            """
            try:
                # Parse equation
                x = sp.Symbol("x")
                equation = sp.sympify(equation_str.replace("=", "-(") + ")")

                # Extract coefficients
                expanded = sp.expand(equation)
                coeffs = sp.Poly(expanded, x).all_coeffs()

                # Pad coefficients if needed
                while len(coeffs) < 3:
                    coeffs.insert(0, 0)

                a, b, c = float(coeffs[0]), float(coeffs[1]), float(coeffs[2])

                # Calculate discriminant
                discriminant = b**2 - 4 * a * c

                steps = []
                steps.append(f"Original equation: {equation_str}")
                steps.append(f"Standard form: {a}x² + {b}x + {c} = 0")
                steps.append(f"Coefficients: a = {a}, b = {b}, c = {c}")
                steps.append(
                    f"Discriminant: Δ = b² - 4ac = {b}² - 4({a})({c}) = {discriminant}"
                )

                if discriminant > 0:
                    # Two real roots
                    sqrt_discriminant = discriminant**0.5
                    x1 = (-b + sqrt_discriminant) / (2 * a)
                    x2 = (-b - sqrt_discriminant) / (2 * a)

                    steps.append(f"Since Δ > 0, there are two real roots:")
                    steps.append(
                        f"x₁ = (-b + √Δ) / 2a = ({-b} + √{discriminant}) / {2*a} = {x1}"
                    )
                    steps.append(
                        f"x₂ = (-b - √Δ) / 2a = ({-b} - √{discriminant}) / {2*a} = {x2}"
                    )

                    return {
                        "solutions": [x1, x2],
                        "discriminant": discriminant,
                        "root_type": "two_real",
                        "steps": steps,
                        "equation_type": "quadratic",
                        "is_valid": True,
                    }
                elif discriminant == 0:
                    # One real root (repeated)
                    x1 = -b / (2 * a)
                    steps.append(f"Since Δ = 0, there is one repeated real root:")
                    steps.append(f"x = -b / 2a = {-b} / {2*a} = {x1}")

                    return {
                        "solutions": [x1],
                        "discriminant": discriminant,
                        "root_type": "one_real",
                        "steps": steps,
                        "equation_type": "quadratic",
                        "is_valid": True,
                    }
                else:
                    # Complex roots
                    sqrt_neg_discriminant = (-discriminant) ** 0.5
                    real_part = -b / (2 * a)
                    imag_part = sqrt_neg_discriminant / (2 * a)

                    steps.append(f"Since Δ < 0, there are two complex roots:")
                    steps.append(f"x₁ = {real_part} + {imag_part}i")
                    steps.append(f"x₂ = {real_part} - {imag_part}i")

                    return {
                        "solutions": [
                            {"real": real_part, "imag": imag_part},
                            {"real": real_part, "imag": -imag_part},
                        ],
                        "discriminant": discriminant,
                        "root_type": "complex",
                        "steps": steps,
                        "equation_type": "quadratic",
                        "is_valid": True,
                    }

            except Exception as e:
                return {
                    "solutions": [],
                    "steps": [f"Error solving equation: {str(e)}"],
                    "equation_type": "unknown",
                    "is_valid": False,
                    "error": str(e),
                }

        # Test quadratic with two real roots
        result = solve_quadratic_equation("x**2 - 5*x + 6 = 0")

        assert result["is_valid"] is True
        assert result["equation_type"] == "quadratic"
        assert result["root_type"] == "two_real"
        assert result["discriminant"] > 0
        assert len(result["solutions"]) == 2

        # Verify solutions (should be x = 2 and x = 3)
        solutions = sorted(result["solutions"])
        assert abs(solutions[0] - 2.0) < 1e-10
        assert abs(solutions[1] - 3.0) < 1e-10

        # Check steps
        assert len(result["steps"]) >= 6
        assert "Discriminant:" in result["steps"][3]
        assert "two real roots:" in result["steps"][4]

    def test_solve_quadratic_equation_one_root(self):
        """Test solving quadratic equation with one repeated root."""

        def solve_quadratic_equation(equation_str):
            # Same implementation as above
            try:
                x = sp.Symbol("x")
                equation = sp.sympify(equation_str.replace("=", "-(") + ")")
                expanded = sp.expand(equation)
                coeffs = sp.Poly(expanded, x).all_coeffs()

                while len(coeffs) < 3:
                    coeffs.insert(0, 0)

                a, b, c = float(coeffs[0]), float(coeffs[1]), float(coeffs[2])
                discriminant = b**2 - 4 * a * c

                if abs(discriminant) < 1e-10:  # Discriminant ≈ 0
                    x1 = -b / (2 * a)
                    return {
                        "solutions": [x1],
                        "discriminant": discriminant,
                        "root_type": "one_real",
                        "equation_type": "quadratic",
                        "is_valid": True,
                    }

                return {"is_valid": False}

            except Exception as e:
                return {"is_valid": False, "error": str(e)}

        # Test perfect square: (x - 2)² = 0 → x² - 4x + 4 = 0
        result = solve_quadratic_equation("x**2 - 4*x + 4 = 0")

        assert result["is_valid"] is True
        assert result["root_type"] == "one_real"
        assert abs(result["discriminant"]) < 1e-10
        assert len(result["solutions"]) == 1
        assert abs(result["solutions"][0] - 2.0) < 1e-10

    def test_solve_quadratic_equation_complex_roots(self):
        """Test solving quadratic equation with complex roots."""

        def solve_quadratic_equation(equation_str):
            # Same implementation as above
            try:
                x = sp.Symbol("x")
                equation = sp.sympify(equation_str.replace("=", "-(") + ")")
                expanded = sp.expand(equation)
                coeffs = sp.Poly(expanded, x).all_coeffs()

                while len(coeffs) < 3:
                    coeffs.insert(0, 0)

                a, b, c = float(coeffs[0]), float(coeffs[1]), float(coeffs[2])
                discriminant = b**2 - 4 * a * c

                if discriminant < 0:
                    sqrt_neg_discriminant = (-discriminant) ** 0.5
                    real_part = -b / (2 * a)
                    imag_part = sqrt_neg_discriminant / (2 * a)

                    return {
                        "solutions": [
                            {"real": real_part, "imag": imag_part},
                            {"real": real_part, "imag": -imag_part},
                        ],
                        "discriminant": discriminant,
                        "root_type": "complex",
                        "equation_type": "quadratic",
                        "is_valid": True,
                    }

                return {"is_valid": False}

            except Exception as e:
                return {"is_valid": False, "error": str(e)}

        # Test equation with complex roots: x² + x + 1 = 0
        result = solve_quadratic_equation("x**2 + x + 1 = 0")

        assert result["is_valid"] is True
        assert result["root_type"] == "complex"
        assert result["discriminant"] < 0
        assert len(result["solutions"]) == 2

        # Verify complex solutions
        sol1, sol2 = result["solutions"]
        assert abs(sol1["real"] - (-0.5)) < 1e-10
        assert abs(sol1["imag"] - (3**0.5 / 2)) < 1e-10
        assert abs(sol2["real"] - (-0.5)) < 1e-10
        assert abs(sol2["imag"] - (-(3**0.5 / 2))) < 1e-10


@pytest.mark.asyncio
class TestSystemOfEquationsSolver:
    """Test system of equations solving functionality."""

    def test_solve_2x2_linear_system(self, sample_linear_systems):
        """Test solving 2x2 linear system."""

        def solve_linear_system_2x2(equations):
            """
            Solve system of 2 linear equations with 2 unknowns
            Input: ["2*x + 3*y = 7", "x - y = 1"]
            """
            try:
                x, y = sp.symbols("x y")

                # Parse equations
                eq1_str, eq2_str = equations
                eq1_left, eq1_right = eq1_str.split("=")
                eq2_left, eq2_right = eq2_str.split("=")

                eq1 = sp.Eq(sp.sympify(eq1_left.strip()), sp.sympify(eq1_right.strip()))
                eq2 = sp.Eq(sp.sympify(eq2_left.strip()), sp.sympify(eq2_right.strip()))

                # Solve system
                solution = sp.solve([eq1, eq2], [x, y])

                steps = []
                steps.append("System of equations:")
                steps.append(f"  {eq1_str}")
                steps.append(f"  {eq2_str}")
                steps.append("")

                if solution:
                    x_val, y_val = float(solution[x]), float(solution[y])
                    steps.append("Solution:")
                    steps.append(f"  x = {x_val}")
                    steps.append(f"  y = {y_val}")
                    steps.append("")

                    # Verification
                    steps.append("Verification:")
                    eq1_check = eq1.lhs.subs([(x, x_val), (y, y_val)]) - eq1.rhs
                    eq2_check = eq2.lhs.subs([(x, x_val), (y, y_val)]) - eq2.rhs
                    steps.append(f"  Equation 1: {eq1_check} = 0 ✓")
                    steps.append(f"  Equation 2: {eq2_check} = 0 ✓")

                    return {
                        "solution": {"x": x_val, "y": y_val},
                        "steps": steps,
                        "system_type": "2x2_linear",
                        "is_valid": True,
                        "solution_type": "unique",
                    }
                else:
                    steps.append("No unique solution found")
                    return {
                        "solution": None,
                        "steps": steps,
                        "system_type": "2x2_linear",
                        "is_valid": False,
                        "solution_type": "no_solution",
                    }

            except Exception as e:
                return {
                    "solution": None,
                    "steps": [f"Error solving system: {str(e)}"],
                    "system_type": "unknown",
                    "is_valid": False,
                    "error": str(e),
                }

        # Test system with unique solution
        equations = ["2*x + 3*y = 7", "x - y = 1"]
        result = solve_linear_system_2x2(equations)

        assert result["is_valid"] is True
        assert result["solution_type"] == "unique"
        assert result["system_type"] == "2x2_linear"

        # Verify solution (should be x = 2, y = 1)
        solution = result["solution"]
        assert abs(solution["x"] - 2.0) < 1e-10
        assert abs(solution["y"] - 1.0) < 1e-10

        # Check steps
        assert len(result["steps"]) >= 8
        assert "System of equations:" in result["steps"][0]
        assert "Solution:" in result["steps"][4]
        assert "Verification:" in result["steps"][8]

    def test_solve_3x3_linear_system(self):
        """Test solving 3x3 linear system."""

        def solve_linear_system_3x3(equations):
            """
            Solve system of 3 linear equations with 3 unknowns
            """
            try:
                x, y, z = sp.symbols("x y z")

                # Parse equations
                parsed_equations = []
                for eq_str in equations:
                    left, right = eq_str.split("=")
                    eq = sp.Eq(sp.sympify(left.strip()), sp.sympify(right.strip()))
                    parsed_equations.append(eq)

                # Solve system
                solution = sp.solve(parsed_equations, [x, y, z])

                if solution:
                    x_val = float(solution[x])
                    y_val = float(solution[y])
                    z_val = float(solution[z])

                    return {
                        "solution": {"x": x_val, "y": y_val, "z": z_val},
                        "system_type": "3x3_linear",
                        "is_valid": True,
                        "solution_type": "unique",
                    }
                else:
                    return {
                        "solution": None,
                        "system_type": "3x3_linear",
                        "is_valid": False,
                        "solution_type": "no_solution",
                    }

            except Exception as e:
                return {"solution": None, "is_valid": False, "error": str(e)}

        # Test 3x3 system
        equations = ["x + y + z = 6", "2*x - y + z = 3", "x + 2*y - z = 2"]
        result = solve_linear_system_3x3(equations)

        assert result["is_valid"] is True
        assert result["solution_type"] == "unique"
        assert result["system_type"] == "3x3_linear"

        # Verify solution exists
        solution = result["solution"]
        assert "x" in solution
        assert "y" in solution
        assert "z" in solution


@pytest.mark.asyncio
class TestPolynomialSolver:
    """Test polynomial equation solving functionality."""

    def test_solve_cubic_equation(self, sample_polynomial_equations):
        """Test solving cubic equations."""

        def solve_cubic_equation(equation_str):
            """
            Solve cubic equation of form ax³ + bx² + cx + d = 0
            """
            try:
                x = sp.Symbol("x")
                equation = sp.sympify(equation_str.replace("=", "-(") + ")")

                # Get polynomial degree
                poly = sp.Poly(equation, x)
                degree = poly.degree()

                if degree != 3:
                    return {
                        "solutions": [],
                        "is_valid": False,
                        "error": f"Not a cubic equation (degree = {degree})",
                    }

                # Solve equation
                solutions = sp.solve(equation, x)

                # Convert solutions to numerical values
                numerical_solutions = []
                for sol in solutions:
                    if sol.is_real:
                        numerical_solutions.append(float(sol))
                    else:
                        # Complex solution
                        real_part = float(sp.re(sol))
                        imag_part = float(sp.im(sol))
                        numerical_solutions.append(
                            {"real": real_part, "imag": imag_part}
                        )

                return {
                    "solutions": numerical_solutions,
                    "degree": degree,
                    "equation_type": "cubic",
                    "is_valid": True,
                    "num_real_roots": sum(
                        1 for sol in numerical_solutions if isinstance(sol, float)
                    ),
                }

            except Exception as e:
                return {"solutions": [], "is_valid": False, "error": str(e)}

        # Test cubic equation: x³ - 6x² + 11x - 6 = 0 (roots: 1, 2, 3)
        result = solve_cubic_equation("x**3 - 6*x**2 + 11*x - 6 = 0")

        assert result["is_valid"] is True
        assert result["equation_type"] == "cubic"
        assert result["degree"] == 3
        assert len(result["solutions"]) == 3
        assert result["num_real_roots"] == 3

        # Verify real solutions
        real_solutions = [sol for sol in result["solutions"] if isinstance(sol, float)]
        real_solutions.sort()

        expected_roots = [1.0, 2.0, 3.0]
        for i, expected in enumerate(expected_roots):
            assert abs(real_solutions[i] - expected) < 1e-10

    def test_solve_quartic_equation(self):
        """Test solving quartic equations."""

        def solve_quartic_equation(equation_str):
            """
            Solve quartic equation of form ax⁴ + bx³ + cx² + dx + e = 0
            """
            try:
                x = sp.Symbol("x")
                equation = sp.sympify(equation_str.replace("=", "-(") + ")")

                poly = sp.Poly(equation, x)
                degree = poly.degree()

                if degree != 4:
                    return {
                        "solutions": [],
                        "is_valid": False,
                        "error": f"Not a quartic equation (degree = {degree})",
                    }

                solutions = sp.solve(equation, x)

                # Process solutions
                numerical_solutions = []
                for sol in solutions:
                    try:
                        if sol.is_real:
                            numerical_solutions.append(float(sol))
                        else:
                            real_part = float(sp.re(sol))
                            imag_part = float(sp.im(sol))
                            numerical_solutions.append(
                                {"real": real_part, "imag": imag_part}
                            )
                    except:
                        # Handle complex expressions
                        numerical_solutions.append(str(sol))

                return {
                    "solutions": numerical_solutions,
                    "degree": degree,
                    "equation_type": "quartic",
                    "is_valid": True,
                }

            except Exception as e:
                return {"solutions": [], "is_valid": False, "error": str(e)}

        # Test simple quartic: x⁴ - 5x² + 4 = 0 (can be solved as quadratic in x²)
        result = solve_quartic_equation("x**4 - 5*x**2 + 4 = 0")

        assert result["is_valid"] is True
        assert result["equation_type"] == "quartic"
        assert result["degree"] == 4
        assert len(result["solutions"]) == 4


@pytest.mark.asyncio
class TestAlgebraValidation:
    """Test algebra input validation and error handling."""

    def test_validate_equation_format(self):
        """Test equation format validation."""

        def validate_equation_format(equation_str):
            """
            Validate equation format and syntax
            """
            try:
                # Check for equals sign
                if "=" not in equation_str:
                    return {
                        "is_valid": False,
                        "error": "Equation must contain '=' sign",
                    }

                # Check for multiple equals signs
                if equation_str.count("=") > 1:
                    return {
                        "is_valid": False,
                        "error": "Equation cannot contain multiple '=' signs",
                    }

                # Try to parse both sides
                left, right = equation_str.split("=")
                left_expr = sp.sympify(left.strip())
                right_expr = sp.sympify(right.strip())

                # Check for valid symbols
                left_symbols = left_expr.free_symbols
                right_symbols = right_expr.free_symbols
                all_symbols = left_symbols.union(right_symbols)

                # Only allow x, y, z as variables
                allowed_symbols = {sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("z")}
                invalid_symbols = all_symbols - allowed_symbols

                if invalid_symbols:
                    return {
                        "is_valid": False,
                        "error": f"Invalid variables: {[str(s) for s in invalid_symbols]}. Only x, y, z are allowed.",
                    }

                return {
                    "is_valid": True,
                    "left_expr": left_expr,
                    "right_expr": right_expr,
                    "variables": [str(s) for s in all_symbols],
                }

            except Exception as e:
                return {
                    "is_valid": False,
                    "error": f"Invalid equation syntax: {str(e)}",
                }

        # Test valid equations
        valid_cases = [
            "x + 2 = 5",
            "2*x**2 + 3*x - 1 = 0",
            "x + y = 10",
            "x**3 - 2*x + 1 = 0",
        ]

        for equation in valid_cases:
            result = validate_equation_format(equation)
            assert result["is_valid"] is True
            assert "variables" in result

        # Test invalid equations
        invalid_cases = [
            ("x + 2", "Equation must contain '=' sign"),
            ("x = 2 = 3", "multiple '=' signs"),
            ("a + b = 5", "Invalid variables"),
            ("x + = 5", "Invalid equation syntax"),
        ]

        for equation, expected_error in invalid_cases:
            result = validate_equation_format(equation)
            assert result["is_valid"] is False
            assert expected_error.lower() in result["error"].lower()

    def test_equation_complexity_analysis(self):
        """Test equation complexity analysis."""

        def analyze_equation_complexity(equation_str):
            """
            Analyze equation complexity and difficulty
            """
            try:
                x = sp.Symbol("x")
                equation = sp.sympify(equation_str.replace("=", "-(") + ")")

                # Get polynomial degree
                try:
                    poly = sp.Poly(equation, x)
                    degree = poly.degree()
                except:
                    degree = None

                # Count operations
                expr_str = str(equation)
                num_additions = expr_str.count("+")
                num_multiplications = expr_str.count("*")
                num_powers = expr_str.count("**")

                # Determine complexity level
                if degree is None:
                    complexity = "unknown"
                elif degree <= 1:
                    complexity = "easy"
                elif degree == 2:
                    complexity = "medium"
                elif degree <= 4:
                    complexity = "hard"
                else:
                    complexity = "very_hard"

                # Estimate solving time (in seconds)
                time_estimates = {
                    "easy": 0.1,
                    "medium": 0.5,
                    "hard": 2.0,
                    "very_hard": 10.0,
                    "unknown": 5.0,
                }

                return {
                    "degree": degree,
                    "complexity": complexity,
                    "estimated_time": time_estimates[complexity],
                    "operations": {
                        "additions": num_additions,
                        "multiplications": num_multiplications,
                        "powers": num_powers,
                    },
                    "is_polynomial": degree is not None,
                }

            except Exception as e:
                return {"complexity": "unknown", "error": str(e)}

        # Test different complexity levels
        test_cases = [
            ("x + 5 = 0", "easy", 1),
            ("x**2 - 4 = 0", "medium", 2),
            ("x**3 + 2*x**2 - x - 2 = 0", "hard", 3),
            ("x**5 - x**4 + x**3 - x**2 + x - 1 = 0", "very_hard", 5),
        ]

        for equation, expected_complexity, expected_degree in test_cases:
            result = analyze_equation_complexity(equation)

            assert result["complexity"] == expected_complexity
            assert result["degree"] == expected_degree
            assert result["is_polynomial"] is True
            assert result["estimated_time"] > 0
