"""Punto de entrada.

Por ahora solo comprueba que la conexión a la base funciona:

    python -m app.main
"""

from app.modelo.conexion import ErrorBD, consultar


def main():
    try:
        version = consultar("SELECT VERSION() AS version")[0]["version"]
    except ErrorBD as error:
        print(f"✗ {error}")
        raise SystemExit(1)
    print(f"✓ Conexión exitosa. MariaDB {version}")


if __name__ == "__main__":
    main()
