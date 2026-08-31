"""
SecureVault Authentication Module.
This module provides master password authentication.
"""

from pathlib import Path

import bcrypt

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
MASTER_HASH_FILE = DATA_DIR / "master.hash"


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password (str):
         Plain-text password to hash.

    Returns:
        str: Bcrypt password hash.

    Raises:
        ValueError: If the password is empty.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt)
    return password_hash.decode()


def save_master_hash(password_hash: str) -> None:
    """
    Save the master password hash to data/master.hash.

    Args:
        password_hash (str):
            Bcrypt password hash to store.

    Raises:
        ValueError: If the password hash is empty.
    """
    if not password_hash:
        raise ValueError("Master password hash cannot be empty.")

    DATA_DIR.mkdir(exist_ok=True)
    with open(MASTER_HASH_FILE, "w", encoding="utf-8") as file:
        file.write(password_hash)


def load_master_hash() -> str:
    """
    Load the master password hash from data/master.hash.

    Returns:
        str: Stored bcrypt password hash.
    Raises:
        FileNotFoundError: If the master password hash file is missing.
    """
    if not MASTER_HASH_FILE.exists():
        raise FileNotFoundError(
            "Master password hash file not found." "Set up a master password first."
        )
    with open(MASTER_HASH_FILE, "r", encoding="utf-8") as file:
        password_hash = file.read()
    return password_hash


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a stored bcrypt password hash.

    Args:
        password (str):
            Plain-text password to verify.
        password_hash (str):
            Stored bcrypt password hash.

    Returns:
        bool: True if the password matches, otherwise False.
    Raises:
        ValueError: If the password or password hash is empty.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    if not password_hash:
        raise ValueError("Password hash cannot be empty.")
    return bcrypt.checkpw(
        password.encode(),
        password_hash.encode(),
    )


def setup_master_password(password: str) -> None:
    """
    Set up the master password for SecureVault.

    Args:
        password (str):
            Plain-text master password to store securely.

    Raises:
        ValueError: If the password is empty.
        FileExistsError: If a master password is already configured.
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    if MASTER_HASH_FILE.exists():
        raise FileExistsError("Master password is already configured.")

    password_hash = hash_password(password)
    save_master_hash(password_hash)


def authenticate_master_password(password: str) -> bool:
    """
    Authenticate a password against the stored master password hash.

    Args:
        password (str):
             Plain-text master password to authenticate..

    Returns:
        bool: True if the password is correct, otherwise False.

    Raises:
        ValueError: If the password is empty.
        FileNotFoundError: If the master password is not configured.
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    password_hash = load_master_hash()
    return verify_password(password, password_hash)


def is_master_password_configured() -> bool:
    """
    Check whether a master password is already configured.

    Returns:
        bool: True if the master password hash file exists, otherwise False.
    """
    return MASTER_HASH_FILE.exists()
