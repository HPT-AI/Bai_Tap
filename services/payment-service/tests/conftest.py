"""
Pytest configuration and fixtures for Payment Service tests.
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
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


# Payment method fixtures
@pytest.fixture
def sample_payment_methods():
    """Sample payment methods for testing."""
    return [
        {
            "id": 1,
            "name": "VNPay",
            "code": "VNPAY",
            "is_active": True,
            "fee_percent": Decimal("2.5"),
            "min_amount": Decimal("10000"),
            "max_amount": Decimal("50000000"),
            "config": {
                "tmn_code": "TEST_TMN_CODE",
                "hash_secret": "TEST_HASH_SECRET",
                "api_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
            },
        },
        {
            "id": 2,
            "name": "MoMo",
            "code": "MOMO",
            "is_active": True,
            "fee_percent": Decimal("2.0"),
            "min_amount": Decimal("5000"),
            "max_amount": Decimal("20000000"),
            "config": {
                "partner_code": "TEST_PARTNER_CODE",
                "access_key": "TEST_ACCESS_KEY",
                "secret_key": "TEST_SECRET_KEY",
                "api_url": "https://test-payment.momo.vn/v2/gateway/api/create",
            },
        },
        {
            "id": 3,
            "name": "ZaloPay",
            "code": "ZALOPAY",
            "is_active": True,
            "fee_percent": Decimal("1.8"),
            "min_amount": Decimal("1000"),
            "max_amount": Decimal("30000000"),
            "config": {
                "app_id": "TEST_APP_ID",
                "key1": "TEST_KEY1",
                "key2": "TEST_KEY2",
                "api_url": "https://sb-openapi.zalopay.vn/v2/create",
            },
        },
    ]


# Transaction fixtures
@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "user_id": 1,
        "amount": Decimal("100000"),
        "currency": "VND",
        "payment_method_id": 1,
        "description": "Nạp tiền vào tài khoản",
        "metadata": {
            "user_ip": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "return_url": "https://mathservice.com/payment/return",
        },
    }


@pytest.fixture
def sample_transaction_create_data():
    """Sample transaction creation data for testing."""
    return {
        "user_id": 1,
        "amount": Decimal("50000"),
        "currency": "VND",
        "payment_method_code": "VNPAY",
        "description": "Thanh toán dịch vụ giải toán",
        "return_url": "https://mathservice.com/payment/success",
        "cancel_url": "https://mathservice.com/payment/cancel",
    }


@pytest.fixture
def sample_successful_transaction():
    """Sample successful transaction for testing."""
    return {
        "id": "TXN_123456789",
        "user_id": 1,
        "amount": Decimal("100000"),
        "currency": "VND",
        "payment_method_id": 1,
        "status": "completed",
        "gateway_transaction_id": "VNPAY_123456789",
        "gateway_response": {
            "vnp_ResponseCode": "00",
            "vnp_Message": "Giao dịch thành công",
            "vnp_TransactionStatus": "00",
        },
        "created_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_failed_transaction():
    """Sample failed transaction for testing."""
    return {
        "id": "TXN_987654321",
        "user_id": 1,
        "amount": Decimal("200000"),
        "currency": "VND",
        "payment_method_id": 1,
        "status": "failed",
        "gateway_transaction_id": "VNPAY_987654321",
        "gateway_response": {
            "vnp_ResponseCode": "24",
            "vnp_Message": "Giao dịch bị hủy",
            "vnp_TransactionStatus": "02",
        },
        "created_at": datetime.utcnow(),
        "failed_at": datetime.utcnow(),
        "failure_reason": "User cancelled transaction",
    }


# Balance fixtures
@pytest.fixture
def sample_balance_data():
    """Sample balance data for testing."""
    return {
        "user_id": 1,
        "current_balance": Decimal("500000"),
        "total_deposited": Decimal("1000000"),
        "total_spent": Decimal("500000"),
        "last_transaction_date": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


# Transaction log fixtures
@pytest.fixture
def sample_transaction_log():
    """Sample transaction log for testing."""
    return {
        "id": 1,
        "transaction_id": "TXN_123456789",
        "action": "payment_initiated",
        "status": "pending",
        "request_data": {"amount": "100000", "payment_method": "VNPAY", "user_id": 1},
        "response_data": {
            "payment_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?...",
            "order_id": "ORDER_123456789",
        },
        "created_at": datetime.utcnow(),
    }


# Mock payment gateway responses
@pytest.fixture
def mock_vnpay_responses():
    """Mock VNPay gateway responses."""
    return {
        "create_payment_success": {
            "payment_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=10000000&vnp_Command=pay&vnp_CreateDate=20240115103000&vnp_CurrCode=VND&vnp_IpAddr=192.168.1.100&vnp_Locale=vn&vnp_OrderInfo=Nap+tien+vao+tai+khoan&vnp_OrderType=other&vnp_ReturnUrl=https%3A%2F%2Fmathservice.com%2Fpayment%2Freturn&vnp_TmnCode=TEST_TMN_CODE&vnp_TxnRef=TXN_123456789&vnp_Version=2.1.0&vnp_SecureHash=test_secure_hash"
        },
        "payment_return_success": {
            "vnp_Amount": "10000000",
            "vnp_BankCode": "NCB",
            "vnp_BankTranNo": "VNP14123456",
            "vnp_CardType": "ATM",
            "vnp_OrderInfo": "Nap tien vao tai khoan",
            "vnp_PayDate": "20240115103500",
            "vnp_ResponseCode": "00",
            "vnp_TmnCode": "TEST_TMN_CODE",
            "vnp_TransactionNo": "14123456",
            "vnp_TransactionStatus": "00",
            "vnp_TxnRef": "TXN_123456789",
            "vnp_SecureHash": "test_return_hash",
        },
        "payment_return_failed": {
            "vnp_Amount": "10000000",
            "vnp_OrderInfo": "Nap tien vao tai khoan",
            "vnp_ResponseCode": "24",
            "vnp_TmnCode": "TEST_TMN_CODE",
            "vnp_TransactionStatus": "02",
            "vnp_TxnRef": "TXN_123456789",
            "vnp_SecureHash": "test_failed_hash",
        },
    }


@pytest.fixture
def mock_momo_responses():
    """Mock MoMo gateway responses."""
    return {
        "create_payment_success": {
            "partnerCode": "TEST_PARTNER_CODE",
            "orderId": "ORDER_123456789",
            "requestId": "REQ_123456789",
            "amount": 100000,
            "responseTime": 1705123456789,
            "message": "Successful.",
            "resultCode": 0,
            "payUrl": "https://test-payment.momo.vn/v2/gateway/pay?t=test_token",
            "deeplink": "momo://app?action=payWithAppInApp&token=test_token",
            "qrCodeUrl": "https://test-payment.momo.vn/v2/gateway/qr?t=test_token",
        },
        "payment_return_success": {
            "partnerCode": "TEST_PARTNER_CODE",
            "orderId": "ORDER_123456789",
            "requestId": "REQ_123456789",
            "amount": 100000,
            "orderInfo": "Nạp tiền vào tài khoản",
            "orderType": "momo_wallet",
            "transId": 2147483647,
            "resultCode": 0,
            "message": "Successful.",
            "payType": "qr",
            "responseTime": 1705123456789,
            "extraData": "",
            "signature": "test_signature",
        },
        "payment_return_failed": {
            "partnerCode": "TEST_PARTNER_CODE",
            "orderId": "ORDER_123456789",
            "requestId": "REQ_123456789",
            "amount": 100000,
            "orderInfo": "Nạp tiền vào tài khoản",
            "orderType": "momo_wallet",
            "resultCode": 1006,
            "message": "Transaction is rejected by user",
            "responseTime": 1705123456789,
            "extraData": "",
            "signature": "test_failed_signature",
        },
    }


@pytest.fixture
def mock_zalopay_responses():
    """Mock ZaloPay gateway responses."""
    return {
        "create_payment_success": {
            "return_code": 1,
            "return_message": "success",
            "sub_return_code": 1,
            "sub_return_message": "",
            "zp_trans_token": "test_zp_trans_token",
            "order_url": "https://sb-openapi.zalopay.vn/v2/gateway/pay?token=test_zp_trans_token",
            "order_token": "test_order_token",
        },
        "payment_return_success": {
            "data": "eyJhcHBfaWQiOjU1MywiYXBwX3RyYW5zX2lkIjoiT1JERVJfMTIzNDU2Nzg5IiwiYXBwX3RpbWUiOjE3MDUxMjM0NTY3ODksImFwcF91c2VyIjoidXNlcjEiLCJhbW91bnQiOjEwMDAwMCwiZW1iZWRfZGF0YSI6IntcInJldHVybl91cmxcIjpcImh0dHBzOi8vbWF0aHNlcnZpY2UuY29tL3BheW1lbnQvcmV0dXJuXCJ9IiwiaXRlbSI6IltdIiwiYmFua19jb2RlIjoiIiwicGF5bWVudF9tZXRob2QiOiIifQ==",
            "mac": "test_mac_signature",
            "type": 1,
        },
        "payment_return_failed": {
            "data": "eyJhcHBfaWQiOjU1MywiYXBwX3RyYW5zX2lkIjoiT1JERVJfMTIzNDU2Nzg5IiwiYXBwX3RpbWUiOjE3MDUxMjM0NTY3ODksImFwcF91c2VyIjoidXNlcjEiLCJhbW91bnQiOjEwMDAwMCwiZW1iZWRfZGF0YSI6IntcInJldHVybl91cmxcIjpcImh0dHBzOi8vbWF0aHNlcnZpY2UuY29tL3BheW1lbnQvcmV0dXJuXCJ9IiwiaXRlbSI6IltdIiwiYmFua19jb2RlIjoiIiwicGF5bWVudF9tZXRob2QiOiIifQ==",
            "mac": "test_failed_mac_signature",
            "type": -1,
        },
    }


# Mock external services
@pytest.fixture
def mock_payment_gateways():
    """Mock payment gateway services."""
    mock_gateways = {"vnpay": MagicMock(), "momo": MagicMock(), "zalopay": MagicMock()}

    # Configure VNPay mock
    mock_gateways["vnpay"].create_payment_url = AsyncMock()
    mock_gateways["vnpay"].verify_payment_return = AsyncMock()
    mock_gateways["vnpay"].query_transaction = AsyncMock()

    # Configure MoMo mock
    mock_gateways["momo"].create_payment = AsyncMock()
    mock_gateways["momo"].verify_payment_return = AsyncMock()
    mock_gateways["momo"].query_transaction = AsyncMock()

    # Configure ZaloPay mock
    mock_gateways["zalopay"].create_payment = AsyncMock()
    mock_gateways["zalopay"].verify_payment_return = AsyncMock()
    mock_gateways["zalopay"].query_transaction = AsyncMock()

    return mock_gateways


@pytest.fixture
def mock_notification_service():
    """Mock notification service for testing."""
    mock_service = MagicMock()
    mock_service.send_payment_success_notification = AsyncMock(return_value=True)
    mock_service.send_payment_failed_notification = AsyncMock(return_value=True)
    mock_service.send_refund_notification = AsyncMock(return_value=True)
    return mock_service


# Test client fixtures
@pytest_asyncio.fixture
async def test_client():
    """Test client for API testing."""
    from fastapi.testclient import TestClient
    from payment_service.main import app

    with TestClient(app) as client:
        yield client


# Environment fixtures
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("PAYMENT_SERVICE_DB_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")

    # VNPay test config
    monkeypatch.setenv("VNPAY_TMN_CODE", "TEST_TMN_CODE")
    monkeypatch.setenv("VNPAY_HASH_SECRET", "TEST_HASH_SECRET")
    monkeypatch.setenv(
        "VNPAY_API_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    )

    # MoMo test config
    monkeypatch.setenv("MOMO_PARTNER_CODE", "TEST_PARTNER_CODE")
    monkeypatch.setenv("MOMO_ACCESS_KEY", "TEST_ACCESS_KEY")
    monkeypatch.setenv("MOMO_SECRET_KEY", "TEST_SECRET_KEY")
    monkeypatch.setenv(
        "MOMO_API_URL", "https://test-payment.momo.vn/v2/gateway/api/create"
    )

    # ZaloPay test config
    monkeypatch.setenv("ZALOPAY_APP_ID", "553")
    monkeypatch.setenv("ZALOPAY_KEY1", "TEST_KEY1")
    monkeypatch.setenv("ZALOPAY_KEY2", "TEST_KEY2")
    monkeypatch.setenv("ZALOPAY_API_URL", "https://sb-openapi.zalopay.vn/v2/create")


# Performance testing fixtures
@pytest.fixture
def performance_threshold():
    """Performance thresholds for payment operations."""
    return {
        "create_payment_time": 2.0,  # seconds
        "process_callback_time": 1.0,  # seconds
        "balance_update_time": 0.5,  # seconds
        "transaction_query_time": 1.0,  # seconds
    }


# Security testing fixtures
@pytest.fixture
def security_test_data():
    """Security test data for payment testing."""
    return {
        "invalid_amounts": [
            Decimal("-100"),
            Decimal("0"),
            Decimal("999999999999"),
            "invalid_amount",
            None,
        ],
        "invalid_currencies": ["USD", "EUR", "INVALID", "", None],
        "malicious_descriptions": [
            "<script>alert('xss')</script>",
            "'; DROP TABLE transactions; --",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
        ],
    }
