from cryptography.fernet import Fernet
import pytest
from src.crypto import encryption


@pytest.fixture
def temporary_key_file(tmp_path, monkeypatch):
    """
    Create an isolated Fernet key file for each test.
    """
    key_file = tmp_path / "secret.key"
    key_file.write_bytes(Fernet.generate_key())
    monkeypatch.setattr(encryption, "KEY_FILE", key_file)
    return key_file


def test_encrypt_decrypt_password(temporary_key_file):
    """
    Verify that an encrypted password can be decrypted.
    """
    password = "RecruiterDemo@123"
    encrypted_password = encryption.encrypt_password(password)
    decrypted_password = encryption.decrypt_password(encrypted_password)
    assert encrypted_password != password
    assert decrypted_password == password


def test_encrypt_empty_password_raises_error(temporary_key_file):
    """
    Verify that an empty password is rejected.
    """
    with pytest.raises(
        ValueError,
        match="Password cannot be empty.",
    ):
        encryption.encrypt_password("")


def test_decrypt_empty_password_raises_error(temporary_key_file):
    """
    Verify that an empty encrypted data is rejected.
    """
    with pytest.raises(
        ValueError,
        match="Encrypted password cannot be empty.",
    ):
        encryption.decrypt_password("")


def test_decrypt_invalid_encrypted_data_raises_error(temporary_key_file):
    """
    Verify that corrupted encrypted data is rejected.
    """
    with pytest.raises(
        ValueError,
        match="Unable to decrypt password",
    ):
        encryption.decrypt_password("invalid_token")


def test_load_key_raises_error_when_key_is_missing(tmp_path, monkeypatch):
    """
    Verify that a missing encryption key is reported.
    """
    missing_key_file = tmp_path / "missing.key"
    monkeypatch.setattr(encryption, "KEY_FILE", missing_key_file)
    with pytest.raises(
        FileNotFoundError,
        match="Encryption key not found.",
    ):
        encryption.load_key()
