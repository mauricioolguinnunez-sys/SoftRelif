import hashlib


def hash_password(password):
    """
    Convierte una contraseña en un hash SHA-256.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password, password_hash):
    """
    Verifica si la contraseña escrita coincide con el hash guardado.
    """
    return hash_password(password) == password_hash