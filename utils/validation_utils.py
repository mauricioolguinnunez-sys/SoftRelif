def validar_requerido(valor, mensaje):
    """Valida que un campo no esté vacío."""
    if not valor:
        return {"success": False, "message": mensaje}
    return {"success": True}


def validar_nombre(nombre):
    if not nombre:
        return {"success": False, "message": "Completa todos los campos."}

    if len(nombre) < 3:
        return {
            "success": False,
            "message": "El nombre debe tener al menos 3 caracteres."
        }

    return {"success": True}


def validar_usuario(usuario):
    if not usuario:
        return {"success": False, "message": "Completa todos los campos."}

    if len(usuario) < 3:
        return {
            "success": False,
            "message": "El usuario debe tener al menos 3 caracteres."
        }

    return {"success": True}


def validar_correo(correo):
    if not correo:
        return {"success": False, "message": "Completa todos los campos."}

    if "@" not in correo or "." not in correo:
        return {
            "success": False,
            "message": "Ingresa un correo válido."
        }

    return {"success": True}


def validar_password(password):
    if not password:
        return {"success": False, "message": "Completa todos los campos."}

    if len(password) < 4:
        return {
            "success": False,
            "message": "La contraseña debe tener al menos 4 caracteres."
        }

    return {"success": True}


def validar_confirmacion(password, confirm_password):
    if confirm_password is not None and password != confirm_password:
        return {
            "success": False,
            "message": "Las contraseñas no coinciden."
        }

    return {"success": True}
