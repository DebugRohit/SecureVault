"""
Password strength analysis service for SecureVault.
"""

import string


def check_password_strength(password: str) -> str:
    """
    Analyse a password and return its strength rating.
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    score = 0

    if len(password) >= 12:
        score += 1

    if any(character.islower() for character in password):
        score += 1

    if any(character.isupper() for character in password):
        score += 1

    if any(character.isdigit() for character in password):
        score += 1

    if any(character in string.punctuation for character in password):
        score += 1

    if score <= 2:
        return "Weak"

    if score <= 4:
        return "Medium"

    return "Strong"
