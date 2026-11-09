import hashlib

USUARIOS_PRUEBA = {
    "admin": {
        "usuario_id": 1,
        "nombre": "Administrador",
        "email": "admin@estacionamiento.com",
        "username": "admin",
        "password": hashlib.sha256(b"admin123").hexdigest(),
        "perfil": "admin",
    },
    "cobrador": {
        "usuario_id": 2,
        "nombre": "Cobrador Turno",
        "email": "cobrador@estacionamiento.com",
        "username": "cobrador",
        "password": hashlib.sha256(b"cobrador123").hexdigest(),
        "perfil": "cobrador",
    },
}


def cifrar_password(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def autenticar_usuario(username, password):
    usuario = USUARIOS_PRUEBA.get(username.strip())
    if not usuario:
        return None

    if usuario["password"] == cifrar_password(password):
        return usuario
    return None