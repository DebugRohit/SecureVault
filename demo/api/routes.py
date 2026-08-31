"""HTTP routes for the SecureVault recruiter demonstration."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request, session

from demo.demo_security import authenticate_demo_user
from demo.services.vault_service import VaultService


routes = Blueprint("routes", __name__)

vault_service = VaultService()

MAX_DELETE_PASSWORD_ATTEMPTS = 2


def _is_authenticated() -> bool:
    """Return whether the current demo session is authenticated."""
    return bool(session.get("authenticated"))


def _authentication_required():
    """Return the standard authentication-required response."""
    return (
        jsonify(
            {
                "success": False,
                "message": "Authentication required.",
            }
        ),
        401,
    )


def _calculate_demo_strength(password: str) -> str:
    """Estimate password strength for newly added demo credentials."""
    length = len(password)

    has_lower = any(character.islower() for character in password)
    has_upper = any(character.isupper() for character in password)
    has_digit = any(character.isdigit() for character in password)
    has_special = any(not character.isalnum() for character in password)

    complexity = sum(
        (
            has_lower,
            has_upper,
            has_digit,
            has_special,
        )
    )

    if length >= 12 and complexity >= 3:
        return "Strong"

    if length >= 8 and complexity >= 2:
        return "Medium"

    return "Weak"


def _delete_attempts() -> int:
    """Return the number of failed deletion-password attempts."""
    return int(session.get("delete_password_attempts", 0))


def _reset_delete_attempts() -> None:
    """Reset failed deletion-password attempts."""
    session["delete_password_attempts"] = 0


@routes.get("/securevault")
def index():
    """Render the SecureVault recruiter landing page."""
    if _is_authenticated():
        return render_template(
            "dashboard.html",
            credentials=vault_service.credentials(),
        )

    return render_template("index.html")


@routes.post("/securevault/api/login")
def login():
    """Authenticate the isolated demonstration account."""
    payload = request.get_json(silent=True) or {}
    password = str(payload.get("password", ""))

    if authenticate_demo_user(password):
        session.clear()
        session["authenticated"] = True
        session["delete_password_attempts"] = 0

        return jsonify(
            {
                "success": True,
                "message": "SecureVault demo unlocked.",
            }
        )

    return (
        jsonify(
            {
                "success": False,
                "message": "Authentication failed.",
            }
        ),
        401,
    )


@routes.post("/securevault/api/logout")
def logout():
    """Lock the demonstration vault."""
    session.clear()

    return jsonify(
        {
            "success": True,
            "message": "SecureVault demo locked.",
        }
    )


@routes.get("/securevault/api/status")
def status():
    """Return the current demonstration security status."""
    authenticated = _is_authenticated()

    return jsonify(
        {
            "authenticated": authenticated,
            "vault_status": (
                "Protected" if authenticated else "Locked"
            ),
            "environment": "Demo",
            "credential_count": (
                vault_service.credential_count()
                if authenticated
                else 0
            ),
            "backup_available": bool(
                session.get("backup")
            ),
        }
    )


@routes.get("/securevault/api/credentials")
def credentials():
    """Return safe demonstration credential metadata."""
    if not _is_authenticated():
        return _authentication_required()

    return jsonify(
        {
            "success": True,
            "credentials": vault_service.credentials(),
        }
    )


@routes.post("/securevault/api/credentials")
def add_credential():
    """Add a demonstration credential."""
    if not _is_authenticated():
        return _authentication_required()

    payload = request.get_json(silent=True) or {}

    service = str(payload.get("service", "")).strip()
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))

    if not service or not username or not password:
        return (
            jsonify(
                {
                    "success": False,
                    "message": (
                        "Service, username and password "
                        "are required."
                    ),
                }
            ),
            400,
        )

    category = str(
        payload.get("category", "Other")
    ).strip() or "Other"

    strength = str(
        payload.get("strength", "")
    ).strip()

    if not strength:
        strength = _calculate_demo_strength(password)

    credential = vault_service.add_credential(
        service=service,
        username=username,
        password=password,
        category=category,
        strength=strength,
    )

    return (
        jsonify(
            {
                "success": True,
                "credential": credential,
                "message": (
                    f"{service} added to the protected vault."
                ),
            }
        ),
        201,
    )


@routes.get("/securevault/api/credentials/<credential_id>")
def get_credential(credential_id: str):
    """Return one demonstration credential."""
    if not _is_authenticated():
        return _authentication_required()

    credential = vault_service.get_credential(credential_id)

    if credential is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Credential not found.",
                }
            ),
            404,
        )

    return jsonify(
        {
            "success": True,
            "credential": credential,
        }
    )


@routes.delete("/securevault/api/credentials/<credential_id>")
def delete_credential(credential_id: str):
    """Delete one demonstration credential."""
    if not _is_authenticated():
        return _authentication_required()

    deleted = vault_service.delete_credential(credential_id)

    if not deleted:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Credential not found.",
                }
            ),
            404,
        )

    return jsonify(
        {
            "success": True,
            "message": "Demonstration credential deleted.",
        }
    )


@routes.post("/securevault/api/credentials/delete")
def delete_selected_credentials():
    """
    Delete one or more selected demonstration credentials.

    Deletion requires the demo master password.
    Two consecutive incorrect passwords lock the
    demonstration vault and clear the authenticated session.
    """
    if not _is_authenticated():
        return _authentication_required()

    payload = request.get_json(silent=True) or {}

    password = str(payload.get("password", ""))

    credential_ids = payload.get("credential_ids", [])

    if not isinstance(credential_ids, list):
        return (
            jsonify(
                {
                    "success": False,
                    "message": (
                        "credential_ids must be a list."
                    ),
                }
            ),
            400,
        )

    normalized_ids = [
        str(credential_id).strip()
        for credential_id in credential_ids
        if str(credential_id).strip()
    ]

    normalized_ids = list(
        dict.fromkeys(normalized_ids)
    )

    if not normalized_ids:
        return (
            jsonify(
                {
                    "success": False,
                    "message": (
                        "Select at least one credential "
                        "to delete."
                    ),
                }
            ),
            400,
        )

    if not password:
        return (
            jsonify(
                {
                    "success": False,
                    "message": (
                        "Demo password is required."
                    ),
                    "attempts_remaining": (
                        MAX_DELETE_PASSWORD_ATTEMPTS
                        - _delete_attempts()
                    ),
                }
            ),
            400,
        )

    if not authenticate_demo_user(password):
        attempts = _delete_attempts() + 1
        session["delete_password_attempts"] = attempts

        if attempts >= MAX_DELETE_PASSWORD_ATTEMPTS:
            session.clear()

            return (
                jsonify(
                    {
                        "success": False,
                        "locked": True,
                        "message": (
                            "Two incorrect deletion "
                            "password attempts were entered. "
                            "SecureVault has been locked."
                        ),
                    }
                ),
                423,
            )

        return (
            jsonify(
                {
                    "success": False,
                    "locked": False,
                    "message": (
                        "Incorrect demo password."
                    ),
                    "attempts_remaining": (
                        MAX_DELETE_PASSWORD_ATTEMPTS
                        - attempts
                    ),
                }
            ),
            401,
        )

    _reset_delete_attempts()

    deleted_ids: list[str] = []
    missing_ids: list[str] = []

    for credential_id in normalized_ids:
        deleted = vault_service.delete_credential(
            credential_id
        )

        if deleted:
            deleted_ids.append(credential_id)
        else:
            missing_ids.append(credential_id)

    if not deleted_ids:
        return (
            jsonify(
                {
                    "success": False,
                    "message": (
                        "None of the selected credentials "
                        "could be deleted."
                    ),
                    "missing_ids": missing_ids,
                }
            ),
            404,
        )

    return jsonify(
        {
            "success": True,
            "message": (
                f"{len(deleted_ids)} credential"
                f"{'s' if len(deleted_ids) != 1 else ''} "
                "deleted successfully."
            ),
            "deleted_ids": deleted_ids,
            "missing_ids": missing_ids,
            "credential_count": (
                vault_service.credential_count()
            ),
        }
    )


@routes.post("/securevault/api/backup")
def create_backup():
    """Create a demonstration backup snapshot."""
    if not _is_authenticated():
        return _authentication_required()

    backup = vault_service.create_backup()

    session["backup"] = backup

    return jsonify(
        {
            "success": True,
            "credential_count": len(backup),
            "message": (
                "Demo backup snapshot created."
            ),
        }
    )


@routes.post("/securevault/api/restore")
def restore_backup():
    """Restore the current demonstration backup snapshot."""
    if not _is_authenticated():
        return _authentication_required()

    backup = session.get("backup")

    if backup is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": (
                        "No demo backup has been created."
                    ),
                }
            ),
            400,
        )

    vault_service.restore_backup(backup)

    return jsonify(
        {
            "success": True,
            "credential_count": (
                vault_service.credential_count()
            ),
            "message": (
                "Demo backup restored successfully."
            ),
        }
    )