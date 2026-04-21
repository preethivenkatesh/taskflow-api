import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, hashed_password: str) -> bool:
    salt, expected_hash = hashed_password.split("$")
    actual_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return actual_hash == expected_hash
