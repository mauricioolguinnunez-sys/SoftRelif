from models.user_model import UserModel
from utils.validation_utils import (
    validar_confirmacion,
    validar_correo,
    validar_nombre,
    validar_password,
    validar_usuario,
)


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

        validaciones = [
            validar_nombre(nombre),
            validar_usuario(usuario),
            validar_correo(correo),
            validar_password(password),
            validar_confirmacion(password, confirm_password),
        ]

        for validacion in validaciones:
            if not validacion["success"]:
                return validacion

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