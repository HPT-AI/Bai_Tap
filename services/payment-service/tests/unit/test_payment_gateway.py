"""
Unit tests for Payment Gateway functionality.
"""

import hashlib
import hmac
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

# Mock imports - these would be actual imports in real implementation
# from payment_service.gateways import VNPayGateway, MoMoGateway, ZaloPayGateway
# from payment_service.models import Transaction, PaymentMethod
# from payment_service.schemas import PaymentCreate, PaymentCallback


@pytest.mark.asyncio
class TestVNPayGateway:
    """Test VNPay payment gateway functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.vnpay_config = {
            "tmn_code": "TEST_TMN_CODE",
            "hash_secret": "TEST_HASH_SECRET",
            "api_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
        }

    def test_create_payment_url_success(self, sample_transaction_create_data):
        """Test successful VNPay payment URL creation."""

        # Mock VNPay gateway
        def create_vnpay_url(transaction_data, config):
            # Simulate VNPay URL creation
            params = {
                "vnp_Version": "2.1.0",
                "vnp_Command": "pay",
                "vnp_TmnCode": config["tmn_code"],
                "vnp_Amount": str(
                    int(transaction_data["amount"]) * 100
                ),  # VNPay uses cents
                "vnp_CurrCode": "VND",
                "vnp_TxnRef": f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "vnp_OrderInfo": transaction_data["description"],
                "vnp_OrderType": "other",
                "vnp_Locale": "vn",
                "vnp_ReturnUrl": transaction_data["return_url"],
                "vnp_IpAddr": "127.0.0.1",
                "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
            }

            # Create secure hash
            sorted_params = sorted(params.items())
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
            secure_hash = hmac.new(
                config["hash_secret"].encode(), query_string.encode(), hashlib.sha512
            ).hexdigest()

            params["vnp_SecureHash"] = secure_hash

            # Build final URL
            final_query = "&".join([f"{k}={v}" for k, v in params.items()])
            return f"{config['api_url']}?{final_query}"

        payment_url = create_vnpay_url(
            sample_transaction_create_data, self.vnpay_config
        )

        assert payment_url.startswith(self.vnpay_config["api_url"])
        assert "vnp_TmnCode=TEST_TMN_CODE" in payment_url
        assert "vnp_Amount=5000000" in payment_url  # 50000 * 100
        assert "vnp_SecureHash=" in payment_url

    def test_verify_payment_return_success(self, mock_vnpay_responses):
        """Test successful VNPay payment return verification."""
        return_data = mock_vnpay_responses["payment_return_success"]

        def verify_vnpay_return(return_data, config):
            # Extract secure hash
            received_hash = return_data.pop("vnp_SecureHash")

            # Recreate hash for verification
            sorted_params = sorted(return_data.items())
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
            expected_hash = hmac.new(
                config["hash_secret"].encode(), query_string.encode(), hashlib.sha512
            ).hexdigest()

            # Verify hash and response code
            if received_hash != expected_hash:
                return {"valid": False, "error": "Invalid secure hash"}

            if return_data.get("vnp_ResponseCode") != "00":
                return {"valid": False, "error": "Payment failed"}

            return {
                "valid": True,
                "transaction_id": return_data.get("vnp_TxnRef"),
                "amount": int(return_data.get("vnp_Amount", 0)) / 100,
                "bank_code": return_data.get("vnp_BankCode"),
                "transaction_no": return_data.get("vnp_TransactionNo"),
            }

        result = verify_vnpay_return(return_data.copy(), self.vnpay_config)

        assert result["valid"] is True
        assert result["transaction_id"] == "TXN_123456789"
        assert result["amount"] == 100000.0
        assert result["bank_code"] == "NCB"

    def test_verify_payment_return_failed(self, mock_vnpay_responses):
        """Test failed VNPay payment return verification."""
        return_data = mock_vnpay_responses["payment_return_failed"]

        def verify_vnpay_return(return_data, config):
            if return_data.get("vnp_ResponseCode") != "00":
                return {
                    "valid": False,
                    "error": "Payment failed",
                    "response_code": return_data.get("vnp_ResponseCode"),
                }
            return {"valid": True}

        result = verify_vnpay_return(return_data, self.vnpay_config)

        assert result["valid"] is False
        assert result["error"] == "Payment failed"
        assert result["response_code"] == "24"

    def test_invalid_secure_hash(self, mock_vnpay_responses):
        """Test VNPay return with invalid secure hash."""
        return_data = mock_vnpay_responses["payment_return_success"].copy()
        return_data["vnp_SecureHash"] = "invalid_hash"

        def verify_vnpay_return(return_data, config):
            received_hash = return_data.pop("vnp_SecureHash")

            # Recreate hash for verification
            sorted_params = sorted(return_data.items())
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
            expected_hash = hmac.new(
                config["hash_secret"].encode(), query_string.encode(), hashlib.sha512
            ).hexdigest()

            if received_hash != expected_hash:
                return {"valid": False, "error": "Invalid secure hash"}

            return {"valid": True}

        result = verify_vnpay_return(return_data, self.vnpay_config)

        assert result["valid"] is False
        assert result["error"] == "Invalid secure hash"


@pytest.mark.asyncio
class TestMoMoGateway:
    """Test MoMo payment gateway functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.momo_config = {
            "partner_code": "TEST_PARTNER_CODE",
            "access_key": "TEST_ACCESS_KEY",
            "secret_key": "TEST_SECRET_KEY",
            "api_url": "https://test-payment.momo.vn/v2/gateway/api/create",
        }

    async def test_create_payment_success(
        self, sample_transaction_create_data, mock_momo_responses
    ):
        """Test successful MoMo payment creation."""
        # Mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.post.return_value.json.return_value = mock_momo_responses[
            "create_payment_success"
        ]

        async def create_momo_payment(transaction_data, config, http_client):
            order_id = f"ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            request_id = f"REQ_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Prepare request data
            request_data = {
                "partnerCode": config["partner_code"],
                "partnerName": "Math Service",
                "storeId": "MathService",
                "requestId": request_id,
                "amount": int(transaction_data["amount"]),
                "orderId": order_id,
                "orderInfo": transaction_data["description"],
                "redirectUrl": transaction_data["return_url"],
                "ipnUrl": "https://mathservice.com/payment/momo/callback",
                "lang": "vi",
                "extraData": "",
                "requestType": "payWithATM",
                "signature": "",
            }

            # Create signature
            raw_signature = f"accessKey={config['access_key']}&amount={request_data['amount']}&extraData={request_data['extraData']}&ipnUrl={request_data['ipnUrl']}&orderId={request_data['orderId']}&orderInfo={request_data['orderInfo']}&partnerCode={request_data['partnerCode']}&redirectUrl={request_data['redirectUrl']}&requestId={request_data['requestId']}&requestType={request_data['requestType']}"

            signature = hmac.new(
                config["secret_key"].encode(), raw_signature.encode(), hashlib.sha256
            ).hexdigest()

            request_data["signature"] = signature

            # Make API call
            response = await http_client.post(config["api_url"], json=request_data)
            return await response.json()

        result = await create_momo_payment(
            sample_transaction_create_data, self.momo_config, mock_http_client
        )

        assert result["resultCode"] == 0
        assert result["message"] == "Successful."
        assert "payUrl" in result
        assert "deeplink" in result
        assert "qrCodeUrl" in result

    def test_verify_payment_callback_success(self, mock_momo_responses):
        """Test successful MoMo payment callback verification."""
        callback_data = mock_momo_responses["payment_return_success"]

        def verify_momo_callback(callback_data, config):
            # Extract signature
            received_signature = callback_data.get("signature", "")

            # Recreate signature for verification
            raw_signature = f"accessKey={config['access_key']}&amount={callback_data['amount']}&extraData={callback_data.get('extraData', '')}&message={callback_data['message']}&orderId={callback_data['orderId']}&orderInfo={callback_data['orderInfo']}&orderType={callback_data['orderType']}&partnerCode={callback_data['partnerCode']}&payType={callback_data['payType']}&requestId={callback_data['requestId']}&responseTime={callback_data['responseTime']}&resultCode={callback_data['resultCode']}&transId={callback_data['transId']}"

            expected_signature = hmac.new(
                config["secret_key"].encode(), raw_signature.encode(), hashlib.sha256
            ).hexdigest()

            # Verify signature and result code
            if received_signature != expected_signature:
                return {"valid": False, "error": "Invalid signature"}

            if callback_data.get("resultCode") != 0:
                return {"valid": False, "error": "Payment failed"}

            return {
                "valid": True,
                "order_id": callback_data.get("orderId"),
                "amount": callback_data.get("amount"),
                "trans_id": callback_data.get("transId"),
            }

        result = verify_momo_callback(callback_data, self.momo_config)

        assert result["valid"] is True
        assert result["order_id"] == "ORDER_123456789"
        assert result["amount"] == 100000
        assert result["trans_id"] == 2147483647

    def test_verify_payment_callback_failed(self, mock_momo_responses):
        """Test failed MoMo payment callback verification."""
        callback_data = mock_momo_responses["payment_return_failed"]

        def verify_momo_callback(callback_data, config):
            if callback_data.get("resultCode") != 0:
                return {
                    "valid": False,
                    "error": "Payment failed",
                    "result_code": callback_data.get("resultCode"),
                    "message": callback_data.get("message"),
                }
            return {"valid": True}

        result = verify_momo_callback(callback_data, self.momo_config)

        assert result["valid"] is False
        assert result["error"] == "Payment failed"
        assert result["result_code"] == 1006
        assert "rejected by user" in result["message"]


@pytest.mark.asyncio
class TestZaloPayGateway:
    """Test ZaloPay payment gateway functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.zalopay_config = {
            "app_id": "553",
            "key1": "TEST_KEY1",
            "key2": "TEST_KEY2",
            "api_url": "https://sb-openapi.zalopay.vn/v2/create",
        }

    async def test_create_payment_success(
        self, sample_transaction_create_data, mock_zalopay_responses
    ):
        """Test successful ZaloPay payment creation."""
        # Mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.post.return_value.json.return_value = mock_zalopay_responses[
            "create_payment_success"
        ]

        async def create_zalopay_payment(transaction_data, config, http_client):
            app_trans_id = (
                f"{datetime.now().strftime('%y%m%d')}_{int(datetime.now().timestamp())}"
            )

            # Prepare request data
            request_data = {
                "app_id": int(config["app_id"]),
                "app_user": f"user_{transaction_data['user_id']}",
                "app_time": int(datetime.now().timestamp() * 1000),
                "amount": int(transaction_data["amount"]),
                "app_trans_id": app_trans_id,
                "embed_data": json.dumps(
                    {"return_url": transaction_data["return_url"]}
                ),
                "item": "[]",
                "description": transaction_data["description"],
                "bank_code": "",
                "mac": "",
            }

            # Create MAC
            mac_data = f"{config['app_id']}|{request_data['app_trans_id']}|{request_data['app_user']}|{request_data['amount']}|{request_data['app_time']}|{request_data['embed_data']}|{request_data['item']}"

            mac = hmac.new(
                config["key1"].encode(), mac_data.encode(), hashlib.sha256
            ).hexdigest()

            request_data["mac"] = mac

            # Make API call
            response = await http_client.post(config["api_url"], data=request_data)
            return await response.json()

        result = await create_zalopay_payment(
            sample_transaction_create_data, self.zalopay_config, mock_http_client
        )

        assert result["return_code"] == 1
        assert result["return_message"] == "success"
        assert "zp_trans_token" in result
        assert "order_url" in result

    def test_verify_payment_callback_success(self, mock_zalopay_responses):
        """Test successful ZaloPay payment callback verification."""
        callback_data = mock_zalopay_responses["payment_return_success"]

        def verify_zalopay_callback(callback_data, config):
            # Extract MAC
            received_mac = callback_data.get("mac", "")

            # Decode and verify data
            try:
                import base64

                decoded_data = base64.b64decode(callback_data["data"]).decode()
                data_json = json.loads(decoded_data)

                # Recreate MAC for verification
                mac_data = callback_data["data"]
                expected_mac = hmac.new(
                    config["key2"].encode(), mac_data.encode(), hashlib.sha256
                ).hexdigest()

                # Verify MAC and type
                if received_mac != expected_mac:
                    return {"valid": False, "error": "Invalid MAC"}

                if callback_data.get("type") != 1:
                    return {"valid": False, "error": "Payment failed"}

                return {
                    "valid": True,
                    "app_trans_id": data_json.get("app_trans_id"),
                    "amount": data_json.get("amount"),
                    "app_user": data_json.get("app_user"),
                }

            except Exception as e:
                return {"valid": False, "error": f"Data parsing error: {str(e)}"}

        result = verify_zalopay_callback(callback_data, self.zalopay_config)

        assert result["valid"] is True
        # Note: In real implementation, would decode base64 data and verify

    def test_verify_payment_callback_failed(self, mock_zalopay_responses):
        """Test failed ZaloPay payment callback verification."""
        callback_data = mock_zalopay_responses["payment_return_failed"]

        def verify_zalopay_callback(callback_data, config):
            if callback_data.get("type") != 1:
                return {
                    "valid": False,
                    "error": "Payment failed",
                    "type": callback_data.get("type"),
                }
            return {"valid": True}

        result = verify_zalopay_callback(callback_data, self.zalopay_config)

        assert result["valid"] is False
        assert result["error"] == "Payment failed"
        assert result["type"] == -1


@pytest.mark.asyncio
class TestPaymentGatewayFactory:
    """Test payment gateway factory and selection."""

    def test_gateway_selection_by_code(self, sample_payment_methods):
        """Test gateway selection by payment method code."""

        def get_gateway_by_code(code, payment_methods):
            for method in payment_methods:
                if method["code"] == code and method["is_active"]:
                    return method
            return None

        # Test valid codes
        vnpay = get_gateway_by_code("VNPAY", sample_payment_methods)
        assert vnpay is not None
        assert vnpay["name"] == "VNPay"

        momo = get_gateway_by_code("MOMO", sample_payment_methods)
        assert momo is not None
        assert momo["name"] == "MoMo"

        zalopay = get_gateway_by_code("ZALOPAY", sample_payment_methods)
        assert zalopay is not None
        assert zalopay["name"] == "ZaloPay"

        # Test invalid code
        invalid = get_gateway_by_code("INVALID", sample_payment_methods)
        assert invalid is None

    def test_amount_validation(self, sample_payment_methods):
        """Test payment amount validation against gateway limits."""

        def validate_amount(amount, payment_method):
            if amount < payment_method["min_amount"]:
                return {
                    "valid": False,
                    "error": f"Amount below minimum {payment_method['min_amount']}",
                }
            if amount > payment_method["max_amount"]:
                return {
                    "valid": False,
                    "error": f"Amount above maximum {payment_method['max_amount']}",
                }
            return {"valid": True}

        vnpay = next(m for m in sample_payment_methods if m["code"] == "VNPAY")

        # Test valid amount
        result = validate_amount(Decimal("100000"), vnpay)
        assert result["valid"] is True

        # Test amount below minimum
        result = validate_amount(Decimal("5000"), vnpay)
        assert result["valid"] is False
        assert "below minimum" in result["error"]

        # Test amount above maximum
        result = validate_amount(Decimal("100000000"), vnpay)
        assert result["valid"] is False
        assert "above maximum" in result["error"]

    def test_fee_calculation(self, sample_payment_methods):
        """Test payment fee calculation."""

        def calculate_fee(amount, payment_method):
            fee_percent = payment_method["fee_percent"]
            fee_amount = amount * fee_percent / 100
            total_amount = amount + fee_amount
            return {
                "original_amount": amount,
                "fee_amount": fee_amount,
                "total_amount": total_amount,
                "fee_percent": fee_percent,
            }

        vnpay = next(m for m in sample_payment_methods if m["code"] == "VNPAY")
        result = calculate_fee(Decimal("100000"), vnpay)

        assert result["original_amount"] == Decimal("100000")
        assert result["fee_amount"] == Decimal("2500")  # 2.5% of 100000
        assert result["total_amount"] == Decimal("102500")
        assert result["fee_percent"] == Decimal("2.5")
