from models.user_model import UserModel


class AuthController:
    """
    Controlador de autenticación de SoftRelief.

    Responsabilidades:
    - Validar campos de login.
    - Validar campos de registro.
    - Delegar consultas y persistencia a UserModel.
    """

    @staticmethod
    def login(usuario, password):
        usuario = str(usuario).strip() if usuario else ""
        password = str(password).strip() if password else ""

        if not usuario or not password:
            return {
                "success": False,
                "message": "Ingresa usuario y contraseña."
            }

        return UserModel.login(usuario, password)

    @staticmethod
    def register(nombre, usuario, correo, password, confirm_password=None, rol="usuario"):
        """
        Registra usuarios normales por defecto.

        Compatible con llamadas de 4 argumentos:
        AuthController.register(nombre, usuario, correo, password)

        Y también con llamadas de 5 argumentos:
        AuthController.register(nombre, usuario, correo, password, confirm_password)
        """

        nombre = str(nombre).strip() if nombre else ""
        usuario = str(usuario).strip() if usuario else ""
        correo = str(correo).strip().lower() if correo else ""
        password = str(password).strip() if password else ""

        if confirm_password is not None:
            confirm_password = str(confirm_password).strip()

        if not nombre or not usuario or not correo or not password:
            return {
                "success": False,
                "message": "Completa todos los campos."
            }

        if len(nombre) < 3:
            return {
                "success": False,
                "message": "El nombre debe tener al menos 3 caracteres."
            }

        if len(usuario) < 3:
            return {
                "success": False,
                "message": "El usuario debe tener al menos 3 caracteres."
            }

        if "@" not in correo or "." not in correo:
            return {
                "success": False,
                "message": "Ingresa un correo válido."
            }

        if len(password) < 4:
            return {
                "success": False,
                "message": "La contraseña debe tener al menos 4 caracteres."
            }

        if confirm_password is not None and password != confirm_password:
            return {
                "success": False,
                "message": "Las contraseñas no coinciden."
            }

        if rol not in ["usuario", "especialista", "superuser"]:
            rol = "usuario"

        if UserModel.user_exists(usuario, correo):
            return {
                "success": False,
                "message": "El usuario o correo ya está registrado."
            }

        return UserModel.create_user(
            nombre=nombre,
            usuario=usuario,
            correo=correo,
            password=password,
            rol=rol
        )