"""Safe demonstration data for the SecureVault recruiter interface."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


_INITIAL_CREDENTIALS: list[dict[str, Any]] = [
    {
        "id": "cred-001",
        "service": "GitHub",
        "username": "demo.developer",
        "password": "G!thub-Demo-2026#Secure",
        "category": "Development",
        "strength": "Strong",
    },
    {
        "id": "cred-002",
        "service": "AWS Console",
        "username": "demo.engineer",
        "password": "AWS-Demo#2026!Vault",
        "category": "Cloud",
        "strength": "Strong",
    },
    {
        "id": "cred-003",
        "service": "PostgreSQL",
        "username": "demo_admin",
        "password": "Postgres-Demo#2026",
        "category": "Database",
        "strength": "Strong",
    },
    {
        "id": "cred-004",
        "service": "Jira",
        "username": "demo.user",
        "password": "JiraDemo-2026!",
        "category": "Project Management",
        "strength": "Medium",
    },
]


def get_initial_credentials() -> list[dict[str, Any]]:
    """Return a fresh copy of the safe demonstration credentials."""
    return deepcopy(_INITIAL_CREDENTIALS)