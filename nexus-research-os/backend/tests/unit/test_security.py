"""
Unit tests for security module.
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenData,
)
from app.core.config import get_settings

settings = get_settings()


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = hash_password("testpassword123")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_salts(self):
        hashed1 = hash_password("testpassword123")
        hashed2 = hash_password("testpassword123")
        assert hashed1 != hashed2  # Different salts

    def test_verify_password_correct(self):
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False


class TestTokenCreation:
    def test_create_access_token_returns_string(self):
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)
        
        # Decode to verify expiry
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in decoded
        assert decoded["type"] == "access"

    def test_create_refresh_token(self):
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["type"] == "refresh"
        assert "exp" in decoded


class TestTokenDecoding:
    def test_decode_valid_access_token(self):
        data = {
            "sub": "user123",
            "email": "test@example.com",
            "org_id": "org456",
            "roles": ["researcher"]
        }
        token = create_access_token(data)
        decoded = decode_token(token)
        
        assert decoded.user_id == "user123"
        assert decoded.email == "test@example.com"
        assert decoded.organization_id == "org456"
        assert "researcher" in decoded.roles

    def test_decode_valid_refresh_token(self):
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        decoded = decode_token(token)
        
        assert decoded.user_id == "user123"

    def test_decode_invalid_token(self):
        with pytest.raises(Exception) as exc_info:
            decode_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_decode_expired_token(self):
        data = {"sub": "user123"}
        # Create token that expired 1 hour ago
        expired_delta = timedelta(hours=-1)
        token = create_access_token(data, expires_delta=expired_delta)
        
        with pytest.raises(Exception) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_decode_token_missing_user_id(self):
        data = {"email": "test@example.com"}  # Missing sub
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire, "type": "access"})
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        with pytest.raises(Exception) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401


class TestTokenData:
    def test_token_data_default_values(self):
        token_data = TokenData()
        assert token_data.user_id is None
        assert token_data.email is None
        assert token_data.organization_id is None
        assert token_data.roles == []

    def test_token_data_with_values(self):
        token_data = TokenData(
            user_id="user123",
            email="test@example.com",
            organization_id="org456",
            roles=["admin", "researcher"]
        )
        assert token_data.user_id == "user123"
        assert token_data.roles == ["admin", "researcher"]
