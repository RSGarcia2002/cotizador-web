from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from db import fetch_one, execute


class Usuario(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


def cargar_usuario(user_id):
    row = fetch_one("SELECT id, username FROM usuarios WHERE id = %s", (int(user_id),))
    if row:
        return Usuario(row["id"], row["username"])
    return None


def autenticar_usuario(username, password):
    row = fetch_one("SELECT id, username, password_hash FROM usuarios WHERE username = %s", (username,))
    if row and check_password_hash(row["password_hash"], password):
        return Usuario(row["id"], row["username"])
    return None


def crear_usuario(username, password):
    """Útil para correrlo una vez desde la consola de Render y crear tu usuario."""
    hash_ = generate_password_hash(password)
    execute(
        "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)",
        (username, hash_)
    )