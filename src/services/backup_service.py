"""
Backup service for SecureVault.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from src.crypto.encryption import decrypt_password

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
VAULT_FILE = DATA_DIR / "vault.json"
BACKUP_DIR = DATA_DIR / "backups"


def create_vault_backup() -> Path:
    """
    Create a timestamped backup of the encrypted vault file.
    """
    if not VAULT_FILE.exists():
        raise FileNotFoundError("Vault file not found.")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_file = BACKUP_DIR / f"vault_backup_{timestamp}.json"

    shutil.copy2(VAULT_FILE, backup_file)

    return backup_file


def list_vault_backups() -> list[Path]:
    """
    Return available vault backups from newest to oldest.
    """
    if not BACKUP_DIR.exists():
        return []

    return sorted(
        BACKUP_DIR.glob("vault_backup_*.json"),
        key=lambda backup_file: backup_file.stat().st_mtime,
        reverse=True,
    )


def validate_vault_backup(backup_file: Path) -> None:
    """
    Validate backup structure and encrypted password data.
    """
    if not backup_file.exists():
        raise FileNotFoundError("Backup file not found.")

    try:
        backup_data = json.loads(backup_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError("Invalid vault backup.") from exc

    if not isinstance(backup_data, list):
        raise ValueError("Invalid vault backup.")

    required_fields = {
        "service",
        "username",
        "password",
    }

    for credential_data in backup_data:
        if not isinstance(credential_data, dict):
            raise ValueError("Invalid vault backup.")

        if set(credential_data) != required_fields:
            raise ValueError("Invalid vault backup.")

        if not all(
            isinstance(credential_data[field], str) for field in required_fields
        ):
            raise ValueError("Invalid vault backup.")

        try:
            decrypt_password(credential_data["password"])
        except (ValueError, FileNotFoundError) as exc:
            raise ValueError("Invalid vault backup.") from exc


def restore_vault_backup(backup_file: Path) -> None:
    """
    Validate and restore an encrypted vault backup.
    """
    validate_vault_backup(backup_file)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy2(backup_file, VAULT_FILE)
