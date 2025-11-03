import os
from cryptography.fernet import Fernet


_cached = None


def _get_fernet() -> Fernet:
    global _cached
    if _cached is not None:
        return _cached
    key = os.getenv('CHAT_ENC_KEY')
    if not key:
        # Generate an ephemeral key if not provided; logs would be better, but avoid printing secrets
        key = Fernet.generate_key().decode('utf-8')
        os.environ['CHAT_ENC_KEY'] = key
    _cached = Fernet(key.encode('utf-8'))
    return _cached


def encrypt_text(plaintext: str) -> str:
    if plaintext is None:
        return ''
    f = _get_fernet()
    token = f.encrypt(plaintext.encode('utf-8'))
    return token.decode('utf-8')


def decrypt_text(token: str) -> str:
    if not token:
        return ''
    f = _get_fernet()
    try:
        return f.decrypt(token.encode('utf-8')).decode('utf-8')
    except Exception:
        # If decrypt fails (legacy plaintext), return as-is
        return token


