from models.wellbeing_model import WellbeingModel


class WellbeingController:

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

        return WellbeingModel.save_checkin(
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

        checkins = WellbeingModel.get_user_checkins(id_usuario)
        summary = WellbeingModel.get_user_wellbeing_summary(id_usuario)
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
        return WellbeingModel.get_latest_checkin(id_usuario)

    @staticmethod
    def get_specialist_user_history(current_user, id_usuario):
        if not current_user:
            return {"success": False, "message": "No hay sesión activa."}
        rol = current_user.get("rol", "")
        if rol not in ("especialista", "superuser"):
            return {"success": False, "message": "No tienes permisos para consultar este historial."}

        data = WellbeingModel.get_specialist_user_history(id_usuario)
        return {
            "success": True,
            "resumen": data["resumen"],
            "checkins": data["checkins"]
        }

    @staticmethod
    def update_music_setting(current_user, setting_name, track_id):
        if not current_user:
            return {"success": False, "message": "No hay sesión activa."}
        id_usuario = current_user.get("id_usuario")
        if not id_usuario:
            return {"success": False, "message": "Usuario no identificado."}

        if setting_name not in ("background_track", "calm_mode_track"):
            return {"success": False, "message": "Nombre de ajuste inválido."}

        return WellbeingModel.update_music_settings(
            id_usuario=id_usuario,
            **{setting_name: track_id}
        )

    @staticmethod
    def toggle_favorite_music(current_user, track_id):
        if not current_user:
            return {"success": False, "message": "No hay sesión activa."}
        id_usuario = current_user.get("id_usuario")
        if not id_usuario:
            return {"success": False, "message": "Usuario no identificado."}

        return WellbeingModel.toggle_favorite_music(id_usuario, track_id)
