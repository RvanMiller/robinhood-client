"""Contains helper functions related to authentication."""

import secrets


def generate_device_token():
    """Generates a cryptographically secure device token."""
    rands = [secrets.randbelow(256) for _ in range(16)]
    token = ""
    for i, r in enumerate(rands):
        token += f"{r:02x}"
        if i in [3, 5, 7, 9]:
            token += "-"
    return token
