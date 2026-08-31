"""
Tests for the SecureVault vault storage service.
"""

import json

from src.models.credential import Credential
from src.services import vault_service


def test_save_credentials_encrypts_password_before_writing(
    tmp_path,
    monkeypatch,
):
    test_vault_file = tmp_path / "vault.json"

    monkeypatch.setattr(
        vault_service,
        "VAULT_FILE",
        test_vault_file,
    )
    monkeypatch.setattr(
        vault_service,
        "DATA_DIR",
        tmp_path,
    )
    monkeypatch.setattr(
        vault_service,
        "encrypt_password",
        lambda password: f"encrypted-{password}",
    )

    credential = Credential(
        service="GitHub",
        username="test-user",
        password="SecretPassword123!",
    )

    vault_service.save_credentials([credential])

    vault_data = json.loads(test_vault_file.read_text(encoding="utf-8"))

    assert vault_data[0]["service"] == "GitHub"
    assert vault_data[0]["username"] == "test-user"
    assert vault_data[0]["password"] == "encrypted-SecretPassword123!"
    assert vault_data[0]["password"] != "SecretPassword123!"


def test_load_credentials_decrypts_stored_password(
    tmp_path,
    monkeypatch,
):
    test_vault_file = tmp_path / "vault.json"

    test_vault_file.write_text(
        json.dumps(
            [
                {
                    "service": "GitHub",
                    "username": "test-user",
                    "password": "encrypted-password",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        vault_service,
        "VAULT_FILE",
        test_vault_file,
    )
    monkeypatch.setattr(
        vault_service,
        "decrypt_password",
        lambda password: "SecretPassword123!",
    )

    credentials = vault_service.load_credentials()

    assert len(credentials) == 1
    assert credentials[0].service == "GitHub"
    assert credentials[0].username == "test-user"
    assert credentials[0].password == "SecretPassword123!"


def test_load_credentials_returns_empty_list_when_vault_is_missing(
    tmp_path,
    monkeypatch,
):
    test_vault_file = tmp_path / "vault.json"

    monkeypatch.setattr(
        vault_service,
        "VAULT_FILE",
        test_vault_file,
    )

    credentials = vault_service.load_credentials()

    assert credentials == []


def test_load_credentials_returns_empty_list_when_vault_is_empty(
    tmp_path,
    monkeypatch,
):
    test_vault_file = tmp_path / "vault.json"
    test_vault_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        vault_service,
        "VAULT_FILE",
        test_vault_file,
    )

    credentials = vault_service.load_credentials()

    assert credentials == []
