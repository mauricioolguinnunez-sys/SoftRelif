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

        asignar_permisos_base(cursor)
        conexion.commit()

        crear_usuario_sistema(
            cursor,
            nombre="Superuser",
            correo=SUPERUSER_EMAIL,
            password=SUPERUSER_PASSWORD,
            rol="superuser",
            tema="dark"
        )

        crear_usuario_sistema(
            cursor,
            nombre="Especialista",
            correo=SPECIALIST_EMAIL,
            password=SPECIALIST_PASSWORD,
            rol="especialista",
            tema="light"
        )

        sincronizar_estructura_documentada(cursor)
        conexion.commit()

        sincronizar_cuentas_iniciales(cursor)
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
            nombre VARCHAR(100) NOT NULL UNIQUE,
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
            nombre VARCHAR(50) NOT NULL UNIQUE,
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
            modo_visualizacion VARCHAR(50) NOT NULL DEFAULT 'estandar',

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
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(150) NOT NULL UNIQUE,
            contrasena VARCHAR(255) NOT NULL,
            fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            id_rol INT NOT NULL,
            id_estado INT NOT NULL,
            id_preferencia INT NOT NULL UNIQUE,

            CONSTRAINT chk_usuario_contrasena
                CHECK (CHAR_LENGTH(contrasena) >= 4),

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
            accion ENUM(
                'asignar_recomendacion',
                'cargar_recurso',
                'sugerir_musica',
                'activa',
                'restringida',
                'eliminar'
            ) NOT NULL,
            descripcion TEXT NOT NULL,
            fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

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
        "consultar_historial_bienestar",
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

def crear_usuario_sistema(cursor, nombre, correo, password, rol, tema="light"):
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
        valor=tema,
        campo_id="id_tema"
    )

    cursor.execute("""
        INSERT INTO preferencia_visual (
            id_tema,
            tamano_fuente,
            modo_visualizacion
        )
        VALUES (%s, %s, %s);
    """, (
        id_tema,
        "normal",
        "estandar"
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
# SINCRONIZACIÓN CON LA DOCUMENTACIÓN DECLARADA
# =====================================================

def obtener_tipo_columna(cursor, tabla, columna):
    cursor.execute("""
        SELECT COLUMN_TYPE, COLUMN_DEFAULT
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s;
    """, (tabla, columna))

    return cursor.fetchone()


def sincronizar_estructura_documentada(cursor):
    """
    Ajusta los tipos de columna a los declarados en la documentación
    (permiso.nombre VARCHAR(100), tema.nombre VARCHAR(50),
    preferencia_visual.modo_visualizacion VARCHAR(50),
    usuario.nombre VARCHAR(100), usuario.fecha_registro DATETIME,
    bitacora_cuenta.accion ENUM, descripcion TEXT,
    fecha_evento DATETIME DEFAULT CURRENT_TIMESTAMP).

    Solo altera cuando el tipo actual difiere; no borra datos.
    """

    accion_enum = (
        "enum('asignar_recomendacion','cargar_recurso','sugerir_musica',"
        "'activa','restringida','eliminar')"
    )

    cambios = [
        ("permiso", "nombre", "VARCHAR(100) NOT NULL", "varchar(100)"),
        ("tema", "nombre", "VARCHAR(50) NOT NULL", "varchar(50)"),
        (
            "preferencia_visual",
            "modo_visualizacion",
            "VARCHAR(50) NOT NULL DEFAULT 'estandar'",
            "varchar(50)",
        ),
        ("usuario", "nombre", "VARCHAR(100) NOT NULL", "varchar(100)"),
        (
            "usuario",
            "fecha_registro",
            "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "datetime",
        ),
        (
            "bitacora_cuenta",
            "accion",
            f"{accion_enum} NOT NULL",
            accion_enum,
        ),
        ("bitacora_cuenta", "descripcion", "TEXT NOT NULL", "text"),
        (
            "bitacora_cuenta",
            "fecha_evento",
            "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "datetime",
        ),
    ]

    for tabla, columna, definicion, tipo_esperado in cambios:
        fila = obtener_tipo_columna(cursor, tabla, columna)

        if not fila:
            continue

        tipo_actual = fila["COLUMN_TYPE"].lower()
        default_actual = fila["COLUMN_DEFAULT"]

        necesita_cambio = tipo_actual != tipo_esperado

        if "DEFAULT" in definicion and default_actual is None:
            necesita_cambio = True

        if necesita_cambio:
            cursor.execute(
                f"ALTER TABLE {tabla} MODIFY COLUMN {columna} {definicion};"
            )
            print(f"Columna '{tabla}.{columna}' ajustada.")

    sincronizar_check_contrasena(cursor)


def sincronizar_check_contrasena(cursor):
    """
    Garantiza la restricción CHECK de usuario.contrasena (mínimo 4 caracteres),
    equivalente a la validación de utils/validation_utils.validar_password.
    """

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM information_schema.table_constraints
        WHERE table_schema = DATABASE()
          AND table_name = 'usuario'
          AND constraint_name = 'chk_usuario_contrasena';
    """)

    fila = cursor.fetchone()
    existe = fila["total"] > 0

    if not existe:
        cursor.execute("""
            ALTER TABLE usuario
            ADD CONSTRAINT chk_usuario_contrasena
            CHECK (CHAR_LENGTH(contrasena) >= 4);
        """)
        print("Restricción CHECK chk_usuario_contrasena agregada a usuario.")


def sincronizar_cuentas_iniciales(cursor):
    """
    Alinea las cuentas del sistema con la documentación:
    - Superuser con tema dark.
    - Nombres exactos 'Superuser' y 'Especialista'.

    Solo se aplica si el nombre sigue siendo el valor legacy,
    por lo que no pisa cambios posteriores hechos desde la app.
    """

    id_tema_dark = obtener_id(
        cursor,
        tabla="tema",
        campo="nombre",
        valor="dark",
        campo_id="id_tema"
    )

    cursor.execute("""
        UPDATE usuario u
        JOIN preferencia_visual pv
            ON u.id_preferencia = pv.id_preferencia
        SET u.nombre = %s,
            pv.id_tema = %s
        WHERE u.correo = %s
          AND u.nombre = %s;
    """, ("Superuser", id_tema_dark, SUPERUSER_EMAIL, "Superuser SoftRelief"))

    cursor.execute("""
        UPDATE usuario u
        SET u.nombre = %s
        WHERE u.correo = %s
          AND u.nombre = %s;
    """, ("Especialista", SPECIALIST_EMAIL, "Especialista SoftRelief"))


if __name__ == "__main__":
    create_tables()
    print("Base de datos relacional de SoftRelief creada/verificada correctamente.")