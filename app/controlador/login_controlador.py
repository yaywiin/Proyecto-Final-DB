import hashlib
from app.modelo.conexion import consultar

def cifrar_password(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

def autenticar_usuario(username, password):
    """
    Verifica las credenciales en la base de datos real.
    Devuelve el diccionario del usuario si es exitoso, o None si falla.
    """
    username_limpio = username.strip()
    password_cifrada = cifrar_password(password)

    sql = "SELECT * FROM usuarios WHERE usuario = %s AND password = %s AND activo = 1"
    
    resultados = consultar(sql, (username_limpio, password_cifrada))


    if resultados:
        return resultados[0]
    
    return None