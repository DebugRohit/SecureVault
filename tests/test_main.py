"""
Tests for the SecureVault command-line interface.
"""

from src import main
from src.models.credential import Credential


def test_setup_master_password_flow_success(monkeypatch, capsys):
    passwords = iter(["TestPassword123", "TestPassword123"])

    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: next(passwords),
    )

    setup_password = None

    def fake_setup_master_password(password):
        nonlocal setup_password
        setup_password = password

    monkeypatch.setattr(
        main,
        "setup_master_password",
        fake_setup_master_password,
    )

    main.setup_master_password_flow()

    captured = capsys.readouterr()

    assert setup_password == "TestPassword123"
    assert "Master password configured successfully." in captured.out


def test_setup_master_password_flow_passwords_do_not_match(
    monkeypatch,
    capsys,
):
    passwords = iter(["TestPassword123", "DifferentPassword"])
    monkeypatch.setattr(main, "getpass", lambda prompt: next(passwords))
    setup_called = False

    def fake_setup_master_password(password):
        nonlocal setup_called
        setup_called = True

    monkeypatch.setattr(
        main,
        "setup_master_password",
        fake_setup_master_password,
    )

    main.setup_master_password_flow()

    captured = capsys.readouterr()

    assert "Passwords do not match." in captured.out
    assert setup_called is False


def test_login_flow_success(monkeypatch, capsys):
    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: "TestPassword123",
    )
    monkeypatch.setattr(
        main,
        "authenticate_master_password",
        lambda password: True,
    )
    result = main.login_flow()

    captured = capsys.readouterr()

    assert "Authentication successful." in captured.out
    assert result is True


def test_login_flow_failure(monkeypatch, capsys):
    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: "WrongPassword",
    )
    monkeypatch.setattr(
        main,
        "authenticate_master_password",
        lambda password: False,
    )
    result = main.login_flow()

    captured = capsys.readouterr()

    assert "Authentication failed." in captured.out
    assert result is False


def test_main_stops_after_setup_when_master_password_is_not_configured(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "is_master_password_configured",
        lambda: False,
    )

    passwords = iter(
        [
            "TestPassword123",
            "TestPassword123",
        ]
    )

    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: next(passwords),
    )

    setup_called = False
    vault_menu_called = False

    def fake_setup_master_password(password):
        nonlocal setup_called
        setup_called = True

    def fake_vault_menu():
        nonlocal vault_menu_called
        vault_menu_called = True

    monkeypatch.setattr(
        main,
        "setup_master_password",
        fake_setup_master_password,
    )
    monkeypatch.setattr(
        main,
        "vault_menu",
        fake_vault_menu,
    )

    main.main()

    assert setup_called is True
    assert vault_menu_called is False


def test_main_denies_vault_access_when_authentication_fails(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "is_master_password_configured",
        lambda: True,
    )
    monkeypatch.setattr(main, "login_flow", lambda: False)

    vault_menu_called = False

    def fake_vault_menu():
        nonlocal vault_menu_called
        vault_menu_called = True

    monkeypatch.setattr(main, "vault_menu", fake_vault_menu)

    main.main()

    assert vault_menu_called is False


def test_main_opens_vault_menu_when_authentication_succeeds(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "is_master_password_configured",
        lambda: True,
    )
    monkeypatch.setattr(main, "login_flow", lambda: True)

    vault_menu_called = False

    def fake_vault_menu():
        nonlocal vault_menu_called
        vault_menu_called = True

    monkeypatch.setattr(main, "vault_menu", fake_vault_menu)

    main.main()

    assert vault_menu_called is True


def test_vault_menu_exit(monkeypatch, capsys):
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "8",
    )

    main.vault_menu()

    captured = capsys.readouterr()

    assert "SecureVault unlocked." in captured.out
    assert "SecureVault Menu" in captured.out
    assert "SecureVault locked." in captured.out


def test_vault_menu_invalid_option(monkeypatch, capsys):
    choices = iter(["99", "8"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(choices),
    )

    main.vault_menu()

    captured = capsys.readouterr()

    assert "Invalid option. " "Please choose 1, 2, 3, 4, 5, 6, 7, or 8." in captured.out
    assert "SecureVault locked." in captured.out


def test_vault_menu_add_password_option(monkeypatch):
    choices = iter(["1", "8"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(choices),
    )

    add_password_called = False

    def fake_add_password_flow():
        nonlocal add_password_called
        add_password_called = True

    monkeypatch.setattr(
        main,
        "add_password_flow",
        fake_add_password_flow,
    )

    main.vault_menu()

    assert add_password_called is True


def test_vault_menu_view_passwords_option(monkeypatch):
    choices = iter(["2", "8"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(choices),
    )

    view_passwords_called = False

    def fake_view_passwords_flow():
        nonlocal view_passwords_called
        view_passwords_called = True

    monkeypatch.setattr(
        main,
        "view_passwords_flow",
        fake_view_passwords_flow,
    )

    main.vault_menu()

    assert view_passwords_called is True


def test_add_password_flow_saves_manually_entered_password(
    monkeypatch,
    capsys,
):
    user_inputs = iter(
        [
            "GitHub",
            "test-user",
            "1",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )
    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: "SecretPassword123!",
    )
    monkeypatch.setattr(
        main,
        "check_password_strength",
        lambda password: "Strong",
    )

    existing_credentials = []

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: existing_credentials,
    )

    saved_credentials = None

    def fake_save_credentials(credentials):
        nonlocal saved_credentials
        saved_credentials = credentials

    monkeypatch.setattr(
        main,
        "save_credentials",
        fake_save_credentials,
    )

    main.add_password_flow()

    captured = capsys.readouterr()

    assert len(saved_credentials) == 1
    assert saved_credentials[0].service == "GitHub"
    assert saved_credentials[0].username == "test-user"
    assert saved_credentials[0].password == "SecretPassword123!"
    assert "Password strength: Strong" in captured.out
    assert "Password added successfully." in captured.out


def test_view_passwords_flow_shows_empty_vault_message(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: [],
    )

    main.view_passwords_flow()

    captured = capsys.readouterr()

    assert "No passwords stored." in captured.out


def test_view_passwords_flow_displays_credentials_without_passwords(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="test-user",
            password="SecretPassword123!",
        )
    ]

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )

    main.view_passwords_flow()

    captured = capsys.readouterr()

    assert "Stored credentials:" in captured.out
    assert "GitHub" in captured.out
    assert "test-user" in captured.out
    assert "SecretPassword123!" not in captured.out


def test_reveal_password_requires_authentication(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="test-user",
            password="SecretPassword123!",
        )
    ]

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1",
    )

    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: "WrongPassword",
    )

    monkeypatch.setattr(
        main,
        "authenticate_master_password",
        lambda password: False,
    )

    main.reveal_password_flow()

    captured = capsys.readouterr()

    assert "Authentication failed." in captured.out
    assert "SecretPassword123!" not in captured.out


def test_reveal_password_after_successful_authentication(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="test-user",
            password="SecretPassword123!",
        )
    ]

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1",
    )

    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: "CorrectPassword",
    )

    monkeypatch.setattr(
        main,
        "authenticate_master_password",
        lambda password: True,
    )

    main.reveal_password_flow()

    captured = capsys.readouterr()

    assert "Password: SecretPassword123!" in captured.out


def test_vault_menu_edit_credential_option(monkeypatch):
    choices = iter(["4", "8"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(choices),
    )

    edit_credential_called = False

    def fake_edit_credential_flow():
        nonlocal edit_credential_called
        edit_credential_called = True

    monkeypatch.setattr(
        main,
        "edit_credential_flow",
        fake_edit_credential_flow,
    )

    main.vault_menu()

    assert edit_credential_called is True


def test_edit_credential_flow_shows_empty_vault_message(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: [],
    )

    main.edit_credential_flow()

    captured = capsys.readouterr()

    assert "No passwords stored." in captured.out


def test_edit_credential_flow_rejects_non_number_selection(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="test-user",
            password="OldPassword123!",
        )
    ]

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "abc",
    )

    main.edit_credential_flow()

    captured = capsys.readouterr()

    assert "Invalid selection." in captured.out


def test_edit_credential_flow_rejects_out_of_range_selection(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="test-user",
            password="OldPassword123!",
        )
    ]

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "99",
    )

    main.edit_credential_flow()

    captured = capsys.readouterr()

    assert "Invalid selection." in captured.out


def test_edit_credential_flow_updates_selected_credential(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="old-user",
            password="OldPassword123!",
        )
    ]

    user_inputs = iter(
        [
            "1",
            "GitLab",
            "new-user",
        ]
    )

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )
    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: "NewPassword123!",
    )

    saved_credentials = None

    def fake_save_credentials(updated_credentials):
        nonlocal saved_credentials
        saved_credentials = updated_credentials

    monkeypatch.setattr(
        main,
        "save_credentials",
        fake_save_credentials,
    )

    main.edit_credential_flow()

    captured = capsys.readouterr()

    assert len(saved_credentials) == 1
    assert saved_credentials[0].service == "GitLab"
    assert saved_credentials[0].username == "new-user"
    assert saved_credentials[0].password == "NewPassword123!"
    assert "Credential updated successfully." in captured.out


def test_vault_menu_delete_credential_option(monkeypatch):
    choices = iter(["5", "8"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(choices),
    )

    delete_credential_called = False

    def fake_delete_credential_flow():
        nonlocal delete_credential_called
        delete_credential_called = True

    monkeypatch.setattr(
        main,
        "delete_credential_flow",
        fake_delete_credential_flow,
    )

    main.vault_menu()

    assert delete_credential_called is True


def test_delete_credential_flow_shows_empty_vault_message(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: [],
    )

    main.delete_credential_flow()

    captured = capsys.readouterr()

    assert "No passwords stored." in captured.out


def test_delete_credential_flow_rejects_non_number_selection(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="test-user",
            password="SecretPassword123!",
        )
    ]

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "abc",
    )

    main.delete_credential_flow()

    captured = capsys.readouterr()

    assert "Invalid selection." in captured.out


def test_delete_credential_flow_rejects_out_of_range_selection(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="test-user",
            password="SecretPassword123!",
        )
    ]

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "99",
    )

    main.delete_credential_flow()

    captured = capsys.readouterr()

    assert "Invalid selection." in captured.out


def test_delete_credential_flow_cancels_without_confirmation(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="test-user",
            password="SecretPassword123!",
        )
    ]

    user_inputs = iter(["1", "n"])

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )

    save_called = False

    def fake_save_credentials(updated_credentials):
        nonlocal save_called
        save_called = True

    monkeypatch.setattr(
        main,
        "save_credentials",
        fake_save_credentials,
    )

    main.delete_credential_flow()

    captured = capsys.readouterr()

    assert len(credentials) == 1
    assert save_called is False
    assert "Deletion cancelled." in captured.out


def test_delete_credential_flow_deletes_selected_credential(
    monkeypatch,
    capsys,
):
    credentials = [
        Credential(
            service="GitHub",
            username="github-user",
            password="GitHubPassword123!",
        ),
        Credential(
            service="GitLab",
            username="gitlab-user",
            password="GitLabPassword123!",
        ),
    ]

    user_inputs = iter(["1", "y"])

    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: credentials,
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )

    saved_credentials = None

    def fake_save_credentials(updated_credentials):
        nonlocal saved_credentials
        saved_credentials = updated_credentials

    monkeypatch.setattr(
        main,
        "save_credentials",
        fake_save_credentials,
    )

    main.delete_credential_flow()

    captured = capsys.readouterr()

    assert len(saved_credentials) == 1
    assert saved_credentials[0].service == "GitLab"
    assert saved_credentials[0].username == "gitlab-user"
    assert "Credential deleted successfully." in captured.out


def test_add_password_flow_saves_generated_password(
    monkeypatch,
    capsys,
):
    user_inputs = iter(
        [
            "GitHub",
            "test-user",
            "2",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )
    monkeypatch.setattr(
        main,
        "generate_password",
        lambda: "GeneratedPassword123!",
    )
    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: [],
    )

    saved_credentials = None

    def fake_save_credentials(credentials):
        nonlocal saved_credentials
        saved_credentials = credentials

    monkeypatch.setattr(
        main,
        "save_credentials",
        fake_save_credentials,
    )

    main.add_password_flow()

    captured = capsys.readouterr()

    assert len(saved_credentials) == 1
    assert saved_credentials[0].password == "GeneratedPassword123!"
    assert "Secure password generated successfully." in captured.out
    assert "GeneratedPassword123!" not in captured.out
    assert "Password added successfully." in captured.out


def test_add_password_flow_displays_weak_password_strength(
    monkeypatch,
    capsys,
):
    user_inputs = iter(
        [
            "GitHub",
            "test-user",
            "1",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )
    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: "password",
    )
    monkeypatch.setattr(
        main,
        "check_password_strength",
        lambda password: "Weak",
    )
    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: [],
    )
    monkeypatch.setattr(
        main,
        "save_credentials",
        lambda credentials: None,
    )

    main.add_password_flow()

    captured = capsys.readouterr()

    assert "Password strength: Weak" in captured.out
    assert "Password added successfully." in captured.out


def test_add_password_flow_displays_medium_password_strength(
    monkeypatch,
    capsys,
):
    user_inputs = iter(
        [
            "GitHub",
            "test-user",
            "1",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )
    monkeypatch.setattr(
        main,
        "getpass",
        lambda prompt: "Password123",
    )
    monkeypatch.setattr(
        main,
        "check_password_strength",
        lambda password: "Medium",
    )
    monkeypatch.setattr(
        main,
        "load_credentials",
        lambda: [],
    )
    monkeypatch.setattr(
        main,
        "save_credentials",
        lambda credentials: None,
    )

    main.add_password_flow()

    captured = capsys.readouterr()

    assert "Password strength: Medium" in captured.out
    assert "Password added successfully." in captured.out


def test_vault_menu_create_backup_option(monkeypatch):
    choices = iter(["6", "8"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(choices),
    )

    create_backup_called = False

    def fake_create_backup_flow():
        nonlocal create_backup_called
        create_backup_called = True

    monkeypatch.setattr(
        main,
        "create_backup_flow",
        fake_create_backup_flow,
    )

    main.vault_menu()

    assert create_backup_called is True


def test_create_backup_flow_reports_created_backup(
    tmp_path,
    monkeypatch,
    capsys,
):
    backup_file = tmp_path / "vault_backup_test.json"

    monkeypatch.setattr(
        main,
        "create_vault_backup",
        lambda: backup_file,
    )

    main.create_backup_flow()

    captured = capsys.readouterr()

    assert "Vault backup created: vault_backup_test.json" in captured.out


def test_create_backup_flow_handles_missing_vault(
    monkeypatch,
    capsys,
):
    def fake_create_vault_backup():
        raise FileNotFoundError("Vault file not found.")

    monkeypatch.setattr(
        main,
        "create_vault_backup",
        fake_create_vault_backup,
    )

    main.create_backup_flow()

    captured = capsys.readouterr()

    assert "Vault file not found." in captured.out


def test_vault_menu_restore_backup_option(monkeypatch):
    choices = iter(["7", "8"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(choices),
    )

    restore_backup_called = False

    def fake_restore_backup_flow():
        nonlocal restore_backup_called
        restore_backup_called = True

    monkeypatch.setattr(
        main,
        "restore_backup_flow",
        fake_restore_backup_flow,
    )

    main.vault_menu()

    assert restore_backup_called is True


def test_restore_backup_flow_shows_no_backups_message(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        main,
        "list_vault_backups",
        lambda: [],
    )

    main.restore_backup_flow()

    captured = capsys.readouterr()

    assert "No vault backups found." in captured.out


def test_restore_backup_flow_rejects_non_number_selection(
    tmp_path,
    monkeypatch,
    capsys,
):
    backup_file = tmp_path / "vault_backup_test.json"

    monkeypatch.setattr(
        main,
        "list_vault_backups",
        lambda: [backup_file],
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "abc",
    )

    main.restore_backup_flow()

    captured = capsys.readouterr()

    assert "Invalid selection." in captured.out


def test_restore_backup_flow_rejects_out_of_range_selection(
    tmp_path,
    monkeypatch,
    capsys,
):
    backup_file = tmp_path / "vault_backup_test.json"

    monkeypatch.setattr(
        main,
        "list_vault_backups",
        lambda: [backup_file],
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "99",
    )

    main.restore_backup_flow()

    captured = capsys.readouterr()

    assert "Invalid selection." in captured.out


def test_restore_backup_flow_cancels_without_confirmation(
    tmp_path,
    monkeypatch,
    capsys,
):
    backup_file = tmp_path / "vault_backup_test.json"
    user_inputs = iter(["1", "n"])

    monkeypatch.setattr(
        main,
        "list_vault_backups",
        lambda: [backup_file],
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )

    restore_called = False

    def fake_restore_vault_backup(selected_backup):
        nonlocal restore_called
        restore_called = True

    monkeypatch.setattr(
        main,
        "restore_vault_backup",
        fake_restore_vault_backup,
    )

    main.restore_backup_flow()

    captured = capsys.readouterr()

    assert restore_called is False
    assert "Restore cancelled." in captured.out


def test_restore_backup_flow_handles_invalid_backup(
    tmp_path,
    monkeypatch,
    capsys,
):
    backup_file = tmp_path / "vault_backup_invalid.json"
    user_inputs = iter(["1", "y"])

    monkeypatch.setattr(
        main,
        "list_vault_backups",
        lambda: [backup_file],
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )

    def fake_restore_vault_backup(selected_backup):
        raise ValueError("Invalid vault backup.")

    monkeypatch.setattr(
        main,
        "restore_vault_backup",
        fake_restore_vault_backup,
    )

    main.restore_backup_flow()

    captured = capsys.readouterr()

    assert "Unable to restore vault backup." in captured.out


def test_restore_backup_flow_restores_selected_backup(
    tmp_path,
    monkeypatch,
    capsys,
):
    backup_file = tmp_path / "vault_backup_valid.json"
    user_inputs = iter(["1", "y"])

    monkeypatch.setattr(
        main,
        "list_vault_backups",
        lambda: [backup_file],
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(user_inputs),
    )

    restored_backup = None

    def fake_restore_vault_backup(selected_backup):
        nonlocal restored_backup
        restored_backup = selected_backup

    monkeypatch.setattr(
        main,
        "restore_vault_backup",
        fake_restore_vault_backup,
    )

    main.restore_backup_flow()

    captured = capsys.readouterr()

    assert restored_backup == backup_file
    assert "Vault backup restored successfully." in captured.out
