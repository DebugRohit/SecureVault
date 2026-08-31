"""
Secure password generation service for SecureVault.
"""

import secrets
import string

MIN_PASSWORD_LENGTH = 12


def generate_password(length: int = 16) -> str:
    """
    Generate a cryptographically secure password.
    """
    if length < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password length must be at least {MIN_PASSWORD_LENGTH}.")

    required_characters = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
    ]

    all_characters = (
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits
        + string.punctuation
    )

    remaining_length = length - len(required_characters)

    password_characters = required_characters + [
        secrets.choice(all_characters) for _ in range(remaining_length)
    ]

    secrets.SystemRandom().shuffle(password_characters)

    return "".join(password_characters)
