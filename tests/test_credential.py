"""
Tests for the SecureVault credential model.
"""

from src.models.credential import Credential


def test_credential_stores_service_username_and_password():
    credential = Credential(
        service="GitHub",
        username="rohith@example.com",
        password="StrongPassword123!",
    )

    assert credential.service == "GitHub"
    assert credential.username == "rohith@example.com"
    assert credential.password == "StrongPassword123!"


def test_credentials_with_same_values_are_equal():
    first_credential = Credential(
        service="GitHub",
        username="test-user",
        password="TestPassword123!",
    )
    second_credential = Credential(
        service="GitHub",
        username="test-user",
        password="TestPassword123!",
    )

    assert first_credential == second_credential


def test_credential_repr_does_not_expose_password():
    credential = Credential(
        service="GitHub",
        username="test-user",
        password="SecretPassword123!",
    )

    credential_repr = repr(credential)

    assert "SecretPassword123!" not in credential_repr


def test_credential_converts_to_dictionary():
    credential = Credential(
        service="GitHub",
        username="test-user",
        password="SecretPassword123!",
    )

    result = credential.to_dict()

    assert result == {
        "service": "GitHub",
        "username": "test-user",
        "password": "SecretPassword123!",
    }
