from datetime import datetime
from database.connection import get_connection
from utils.password_utils import hash_password, verify_password


class UserModel:

    @staticmethod
    def create_user(nombre, usuario, correo, password):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            password_hash = hash_password(password)
            fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
                "usuario",
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
                "message": "Usuario creado correctamente.",
                "id_usuario": id_usuario
            }

        except Exception as error:
            connection.rollback()

            return {
                "success": False,
                "message": f"No se pudo crear el usuario: {error}"
            }

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def login(usuario, password):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM usuarios
            WHERE usuario = %s;
        """, (usuario,))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user is None:
            return {
                "success": False,
                "message": "El usuario no existe."
            }

        if user["estado"] == "restringida":
            return {
                "success": False,
                "message": "Esta cuenta está restringida."
            }

        if verify_password(password, user["password_hash"]):
            preferences = UserModel.get_preferences(user["id_usuario"])

            return {
                "success": True,
                "message": "Inicio de sesión correcto.",
                "user": {
                    "id_usuario": user["id_usuario"],
                    "nombre": user["nombre"],
                    "usuario": user["usuario"],
                    "correo": user["correo"],
                    "rol": user["rol"],
                    "estado": user["estado"],
                    "tema_visual": preferences.get("tema_visual", "light")
                }
            }

        return {
            "success": False,
            "message": "Contraseña incorrecta."
        }

    @staticmethod
    def user_exists(usuario, correo):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM usuarios
            WHERE usuario = %s OR correo = %s;
        """, (usuario, correo))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        return user is not None

    @staticmethod
    def get_preferences(id_usuario):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM preferencias
            WHERE id_usuario = %s;
        """, (id_usuario,))

        preferences = cursor.fetchone()

        cursor.close()
        connection.close()

        if preferences:
            return preferences

        return {
            "tema_visual": "light",
            "sonido_default": "lluvia",
            "volumen": 50,
            "animaciones": 1
        }

    @staticmethod
    def update_theme(id_usuario, theme):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                UPDATE preferencias
                SET tema_visual = %s
                WHERE id_usuario = %s;
            """, (theme, id_usuario))

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
    def get_all_users():
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT 
                id_usuario,
                nombre,
                usuario,
                correo,
                fecha_registro,
                rol,
                estado
            FROM usuarios
            ORDER BY id_usuario ASC;
        """)

        users = cursor.fetchall()

        cursor.close()
        connection.close()

        return users

    @staticmethod
    def restrict_user(id_usuario):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                UPDATE usuarios
                SET estado = 'restringida'
                WHERE id_usuario = %s AND rol != 'superuser';
            """, (id_usuario,))

            connection.commit()

            return {
                "success": True,
                "message": "Usuario restringido correctamente."
            }

        except Exception as error:
            connection.rollback()

            return {
                "success": False,
                "message": f"No se pudo restringir el usuario: {error}"
            }

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def activate_user(id_usuario):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                UPDATE usuarios
                SET estado = 'activa'
                WHERE id_usuario = %s AND rol != 'superuser';
            """, (id_usuario,))

            connection.commit()

            return {
                "success": True,
                "message": "Usuario activado correctamente."
            }

        except Exception as error:
            connection.rollback()

            return {
                "success": False,
                "message": f"No se pudo activar el usuario: {error}"
            }

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def delete_user(id_usuario):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                DELETE FROM usuarios
                WHERE id_usuario = %s AND rol != 'superuser';
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
    def delete_own_account(id_usuario):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                DELETE FROM usuarios
                WHERE id_usuario = %s AND rol != 'superuser';
            """, (id_usuario,))

            connection.commit()

            return {
                "success": True,
                "message": "Cuenta eliminada correctamente."
            }

        except Exception as error:
            connection.rollback()

            return {
                "success": False,
                "message": f"No se pudo eliminar la cuenta: {error}"
            }

        finally:
            cursor.close()
            connection.close()