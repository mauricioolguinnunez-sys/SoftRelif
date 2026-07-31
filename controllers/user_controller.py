from models.user_model import UserModel


class UserController:

    @staticmethod
    def get_all_users(current_user):
        if str(current_user.get("rol", "")).lower() != "superuser":
            return {
                "success": False,
                "message": "No tienes permisos para ver usuarios.",
                "users": []
            }

        return {
            "success": True,
            "message": "Usuarios obtenidos correctamente.",
            "users": UserModel.get_all_users()
        }

    @staticmethod
    def restrict_user(current_user, id_usuario):
        if str(current_user.get("rol", "")).lower() != "superuser":
            return {
                "success": False,
                "message": "No tienes permisos para restringir usuarios."
            }

        return UserModel.restrict_user(id_usuario)

    @staticmethod
    def activate_user(current_user, id_usuario):
        if str(current_user.get("rol", "")).lower() != "superuser":
            return {
                "success": False,
                "message": "No tienes permisos para activar usuarios."
            }

        return UserModel.activate_user(id_usuario)

    @staticmethod
    def delete_user(current_user, id_usuario):
        if str(current_user.get("rol", "")).lower() != "superuser":
            return {
                "success": False,
                "message": "No tienes permisos para eliminar usuarios."
            }

        return UserModel.delete_user(id_usuario)

    @staticmethod
    def delete_own_account(current_user):
        if str(current_user.get("rol", "")).lower() == "superuser":
            return {
                "success": False,
                "message": "La cuenta superuser no se puede eliminar."
            }

        return UserModel.delete_own_account(current_user["id_usuario"])

    @staticmethod
    def update_theme(current_user, theme):
        if theme not in ["light", "dark"]:
            return {
                "success": False,
                "message": "Tema no válido."
            }

        return UserModel.update_theme(current_user.get("id_usuario"), theme)

    @staticmethod
    def get_account_settings(current_user):
        if not current_user:
            return {
                "success": False,
                "message": "No hay usuario activo.",
                "user": None
            }

        return UserModel.get_account_settings(current_user.get("id_usuario"))

    @staticmethod
    def update_account_settings(current_user, nombre, nombre_usuario, correo):
        if not current_user:
            return {
                "success": False,
                "message": "No hay usuario activo."
            }

        return UserModel.update_account_settings(
            current_user.get("id_usuario"),
            nombre,
            nombre_usuario,
            correo
        )

    @staticmethod
    def update_password(current_user, current_password, new_password, confirm_password):
        if not current_user:
            return {
                "success": False,
                "message": "No hay usuario activo."
            }

        return UserModel.update_password(
            current_user.get("id_usuario"),
            current_password,
            new_password,
            confirm_password
        )

    @staticmethod
    def update_language(current_user, idioma):
        if not current_user:
            return {
                "success": False,
                "message": "No hay usuario activo."
            }

        if idioma not in ["es", "en"]:
            return {
                "success": False,
                "message": "Idioma no válido."
            }

        return UserModel.update_language(current_user.get("id_usuario"), idioma)