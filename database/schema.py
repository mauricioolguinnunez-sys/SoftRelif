from datetime import date

from database.connection import get_connection
from utils.constants import (
    SPECIALIST_EMAIL,
    SPECIALIST_PASSWORD,
    SUPERUSER_EMAIL,
    SUPERUSER_PASSWORD,
)
from utils.password_utils import hash_password


def create_tables():
    """
    Crea únicamente la base de datos relacional definida para SoftRelief.

    Modelo relacional:
    - ESTADO_CUENTA
    - ROL
    - PERMISO
    - ROL_PERMISO
    - TEMA
    - PREFERENCIA_VISUAL
    - USUARIO
    - BITACORA_CUENTA

    Los datos de bienestar (check-ins, música, microdescansos)
    se almacenan en MongoDB, identificados por id_usuario.
    """

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        crear_tablas(cursor)
        conexion.commit()

        insertar_catalogos_base(cursor)
        conexion.commit()

        migrar_idioma_preferencia_visual(cursor)
        conexion.commit()

        asignar_permisos_base(cursor)
        conexion.commit()

        crear_usuario_sistema(
            cursor,
            nombre="Superuser SoftRelief",
            correo=SUPERUSER_EMAIL,
            password=SUPERUSER_PASSWORD,
            rol="superuser"
        )

        crear_usuario_sistema(
            cursor,
            nombre="Especialista SoftRelief",
            correo=SPECIALIST_EMAIL,
            password=SPECIALIST_PASSWORD,
            rol="especialista"
        )

        conexion.commit()

    finally:
        cursor.close()
        conexion.close()


# =====================================================
# CREACIÓN DE TABLAS
# =====================================================

def crear_tablas(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estado_cuenta (
            id_estado INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL UNIQUE,
            descripcion VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rol (
            id_rol INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL UNIQUE,
            descripcion VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permiso (
            id_permiso INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(80) NOT NULL UNIQUE,
            descripcion VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rol_permiso (
            id_rol INT NOT NULL,
            id_permiso INT NOT NULL,

            PRIMARY KEY (id_rol, id_permiso),

            CONSTRAINT fk_rol_permiso_rol
                FOREIGN KEY (id_rol)
                REFERENCES rol(id_rol)
                ON UPDATE CASCADE
                ON DELETE CASCADE,

            CONSTRAINT fk_rol_permiso_permiso
                FOREIGN KEY (id_permiso)
                REFERENCES permiso(id_permiso)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tema (
            id_tema INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(30) NOT NULL UNIQUE,
            descripcion VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferencia_visual (
            id_preferencia INT AUTO_INCREMENT PRIMARY KEY,
            id_tema INT NOT NULL,
            tamano_fuente VARCHAR(30) NOT NULL DEFAULT 'normal',
            modo_visualizacion VARCHAR(30) NOT NULL DEFAULT 'estandar',
            idioma VARCHAR(10) NOT NULL DEFAULT 'es',

            CONSTRAINT fk_preferencia_tema
                FOREIGN KEY (id_tema)
                REFERENCES tema(id_tema)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL,
            correo VARCHAR(150) NOT NULL UNIQUE,
            contrasena VARCHAR(255) NOT NULL,
            fecha_registro DATE NOT NULL,
            id_rol INT NOT NULL,
            id_estado INT NOT NULL,
            id_preferencia INT NOT NULL UNIQUE,

            CONSTRAINT fk_usuario_rol
                FOREIGN KEY (id_rol)
                REFERENCES rol(id_rol)
                ON UPDATE CASCADE
                ON DELETE RESTRICT,

            CONSTRAINT fk_usuario_estado
                FOREIGN KEY (id_estado)
                REFERENCES estado_cuenta(id_estado)
                ON UPDATE CASCADE
                ON DELETE RESTRICT,

            CONSTRAINT fk_usuario_preferencia
                FOREIGN KEY (id_preferencia)
                REFERENCES preferencia_visual(id_preferencia)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitacora_cuenta (
            id_bitacora INT AUTO_INCREMENT PRIMARY KEY,
            id_admin INT NULL,
            id_usuario INT NULL,
            accion VARCHAR(80) NOT NULL,
            descripcion VARCHAR(255) NOT NULL,
            fecha_evento DATETIME NOT NULL,

            CONSTRAINT fk_bitacora_admin
                FOREIGN KEY (id_admin)
                REFERENCES usuario(id_usuario)
                ON UPDATE CASCADE
                ON DELETE SET NULL,

            CONSTRAINT fk_bitacora_usuario
                FOREIGN KEY (id_usuario)
                REFERENCES usuario(id_usuario)
                ON UPDATE CASCADE
                ON DELETE SET NULL
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_unicode_ci;
    """)


# =====================================================
# CATÁLOGOS BASE
# =====================================================

def insertar_catalogos_base(cursor):
    estados = [
        (
            "activa",
            "Cuenta activa con acceso permitido al sistema."
        ),
        (
            "restringida",
            "Cuenta limitada por decisión administrativa."
        ),
    ]

    roles = [
        (
            "usuario",
            "Usuario regular con acceso a funciones de bienestar personal."
        ),
        (
            "especialista",
            "Usuario encargado de asesoría, seguimiento y recursos."
        ),
        (
            "superuser",
            "Administrador principal del sistema."
        ),
    ]

    temas = [
        (
            "light",
            "Tema visual claro."
        ),
        (
            "dark",
            "Tema visual oscuro."
        ),
    ]

    permisos = [
        (
            "checkin",
            "Permite registrar check-in emocional."
        ),
        (
            "modo_calma",
            "Permite acceder al modo calma."
        ),
        (
            "sonidos",
            "Permite acceder a sonidos ambientales."
        ),
        (
            "microdescansos",
            "Permite realizar microdescansos."
        ),
        (
            "historial",
            "Permite consultar historial personal."
        ),
        (
            "configuracion",
            "Permite modificar preferencias visuales."
        ),
        (
            "panel_especialista",
            "Permite acceder al panel especialista."
        ),
        (
            "trayectoria_usuario",
            "Permite consultar trayectoria de usuarios."
        ),
        (
            "asignar_recomendacion",
            "Permite asignar recomendaciones."
        ),
        (
            "marcar_seguimiento",
            "Permite marcar seguimiento."
        ),
        (
            "cargar_recurso",
            "Permite cargar recursos de apoyo."
        ),
        (
            "gestionar_usuarios",
            "Permite administrar cuentas."
        ),
        (
            "moderar_usuarios",
            "Permite activar, restringir o eliminar usuarios."
        ),
        (
            "gestionar_roles",
            "Permite gestionar roles y permisos."
        ),
        (
            "consultar_historial_bienestar",
            "Permite consultar el historial de bienestar en MongoDB."
        ),
        (
            "sugerir_musica",
            "Permite sugerir música a usuarios."
        ),
    ]

    for nombre, descripcion in estados:
        cursor.execute("""
            INSERT IGNORE INTO estado_cuenta (
                nombre,
                descripcion
            )
            VALUES (%s, %s);
        """, (nombre, descripcion))

    for nombre, descripcion in roles:
        cursor.execute("""
            INSERT IGNORE INTO rol (
                nombre,
                descripcion
            )
            VALUES (%s, %s);
        """, (nombre, descripcion))

    for nombre, descripcion in temas:
        cursor.execute("""
            INSERT IGNORE INTO tema (
                nombre,
                descripcion
            )
            VALUES (%s, %s);
        """, (nombre, descripcion))

    for nombre, descripcion in permisos:
        cursor.execute("""
            INSERT IGNORE INTO permiso (
                nombre,
                descripcion
            )
            VALUES (%s, %s);
        """, (nombre, descripcion))


# =====================================================
# PERMISOS POR ROL
# =====================================================

def asignar_permisos_base(cursor):
    permisos_usuario = [
        "checkin",
        "modo_calma",
        "sonidos",
        "microdescansos",
        "historial",
        "configuracion",
    ]

    permisos_especialista = [
        "panel_especialista",
        "trayectoria_usuario",
        "asignar_recomendacion",
        "marcar_seguimiento",
        "cargar_recurso",
        "sugerir_musica",
        "consultar_historial_bienestar",
        "configuracion",
    ]

    permisos_superuser = [
        "gestionar_usuarios",
        "moderar_usuarios",
        "gestionar_roles",
        "configuracion",
    ]

    for permiso in permisos_usuario:
        asignar_permiso(cursor, "usuario", permiso)

    for permiso in permisos_especialista:
        asignar_permiso(cursor, "especialista", permiso)

    for permiso in permisos_superuser:
        asignar_permiso(cursor, "superuser", permiso)


def asignar_permiso(cursor, nombre_rol, nombre_permiso):
    id_rol = obtener_id(
        cursor,
        tabla="rol",
        campo="nombre",
        valor=nombre_rol,
        campo_id="id_rol"
    )

    id_permiso = obtener_id(
        cursor,
        tabla="permiso",
        campo="nombre",
        valor=nombre_permiso,
        campo_id="id_permiso"
    )

    cursor.execute("""
        INSERT IGNORE INTO rol_permiso (
            id_rol,
            id_permiso
        )
        VALUES (%s, %s);
    """, (id_rol, id_permiso))


# =====================================================
# USUARIOS BASE
# =====================================================

def crear_usuario_sistema(cursor, nombre, correo, password, rol):
    cursor.execute("""
        SELECT id_usuario
        FROM usuario
        WHERE correo = %s
        LIMIT 1;
    """, (correo,))

    if cursor.fetchone():
        return

    id_rol = obtener_id(
        cursor,
        tabla="rol",
        campo="nombre",
        valor=rol,
        campo_id="id_rol"
    )

    id_estado = obtener_id(
        cursor,
        tabla="estado_cuenta",
        campo="nombre",
        valor="activa",
        campo_id="id_estado"
    )

    id_tema = obtener_id(
        cursor,
        tabla="tema",
        campo="nombre",
        valor="light",
        campo_id="id_tema"
    )

    cursor.execute("""
        INSERT INTO preferencia_visual (
            id_tema,
            tamano_fuente,
            modo_visualizacion,
            idioma
        )
        VALUES (%s, %s, %s, %s);
    """, (
        id_tema,
        "normal",
        "estandar",
        "es"
    ))

    id_preferencia = cursor.lastrowid

    cursor.execute("""
        INSERT INTO usuario (
            nombre,
            correo,
            contrasena,
            fecha_registro,
            id_rol,
            id_estado,
            id_preferencia
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (
        nombre,
        correo,
        hash_password(password),
        date.today(),
        id_rol,
        id_estado,
        id_preferencia
    ))

    id_usuario = cursor.lastrowid


# =====================================================
# UTILIDADES
# =====================================================

def obtener_id(cursor, tabla, campo, valor, campo_id):
    cursor.execute(
        f"""
        SELECT {campo_id}
        FROM {tabla}
        WHERE {campo} = %s
        LIMIT 1;
        """,
        (valor,)
    )

    resultado = cursor.fetchone()

    if not resultado:
        raise ValueError(f"No existe '{valor}' en la tabla '{tabla}'.")

    return resultado[campo_id]


# =====================================================
# MIGRACIÓN SEGURA: idioma en preferencia_visual
# =====================================================

def migrar_idioma_preferencia_visual(cursor):
    """
    Agrega la columna 'idioma' a preferencia_visual si no existe.
    No hace DROP ni borra datos.
    """

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'preferencia_visual'
          AND column_name = 'idioma';
    """)

    row = cursor.fetchone()
    existe = row["total"] > 0

    if not existe:
        cursor.execute("""
            ALTER TABLE preferencia_visual
            ADD COLUMN idioma VARCHAR(10) NOT NULL DEFAULT 'es';
        """)

        print("Columna 'idioma' agregada a preferencia_visual.")


if __name__ == "__main__":
    create_tables()
    print("Base de datos relacional de SoftRelief creada/verificada correctamente.")