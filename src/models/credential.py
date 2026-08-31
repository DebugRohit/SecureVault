"""
Credential model for SecureVault.
"""

from dataclasses import dataclass, field


@dataclass
class Credential:
    """
    Represent a credential stored in SecureVault.
    """

    service: str
    username: str
    password: str = field(repr=False)

    def to_dict(self) -> dict[str, str]:
        """
        Convert the credential to a dictionary.
        """
        return {
            "service": self.service,
            "username": self.username,
            "password": self.password,
        }
