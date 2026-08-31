"""
SecureVault command-line interface.
"""

from getpass import getpass

from src.auth.authentication import (
    authenticate_master_password,
    is_master_password_configured,
    setup_master_password,
)
from src.models.credential import Credential
from src.services.backup_service import (
    create_vault_backup,
    list_vault_backups,
    restore_vault_backup,
)
from src.services.password_generator import generate_password
from src.services.password_strength import check_password_strength
from src.services.vault_service import load_credentials, save_credentials


def setup_master_password_flow() -> None:
    """
    Guide the user through master password setup.
    """
    print("No master password is configured.")
    print("Set up a master password to continue.")

    password = getpass("Enter master password: ")
    confirm_password = getpass("Confirm master password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        return

    setup_master_password(password)

    print("Master password configured successfully.")


def login_flow() -> bool:
    """
    Authenticate the user with the master password.

    Returns:
        bool:True if authentication succeeds, otherwise False.
    """
    password = getpass("Enter master password: ")

    if authenticate_master_password(password):
        print("Authentication successful.")
        return True

    print("Authentication failed.")
    return False


def add_password_flow() -> None:
    """
    Add a new credential to the encrypted vault.
    """
    service = input("Enter service name: ").strip()
    username = input("Enter username: ").strip()

    print("1. Enter password manually")
    print("2. Generate secure password")

    password_choice = input("Choose password option: ").strip()

    if password_choice == "1":
        password = getpass("Enter password: ")
        strength = check_password_strength(password)
        print(f"Password strength: {strength}")
    elif password_choice == "2":
        password = generate_password()
        print("Secure password generated successfully.")
    else:
        print("Invalid password option.")
        return

    credential = Credential(
        service=service,
        username=username,
        password=password,
    )

    credentials = load_credentials()
    credentials.append(credential)
    save_credentials(credentials)

    print("Password added successfully.")


def view_passwords_flow() -> None:
    """
    Display stored credentials without exposing passwords.
    """
    credentials = load_credentials()

    if not credentials:
        print("No passwords stored.")
        return

    print("Stored credentials:")

    for index, credential in enumerate(credentials, start=1):
        print(
            f"{index}. Service: {credential.service} | "
            f"Username: {credential.username}"
        )


def reveal_password_flow() -> None:
    """
    Reveal one stored password after re-authentication.
    """
    credentials = load_credentials()

    if not credentials:
        print("No passwords stored.")
        return

    print("Stored credentials:")

    for index, credential in enumerate(credentials, start=1):
        print(f"{index}. {credential.service} " f"({credential.username})")

    choice = input("Select credential number: ").strip()

    if not choice.isdigit():
        print("Invalid selection.")
        return

    index = int(choice) - 1

    if index < 0 or index >= len(credentials):
        print("Invalid selection.")
        return

    master_password = getpass("Re-enter master password: ")

    if not authenticate_master_password(master_password):
        print("Authentication failed.")
        return

    print(f"Password: {credentials[index].password}")


def edit_credential_flow() -> None:
    """
    Edit an existing credential in the encrypted vault.
    """
    credentials = load_credentials()

    if not credentials:
        print("No passwords stored.")
        return

    print("Stored credentials:")

    for index, credential in enumerate(credentials, start=1):
        print(f"{index}. {credential.service} ({credential.username})")

    choice = input("Select credential number to edit: ").strip()

    if not choice.isdigit():
        print("Invalid selection.")
        return

    index = int(choice) - 1

    if index < 0 or index >= len(credentials):
        print("Invalid selection.")
        return

    service = input("Enter new service name: ").strip()
    username = input("Enter new username: ").strip()
    password = getpass("Enter new password: ")

    credentials[index] = Credential(
        service=service,
        username=username,
        password=password,
    )

    save_credentials(credentials)

    print("Credential updated successfully.")


def delete_credential_flow() -> None:
    """
    Delete a selected credential after explicit confirmation.
    """
    credentials = load_credentials()

    if not credentials:
        print("No passwords stored.")
        return

    print("Stored credentials:")

    for index, credential in enumerate(credentials, start=1):
        print(f"{index}. {credential.service} ({credential.username})")

    choice = input("Select credential number to delete: ").strip()

    if not choice.isdigit():
        print("Invalid selection.")
        return

    index = int(choice) - 1

    if index < 0 or index >= len(credentials):
        print("Invalid selection.")
        return

    credential = credentials[index]

    confirmation = (
        input(
            f"Delete {credential.service} ({credential.username})? "
            "Type y to confirm: "
        )
        .strip()
        .lower()
    )

    if confirmation != "y":
        print("Deletion cancelled.")
        return

    credentials.pop(index)
    save_credentials(credentials)

    print("Credential deleted successfully.")


def create_backup_flow() -> None:
    """
    Create a backup of the encrypted vault.
    """
    try:
        backup_file = create_vault_backup()
    except FileNotFoundError:
        print("Vault file not found.")
        return

    print(f"Vault backup created: {backup_file.name}")


def restore_backup_flow() -> None:
    """
    Restore a validated vault backup after explicit confirmation.
    """
    backups = list_vault_backups()

    if not backups:
        print("No vault backups found.")
        return

    print("Available vault backups:")

    for index, backup_file in enumerate(backups, start=1):
        print(f"{index}. {backup_file.name}")

    choice = input("Select backup number to restore: ").strip()

    if not choice.isdigit():
        print("Invalid selection.")
        return

    index = int(choice) - 1

    if index < 0 or index >= len(backups):
        print("Invalid selection.")
        return

    selected_backup = backups[index]

    confirmation = (
        input(f"Restore {selected_backup.name}? " "Type y to confirm: ").strip().lower()
    )

    if confirmation != "y":
        print("Restore cancelled.")
        return

    try:
        restore_vault_backup(selected_backup)
    except (FileNotFoundError, ValueError):
        print("Unable to restore vault backup.")
        return

    print("Vault backup restored successfully.")


def vault_menu() -> None:
    """
    Display the SecureVault menu after successful authentication.
    """
    print("SecureVault unlocked.")

    while True:
        print()
        print("SecureVault Menu")
        print("1. Add password")
        print("2. View passwords")
        print("3. Reveal password")
        print("4. Edit credential")
        print("5. Delete credential")
        print("6. Create vault backup")
        print("7. Restore vault backup")
        print("8. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_password_flow()
        elif choice == "2":
            view_passwords_flow()
        elif choice == "3":
            reveal_password_flow()
        elif choice == "4":
            edit_credential_flow()
        elif choice == "5":
            delete_credential_flow()
        elif choice == "6":
            create_backup_flow()
        elif choice == "7":
            restore_backup_flow()
        elif choice == "8":
            print("SecureVault locked.")
            return
        else:
            print("Invalid option. " "Please choose 1, 2, 3, 4, 5, 6, 7, or 8.")


def main() -> None:
    """
    Run the SecureVault command-line interface.
    """
    if not is_master_password_configured():
        setup_master_password_flow()
        return

    if login_flow():
        vault_menu()


if __name__ == "__main__":
    main()
