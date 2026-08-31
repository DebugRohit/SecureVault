"""
SecureVault Encryption Module
This module provides :
- Key Generation
- Encryption
- Decryption
"""

from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

# Project Directories

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
KEY_FILE = DATA_DIR / "secret.key"


def generate_key() -> None:
    """
    Generates a new encryption key.
    The key is stored inside the data/secret.key.
    """
    DATA_DIR.mkdir(exist_ok=True)
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as file:
        file.write(key)
    print("Encryption key generated succcessfully.")


def load_key():
    """
    Loads the encryption key from data/secret.key.
    Returns:
        bytes: Encryption key.
    """
    if not KEY_FILE.exists():
        raise FileNotFoundError("Encryption key not found. Run generate_key() first.")
    with open(KEY_FILE, "rb") as file:
        key = file.read()
    return key


def encrypt_password(password: str) -> str:
    """
    Encrypts a password using Fernet symmetric encryption.
    Args:
        password (str):
            Plain-text password to encrypt.
    Returns:
        str: Encrypted Fernet Token.
    Raises:
        ValueError: If the password is empty.
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    key = load_key()
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password.encode())
    return encrypted_password.decode()


def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypt a Fernet encrypted password.
    Args:
        encrypted_password (str):
            Encrypted Fernet token.
    Returns:
        str: Original plain-text password.
    Raises:
        ValueError: If the encrypted password is empty or invalid.
    """
    if not encrypted_password:
        raise ValueError("Encrypted password cannot be empty.")

    key = load_key()
    cipher = Fernet(key)
    try:
        decrypted_password = cipher.decrypt(encrypted_password.encode())
    except InvalidToken as exc:
        raise ValueError("Unable to decrypt password: invalid encrypted data.") from exc
    return decrypted_password.decode()
