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
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    u.id_usuario,
                    u.nombre,
                    u.usuario,
                    u.correo,
                    u.password_hash,
                    u.fecha_registro,
                    u.rol,
                    u.estado,
                    p.tema_visual,
                    p.sonido_default,
                    p.volumen,
                    p.animaciones
                FROM usuarios u
                LEFT JOIN preferencias p
                    ON u.id_usuario = p.id_usuario
                WHERE u.usuario = %s OR u.correo = %s
                LIMIT 1;
            """, (identifier, identifier))

            return cursor.fetchone()

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
                    u.usuario,
                    u.correo,
                    u.fecha_registro,
                    u.rol,
                    u.estado,
                    p.tema_visual,
                    p.sonido_default,
                    p.volumen,
                    p.animaciones
                FROM usuarios u
                LEFT JOIN preferencias p
                    ON u.id_usuario = p.id_usuario
                WHERE u.id_usuario = %s
                LIMIT 1;
            """, (id_usuario,))

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_all_users():
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    u.id_usuario,
                    u.nombre,
                    u.usuario,
                    u.correo,
                    u.fecha_registro,
                    u.rol,
                    u.estado,
                    p.tema_visual
                FROM usuarios u
                LEFT JOIN preferencias p
                    ON u.id_usuario = p.id_usuario
                ORDER BY u.id_usuario DESC;
            """)

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_users():
        return UserModel.get_all_users()

    @staticmethod
    def get_preferences(id_usuario):
        id_usuario = UserModel.normalize_user_id(id_usuario)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    id_preferencia,
                    id_usuario,
                    tema_visual,
                    sonido_default,
                    volumen,
                    animaciones
                FROM preferencias
                WHERE id_usuario = %s
                LIMIT 1;
            """, (id_usuario,))

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

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
                FROM usuarios
                WHERE usuario = %s
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
                FROM usuarios
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
    def update_theme(id_usuario, tema_visual):
        id_usuario = UserModel.normalize_user_id(id_usuario)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                UPDATE preferencias
                SET tema_visual = %s
                WHERE id_usuario = %s;
            """, (tema_visual, id_usuario))

            connection.commit()

            return {
                "success": True,
                "message": "Tema actualizado correctamente."
            }

        except Exception as error:
            connection.rollback()

            return {
                "success": False,
                "message": f"No se pudo actualizar el tema: {error}"
            }

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def update_status(id_usuario, estado):
        id_usuario = UserModel.normalize_user_id(id_usuario)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                UPDATE usuarios
                SET estado = %s
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
                DELETE FROM usuarios
                WHERE id_usuario = %s;
            """, (id_usuario,))

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