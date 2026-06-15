from models.user_model import UserModel


class AuthController:

    @staticmethod
    def login(usuario, password):
        """
        Controlador para iniciar sesión.
        """

        if not usuario or not password:
            return {
                "success": False,
                "message": "Ingresa usuario y contraseña."
            }

        return UserModel.login(usuario, password)

    @staticmethod
    def register(nombre, usuario, correo, password, confirm_password):
        """
        Controlador para crear cuenta.
        """

        if not nombre or not usuario or not correo or not password:
            return {
                "success": False,
                "message": "Todos los campos son obligatorios."
            }

        if len(password) < 6:
            return {
                "success": False,
                "message": "La contraseña debe tener mínimo 6 caracteres."
            }

        if password != confirm_password:
            return {
                "success": False,
                "message": "Las contraseñas no coinciden."
            }

        if UserModel.user_exists(usuario, correo):
            return {
                "success": False,
                "message": "El usuario o correo ya está registrado."
            }

        return UserModel.create_user(nombre, usuario, correo, password)