import secrets
import hashlib


def generate_reset_token():

    return secrets.token_urlsafe(32)


def hash_reset_token(token: str):

    return hashlib.sha256(
        token.encode()
    ).hexdigest()