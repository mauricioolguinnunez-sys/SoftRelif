from datetime import datetime

from database.connection import get_connection
from utils.password_utils import hash_password


SUPERUSER_USERNAME = "superuser"
SUPERUSER_PASSWORD = "admin123"
SUPERUSER_EMAIL = "superuser@softrelief.local"

SPECIALIST_USERNAME = "especialista"
SPECIALIST_PASSWORD = "especialista123"
SPECIALIST_EMAIL = "especialista@softrelief.local"


def create_tables():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    create_core_tables(cursor)
    create_role_catalog(cursor)
    create_specialist_tables(cursor)

    connection.commit()

    ensure_role_catalog(cursor, connection)
    ensure_preferences_for_existing_users(cursor, connection)

    create_system_user(
        cursor,
        connection,
        nombre="Superuser SoftRelief",
        usuario=SUPERUSER_USERNAME,
        correo=SUPERUSER_EMAIL,
        password=SUPERUSER_PASSWORD,
        rol="superuser"
    )

    create_system_user(
        cursor,
        connection,
        nombre="Especialista SoftRelief",
        usuario=SPECIALIST_USERNAME,
        correo=SPECIALIST_EMAIL,
        password=SPECIALIST_PASSWORD,
        rol="especialista"
    )

    cursor.close()
    connection.close()


def create_core_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL,
            usuario VARCHAR(80) NOT NULL UNIQUE,
            correo VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            fecha_registro DATETIME NOT NULL,
            rol ENUM('usuario', 'especialista', 'superuser') NOT NULL DEFAULT 'usuario',
            estado ENUM('activa', 'restringida') NOT NULL DEFAULT 'activa'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferencias (
            id_preferencia INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL UNIQUE,
            tema_visual ENUM('light', 'dark') DEFAULT 'light',
            sonido_default VARCHAR(80) DEFAULT 'lluvia',
            volumen INT DEFAULT 50,
            animaciones TINYINT DEFAULT 1,
            CONSTRAINT fk_preferencias_usuario
                FOREIGN KEY (id_usuario)
                REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)


def create_role_catalog(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INT AUTO_INCREMENT PRIMARY KEY,
            nombre_rol VARCHAR(50) NOT NULL UNIQUE,
            descripcion TEXT NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)


def create_specialist_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recomendaciones_especialista (
            id_recomendacion INT AUTO_INCREMENT PRIMARY KEY,
            id_especialista INT NOT NULL,
            id_usuario INT NOT NULL,
            titulo VARCHAR(150) NOT NULL,
            descripcion TEXT NOT NULL,
            fecha_asignacion DATETIME NOT NULL,
            estado ENUM('activa', 'atendida', 'cancelada') NOT NULL DEFAULT 'activa',
            CONSTRAINT fk_recomendacion_especialista
                FOREIGN KEY (id_especialista)
                REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE,
            CONSTRAINT fk_recomendacion_usuario
                FOREIGN KEY (id_usuario)
                REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seguimientos (
            id_seguimiento INT AUTO_INCREMENT PRIMARY KEY,
            id_especialista INT NOT NULL,
            id_usuario INT NOT NULL,
            nota TEXT NOT NULL,
            estado_seguimiento ENUM('revisado', 'pendiente', 'cerrado') NOT NULL DEFAULT 'revisado',
            fecha_seguimiento DATETIME NOT NULL,
            CONSTRAINT fk_seguimiento_especialista
                FOREIGN KEY (id_especialista)
                REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE,
            CONSTRAINT fk_seguimiento_usuario
                FOREIGN KEY (id_usuario)
                REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recursos_especialista (
            id_recurso INT AUTO_INCREMENT PRIMARY KEY,
            id_especialista INT NOT NULL,
            titulo VARCHAR(150) NOT NULL,
            descripcion TEXT,
            tipo_recurso VARCHAR(80) DEFAULT 'texto',
            contenido TEXT NOT NULL,
            fecha_carga DATETIME NOT NULL,
            estado ENUM('activo', 'inactivo') NOT NULL DEFAULT 'activo',
            CONSTRAINT fk_recurso_especialista
                FOREIGN KEY (id_especialista)
                REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id_checkin INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            stress INT,
            energy INT,
            focus INT,
            mental_fatigue INT,
            mood VARCHAR(80),
            phrase TEXT,
            recommendation_title VARCHAR(150),
            recommendation_text TEXT,
            created_at DATETIME NOT NULL,
            CONSTRAINT fk_checkin_usuario
                FOREIGN KEY (id_usuario)
                REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS microdescansos_historial (
            id_microdescanso INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            title VARCHAR(150) NOT NULL,
            category VARCHAR(80),
            duration INT,
            description TEXT,
            started_at DATETIME NOT NULL,
            completed TINYINT DEFAULT 1,
            CONSTRAINT fk_microdescanso_usuario
                FOREIGN KEY (id_usuario)
                REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)


def ensure_role_catalog(cursor, connection):
    roles = [
        ("usuario", "Usuario regular con acceso a funciones de bienestar personal."),
        ("especialista", "Usuario con acceso a seguimiento, recomendaciones y recursos."),
        ("superuser", "Administrador principal con acceso a gestión del sistema."),
    ]

    for nombre_rol, descripcion in roles:
        cursor.execute("""
            INSERT IGNORE INTO roles (nombre_rol, descripcion)
            VALUES (%s, %s);
        """, (nombre_rol, descripcion))

    connection.commit()


def ensure_preferences_for_existing_users(cursor, connection):
    cursor.execute("""
        INSERT IGNORE INTO preferencias (
            id_usuario,
            tema_visual,
            sonido_default,
            volumen,
            animaciones
        )
        SELECT
            id_usuario,
            'light',
            'lluvia',
            50,
            1
        FROM usuarios;
    """)

    connection.commit()


def create_system_user(cursor, connection, nombre, usuario, correo, password, rol):
    cursor.execute("""
        SELECT id_usuario
        FROM usuarios
        WHERE usuario = %s OR correo = %s OR rol = %s
        LIMIT 1;
    """, (usuario, correo, rol))

    existing_user = cursor.fetchone()

    if existing_user:
        return

    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    password_hash = hash_password(password)

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
        nombre,
        usuario,
        correo,
        password_hash,
        fecha_registro,
        rol,
        "activa"
    ))

    id_usuario = cursor.lastrowid

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
        id_usuario,
        "light",
        "lluvia",
        50,
        1
    ))

    connection.commit()


if __name__ == "__main__":
    create_tables()
    print("Base de datos MySQL creada/verificada correctamente.")