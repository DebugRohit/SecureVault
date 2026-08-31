"""
Tests for the SecureVault backup service.
"""

import json

import pytest

from src.services import backup_service


def test_create_vault_backup_rejects_missing_vault(
    tmp_path,
    monkeypatch,
):
    test_vault_file = tmp_path / "vault.json"
    test_backup_dir = tmp_path / "backups"

    monkeypatch.setattr(
        backup_service,
        "VAULT_FILE",
        test_vault_file,
    )
    monkeypatch.setattr(
        backup_service,
        "BACKUP_DIR",
        test_backup_dir,
    )

    with pytest.raises(
        FileNotFoundError,
        match="Vault file not found.",
    ):
        backup_service.create_vault_backup()


def test_create_vault_backup_creates_backup_directory(
    tmp_path,
    monkeypatch,
):
    test_vault_file = tmp_path / "vault.json"
    test_backup_dir = tmp_path / "backups"

    test_vault_file.write_text(
        "encrypted-vault-data",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        backup_service,
        "VAULT_FILE",
        test_vault_file,
    )
    monkeypatch.setattr(
        backup_service,
        "BACKUP_DIR",
        test_backup_dir,
    )

    backup_service.create_vault_backup()

    assert test_backup_dir.exists()
    assert test_backup_dir.is_dir()


def test_create_vault_backup_creates_json_backup_file(
    tmp_path,
    monkeypatch,
):
    test_vault_file = tmp_path / "vault.json"
    test_backup_dir = tmp_path / "backups"

    test_vault_file.write_text(
        "encrypted-vault-data",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        backup_service,
        "VAULT_FILE",
        test_vault_file,
    )
    monkeypatch.setattr(
        backup_service,
        "BACKUP_DIR",
        test_backup_dir,
    )

    backup_file = backup_service.create_vault_backup()

    assert backup_file.exists()
    assert backup_file.suffix == ".json"
    assert backup_file.name.startswith("vault_backup_")


def test_create_vault_backup_preserves_vault_content(
    tmp_path,
    monkeypatch,
):
    test_vault_file = tmp_path / "vault.json"
    test_backup_dir = tmp_path / "backups"

    vault_data = [
        {
            "service": "GitHub",
            "username": "test-user",
            "password": "encrypted-password-token",
        }
    ]

    test_vault_file.write_text(
        json.dumps(vault_data),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        backup_service,
        "VAULT_FILE",
        test_vault_file,
    )
    monkeypatch.setattr(
        backup_service,
        "BACKUP_DIR",
        test_backup_dir,
    )

    backup_file = backup_service.create_vault_backup()

    original_content = test_vault_file.read_text(encoding="utf-8")
    backup_content = backup_file.read_text(encoding="utf-8")

    assert backup_content == original_content
    assert "encrypted-password-token" in backup_content


def test_create_vault_backup_returns_backup_path(
    tmp_path,
    monkeypatch,
):
    test_vault_file = tmp_path / "vault.json"
    test_backup_dir = tmp_path / "backups"

    test_vault_file.write_text(
        "encrypted-vault-data",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        backup_service,
        "VAULT_FILE",
        test_vault_file,
    )
    monkeypatch.setattr(
        backup_service,
        "BACKUP_DIR",
        test_backup_dir,
    )

    backup_file = backup_service.create_vault_backup()

    assert backup_file.parent == test_backup_dir
    assert backup_file.exists()


def test_list_vault_backups_returns_empty_list_when_directory_missing(
    tmp_path,
    monkeypatch,
):
    test_backup_dir = tmp_path / "backups"

    monkeypatch.setattr(
        backup_service,
        "BACKUP_DIR",
        test_backup_dir,
    )

    backups = backup_service.list_vault_backups()

    assert backups == []


def test_list_vault_backups_returns_only_vault_backups(
    tmp_path,
    monkeypatch,
):
    test_backup_dir = tmp_path / "backups"
    test_backup_dir.mkdir()

    valid_backup = test_backup_dir / "vault_backup_20260709_120000_000000.json"
    unrelated_file = test_backup_dir / "notes.txt"

    valid_backup.write_text("[]", encoding="utf-8")
    unrelated_file.write_text("test", encoding="utf-8")

    monkeypatch.setattr(
        backup_service,
        "BACKUP_DIR",
        test_backup_dir,
    )

    backups = backup_service.list_vault_backups()

    assert backups == [valid_backup]


def test_validate_vault_backup_rejects_missing_backup(
    tmp_path,
):
    backup_file = tmp_path / "missing.json"

    with pytest.raises(
        FileNotFoundError,
        match="Backup file not found.",
    ):
        backup_service.validate_vault_backup(backup_file)


def test_validate_vault_backup_rejects_invalid_json(
    tmp_path,
):
    backup_file = tmp_path / "vault_backup_invalid.json"

    backup_file.write_text(
        "not-valid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Invalid vault backup.",
    ):
        backup_service.validate_vault_backup(backup_file)


def test_validate_vault_backup_rejects_invalid_structure(
    tmp_path,
):
    backup_file = tmp_path / "vault_backup_invalid.json"

    backup_file.write_text(
        json.dumps(
            {
                "service": "GitHub",
                "username": "test-user",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Invalid vault backup.",
    ):
        backup_service.validate_vault_backup(backup_file)


def test_validate_vault_backup_rejects_invalid_encrypted_password(
    tmp_path,
    monkeypatch,
):
    backup_file = tmp_path / "vault_backup_invalid.json"

    backup_data = [
        {
            "service": "GitHub",
            "username": "test-user",
            "password": "invalid-encrypted-password",
        }
    ]

    backup_file.write_text(
        json.dumps(backup_data),
        encoding="utf-8",
    )

    def fake_decrypt_password(password):
        raise ValueError("Invalid encrypted password.")

    monkeypatch.setattr(
        backup_service,
        "decrypt_password",
        fake_decrypt_password,
    )

    with pytest.raises(
        ValueError,
        match="Invalid vault backup.",
    ):
        backup_service.validate_vault_backup(backup_file)


def test_validate_vault_backup_accepts_valid_backup(
    tmp_path,
    monkeypatch,
):
    backup_file = tmp_path / "vault_backup_valid.json"

    backup_data = [
        {
            "service": "GitHub",
            "username": "test-user",
            "password": "encrypted-password-token",
        }
    ]

    backup_file.write_text(
        json.dumps(backup_data),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        backup_service,
        "decrypt_password",
        lambda password: "SecretPassword123!",
    )

    backup_service.validate_vault_backup(backup_file)


def test_restore_vault_backup_does_not_replace_vault_when_invalid(
    tmp_path,
    monkeypatch,
):
    test_data_dir = tmp_path / "data"
    test_data_dir.mkdir()

    test_vault_file = test_data_dir / "vault.json"
    backup_file = tmp_path / "vault_backup_invalid.json"

    test_vault_file.write_text(
        "original-vault-data",
        encoding="utf-8",
    )
    backup_file.write_text(
        "invalid-backup-data",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        backup_service,
        "DATA_DIR",
        test_data_dir,
    )
    monkeypatch.setattr(
        backup_service,
        "VAULT_FILE",
        test_vault_file,
    )

    with pytest.raises(
        ValueError,
        match="Invalid vault backup.",
    ):
        backup_service.restore_vault_backup(backup_file)

    assert test_vault_file.read_text(encoding="utf-8") == "original-vault-data"


def test_restore_vault_backup_replaces_active_vault(
    tmp_path,
    monkeypatch,
):
    test_data_dir = tmp_path / "data"
    test_data_dir.mkdir()

    test_vault_file = test_data_dir / "vault.json"
    backup_file = tmp_path / "vault_backup_valid.json"

    test_vault_file.write_text(
        "old-vault-data",
        encoding="utf-8",
    )
    backup_file.write_text(
        "new-encrypted-vault-data",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        backup_service,
        "DATA_DIR",
        test_data_dir,
    )
    monkeypatch.setattr(
        backup_service,
        "VAULT_FILE",
        test_vault_file,
    )
    monkeypatch.setattr(
        backup_service,
        "validate_vault_backup",
        lambda selected_backup: None,
    )

    backup_service.restore_vault_backup(backup_file)

    assert test_vault_file.read_text(encoding="utf-8") == "new-encrypted-vault-data"
