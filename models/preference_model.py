from database.connection import get_connection
from utils.constants import TEMAS_VALIDOS


class PreferenceModel:
    """
    Modelo de preferencias visuales (MySQL): tema y configuraciones
    de visualización del usuario.
    """

    @staticmethod
    def update_theme(user_or_id, tema_visual):
        id_usuario = PreferenceModel.normalize_user_id(user_or_id)

        if tema_visual not in TEMAS_VALIDOS:
            return {
                "success": False,
                "message": "Tema visual no válido."
            }

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT id_tema
                FROM tema
                WHERE nombre = %s
                LIMIT 1;
            """, (tema_visual,))

            tema = cursor.fetchone()

            if not tema:
                return {
                    "success": False,
                    "message": "El tema seleccionado no existe en la base de datos."
                }

            cursor.execute("""
                UPDATE preferencia_visual pv
                INNER JOIN usuario u
                    ON pv.id_preferencia = u.id_preferencia
                SET pv.id_tema = %s
                WHERE u.id_usuario = %s;
            """, (
                tema["id_tema"],
                id_usuario
            ))

            conexion.commit()

            return {
                "success": True,
                "message": "Tema actualizado correctamente."
            }

        except Exception as error:
            conexion.rollback()

            return {
                "success": False,
                "message": f"No se pudo actualizar el tema: {error}"
            }

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def normalize_user_id(user_or_id):
        if isinstance(user_or_id, dict):
            return user_or_id.get("id_usuario") or user_or_id.get("id")

        return user_or_id
