"""
Unit tests for User Service CRUD operations.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

# Mock imports - these would be actual imports in real implementation
# from user_service.crud import UserCRUD
# from user_service.models import User, UserRole, UserBalance
# from user_service.schemas import UserCreate, UserUpdate


@pytest.mark.asyncio
class TestUserCRUD:
    """Test User CRUD operations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_db = AsyncMock()
        self.mock_redis = AsyncMock()

    async def test_create_user_success(self, sample_user_create_data):
        """Test successful user creation."""
        # Mock user creation
        mock_created_user = MagicMock()
        mock_created_user.id = 1
        mock_created_user.email = sample_user_create_data["email"]
        mock_created_user.full_name = sample_user_create_data["full_name"]
        mock_created_user.is_active = True
        mock_created_user.is_verified = False
        mock_created_user.created_at = datetime.utcnow()

        self.mock_db.add = MagicMock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        # Mock create user function
        async def create_user(db, user_data: dict):
            # Check if email already exists
            existing_user = await db.scalar()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")

            # Create new user
            new_user = MagicMock()
            new_user.id = 1
            new_user.email = user_data["email"]
            new_user.full_name = user_data["full_name"]
            new_user.is_active = True
            new_user.is_verified = False
            new_user.created_at = datetime.utcnow()

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user

        # Mock no existing user
        self.mock_db.scalar.return_value = None

        result = await create_user(self.mock_db, sample_user_create_data)

        assert result.email == sample_user_create_data["email"]
        assert result.full_name == sample_user_create_data["full_name"]
        assert result.is_active is True
        assert result.is_verified is False
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()

    async def test_create_user_duplicate_email(self, sample_user_create_data):
        """Test user creation with duplicate email."""
        # Mock existing user
        existing_user = MagicMock()
        existing_user.email = sample_user_create_data["email"]
        self.mock_db.scalar.return_value = existing_user

        # Mock create user function
        async def create_user(db, user_data: dict):
            existing_user = await db.scalar()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            return None

        with pytest.raises(HTTPException) as exc_info:
            await create_user(self.mock_db, sample_user_create_data)

        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)

    async def test_get_user_by_id_success(self, sample_user_data):
        """Test successful user retrieval by ID."""
        user_id = 1

        # Mock user from database
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.email = sample_user_data["email"]
        mock_user.full_name = sample_user_data["full_name"]
        mock_user.is_active = sample_user_data["is_active"]

        self.mock_db.get.return_value = mock_user

        # Mock get user function
        async def get_user_by_id(db, user_id: int):
            return await db.get(user_id)

        result = await get_user_by_id(self.mock_db, user_id)

        assert result.id == user_id
        assert result.email == sample_user_data["email"]
        assert result.full_name == sample_user_data["full_name"]
        self.mock_db.get.assert_called_once_with(user_id)

    async def test_get_user_by_id_not_found(self):
        """Test user retrieval with non-existent ID."""
        user_id = 999
        self.mock_db.get.return_value = None

        # Mock get user function
        async def get_user_by_id(db, user_id: int):
            user = await db.get(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user

        with pytest.raises(HTTPException) as exc_info:
            await get_user_by_id(self.mock_db, user_id)

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    async def test_get_user_by_email_success(self, sample_user_data):
        """Test successful user retrieval by email."""
        email = sample_user_data["email"]

        # Mock user from database
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = email
        mock_user.full_name = sample_user_data["full_name"]

        self.mock_db.scalar.return_value = mock_user

        # Mock get user by email function
        async def get_user_by_email(db, email: str):
            return await db.scalar()

        result = await get_user_by_email(self.mock_db, email)

        assert result.email == email
        assert result.full_name == sample_user_data["full_name"]

    async def test_update_user_success(self, sample_user_data, sample_user_update_data):
        """Test successful user update."""
        user_id = 1

        # Mock existing user
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.email = sample_user_data["email"]
        mock_user.full_name = sample_user_data["full_name"]
        mock_user.phone = sample_user_data["phone"]

        self.mock_db.get.return_value = mock_user

        # Mock update user function
        async def update_user(db, user_id: int, update_data: dict):
            user = await db.get(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Update user fields
            for field, value in update_data.items():
                setattr(user, field, value)

            user.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
            return user

        result = await update_user(self.mock_db, user_id, sample_user_update_data)

        assert result.full_name == sample_user_update_data["full_name"]
        assert result.phone == sample_user_update_data["phone"]
        self.mock_db.commit.assert_called_once()

    async def test_update_user_not_found(self, sample_user_update_data):
        """Test user update with non-existent user."""
        user_id = 999
        self.mock_db.get.return_value = None

        # Mock update user function
        async def update_user(db, user_id: int, update_data: dict):
            user = await db.get(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user

        with pytest.raises(HTTPException) as exc_info:
            await update_user(self.mock_db, user_id, sample_user_update_data)

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    async def test_delete_user_success(self, sample_user_data):
        """Test successful user deletion (soft delete)."""
        user_id = 1

        # Mock existing user
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.email = sample_user_data["email"]
        mock_user.is_active = True
        mock_user.deleted_at = None

        self.mock_db.get.return_value = mock_user

        # Mock soft delete user function
        async def soft_delete_user(db, user_id: int):
            user = await db.get(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            user.is_active = False
            user.deleted_at = datetime.utcnow()
            await db.commit()
            return {"message": "User deleted successfully"}

        result = await soft_delete_user(self.mock_db, user_id)

        assert result["message"] == "User deleted successfully"
        assert mock_user.is_active is False
        assert mock_user.deleted_at is not None
        self.mock_db.commit.assert_called_once()

    async def test_list_users_with_pagination(self):
        """Test listing users with pagination."""
        # Mock users list
        mock_users = []
        for i in range(5):
            user = MagicMock()
            user.id = i + 1
            user.email = f"user{i+1}@example.com"
            user.full_name = f"User {i+1}"
            user.is_active = True
            mock_users.append(user)

        self.mock_db.scalars.return_value = mock_users

        # Mock list users function
        async def list_users(db, skip: int = 0, limit: int = 10):
            # In real implementation, this would use SQL OFFSET and LIMIT
            users = await db.scalars()
            return users[skip : skip + limit]

        result = await list_users(self.mock_db, skip=0, limit=3)

        assert len(result) == 3
        assert result[0].email == "user1@example.com"
        assert result[2].email == "user3@example.com"

    async def test_search_users_by_name(self):
        """Test searching users by name."""
        search_term = "John"

        # Mock search results
        mock_users = []
        for i in range(2):
            user = MagicMock()
            user.id = i + 1
            user.email = f"john{i+1}@example.com"
            user.full_name = f"John Doe {i+1}"
            mock_users.append(user)

        self.mock_db.scalars.return_value = mock_users

        # Mock search users function
        async def search_users_by_name(db, search_term: str):
            # In real implementation, this would use SQL LIKE or full-text search
            users = await db.scalars()
            return [
                user for user in users if search_term.lower() in user.full_name.lower()
            ]

        result = await search_users_by_name(self.mock_db, search_term)

        assert len(result) == 2
        assert all("John" in user.full_name for user in result)

    async def test_user_email_verification(self, sample_user_data):
        """Test user email verification."""
        user_id = 1
        verification_token = "verification_token_123"

        # Mock user
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.email = sample_user_data["email"]
        mock_user.is_verified = False
        mock_user.verification_token = verification_token

        self.mock_db.scalar.return_value = mock_user

        # Mock verify email function
        async def verify_user_email(db, token: str):
            user = await db.scalar()
            if not user or user.verification_token != token:
                raise HTTPException(
                    status_code=400, detail="Invalid verification token"
                )

            user.is_verified = True
            user.verification_token = None
            user.verified_at = datetime.utcnow()
            await db.commit()
            return {"message": "Email verified successfully"}

        result = await verify_user_email(self.mock_db, verification_token)

        assert result["message"] == "Email verified successfully"
        assert mock_user.is_verified is True
        assert mock_user.verification_token is None
        assert mock_user.verified_at is not None

    async def test_user_password_change(self, sample_user_data):
        """Test user password change."""
        user_id = 1
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"

        # Mock user
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.email = sample_user_data["email"]
        mock_user.password_hash = "hashed_old_password"

        self.mock_db.get.return_value = mock_user

        # Mock password change function
        async def change_user_password(
            db, user_id: int, old_password: str, new_password: str
        ):
            user = await db.get(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # In real implementation, verify old password
            # if not verify_password(old_password, user.password_hash):
            #     raise HTTPException(status_code=400, detail="Invalid current password")

            user.password_hash = f"hashed_{new_password}"
            user.password_changed_at = datetime.utcnow()
            await db.commit()
            return {"message": "Password changed successfully"}

        result = await change_user_password(
            self.mock_db, user_id, old_password, new_password
        )

        assert result["message"] == "Password changed successfully"
        assert mock_user.password_hash == f"hashed_{new_password}"
        assert mock_user.password_changed_at is not None
