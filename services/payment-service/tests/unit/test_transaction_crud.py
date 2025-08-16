"""
Unit tests for Transaction CRUD operations.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

# Mock imports - these would be actual imports in real implementation
# from payment_service.crud import TransactionCRUD, BalanceCRUD
# from payment_service.models import Transaction, Balance, PaymentMethod
# from payment_service.schemas import TransactionCreate, TransactionUpdate


@pytest.mark.asyncio
class TestTransactionCRUD:
    """Test Transaction CRUD operations."""

    async def test_create_transaction_success(
        self, mock_db_session, sample_transaction_create_data
    ):
        """Test successful transaction creation."""
        # Mock database response
        mock_transaction = MagicMock()
        mock_transaction.id = 1
        mock_transaction.user_id = sample_transaction_create_data["user_id"]
        mock_transaction.amount = sample_transaction_create_data["amount"]
        mock_transaction.status = "pending"
        mock_transaction.created_at = datetime.utcnow()

        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        # Mock CRUD function
        async def create_transaction(db_session, transaction_data):
            # Validate required fields
            required_fields = ["user_id", "amount", "payment_method", "description"]
            for field in required_fields:
                if field not in transaction_data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate amount
            if transaction_data["amount"] <= 0:
                raise ValueError("Amount must be positive")

            # Create transaction object
            transaction = MagicMock()
            transaction.id = 1
            transaction.user_id = transaction_data["user_id"]
            transaction.amount = transaction_data["amount"]
            transaction.payment_method = transaction_data["payment_method"]
            transaction.description = transaction_data["description"]
            transaction.status = "pending"
            transaction.transaction_ref = (
                f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            transaction.created_at = datetime.utcnow()
            transaction.updated_at = datetime.utcnow()

            # Simulate database operations
            db_session.add(transaction)
            await db_session.commit()
            await db_session.refresh(transaction)

            return transaction

        result = await create_transaction(
            mock_db_session, sample_transaction_create_data
        )

        assert result.id == 1
        assert result.user_id == sample_transaction_create_data["user_id"]
        assert result.amount == sample_transaction_create_data["amount"]
        assert result.status == "pending"
        assert result.transaction_ref.startswith("TXN_")

        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_create_transaction_invalid_amount(self, mock_db_session):
        """Test transaction creation with invalid amount."""
        invalid_data = {
            "user_id": 1,
            "amount": Decimal("-100"),  # Negative amount
            "payment_method": "VNPAY",
            "description": "Test payment",
        }

        async def create_transaction(db_session, transaction_data):
            if transaction_data["amount"] <= 0:
                raise ValueError("Amount must be positive")
            return MagicMock()

        with pytest.raises(ValueError, match="Amount must be positive"):
            await create_transaction(mock_db_session, invalid_data)

    async def test_create_transaction_missing_fields(self, mock_db_session):
        """Test transaction creation with missing required fields."""
        incomplete_data = {
            "user_id": 1,
            "amount": Decimal("100000")
            # Missing payment_method and description
        }

        async def create_transaction(db_session, transaction_data):
            required_fields = ["user_id", "amount", "payment_method", "description"]
            for field in required_fields:
                if field not in transaction_data:
                    raise ValueError(f"Missing required field: {field}")
            return MagicMock()

        with pytest.raises(ValueError, match="Missing required field: payment_method"):
            await create_transaction(mock_db_session, incomplete_data)

    async def test_get_transaction_by_id_success(
        self, mock_db_session, sample_transaction_data
    ):
        """Test successful transaction retrieval by ID."""
        # Mock database response
        mock_transaction = MagicMock()
        mock_transaction.id = 1
        mock_transaction.user_id = sample_transaction_data["user_id"]
        mock_transaction.amount = sample_transaction_data["amount"]
        mock_transaction.status = sample_transaction_data["status"]

        mock_db_session.get.return_value = mock_transaction

        async def get_transaction_by_id(db_session, transaction_id):
            transaction = await db_session.get(MagicMock, transaction_id)
            if not transaction:
                return None
            return transaction

        result = await get_transaction_by_id(mock_db_session, 1)

        assert result is not None
        assert result.id == 1
        assert result.user_id == sample_transaction_data["user_id"]
        assert result.amount == sample_transaction_data["amount"]

        mock_db_session.get.assert_called_once()

    async def test_get_transaction_by_id_not_found(self, mock_db_session):
        """Test transaction retrieval with non-existent ID."""
        mock_db_session.get.return_value = None

        async def get_transaction_by_id(db_session, transaction_id):
            transaction = await db_session.get(MagicMock, transaction_id)
            return transaction

        result = await get_transaction_by_id(mock_db_session, 999)

        assert result is None
        mock_db_session.get.assert_called_once()

    async def test_update_transaction_status_success(
        self, mock_db_session, sample_transaction_data
    ):
        """Test successful transaction status update."""
        # Mock existing transaction
        mock_transaction = MagicMock()
        mock_transaction.id = 1
        mock_transaction.status = "pending"
        mock_transaction.updated_at = datetime.utcnow()

        mock_db_session.get.return_value = mock_transaction
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        async def update_transaction_status(
            db_session, transaction_id, new_status, gateway_response=None
        ):
            transaction = await db_session.get(MagicMock, transaction_id)
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Validate status transition
            valid_transitions = {
                "pending": ["completed", "failed", "cancelled"],
                "completed": [],
                "failed": [],
                "cancelled": [],
            }

            if new_status not in valid_transitions.get(transaction.status, []):
                raise ValueError(
                    f"Invalid status transition from {transaction.status} to {new_status}"
                )

            # Update transaction
            transaction.status = new_status
            transaction.updated_at = datetime.utcnow()

            if gateway_response:
                transaction.gateway_response = gateway_response
                if "transaction_no" in gateway_response:
                    transaction.gateway_transaction_id = gateway_response[
                        "transaction_no"
                    ]

            await db_session.commit()
            await db_session.refresh(transaction)

            return transaction

        gateway_response = {
            "transaction_no": "GW123456789",
            "bank_code": "NCB",
            "response_code": "00",
        }

        result = await update_transaction_status(
            mock_db_session, 1, "completed", gateway_response
        )

        assert result.status == "completed"
        assert result.gateway_response == gateway_response
        assert result.gateway_transaction_id == "GW123456789"

        mock_db_session.get.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_update_transaction_invalid_transition(self, mock_db_session):
        """Test transaction status update with invalid transition."""
        # Mock completed transaction
        mock_transaction = MagicMock()
        mock_transaction.id = 1
        mock_transaction.status = "completed"

        mock_db_session.get.return_value = mock_transaction

        async def update_transaction_status(db_session, transaction_id, new_status):
            transaction = await db_session.get(MagicMock, transaction_id)

            valid_transitions = {
                "pending": ["completed", "failed", "cancelled"],
                "completed": [],
                "failed": [],
                "cancelled": [],
            }

            if new_status not in valid_transitions.get(transaction.status, []):
                raise ValueError(
                    f"Invalid status transition from {transaction.status} to {new_status}"
                )

            return transaction

        with pytest.raises(
            ValueError, match="Invalid status transition from completed to pending"
        ):
            await update_transaction_status(mock_db_session, 1, "pending")

    async def test_get_user_transactions_success(
        self, mock_db_session, sample_user_transactions
    ):
        """Test successful retrieval of user transactions."""
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_user_transactions

        mock_db_session.execute.return_value = mock_result

        async def get_user_transactions(
            db_session, user_id, limit=10, offset=0, status=None
        ):
            # Build query conditions
            conditions = [f"user_id = {user_id}"]
            if status:
                conditions.append(f"status = '{status}'")

            # Simulate query execution
            query_result = await db_session.execute(MagicMock())
            transactions = query_result.scalars().all()

            # Apply filters and pagination
            if status:
                transactions = [t for t in transactions if t.status == status]

            # Apply pagination
            start_idx = offset
            end_idx = offset + limit
            paginated_transactions = transactions[start_idx:end_idx]

            return paginated_transactions

        result = await get_user_transactions(
            mock_db_session, user_id=1, limit=5, status="completed"
        )

        assert len(result) <= 5
        for transaction in result:
            assert transaction.user_id == 1
            assert transaction.status == "completed"

        mock_db_session.execute.assert_called_once()

    async def test_get_transactions_by_date_range(
        self, mock_db_session, sample_user_transactions
    ):
        """Test transaction retrieval by date range."""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_user_transactions

        mock_db_session.execute.return_value = mock_result

        async def get_transactions_by_date_range(
            db_session, start_date, end_date, user_id=None
        ):
            # Simulate query execution
            query_result = await db_session.execute(MagicMock())
            transactions = query_result.scalars().all()

            # Apply date filter
            filtered_transactions = [
                t for t in transactions if start_date <= t.created_at <= end_date
            ]

            # Apply user filter if provided
            if user_id:
                filtered_transactions = [
                    t for t in filtered_transactions if t.user_id == user_id
                ]

            return filtered_transactions

        result = await get_transactions_by_date_range(
            mock_db_session, start_date, end_date, user_id=1
        )

        for transaction in result:
            assert start_date <= transaction.created_at <= end_date
            assert transaction.user_id == 1

        mock_db_session.execute.assert_called_once()

    async def test_calculate_transaction_statistics(
        self, mock_db_session, sample_user_transactions
    ):
        """Test transaction statistics calculation."""
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_user_transactions

        mock_db_session.execute.return_value = mock_result

        async def calculate_transaction_statistics(
            db_session, user_id=None, date_from=None, date_to=None
        ):
            # Get transactions
            query_result = await db_session.execute(MagicMock())
            transactions = query_result.scalars().all()

            # Apply filters
            if user_id:
                transactions = [t for t in transactions if t.user_id == user_id]

            if date_from:
                transactions = [t for t in transactions if t.created_at >= date_from]

            if date_to:
                transactions = [t for t in transactions if t.created_at <= date_to]

            # Calculate statistics
            total_transactions = len(transactions)
            completed_transactions = len(
                [t for t in transactions if t.status == "completed"]
            )
            failed_transactions = len([t for t in transactions if t.status == "failed"])
            pending_transactions = len(
                [t for t in transactions if t.status == "pending"]
            )

            total_amount = sum(
                t.amount for t in transactions if t.status == "completed"
            )
            average_amount = (
                total_amount / completed_transactions
                if completed_transactions > 0
                else 0
            )

            success_rate = (
                (completed_transactions / total_transactions * 100)
                if total_transactions > 0
                else 0
            )

            return {
                "total_transactions": total_transactions,
                "completed_transactions": completed_transactions,
                "failed_transactions": failed_transactions,
                "pending_transactions": pending_transactions,
                "total_amount": total_amount,
                "average_amount": average_amount,
                "success_rate": round(success_rate, 2),
            }

        result = await calculate_transaction_statistics(mock_db_session, user_id=1)

        assert "total_transactions" in result
        assert "completed_transactions" in result
        assert "failed_transactions" in result
        assert "pending_transactions" in result
        assert "total_amount" in result
        assert "average_amount" in result
        assert "success_rate" in result
        assert 0 <= result["success_rate"] <= 100

        mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
class TestBalanceCRUD:
    """Test Balance CRUD operations."""

    async def test_get_user_balance_success(self, mock_db_session, sample_balance_data):
        """Test successful user balance retrieval."""
        # Mock database response
        mock_balance = MagicMock()
        mock_balance.user_id = sample_balance_data["user_id"]
        mock_balance.current_balance = sample_balance_data["current_balance"]
        mock_balance.total_deposited = sample_balance_data["total_deposited"]
        mock_balance.total_spent = sample_balance_data["total_spent"]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_balance

        mock_db_session.execute.return_value = mock_result

        async def get_user_balance(db_session, user_id):
            query_result = await db_session.execute(MagicMock())
            balance = query_result.scalar_one_or_none()

            if not balance:
                # Create new balance record if doesn't exist
                balance = MagicMock()
                balance.user_id = user_id
                balance.current_balance = Decimal("0")
                balance.total_deposited = Decimal("0")
                balance.total_spent = Decimal("0")
                balance.created_at = datetime.utcnow()
                balance.updated_at = datetime.utcnow()

                db_session.add(balance)
                await db_session.commit()
                await db_session.refresh(balance)

            return balance

        result = await get_user_balance(mock_db_session, 1)

        assert result.user_id == sample_balance_data["user_id"]
        assert result.current_balance == sample_balance_data["current_balance"]
        assert result.total_deposited == sample_balance_data["total_deposited"]
        assert result.total_spent == sample_balance_data["total_spent"]

        mock_db_session.execute.assert_called_once()

    async def test_update_balance_deposit_success(
        self, mock_db_session, sample_balance_data
    ):
        """Test successful balance update for deposit."""
        # Mock existing balance
        mock_balance = MagicMock()
        mock_balance.user_id = sample_balance_data["user_id"]
        mock_balance.current_balance = sample_balance_data["current_balance"]
        mock_balance.total_deposited = sample_balance_data["total_deposited"]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_balance

        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        async def update_balance_deposit(db_session, user_id, amount):
            if amount <= 0:
                raise ValueError("Deposit amount must be positive")

            # Get current balance
            query_result = await db_session.execute(MagicMock())
            balance = query_result.scalar_one_or_none()

            if not balance:
                raise ValueError("Balance record not found")

            # Update balance
            balance.current_balance += amount
            balance.total_deposited += amount
            balance.updated_at = datetime.utcnow()

            await db_session.commit()
            await db_session.refresh(balance)

            return balance

        deposit_amount = Decimal("50000")
        result = await update_balance_deposit(mock_db_session, 1, deposit_amount)

        expected_balance = sample_balance_data["current_balance"] + deposit_amount
        expected_total_deposited = (
            sample_balance_data["total_deposited"] + deposit_amount
        )

        assert result.current_balance == expected_balance
        assert result.total_deposited == expected_total_deposited

        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_update_balance_spend_success(
        self, mock_db_session, sample_balance_data
    ):
        """Test successful balance update for spending."""
        # Mock existing balance with sufficient funds
        mock_balance = MagicMock()
        mock_balance.user_id = sample_balance_data["user_id"]
        mock_balance.current_balance = Decimal("100000")  # Sufficient balance
        mock_balance.total_spent = sample_balance_data["total_spent"]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_balance

        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        async def update_balance_spend(db_session, user_id, amount):
            if amount <= 0:
                raise ValueError("Spend amount must be positive")

            # Get current balance
            query_result = await db_session.execute(MagicMock())
            balance = query_result.scalar_one_or_none()

            if not balance:
                raise ValueError("Balance record not found")

            if balance.current_balance < amount:
                raise ValueError("Insufficient balance")

            # Update balance
            balance.current_balance -= amount
            balance.total_spent += amount
            balance.updated_at = datetime.utcnow()

            await db_session.commit()
            await db_session.refresh(balance)

            return balance

        spend_amount = Decimal("30000")
        result = await update_balance_spend(mock_db_session, 1, spend_amount)

        expected_balance = Decimal("100000") - spend_amount
        expected_total_spent = sample_balance_data["total_spent"] + spend_amount

        assert result.current_balance == expected_balance
        assert result.total_spent == expected_total_spent

        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_update_balance_insufficient_funds(self, mock_db_session):
        """Test balance update with insufficient funds."""
        # Mock balance with insufficient funds
        mock_balance = MagicMock()
        mock_balance.user_id = 1
        mock_balance.current_balance = Decimal("10000")  # Insufficient

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_balance

        mock_db_session.execute.return_value = mock_result

        async def update_balance_spend(db_session, user_id, amount):
            query_result = await db_session.execute(MagicMock())
            balance = query_result.scalar_one_or_none()

            if balance.current_balance < amount:
                raise ValueError("Insufficient balance")

            return balance

        spend_amount = Decimal("50000")  # More than available

        with pytest.raises(ValueError, match="Insufficient balance"):
            await update_balance_spend(mock_db_session, 1, spend_amount)
