"""Service layer for the SecureVault recruiter demonstration."""

from __future__ import annotations

from typing import Any

from demo.demo_data import get_initial_credentials
from demo.demo_vault import DemoVault


class VaultService:
    """Coordinate safe demonstration-vault operations."""

    def __init__(self) -> None:
        """Create a fresh isolated demonstration vault."""
        self._vault = DemoVault(get_initial_credentials())

    @property
    def vault(self) -> DemoVault:
        """Return the isolated demo vault."""
        return self._vault

    def credentials(self) -> list[dict[str, Any]]:
        """Return demonstration credentials."""
        return self._vault.list_credentials()

    def credential_count(self) -> int:
        """Return the number of demonstration credentials."""
        return self._vault.credential_count

    def add_credential(
        self,
        service: str,
        username: str,
        password: str,
        category: str,
        strength: str,
    ) -> dict[str, Any]:
        """Add a credential to the demonstration vault."""
        return self._vault.add_credential(
            service=service,
            username=username,
            password=password,
            category=category,
            strength=strength,
        )

    def get_credential(
        self,
        credential_id: str,
    ) -> dict[str, Any] | None:
        """Retrieve a demonstration credential."""
        return self._vault.get_credential(credential_id)

    def delete_credential(self, credential_id: str) -> bool:
        """Delete a demonstration credential."""
        return self._vault.delete_credential(credential_id)

    def create_backup(self) -> list[dict[str, Any]]:
        """Create an isolated demonstration backup."""
        return self._vault.create_backup()

    def restore_backup(
        self,
        backup: list[dict[str, Any]],
    ) -> None:
        """Restore an isolated demonstration backup."""
        self._vault.restore_backup(backup)