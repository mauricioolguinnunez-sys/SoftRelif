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
        id_usuario INT NOT NULL AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        usuario VARCHAR(80) NOT NULL UNIQUE,
        correo VARCHAR(150) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        fecha_registro VARCHAR(30) NOT NULL,
        rol VARCHAR(30) NOT NULL DEFAULT 'usuario',
        estado VARCHAR(30) NOT NULL DEFAULT 'activa',
        PRIMARY KEY (id_usuario)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS preferencias (
        id_preferencia INT NOT NULL AUTO_INCREMENT,
        id_usuario INT NOT NULL UNIQUE,
        tema_visual VARCHAR(20) DEFAULT 'light',
        sonido_default VARCHAR(50) DEFAULT 'lluvia',
        volumen INT DEFAULT 50,
        animaciones INT DEFAULT 1,
        PRIMARY KEY (id_preferencia),
        CONSTRAINT fk_preferencias_usuario
            FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id_usuario)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    connection.commit()

    ensure_columns(cursor, connection)
    create_superuser(cursor, connection)

    cursor.close()
    connection.close()


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE %s;", (column_name,))
    return cursor.fetchone() is not None


def ensure_columns(cursor, connection):
    if not column_exists(cursor, "usuarios", "rol"):
        cursor.execute("ALTER TABLE usuarios ADD COLUMN rol VARCHAR(30) NOT NULL DEFAULT 'usuario';")

    if not column_exists(cursor, "usuarios", "estado"):
        cursor.execute("ALTER TABLE usuarios ADD COLUMN estado VARCHAR(30) NOT NULL DEFAULT 'activa';")

    if not column_exists(cursor, "preferencias", "tema_visual"):
        cursor.execute("ALTER TABLE preferencias ADD COLUMN tema_visual VARCHAR(20) DEFAULT 'light';")

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
        VALUES (%s, %s, %s, %s, %s, %s, %s);
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
        VALUES (%s, %s, %s, %s, %s);
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
    print("Base de datos creada correctamente en MariaDB.")