"""
Tests for the SecureVault password generation service.
"""

import string

import pytest

from src.services.password_generator import generate_password


def test_generate_password_uses_default_length():
    password = generate_password()

    assert len(password) == 16


def test_generate_password_uses_requested_length():
    password = generate_password(24)

    assert len(password) == 24


def test_generate_password_contains_lowercase_character():
    password = generate_password()

    assert any(character.islower() for character in password)


def test_generate_password_contains_uppercase_character():
    password = generate_password()

    assert any(character.isupper() for character in password)


def test_generate_password_contains_digit():
    password = generate_password()

    assert any(character.isdigit() for character in password)


def test_generate_password_contains_special_character():
    password = generate_password()

    assert any(character in string.punctuation for character in password)


def test_generate_password_rejects_short_length():
    with pytest.raises(
        ValueError,
        match="Password length must be at least 12.",
    ):
        generate_password(11)
