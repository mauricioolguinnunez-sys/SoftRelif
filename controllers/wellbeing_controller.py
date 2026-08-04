from models.wellbeing_model import WellbeingModel


class WellbeingController:
    """
    Controlador de bienestar: configuraciones musicales del usuario.

    Los check-ins emocionales se gestionan en CheckinController.
    """

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
