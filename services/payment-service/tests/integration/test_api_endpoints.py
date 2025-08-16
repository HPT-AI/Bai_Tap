"""
Integration tests for Payment Service API endpoints.
"""

import asyncio
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPaymentServiceAPIEndpoints:
    """Integration tests for Payment Service API endpoints."""

    @pytest.fixture
    def mock_app(self):
        """Mock FastAPI application for testing."""
        from fastapi import Depends, FastAPI, HTTPException
        from fastapi.security import HTTPBearer

        app = FastAPI(title="Payment Service", version="1.0.0")
        security = HTTPBearer()

        # Mock authentication dependency
        async def get_current_user(token: str = Depends(security)):
            if token.credentials == "valid_token":
                return {"user_id": 123, "email": "test@example.com", "role": "user"}
            elif token.credentials == "admin_token":
                return {"user_id": 456, "email": "admin@example.com", "role": "admin"}
            else:
                raise HTTPException(status_code=401, detail="Invalid token")

        # Payment method endpoints
        @app.get("/payment-methods")
        async def get_payment_methods():
            """Get available payment methods."""
            return {
                "success": True,
                "payment_methods": [
                    {
                        "code": "vnpay",
                        "name": "VNPay",
                        "description": "VNPay Payment Gateway",
                        "fee_percent": 2.5,
                        "min_amount": 10000,
                        "max_amount": 500000000,
                        "is_active": True,
                    },
                    {
                        "code": "momo",
                        "name": "MoMo",
                        "description": "MoMo E-Wallet",
                        "fee_percent": 2.0,
                        "min_amount": 10000,
                        "max_amount": 50000000,
                        "is_active": True,
                    },
                    {
                        "code": "zalopay",
                        "name": "ZaloPay",
                        "description": "ZaloPay E-Wallet",
                        "fee_percent": 1.8,
                        "min_amount": 10000,
                        "max_amount": 20000000,
                        "is_active": True,
                    },
                ],
            }

        @app.post("/payments/create")
        async def create_payment(
            payment_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Create payment transaction."""
            amount = payment_data.get("amount")
            payment_method = payment_data.get("payment_method")
            description = payment_data.get("description", "Payment")

            # Validation
            if not amount or amount <= 0:
                raise HTTPException(status_code=400, detail="Invalid amount")

            if not payment_method:
                raise HTTPException(status_code=400, detail="Payment method required")

            valid_methods = ["vnpay", "momo", "zalopay"]
            if payment_method not in valid_methods:
                raise HTTPException(status_code=400, detail="Invalid payment method")

            # Amount validation based on payment method
            limits = {
                "vnpay": {"min": 10000, "max": 500000000},
                "momo": {"min": 10000, "max": 50000000},
                "zalopay": {"min": 10000, "max": 20000000},
            }

            method_limits = limits[payment_method]
            if amount < method_limits["min"] or amount > method_limits["max"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Amount must be between {method_limits['min']} and {method_limits['max']} VND",
                )

            # Create transaction
            transaction_id = f"txn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{current_user['user_id']}"

            # Generate payment URL based on method
            if payment_method == "vnpay":
                payment_url = f"https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_TxnRef={transaction_id}&vnp_Amount={amount * 100}"
            elif payment_method == "momo":
                payment_url = (
                    f"https://test-payment.momo.vn/pay/{transaction_id}?amount={amount}"
                )
            else:  # zalopay
                payment_url = f"https://sb-openapi.zalopay.vn/v2/create?app_trans_id={transaction_id}&amount={amount}"

            return {
                "success": True,
                "transaction": {
                    "transaction_id": transaction_id,
                    "user_id": current_user["user_id"],
                    "amount": amount,
                    "payment_method": payment_method,
                    "description": description,
                    "status": "pending",
                    "created_at": datetime.utcnow().isoformat(),
                    "expires_at": (
                        datetime.utcnow() + timedelta(minutes=15)
                    ).isoformat(),
                },
                "payment_url": payment_url,
            }

        @app.post("/payments/callback/{payment_method}")
        async def payment_callback(payment_method: str, callback_data: dict):
            """Handle payment gateway callbacks."""
            if payment_method == "vnpay":
                return handle_vnpay_callback(callback_data)
            elif payment_method == "momo":
                return handle_momo_callback(callback_data)
            elif payment_method == "zalopay":
                return handle_zalopay_callback(callback_data)
            else:
                raise HTTPException(status_code=400, detail="Invalid payment method")

        def handle_vnpay_callback(data):
            """Handle VNPay callback."""
            vnp_response_code = data.get("vnp_ResponseCode")
            vnp_txn_ref = data.get("vnp_TxnRef")
            vnp_amount = data.get("vnp_Amount")
            vnp_secure_hash = data.get("vnp_SecureHash")

            if not all([vnp_response_code, vnp_txn_ref, vnp_amount, vnp_secure_hash]):
                raise HTTPException(
                    status_code=400, detail="Missing required VNPay parameters"
                )

            # Mock hash verification
            expected_hash = "mock_valid_hash"
            if vnp_secure_hash != expected_hash and vnp_secure_hash != "valid_hash":
                raise HTTPException(status_code=400, detail="Invalid VNPay signature")

            status = "completed" if vnp_response_code == "00" else "failed"

            return {
                "success": True,
                "transaction_id": vnp_txn_ref,
                "status": status,
                "amount": int(vnp_amount) // 100,  # VNPay sends amount * 100
                "gateway_response": {
                    "response_code": vnp_response_code,
                    "message": "Success" if vnp_response_code == "00" else "Failed",
                },
            }

        def handle_momo_callback(data):
            """Handle MoMo callback."""
            result_code = data.get("resultCode")
            order_id = data.get("orderId")
            amount = data.get("amount")
            signature = data.get("signature")

            if not all([result_code is not None, order_id, amount, signature]):
                raise HTTPException(
                    status_code=400, detail="Missing required MoMo parameters"
                )

            # Mock signature verification
            if signature not in ["valid_signature", "mock_valid_signature"]:
                raise HTTPException(status_code=400, detail="Invalid MoMo signature")

            status = "completed" if result_code == 0 else "failed"

            return {
                "success": True,
                "transaction_id": order_id,
                "status": status,
                "amount": amount,
                "gateway_response": {
                    "result_code": result_code,
                    "message": "Success" if result_code == 0 else "Failed",
                },
            }

        def handle_zalopay_callback(data):
            """Handle ZaloPay callback."""
            return_code = data.get("return_code")
            app_trans_id = data.get("app_trans_id")
            amount = data.get("amount")
            mac = data.get("mac")

            if not all([return_code is not None, app_trans_id, amount, mac]):
                raise HTTPException(
                    status_code=400, detail="Missing required ZaloPay parameters"
                )

            # Mock MAC verification
            if mac not in ["valid_mac", "mock_valid_mac"]:
                raise HTTPException(status_code=400, detail="Invalid ZaloPay MAC")

            status = "completed" if return_code == 1 else "failed"

            return {
                "success": True,
                "transaction_id": app_trans_id,
                "status": status,
                "amount": amount,
                "gateway_response": {
                    "return_code": return_code,
                    "message": "Success" if return_code == 1 else "Failed",
                },
            }

        @app.get("/transactions")
        async def get_transactions(
            page: int = 1,
            limit: int = 10,
            status: str = None,
            current_user: dict = Depends(get_current_user),
        ):
            """Get user transactions."""
            # Mock transaction data
            all_transactions = [
                {
                    "transaction_id": "txn_20241215_120000_123",
                    "user_id": 123,
                    "amount": 100000,
                    "payment_method": "vnpay",
                    "description": "Test payment",
                    "status": "completed",
                    "created_at": "2024-12-15T12:00:00",
                    "completed_at": "2024-12-15T12:01:00",
                },
                {
                    "transaction_id": "txn_20241215_130000_123",
                    "user_id": 123,
                    "amount": 50000,
                    "payment_method": "momo",
                    "description": "Another payment",
                    "status": "failed",
                    "created_at": "2024-12-15T13:00:00",
                    "failed_at": "2024-12-15T13:01:00",
                },
            ]

            # Filter by user
            user_transactions = [
                t for t in all_transactions if t["user_id"] == current_user["user_id"]
            ]

            # Filter by status if provided
            if status:
                user_transactions = [
                    t for t in user_transactions if t["status"] == status
                ]

            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_transactions = user_transactions[start:end]

            return {
                "success": True,
                "transactions": paginated_transactions,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(user_transactions),
                    "pages": (len(user_transactions) + limit - 1) // limit,
                },
            }

        @app.get("/transactions/{transaction_id}")
        async def get_transaction(
            transaction_id: str, current_user: dict = Depends(get_current_user)
        ):
            """Get specific transaction."""
            # Mock transaction lookup
            if transaction_id == "txn_20241215_120000_123":
                transaction = {
                    "transaction_id": transaction_id,
                    "user_id": 123,
                    "amount": 100000,
                    "payment_method": "vnpay",
                    "description": "Test payment",
                    "status": "completed",
                    "created_at": "2024-12-15T12:00:00",
                    "completed_at": "2024-12-15T12:01:00",
                    "gateway_response": {"response_code": "00", "message": "Success"},
                }

                # Check if user owns this transaction
                if (
                    transaction["user_id"] != current_user["user_id"]
                    and current_user["role"] != "admin"
                ):
                    raise HTTPException(status_code=403, detail="Access denied")

                return {"success": True, "transaction": transaction}
            else:
                raise HTTPException(status_code=404, detail="Transaction not found")

        @app.get("/balance")
        async def get_balance(current_user: dict = Depends(get_current_user)):
            """Get user balance."""
            # Mock balance data
            balance_data = {
                "user_id": current_user["user_id"],
                "current_balance": 500000,
                "total_deposited": 1000000,
                "total_spent": 500000,
                "pending_amount": 0,
                "last_updated": datetime.utcnow().isoformat(),
            }

            return {"success": True, "balance": balance_data}

        @app.post("/balance/deposit")
        async def deposit_balance(
            deposit_data: dict, current_user: dict = Depends(get_current_user)
        ):
            """Deposit to user balance."""
            amount = deposit_data.get("amount")
            transaction_id = deposit_data.get("transaction_id")

            if not amount or amount <= 0:
                raise HTTPException(status_code=400, detail="Invalid amount")

            if not transaction_id:
                raise HTTPException(status_code=400, detail="Transaction ID required")

            # Mock balance update
            new_balance = 500000 + amount  # Mock current balance + deposit

            return {
                "success": True,
                "message": "Balance deposited successfully",
                "balance": {
                    "user_id": current_user["user_id"],
                    "previous_balance": 500000,
                    "deposit_amount": amount,
                    "new_balance": new_balance,
                    "transaction_id": transaction_id,
                },
            }

        # Admin endpoints
        @app.get("/admin/transactions")
        async def admin_get_transactions(
            page: int = 1,
            limit: int = 10,
            status: str = None,
            payment_method: str = None,
            current_user: dict = Depends(get_current_user),
        ):
            """Get all transactions (admin only)."""
            if current_user["role"] != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")

            # Mock all transactions
            all_transactions = [
                {
                    "transaction_id": "txn_20241215_120000_123",
                    "user_id": 123,
                    "amount": 100000,
                    "payment_method": "vnpay",
                    "status": "completed",
                    "created_at": "2024-12-15T12:00:00",
                },
                {
                    "transaction_id": "txn_20241215_130000_456",
                    "user_id": 456,
                    "amount": 200000,
                    "payment_method": "momo",
                    "status": "pending",
                    "created_at": "2024-12-15T13:00:00",
                },
            ]

            # Apply filters
            filtered_transactions = all_transactions
            if status:
                filtered_transactions = [
                    t for t in filtered_transactions if t["status"] == status
                ]
            if payment_method:
                filtered_transactions = [
                    t
                    for t in filtered_transactions
                    if t["payment_method"] == payment_method
                ]

            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_transactions = filtered_transactions[start:end]

            return {
                "success": True,
                "transactions": paginated_transactions,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(filtered_transactions),
                    "pages": (len(filtered_transactions) + limit - 1) // limit,
                },
            }

        @app.get("/admin/statistics")
        async def get_payment_statistics(
            current_user: dict = Depends(get_current_user),
        ):
            """Get payment statistics (admin only)."""
            if current_user["role"] != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")

            return {
                "success": True,
                "statistics": {
                    "total_transactions": 1250,
                    "completed_transactions": 1100,
                    "failed_transactions": 150,
                    "total_amount": 125000000,
                    "success_rate": 88.0,
                    "payment_methods": {
                        "vnpay": {"count": 600, "amount": 60000000},
                        "momo": {"count": 400, "amount": 40000000},
                        "zalopay": {"count": 250, "amount": 25000000},
                    },
                    "daily_stats": [
                        {"date": "2024-12-15", "transactions": 45, "amount": 4500000},
                        {"date": "2024-12-14", "transactions": 52, "amount": 5200000},
                        {"date": "2024-12-13", "transactions": 38, "amount": 3800000},
                    ],
                },
            }

        return app

    @pytest.fixture
    async def client(self, mock_app):
        """Create test client."""
        async with AsyncClient(app=mock_app, base_url="http://test") as ac:
            yield ac

    async def test_get_payment_methods(self, client):
        """Test get payment methods endpoint."""
        response = await client.get("/payment-methods")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "payment_methods" in data

        methods = data["payment_methods"]
        assert len(methods) == 3

        # Check VNPay method
        vnpay = next(m for m in methods if m["code"] == "vnpay")
        assert vnpay["name"] == "VNPay"
        assert vnpay["fee_percent"] == 2.5
        assert vnpay["min_amount"] == 10000
        assert vnpay["max_amount"] == 500000000
        assert vnpay["is_active"] is True

        # Check MoMo method
        momo = next(m for m in methods if m["code"] == "momo")
        assert momo["name"] == "MoMo"
        assert momo["fee_percent"] == 2.0

        # Check ZaloPay method
        zalopay = next(m for m in methods if m["code"] == "zalopay")
        assert zalopay["name"] == "ZaloPay"
        assert zalopay["fee_percent"] == 1.8

    async def test_create_payment(self, client):
        """Test create payment endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test successful VNPay payment creation
        payment_data = {
            "amount": 100000,
            "payment_method": "vnpay",
            "description": "Test payment",
        }

        response = await client.post(
            "/payments/create", json=payment_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "transaction" in data
        assert "payment_url" in data

        transaction = data["transaction"]
        assert transaction["user_id"] == 123
        assert transaction["amount"] == 100000
        assert transaction["payment_method"] == "vnpay"
        assert transaction["status"] == "pending"
        assert "transaction_id" in transaction
        assert "created_at" in transaction
        assert "expires_at" in transaction

        # Check payment URL
        assert "vnpayment.vn" in data["payment_url"]
        assert transaction["transaction_id"] in data["payment_url"]

        # Test MoMo payment creation
        momo_data = {
            "amount": 50000,
            "payment_method": "momo",
            "description": "MoMo test payment",
        }

        response = await client.post(
            "/payments/create", json=momo_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        transaction = data["transaction"]
        assert transaction["payment_method"] == "momo"
        assert "momo.vn" in data["payment_url"]

        # Test ZaloPay payment creation
        zalopay_data = {
            "amount": 75000,
            "payment_method": "zalopay",
            "description": "ZaloPay test payment",
        }

        response = await client.post(
            "/payments/create", json=zalopay_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        transaction = data["transaction"]
        assert transaction["payment_method"] == "zalopay"
        assert "zalopay.vn" in data["payment_url"]

    async def test_create_payment_validation(self, client):
        """Test payment creation validation."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test invalid amount
        invalid_amount_data = {"amount": -1000, "payment_method": "vnpay"}

        response = await client.post(
            "/payments/create", json=invalid_amount_data, headers=headers
        )
        assert response.status_code == 400
        assert "Invalid amount" in response.json()["detail"]

        # Test missing payment method
        missing_method_data = {"amount": 100000}

        response = await client.post(
            "/payments/create", json=missing_method_data, headers=headers
        )
        assert response.status_code == 400
        assert "Payment method required" in response.json()["detail"]

        # Test invalid payment method
        invalid_method_data = {"amount": 100000, "payment_method": "invalid_method"}

        response = await client.post(
            "/payments/create", json=invalid_method_data, headers=headers
        )
        assert response.status_code == 400
        assert "Invalid payment method" in response.json()["detail"]

        # Test amount below minimum for VNPay
        below_min_data = {
            "amount": 5000,  # Below 10000 minimum
            "payment_method": "vnpay",
        }

        response = await client.post(
            "/payments/create", json=below_min_data, headers=headers
        )
        assert response.status_code == 400
        assert "Amount must be between" in response.json()["detail"]

        # Test amount above maximum for MoMo
        above_max_data = {
            "amount": 60000000,  # Above 50000000 maximum
            "payment_method": "momo",
        }

        response = await client.post(
            "/payments/create", json=above_max_data, headers=headers
        )
        assert response.status_code == 400
        assert "Amount must be between" in response.json()["detail"]

    async def test_payment_callbacks(self, client):
        """Test payment gateway callbacks."""
        # Test VNPay successful callback
        vnpay_success_data = {
            "vnp_ResponseCode": "00",
            "vnp_TxnRef": "txn_20241215_120000_123",
            "vnp_Amount": "10000000",  # 100000 * 100
            "vnp_SecureHash": "valid_hash",
        }

        response = await client.post(
            "/payments/callback/vnpay", json=vnpay_success_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["transaction_id"] == "txn_20241215_120000_123"
        assert data["status"] == "completed"
        assert data["amount"] == 100000
        assert data["gateway_response"]["response_code"] == "00"

        # Test VNPay failed callback
        vnpay_failed_data = {
            "vnp_ResponseCode": "01",
            "vnp_TxnRef": "txn_20241215_120001_123",
            "vnp_Amount": "5000000",
            "vnp_SecureHash": "valid_hash",
        }

        response = await client.post("/payments/callback/vnpay", json=vnpay_failed_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "failed"
        assert data["gateway_response"]["response_code"] == "01"

        # Test MoMo successful callback
        momo_success_data = {
            "resultCode": 0,
            "orderId": "txn_20241215_130000_123",
            "amount": 50000,
            "signature": "valid_signature",
        }

        response = await client.post("/payments/callback/momo", json=momo_success_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["status"] == "completed"
        assert data["gateway_response"]["result_code"] == 0

        # Test ZaloPay successful callback
        zalopay_success_data = {
            "return_code": 1,
            "app_trans_id": "txn_20241215_140000_123",
            "amount": 75000,
            "mac": "valid_mac",
        }

        response = await client.post(
            "/payments/callback/zalopay", json=zalopay_success_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["status"] == "completed"
        assert data["gateway_response"]["return_code"] == 1

    async def test_callback_validation(self, client):
        """Test payment callback validation."""
        # Test VNPay callback with invalid signature
        invalid_vnpay_data = {
            "vnp_ResponseCode": "00",
            "vnp_TxnRef": "txn_test",
            "vnp_Amount": "10000000",
            "vnp_SecureHash": "invalid_hash",
        }

        response = await client.post(
            "/payments/callback/vnpay", json=invalid_vnpay_data
        )
        assert response.status_code == 400
        assert "Invalid VNPay signature" in response.json()["detail"]

        # Test MoMo callback with missing parameters
        incomplete_momo_data = {
            "resultCode": 0,
            "orderId": "txn_test"
            # Missing amount and signature
        }

        response = await client.post(
            "/payments/callback/momo", json=incomplete_momo_data
        )
        assert response.status_code == 400
        assert "Missing required MoMo parameters" in response.json()["detail"]

        # Test invalid payment method callback
        response = await client.post("/payments/callback/invalid_method", json={})
        assert response.status_code == 400
        assert "Invalid payment method" in response.json()["detail"]

    async def test_get_transactions(self, client):
        """Test get user transactions endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test get all transactions
        response = await client.get("/transactions", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "transactions" in data
        assert "pagination" in data

        transactions = data["transactions"]
        assert len(transactions) == 2

        # Check first transaction
        first_txn = transactions[0]
        assert first_txn["user_id"] == 123
        assert first_txn["amount"] == 100000
        assert first_txn["payment_method"] == "vnpay"
        assert first_txn["status"] == "completed"

        # Test pagination
        response = await client.get("/transactions?page=1&limit=1", headers=headers)
        assert response.status_code == 200

        data = response.json()
        transactions = data["transactions"]
        assert len(transactions) == 1

        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 1
        assert pagination["total"] == 2
        assert pagination["pages"] == 2

        # Test filter by status
        response = await client.get("/transactions?status=completed", headers=headers)
        assert response.status_code == 200

        data = response.json()
        transactions = data["transactions"]
        assert len(transactions) == 1
        assert transactions[0]["status"] == "completed"

    async def test_get_specific_transaction(self, client):
        """Test get specific transaction endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test get existing transaction
        response = await client.get(
            "/transactions/txn_20241215_120000_123", headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "transaction" in data

        transaction = data["transaction"]
        assert transaction["transaction_id"] == "txn_20241215_120000_123"
        assert transaction["user_id"] == 123
        assert transaction["status"] == "completed"
        assert "gateway_response" in transaction

        # Test get non-existent transaction
        response = await client.get("/transactions/non_existent_txn", headers=headers)
        assert response.status_code == 404
        assert "Transaction not found" in response.json()["detail"]

    async def test_get_balance(self, client):
        """Test get user balance endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        response = await client.get("/balance", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "balance" in data

        balance = data["balance"]
        assert balance["user_id"] == 123
        assert balance["current_balance"] == 500000
        assert balance["total_deposited"] == 1000000
        assert balance["total_spent"] == 500000
        assert balance["pending_amount"] == 0
        assert "last_updated" in balance

    async def test_deposit_balance(self, client):
        """Test deposit balance endpoint."""
        headers = {"Authorization": "Bearer valid_token"}

        # Test successful deposit
        deposit_data = {"amount": 100000, "transaction_id": "txn_20241215_120000_123"}

        response = await client.post(
            "/balance/deposit", json=deposit_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Balance deposited successfully" in data["message"]
        assert "balance" in data

        balance = data["balance"]
        assert balance["user_id"] == 123
        assert balance["previous_balance"] == 500000
        assert balance["deposit_amount"] == 100000
        assert balance["new_balance"] == 600000
        assert balance["transaction_id"] == "txn_20241215_120000_123"

        # Test deposit with invalid amount
        invalid_deposit_data = {"amount": -50000, "transaction_id": "txn_test"}

        response = await client.post(
            "/balance/deposit", json=invalid_deposit_data, headers=headers
        )
        assert response.status_code == 400
        assert "Invalid amount" in response.json()["detail"]

        # Test deposit without transaction ID
        no_txn_data = {"amount": 50000}

        response = await client.post(
            "/balance/deposit", json=no_txn_data, headers=headers
        )
        assert response.status_code == 400
        assert "Transaction ID required" in response.json()["detail"]

    async def test_admin_endpoints(self, client):
        """Test admin-only endpoints."""
        admin_headers = {"Authorization": "Bearer admin_token"}
        user_headers = {"Authorization": "Bearer valid_token"}

        # Test admin get all transactions
        response = await client.get("/admin/transactions", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "transactions" in data

        transactions = data["transactions"]
        assert len(transactions) == 2

        # Test admin get transactions with filters
        response = await client.get(
            "/admin/transactions?status=completed&payment_method=vnpay",
            headers=admin_headers,
        )
        assert response.status_code == 200

        data = response.json()
        transactions = data["transactions"]
        assert len(transactions) == 1
        assert transactions[0]["status"] == "completed"
        assert transactions[0]["payment_method"] == "vnpay"

        # Test admin get statistics
        response = await client.get("/admin/statistics", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "statistics" in data

        stats = data["statistics"]
        assert stats["total_transactions"] == 1250
        assert stats["success_rate"] == 88.0
        assert "payment_methods" in stats
        assert "daily_stats" in stats

        # Test non-admin access to admin endpoints
        response = await client.get("/admin/transactions", headers=user_headers)
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

        response = await client.get("/admin/statistics", headers=user_headers)
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    async def test_authentication_required(self, client):
        """Test endpoints require authentication."""
        # Test endpoints without token
        endpoints_requiring_auth = [
            "/payments/create",
            "/transactions",
            "/transactions/txn_test",
            "/balance",
            "/balance/deposit",
        ]

        for endpoint in endpoints_requiring_auth:
            if endpoint == "/payments/create" or endpoint == "/balance/deposit":
                response = await client.post(endpoint, json={})
            else:
                response = await client.get(endpoint)

            assert response.status_code == 403  # FastAPI returns 403 for missing auth

    async def test_concurrent_payment_creation(self, client):
        """Test concurrent payment creation."""
        headers = {"Authorization": "Bearer valid_token"}

        async def create_payment(amount):
            payment_data = {
                "amount": amount,
                "payment_method": "vnpay",
                "description": f"Concurrent payment {amount}",
            }
            response = await client.post(
                "/payments/create", json=payment_data, headers=headers
            )
            return response.status_code == 200

        # Test 5 concurrent payment creations
        tasks = [create_payment(10000 + i * 1000) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # All payments should succeed
        assert all(results)
