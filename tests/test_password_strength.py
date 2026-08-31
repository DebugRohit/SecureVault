"""
Tests for the SecureVault password strength analysis service.
"""

import pytest

from src.services.password_strength import check_password_strength


def test_check_password_strength_rejects_empty_password():
    with pytest.raises(
        ValueError,
        match="Password cannot be empty.",
    ):
        check_password_strength("")


def test_check_password_strength_returns_weak():
    result = check_password_strength("password")

    assert result == "Weak"


def test_check_password_strength_returns_medium():
    result = check_password_strength("Password123")

    assert result == "Medium"


def test_check_password_strength_returns_strong():
    result = check_password_strength("StrongPassword123!")

    assert result == "Strong"
