from database.connection import get_connection
from utils.password_utils import hash_password
from datetime import datetime


SUPERUSER_USERNAME = "superuser"
SUPERUSER_PASSWORD = "admin123"
SUPERUSER_EMAIL = "superuser@softrelief.local"


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            correo TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            fecha_registro TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'usuario',
            estado TEXT NOT NULL DEFAULT 'activa'
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferencias (
            id_preferencia INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL UNIQUE,
            tema_visual TEXT DEFAULT 'light',
            sonido_default TEXT DEFAULT 'lluvia',
            volumen INTEGER DEFAULT 50,
            animaciones INTEGER DEFAULT 1,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
    """)

    connection.commit()

    ensure_columns(cursor, connection)
    create_superuser(cursor, connection)

    connection.close()


def ensure_columns(cursor, connection):
    cursor.execute("PRAGMA table_info(usuarios);")
    columnas_usuarios = [columna["name"] for columna in cursor.fetchall()]

    if "rol" not in columnas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN rol TEXT NOT NULL DEFAULT 'usuario';")

    if "estado" not in columnas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN estado TEXT NOT NULL DEFAULT 'activa';")

    cursor.execute("PRAGMA table_info(preferencias);")
    columnas_preferencias = [columna["name"] for columna in cursor.fetchall()]

    if "tema_visual" not in columnas_preferencias:
        cursor.execute("ALTER TABLE preferencias ADD COLUMN tema_visual TEXT DEFAULT 'light';")

    connection.commit()


def create_superuser(cursor, connection):
    cursor.execute("""
        SELECT id_usuario
        FROM usuarios
        WHERE rol = 'superuser'
        LIMIT 1;
    """)

    superuser = cursor.fetchone()

    if superuser:
        return

    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    password_hash = hash_password(SUPERUSER_PASSWORD)

    cursor.execute("""
        INSERT INTO usuarios (
            nombre,
            usuario,
            correo,
            password_hash,
            fecha_registro,
            rol,
            estado
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (
        "Superuser SoftRelief",
        SUPERUSER_USERNAME,
        SUPERUSER_EMAIL,
        password_hash,
        fecha_registro,
        "superuser",
        "activa"
    ))

    id_superuser = cursor.lastrowid

    cursor.execute("""
        INSERT INTO preferencias (
            id_usuario,
            tema_visual,
            sonido_default,
            volumen,
            animaciones
        )
        VALUES (?, ?, ?, ?, ?);
    """, (
        id_superuser,
        "light",
        "lluvia",
        50,
        1
    ))

    connection.commit()


if __name__ == "__main__":
    create_tables()
    print("Base de datos creada correctamente.")