"""Isolated in-memory vault used by the SecureVault recruiter demo."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class DemoVault:
    """Small in-memory vault for safe recruiter demonstrations."""

    def __init__(self, credentials: list[dict[str, Any]] | None = None) -> None:
        """Initialize the demo vault with isolated credential data."""
        self.credentials: list[dict[str, Any]] = deepcopy(
            credentials or []
        )

    def list_credentials(self) -> list[dict[str, Any]]:
        """Return a copy of all stored demonstration credentials."""
        return deepcopy(self.credentials)

    def get_credential(
        self,
        credential_id: str,
    ) -> dict[str, Any] | None:
        """Return a credential by ID without exposing internal state."""
        for credential in self.credentials:
            if credential["id"] == credential_id:
                return deepcopy(credential)

        return None

    def add_credential(
        self,
        service: str,
        username: str,
        password: str,
        category: str,
        strength: str,
    ) -> dict[str, Any]:
        """Add a new demonstration credential."""
        next_id = f"cred-{len(self.credentials) + 1:03d}"

        credential = {
            "id": next_id,
            "service": service.strip(),
            "username": username.strip(),
            "password": password,
            "category": category.strip(),
            "strength": strength.strip(),
        }

        self.credentials.append(credential)

        return deepcopy(credential)

    def delete_credential(self, credential_id: str) -> bool:
        """Delete a demonstration credential by ID."""
        for index, credential in enumerate(self.credentials):
            if credential["id"] == credential_id:
                del self.credentials[index]
                return True

        return False

    def create_backup(self) -> list[dict[str, Any]]:
        """Create an in-memory backup snapshot."""
        return deepcopy(self.credentials)

    def restore_backup(
        self,
        backup: list[dict[str, Any]],
    ) -> None:
        """Restore the vault from a validated in-memory snapshot."""
        if not isinstance(backup, list):
            raise TypeError("Demo backup must be a list.")

        self.credentials = deepcopy(backup)

    @property
    def credential_count(self) -> int:
        """Return the number of demonstration credentials."""
        return len(self.credentials)