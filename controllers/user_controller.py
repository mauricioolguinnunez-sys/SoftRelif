from models.user_model import UserModel


class UserController:

    @staticmethod
    def get_all_users(current_user):
        if current_user["rol"] != "superuser":
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
        if current_user["rol"] != "superuser":
            return {
                "success": False,
                "message": "No tienes permisos para restringir usuarios."
            }

        return UserModel.restrict_user(id_usuario)

    @staticmethod
    def activate_user(current_user, id_usuario):
        if current_user["rol"] != "superuser":
            return {
                "success": False,
                "message": "No tienes permisos para activar usuarios."
            }

        return UserModel.activate_user(id_usuario)

    @staticmethod
    def delete_user(current_user, id_usuario):
        if current_user["rol"] != "superuser":
            return {
                "success": False,
                "message": "No tienes permisos para eliminar usuarios."
            }

        return UserModel.delete_user(id_usuario)

    @staticmethod
    def delete_own_account(current_user):
        if current_user["rol"] == "superuser":
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

        return UserModel.update_theme(current_user["id_usuario"], theme)