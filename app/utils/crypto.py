import bcrypt


def hash_password(password):
    if password is None:
        return None

    if isinstance(password, unicode):
        password = password.encode('utf-8')

    return bcrypt.hashpw(password, bcrypt.gensalt())


def authenticate_password(password, hash):
    if password is None or hash is None:
        return False

    if isinstance(password, unicode):
        password = password.encode('utf-8')

    return hash == bcrypt.hashpw(password, hash)
