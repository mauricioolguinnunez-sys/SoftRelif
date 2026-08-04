from models.checkin_model import CheckinModel


class CheckinController:

    @staticmethod
    def save_checkin(current_user, payload):
        if not current_user:
            return {"success": False, "message": "No hay sesión activa."}
        rol = current_user.get("rol", "")
        if rol != "usuario":
            return {"success": False, "message": "Solo usuarios pueden hacer check-in."}
        id_usuario = current_user.get("id_usuario")
        if not id_usuario:
            return {"success": False, "message": "Usuario no identificado."}

        return CheckinModel.save_checkin(
            id_usuario=id_usuario,
            tipo_checkin=payload.get("tipo_checkin"),
            titulo_checkin=payload.get("titulo_checkin"),
            estado_animo_general=payload.get("estado_animo_general"),
            respuestas=payload.get("respuestas", []),
            recomendacion_automatica=payload.get("recomendacion_automatica")
        )

    @staticmethod
    def get_history(current_user):
        if not current_user:
            return {"success": False, "message": "No hay sesión activa."}
        id_usuario = current_user.get("id_usuario")
        if not id_usuario:
            return {"success": False, "message": "Usuario no identificado."}

        checkins = CheckinModel.get_user_checkins(id_usuario)
        summary = CheckinModel.get_user_wellbeing_summary(id_usuario)
        return {
            "success": True,
            "checkins": checkins,
            "summary": summary
        }

    @staticmethod
    def get_latest_checkin(current_user):
        if not current_user:
            return None
        id_usuario = current_user.get("id_usuario")
        if not id_usuario:
            return None
        return CheckinModel.get_latest_checkin(id_usuario)

    @staticmethod
    def get_specialist_user_history(current_user, id_usuario):
        if not current_user:
            return {"success": False, "message": "No hay sesión activa."}
        rol = current_user.get("rol", "")
        if rol not in ("especialista", "superuser"):
            return {"success": False, "message": "No tienes permisos para consultar este historial."}

        data = CheckinModel.get_specialist_user_history(id_usuario)
        return {
            "success": True,
            "resumen": data["resumen"],
            "checkins": data["checkins"]
        }
