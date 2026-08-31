import pytest

from src.auth import authentication


def test_hash_password_returns_bcrypt_hash():
    password_hash = authentication.hash_password("TestPassword123")

    assert isinstance(password_hash, str)
    assert password_hash.startswith("$2")


def test_hash_password_empty_password_raises_value_error():
    with pytest.raises(ValueError, match="Password cannot be empty."):
        authentication.hash_password("")


def test_save_and_load_master_hash(tmp_path, monkeypatch):
    test_hash_file = tmp_path / "master.hash"
    monkeypatch.setattr(
        authentication,
        "DATA_DIR",
        tmp_path,
    )
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)

    password_hash = authentication.hash_password("TestPassword123")
    authentication.save_master_hash(password_hash)

    loaded_hash = authentication.load_master_hash()
    assert loaded_hash == password_hash


def test_save_master_hash_empty_hash_raises_error():
    with pytest.raises(ValueError, match="Master password hash cannot be empty."):
        authentication.save_master_hash("")


def test_load_master_hash_missing_file_raises_error(tmp_path, monkeypatch):
    test_hash_file = tmp_path / "master.hash"
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)
    with pytest.raises(FileNotFoundError, match="Master password hash file not found."):
        authentication.load_master_hash()


def test_verify_password_correct_password_returns_true():
    password_hash = authentication.hash_password("TestPassword123")
    result = authentication.verify_password("TestPassword123", password_hash)
    assert result is True


def test_verify_password_wrong_password_returns_false():
    password_hash = authentication.hash_password("TestPassword123")
    result = authentication.verify_password("WrongPassword", password_hash)
    assert result is False


def test_verify_password_empty_password_raises_error():
    password_hash = authentication.hash_password("TestPassword123")
    with pytest.raises(ValueError, match="Password cannot be empty."):
        authentication.verify_password("", password_hash)


def test_verify_password_empty_hash_raises_error():
    with pytest.raises(ValueError, match="Password hash cannot be empty."):
        authentication.verify_password("TestPassword123", "")


def test_setup_master_password_creates_hash_file(tmp_path, monkeypatch):
    test_hash_file = tmp_path / "master.hash"
    monkeypatch.setattr(authentication, "DATA_DIR", tmp_path)
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)

    authentication.setup_master_password("TestPassword123")

    assert test_hash_file.exists()
    stored_hash = test_hash_file.read_text(encoding="utf-8")
    assert authentication.verify_password("TestPassword123", stored_hash)


def test_setup_master_password_empty_password_raises_error(tmp_path, monkeypatch):
    test_hash_file = tmp_path / "master.hash"
    monkeypatch.setattr(authentication, "DATA_DIR", tmp_path)
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)

    with pytest.raises(ValueError, match="Password cannot be empty."):
        authentication.setup_master_password("")


def test_setup_master_password_already_configured_raises_error(tmp_path, monkeypatch):
    test_hash_file = tmp_path / "master.hash"
    monkeypatch.setattr(authentication, "DATA_DIR", tmp_path)
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)

    # First setup
    authentication.setup_master_password("TestPassword123")

    # Attempt to setup again
    with pytest.raises(FileExistsError, match="Master password is already configured."):
        authentication.setup_master_password("AnotherPassword123")


def test_authenticate_master_password_correct_password_returns_true(
    tmp_path, monkeypatch
):
    test_hash_file = tmp_path / "master.hash"
    monkeypatch.setattr(authentication, "DATA_DIR", tmp_path)
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)

    authentication.setup_master_password("TestPassword123")

    result = authentication.authenticate_master_password("TestPassword123")
    assert result is True


def test_authenticate_master_password_wrong_password_returns_false(
    tmp_path, monkeypatch
):
    test_hash_file = tmp_path / "master.hash"
    monkeypatch.setattr(authentication, "DATA_DIR", tmp_path)
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)

    authentication.setup_master_password("TestPassword123")

    result = authentication.authenticate_master_password("WrongPassword")
    assert result is False


def test_authenticate_master_password_empty_password_raises_error():
    with pytest.raises(ValueError, match="Password cannot be empty."):
        authentication.authenticate_master_password("")


def test_authenticate_master_password_missing_hash_file_raises_error(
    tmp_path, monkeypatch
):
    test_hash_file = tmp_path / "master.hash"
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)
    with pytest.raises(FileNotFoundError, match="Master password hash file not found."):
        authentication.authenticate_master_password("TestPassword123")


def test_is_master_configured_returns_true(tmp_path, monkeypatch):
    test_hash_file = tmp_path / "master.hash"
    test_hash_file.write_text("test-hash", encoding="utf-8")
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)

    result = authentication.is_master_password_configured()

    assert result is True


def test_is_master_password_configured_returns_false(tmp_path, monkeypatch):
    test_hash_file = tmp_path / "master.hash"
    monkeypatch.setattr(authentication, "MASTER_HASH_FILE", test_hash_file)

    result = authentication.is_master_password_configured()

    assert result is False
