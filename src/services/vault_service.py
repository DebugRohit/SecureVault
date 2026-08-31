"""
Vault storage service for SecureVault.
"""

import json
from pathlib import Path

from src.crypto.encryption import decrypt_password, encrypt_password
from src.models.credential import Credential

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
VAULT_FILE = DATA_DIR / "vault.json"


def save_credentials(credentials: list[Credential]) -> None:
    """
    Save credentials to the vault with encrypted passwords.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    vault_data = []

    for credential in credentials:
        vault_data.append(
            {
                "service": credential.service,
                "username": credential.username,
                "password": encrypt_password(credential.password),
            }
        )

    VAULT_FILE.write_text(
        json.dumps(vault_data, indent=4),
        encoding="utf-8",
    )


def load_credentials() -> list[Credential]:
    """
    Load credentials from the vault and decrypt their passwords.
    """
    if not VAULT_FILE.exists():
        return []

    vault_content = VAULT_FILE.read_text(encoding="utf-8")

    if not vault_content.strip():
        return []

    vault_data = json.loads(vault_content)

    credentials = []

    for item in vault_data:
        credentials.append(
            Credential(
                service=item["service"],
                username=item["username"],
                password=decrypt_password(item["password"]),
            )
        )

    return credentials
