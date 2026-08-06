from datetime import datetime
import hmac

from database.connection import get_connection
import utils.password_utils as password_utils


class UserModel:
    """
    Modelo de usuarios compatible con MySQL.

    Compatible con:
    - AuthController.login()
    - AuthController.register()
    - UserController
    - SettingsView
    - SuperuserView
    """

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def normalize_user_id(user_or_id):
        """
        Permite recibir:
        - id_usuario directo
        - diccionario de usuario
        """

        if isinstance(user_or_id, dict):
            return user_or_id.get("id_usuario") or user_or_id.get("id")

        return user_or_id

    @staticmethod
    def is_probably_hash(value):
        if not value:
            return False

        value = str(value)

        # Hash SHA256 común: 64 caracteres hexadecimales
        if len(value) == 64:
            try:
                int(value, 16)
                return True
            except ValueError:
                pass

        # Formatos comunes de hash
        if value.startswith(("$2a$", "$2b$", "$2y$", "pbkdf2:", "scrypt:")):
            return True

        return False

    # =====================================================
    # PASSWORD
    # =====================================================

    @staticmethod
    def make_password_hash(password):
        """
        Genera hash de contraseña.

        Si por error llega una contraseña ya hasheada, evita hacer doble hash.
        """

        if not password:
            return ""

        password = str(password)

        if UserModel.is_probably_hash(password):
            return password

        if hasattr(password_utils, "hash_password"):
            return password_utils.hash_password(password)

        return password

    @staticmethod
    def verify_password(password, stored_hash):
        """
        Verifica contraseña soportando:
        - contraseña hasheada correctamente;
        - contraseña guardada en texto plano por error;
        - contraseña con doble hash accidental.
        """

        if not password or not stored_hash:
            return False

        password = str(password)
        stored_hash = str(stored_hash)

        # Caso 1: si existe verify_password en password_utils.py
        if hasattr(password_utils, "verify_password"):
            try:
                if password_utils.verify_password(password, stored_hash):
                    return True
            except TypeError:
                try:
                    if password_utils.verify_password(stored_hash, password):
                        return True
                except Exception:
                    pass
            except Exception:
                pass

        # Caso 2: hash normal
        if hasattr(password_utils, "hash_password"):
            hashed_once = password_utils.hash_password(password)

            if hmac.compare_digest(hashed_once, stored_hash):
                return True

            # Caso 3: por si algún usuario quedó con doble hash accidental
            hashed_twice = password_utils.hash_password(hashed_once)

            if hmac.compare_digest(hashed_twice, stored_hash):
                return True

        # Caso 4: por si algún usuario viejo quedó en texto plano
        if hmac.compare_digest(password, stored_hash):
            return True

        return False

    # =====================================================
    # AUTH
    # =====================================================

    @staticmethod
    def login(usuario, password):
        if not usuario or not password:
            return {
                "success": False,
                "message": "Ingresa usuario y contraseña."
            }

        user = UserModel.get_user_by_username_or_email(usuario)

        if not user:
            return {
                "success": False,
                "message": "Usuario o contraseña incorrectos."
            }

        if user.get("estado") == "restringida":
            return {
                "success": False,
                "message": "La cuenta está restringida. Contacta al administrador."
            }

        stored_hash = user.get("password_hash")

        if not UserModel.verify_password(password, stored_hash):
            return {
                "success": False,
                "message": "Usuario o contraseña incorrectos."
            }

        user.pop("password_hash", None)

        if not user.get("tema_visual"):
            user["tema_visual"] = "light"

        return {
            "success": True,
            "message": "Inicio de sesión correcto.",
            "user": user
        }

    @staticmethod
    def create_user(nombre, usuario, correo, password, rol="usuario"):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            password_hash = UserModel.make_password_hash(password)

            cursor.execute("""
                SELECT id_rol
                FROM rol
                WHERE nombre = %s
                LIMIT 1;
            """, (rol,))

            rol_row = cursor.fetchone()
            if not rol_row:
                rol = "usuario"
                cursor.execute("""
                    SELECT id_rol
                    FROM rol
                    WHERE nombre = %s
                    LIMIT 1;
                """, (rol,))
                rol_row = cursor.fetchone()

            if not rol_row:
                raise ValueError("No existe el rol solicitado en la base de datos.")

            cursor.execute("""
                SELECT id_estado
                FROM estado_cuenta
                WHERE nombre = 'activa'
                LIMIT 1;
            """)
            estado_row = cursor.fetchone()
            if not estado_row:
                raise ValueError("No existe el estado activa en la base de datos.")

            cursor.execute("""
                INSERT INTO tema (nombre, descripcion)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE nombre = nombre;
            """, ("light", "Tema claro predeterminado."))

            cursor.execute("""
                SELECT id_tema
                FROM tema
                WHERE nombre = 'light'
                LIMIT 1;
            """)
            tema_row = cursor.fetchone()
            if not tema_row:
                raise ValueError("No se pudo crear o localizar el tema light.")

            cursor.execute("""
                INSERT INTO preferencia_visual (
                    id_tema,
                    tamano_fuente,
                    modo_visualizacion,
                    idioma
                )
                VALUES (%s, %s, %s, %s);
            """, (
                tema_row["id_tema"],
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
                password_hash,
                datetime.now().strftime("%Y-%m-%d"),
                rol_row["id_rol"],
                estado_row["id_estado"],
                id_preferencia
            ))

            id_usuario = cursor.lastrowid
            connection.commit()

            return {
                "success": True,
                "message": "Usuario registrado correctamente.",
                "id_usuario": id_usuario
            }

        except Exception as error:
            connection.rollback()

            return {
                "success": False,
                "message": f"No se pudo registrar el usuario: {error}"
            }

        finally:
            cursor.close()
            connection.close()

    # =====================================================
    # GETTERS
    # =====================================================

    @staticmethod
    def get_user_by_username_or_email(identifier):
        identifier = str(identifier or "").strip()

        if not identifier:
            return None

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    u.id_usuario,
                    u.nombre,
                    u.correo,
                    u.contrasena AS password_hash,
                    u.fecha_registro,
                    r.nombre AS rol,
                    ec.nombre AS estado,
                    pv.id_preferencia,
                    t.nombre AS tema_visual,
                    pv.tamano_fuente,
                    pv.modo_visualizacion,
                    COALESCE(pv.idioma, 'es') AS idioma
                FROM usuario u
                LEFT JOIN rol r
                    ON u.id_rol = r.id_rol
                LEFT JOIN estado_cuenta ec
                    ON u.id_estado = ec.id_estado
                LEFT JOIN preferencia_visual pv
                    ON u.id_preferencia = pv.id_preferencia
                LEFT JOIN tema t
                    ON pv.id_tema = t.id_tema
                WHERE LOWER(TRIM(u.correo)) = LOWER(TRIM(%s))
                   OR LOWER(TRIM(u.nombre)) = LOWER(TRIM(%s))
                LIMIT 1;
            """, (identifier, identifier))

            user = cursor.fetchone()

            if user:
                user["usuario"] = user.get("correo")
                user["tema_visual"] = user.get("tema_visual") or "light"
                user["idioma"] = user.get("idioma") or "es"

            return user

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_user_by_username(usuario):
        return UserModel.get_user_by_username_or_email(usuario)

    @staticmethod
    def get_by_username(usuario):
        return UserModel.get_user_by_username_or_email(usuario)

    @staticmethod
    def get_user_by_id(id_usuario):
        id_usuario = UserModel.normalize_user_id(id_usuario)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    u.id_usuario,
                    u.nombre,
                    u.correo,
                    u.fecha_registro,
                    r.nombre AS rol,
                    ec.nombre AS estado,
                    t.nombre AS tema_visual,
                    pv.tamano_fuente,
                    pv.modo_visualizacion,
                    COALESCE(pv.idioma, 'es') AS idioma
                FROM usuario u
                LEFT JOIN rol r
                    ON u.id_rol = r.id_rol
                LEFT JOIN estado_cuenta ec
                    ON u.id_estado = ec.id_estado
                LEFT JOIN preferencia_visual pv
                    ON u.id_preferencia = pv.id_preferencia
                LEFT JOIN tema t
                    ON pv.id_tema = t.id_tema
                WHERE u.id_usuario = %s
                LIMIT 1;
            """, (id_usuario,))

            user = cursor.fetchone()

            if user:
                user["usuario"] = user.get("correo")
                user["tema_visual"] = user.get("tema_visual") or "light"
                user["idioma"] = user.get("idioma") or "es"

            return user

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_all_users():
        """
        Consulta todos los usuarios existentes para SuperuserView.

        Usa LEFT JOIN para no ocultar usuarios aunque falte alguna relación secundaria.
        Los datos de bienestar se consultan en MongoDB por id_usuario.
        """

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    u.id_usuario,
                    u.nombre,
                    u.correo,
                    u.correo AS usuario,
                    u.fecha_registro,

                    COALESCE(r.nombre, 'sin_rol') AS rol,
                    COALESCE(ec.nombre, 'sin_estado') AS estado,

                    pv.id_preferencia,
                    COALESCE(t.nombre, 'light') AS tema_visual,
                    COALESCE(pv.tamano_fuente, 'normal') AS tamano_fuente,
                    COALESCE(pv.modo_visualizacion, 'estandar') AS modo_visualizacion,
                    COALESCE(pv.idioma, 'es') AS idioma
                FROM usuario u
                LEFT JOIN rol r
                    ON u.id_rol = r.id_rol
                LEFT JOIN estado_cuenta ec
                    ON u.id_estado = ec.id_estado
                LEFT JOIN preferencia_visual pv
                    ON u.id_preferencia = pv.id_preferencia
                LEFT JOIN tema t
                    ON pv.id_tema = t.id_tema
                ORDER BY u.id_usuario DESC;
            """)

            return cursor.fetchall()

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def get_common_users_for_specialist(id_especialista):
        """
        Consulta solo usuarios comunes para SpecialistView.

        El especialista ve usuarios con rol 'usuario'.
        También muestra cuántas acciones ha registrado ese especialista sobre cada usuario.
        Los datos de bienestar se consultan en MongoDB por id_usuario.
        """

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    u.id_usuario,
                    u.nombre,
                    u.correo,
                    u.correo AS usuario,
                    u.fecha_registro,

                    COALESCE(r.nombre, 'sin_rol') AS rol,
                    COALESCE(ec.nombre, 'sin_estado') AS estado,

                    pv.id_preferencia,
                    COALESCE(t.nombre, 'light') AS tema_visual,
                    COALESCE(pv.tamano_fuente, 'normal') AS tamano_fuente,
                    COALESCE(pv.modo_visualizacion, 'estandar') AS modo_visualizacion,
                    COALESCE(pv.idioma, 'es') AS idioma,

                    COUNT(b.id_bitacora) AS acciones_especialista,

                    MAX(
                        CASE
                            WHEN b.accion = 'asignar_recomendacion'
                            THEN b.fecha_evento
                            ELSE NULL
                        END
                    ) AS ultima_recomendacion
                FROM usuario u
                LEFT JOIN rol r
                    ON u.id_rol = r.id_rol
                LEFT JOIN estado_cuenta ec
                    ON u.id_estado = ec.id_estado
                LEFT JOIN preferencia_visual pv
                    ON u.id_preferencia = pv.id_preferencia
                LEFT JOIN tema t
                    ON pv.id_tema = t.id_tema
                LEFT JOIN bitacora_cuenta b
                    ON b.id_usuario = u.id_usuario
                    AND b.id_admin = %s
                    AND b.accion IN ('asignar_recomendacion', 'cargar_recurso')
                WHERE r.nombre = 'usuario'
                GROUP BY
                    u.id_usuario,
                    u.nombre,
                    u.correo,
                    u.fecha_registro,
                    r.nombre,
                    ec.nombre,
                    pv.id_preferencia,
                    t.nombre,
                    pv.tamano_fuente,
                    pv.modo_visualizacion,
                    pv.idioma
                ORDER BY u.id_usuario DESC;
            """, (id_especialista,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def get_user_detail(id_usuario):
        """
        Obtiene un usuario por ID usando el modelo relacional corregido.
        Los datos de bienestar se consultan en MongoDB por id_usuario.
        """

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    u.id_usuario,
                    u.nombre,
                    u.correo,
                    u.correo AS usuario,
                    u.fecha_registro,

                    COALESCE(r.nombre, 'sin_rol') AS rol,
                    COALESCE(ec.nombre, 'sin_estado') AS estado,

                    pv.id_preferencia,
                    COALESCE(t.nombre, 'light') AS tema_visual,
                    COALESCE(pv.tamano_fuente, 'normal') AS tamano_fuente,
                    COALESCE(pv.modo_visualizacion, 'estandar') AS modo_visualizacion,
                    COALESCE(pv.idioma, 'es') AS idioma
                FROM usuario u
                LEFT JOIN rol r
                    ON u.id_rol = r.id_rol
                LEFT JOIN estado_cuenta ec
                    ON u.id_estado = ec.id_estado
                LEFT JOIN preferencia_visual pv
                    ON u.id_preferencia = pv.id_preferencia
                LEFT JOIN tema t
                    ON pv.id_tema = t.id_tema
                WHERE u.id_usuario = %s
                LIMIT 1;
            """, (id_usuario,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def get_history_for_specialist(id_usuario, id_especialista):
        """
        Trayectoria del usuario relacionada con el especialista actual.

        Solo muestra acciones hechas por ese especialista:
        - asignar_recomendacion
        - cargar_recurso
        """

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    b.id_bitacora,
                    b.accion,
                    b.descripcion,
                    b.fecha_evento,
                    actor.nombre AS actor_nombre,
                    actor.correo AS actor_correo
                FROM bitacora_cuenta b
                LEFT JOIN usuario actor
                    ON b.id_admin = actor.id_usuario
                WHERE b.id_usuario = %s
                  AND b.id_admin = %s
                  AND b.accion IN ('asignar_recomendacion', 'cargar_recurso')
                ORDER BY b.fecha_evento DESC
                LIMIT 50;
            """, (
                id_usuario,
                id_especialista
            ))

            return cursor.fetchall()

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def get_latest_recommendation_for_user(id_usuario):
        """
        Última recomendación asignada a un usuario.
        Se usa en HomeView del usuario normal.
        """

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    b.id_bitacora,
                    b.descripcion,
                    b.fecha_evento,
                    especialista.nombre AS especialista_nombre,
                    especialista.correo AS especialista_correo
                FROM bitacora_cuenta b
                LEFT JOIN usuario especialista
                    ON b.id_admin = especialista.id_usuario
                WHERE b.id_usuario = %s
                  AND b.accion = 'asignar_recomendacion'
                ORDER BY b.fecha_evento DESC
                LIMIT 1;
            """, (id_usuario,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def get_resources_for_user(id_usuario):
        """
        Recursos de apoyo asignados a un usuario por el especialista
        (accion 'cargar_recurso'). Se usa en HomeView del usuario normal.
        """

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    b.id_bitacora,
                    b.descripcion,
                    b.fecha_evento,
                    especialista.nombre AS especialista_nombre
                FROM bitacora_cuenta b
                LEFT JOIN usuario especialista
                    ON b.id_admin = especialista.id_usuario
                WHERE b.id_usuario = %s
                  AND b.accion = 'cargar_recurso'
                ORDER BY b.fecha_evento DESC
                LIMIT 6;
            """, (id_usuario,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def get_users():
        return UserModel.get_all_users()

    @staticmethod
    def table_has_column(table_name, column_name):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = %s
                  AND column_name = %s;
            """, (table_name, column_name))

            row = cursor.fetchone()
            return row["total"] > 0

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def get_account_settings(user_or_id):
        id_usuario = UserModel.normalize_user_id(user_or_id)

        username_supported = UserModel.table_has_column("usuario", "usuario")

        if username_supported:
            username_select = "u.usuario AS nombre_usuario"
        else:
            username_select = "SUBSTRING_INDEX(u.correo, '@', 1) AS nombre_usuario"

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(f"""
                SELECT
                    u.id_usuario,
                    u.nombre,
                    {username_select},
                    u.correo,
                    u.fecha_registro,
                    r.nombre AS rol,
                    ec.nombre AS estado,
                    t.nombre AS tema_visual,
                    pv.tamano_fuente,
                    pv.modo_visualizacion,
                    COALESCE(pv.idioma, 'es') AS idioma
                FROM usuario u
                LEFT JOIN rol r
                    ON u.id_rol = r.id_rol
                LEFT JOIN estado_cuenta ec
                    ON u.id_estado = ec.id_estado
                LEFT JOIN preferencia_visual pv
                    ON u.id_preferencia = pv.id_preferencia
                LEFT JOIN tema t
                    ON pv.id_tema = t.id_tema
                WHERE u.id_usuario = %s
                LIMIT 1;
            """, (id_usuario,))

            user = cursor.fetchone()

            if not user:
                return {
                    "success": False,
                    "message": "Usuario no encontrado.",
                    "user": None,
                    "username_supported": username_supported
                }

            user["username_supported"] = username_supported

            return {
                "success": True,
                "message": "Datos cargados correctamente.",
                "user": user,
                "username_supported": username_supported
            }

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def update_account_settings(user_or_id, nombre, nombre_usuario, correo):
        """
        Actualiza datos básicos de cuenta.
        Usa solamente UPDATE.
        No crea tablas.
        No modifica estructura SQL.

        Si existe columna usuario.usuario, también actualiza nombre_usuario.
        Si no existe, ignora nombre_usuario para respetar el MR actual.
        """

        id_usuario = UserModel.normalize_user_id(user_or_id)

        nombre = str(nombre).strip()
        nombre_usuario = str(nombre_usuario).strip()
        correo = str(correo).strip().lower()

        if not nombre:
            return {
                "success": False,
                "message": "El nombre no puede estar vacío."
            }

        if len(nombre) < 3:
            return {
                "success": False,
                "message": "El nombre debe tener al menos 3 caracteres."
            }

        if not correo or "@" not in correo or "." not in correo:
            return {
                "success": False,
                "message": "Ingresa un correo válido."
            }

        username_supported = UserModel.table_has_column("usuario", "usuario")

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT id_usuario
                FROM usuario
                WHERE LOWER(correo) = %s
                  AND id_usuario <> %s
                LIMIT 1;
            """, (correo, id_usuario))

            if cursor.fetchone():
                return {
                    "success": False,
                    "message": "Ese correo ya está registrado por otra cuenta."
                }

            if username_supported:
                if not nombre_usuario:
                    return {
                        "success": False,
                        "message": "El nombre de usuario no puede estar vacío."
                    }

                if len(nombre_usuario) < 3:
                    return {
                        "success": False,
                        "message": "El nombre de usuario debe tener al menos 3 caracteres."
                    }

                cursor.execute("""
                    SELECT id_usuario
                    FROM usuario
                    WHERE LOWER(usuario) = %s
                      AND id_usuario <> %s
                    LIMIT 1;
                """, (nombre_usuario.lower(), id_usuario))

                if cursor.fetchone():
                    return {
                        "success": False,
                        "message": "Ese nombre de usuario ya está registrado."
                    }

                cursor.execute("""
                    UPDATE usuario
                    SET
                        nombre = %s,
                        usuario = %s,
                        correo = %s
                    WHERE id_usuario = %s;
                """, (
                    nombre,
                    nombre_usuario,
                    correo,
                    id_usuario
                ))

            else:
                cursor.execute("""
                    UPDATE usuario
                    SET
                        nombre = %s,
                        correo = %s
                    WHERE id_usuario = %s;
                """, (
                    nombre,
                    correo,
                    id_usuario
                ))

            conexion.commit()

            user_result = UserModel.get_account_settings(id_usuario)

            return {
                "success": True,
                "message": "Datos de cuenta actualizados correctamente.",
                "user": user_result.get("user")
            }

        except Exception as error:
            conexion.rollback()

            return {
                "success": False,
                "message": f"No se pudieron actualizar los datos: {error}"
            }

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def update_password(user_or_id, current_password, new_password, confirm_password):
        id_usuario = UserModel.normalize_user_id(user_or_id)

        current_password = str(current_password).strip()
        new_password = str(new_password).strip()
        confirm_password = str(confirm_password).strip()

        if not current_password or not new_password or not confirm_password:
            return {
                "success": False,
                "message": "Completa todos los campos de contraseña."
            }

        if len(new_password) < 4:
            return {
                "success": False,
                "message": "La nueva contraseña debe tener al menos 4 caracteres."
            }

        if new_password != confirm_password:
            return {
                "success": False,
                "message": "Las nuevas contraseñas no coinciden."
            }

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT contrasena
                FROM usuario
                WHERE id_usuario = %s
                LIMIT 1;
            """, (id_usuario,))

            user = cursor.fetchone()

            if not user:
                return {
                    "success": False,
                    "message": "Usuario no encontrado."
                }

            stored_hash = user.get("contrasena")

            if not UserModel.verify_password(current_password, stored_hash):
                return {
                    "success": False,
                    "message": "La contraseña actual es incorrecta."
                }

            new_hash = UserModel.make_password_hash(new_password)

            cursor.execute("""
                UPDATE usuario
                SET contrasena = %s
                WHERE id_usuario = %s;
            """, (
                new_hash,
                id_usuario
            ))

            conexion.commit()

            return {
                "success": True,
                "message": "Contraseña actualizada correctamente."
            }

        except Exception as error:
            conexion.rollback()

            return {
                "success": False,
                "message": f"No se pudo actualizar la contraseña: {error}"
            }

        finally:
            cursor.close()
            conexion.close()

    # =====================================================
    # EXISTS
    # =====================================================

    @staticmethod
    def username_exists(usuario):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT id_usuario
                FROM usuario
                WHERE correo = %s
                LIMIT 1;
            """, (usuario,))

            return cursor.fetchone() is not None

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def email_exists(correo):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT id_usuario
                FROM usuario
                WHERE correo = %s
                LIMIT 1;
            """, (correo,))

            return cursor.fetchone() is not None

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def user_exists(usuario, correo):
        """
        Método usado por AuthController.register().
        """

        return UserModel.username_exists(usuario) or UserModel.email_exists(correo)

    # =====================================================
    # UPDATE
    # =====================================================

    @staticmethod
    def update_status(id_usuario, estado):
        id_usuario = UserModel.normalize_user_id(id_usuario)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                UPDATE usuario
                SET id_estado = (
                    SELECT id_estado
                    FROM estado_cuenta
                    WHERE nombre = %s
                    LIMIT 1
                )
                WHERE id_usuario = %s;
            """, (estado, id_usuario))

            connection.commit()

            return {
                "success": True,
                "message": "Estado actualizado correctamente."
            }

        except Exception as error:
            connection.rollback()

            return {
                "success": False,
                "message": f"No se pudo actualizar el estado: {error}"
            }

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def restrict_user(id_usuario):
        return UserModel.update_status(id_usuario, "restringida")

    @staticmethod
    def activate_user(id_usuario):
        return UserModel.update_status(id_usuario, "activa")

    @staticmethod
    def restrict_account(id_usuario):
        return UserModel.restrict_user(id_usuario)

    @staticmethod
    def activate_account(id_usuario):
        return UserModel.activate_user(id_usuario)

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def delete_user(id_usuario):
        id_usuario = UserModel.normalize_user_id(id_usuario)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT id_preferencia
                FROM usuario
                WHERE id_usuario = %s
                LIMIT 1;
            """, (id_usuario,))

            usuario_row = cursor.fetchone()

            cursor.execute("""
                DELETE FROM usuario
                WHERE id_usuario = %s;
            """, (id_usuario,))

            if usuario_row and usuario_row.get("id_preferencia"):
                cursor.execute("""
                    DELETE FROM preferencia_visual
                    WHERE id_preferencia = %s;
                """, (usuario_row["id_preferencia"],))

            connection.commit()

            return {
                "success": True,
                "message": "Usuario eliminado correctamente."
            }

        except Exception as error:
            connection.rollback()

            return {
                "success": False,
                "message": f"No se pudo eliminar el usuario: {error}"
            }

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def delete_account(id_usuario):
        return UserModel.delete_user(id_usuario)

    @staticmethod
    def delete_own_account(id_usuario):
        return UserModel.delete_user(id_usuario)