from models.wellbeing_model import WellbeingModel


def get_user_music_settings(id_usuario):
    if not id_usuario:
        return {
            "calm_mode_track": None,
            "background_track": None,
            "favorites": []
        }

    try:
        return WellbeingModel.get_music_settings(int(id_usuario))
    except Exception:
        return {
            "calm_mode_track": None,
            "background_track": None,
            "favorites": []
        }


def update_user_music_setting(id_usuario, setting_name, track_id):
    if not id_usuario:
        return {"success": False, "message": "Usuario no identificado."}

    if setting_name not in ("background_track", "calm_mode_track"):
        return {"success": False, "message": "Nombre de ajuste inválido."}

    try:
        return WellbeingModel.update_music_settings(
            id_usuario=int(id_usuario),
            **{setting_name: track_id}
        )
    except Exception as error:
        return {"success": False, "message": str(error)}


def toggle_favorite_track(id_usuario, track_id):
    if not id_usuario:
        return {"success": False, "favorite": False, "message": "Usuario no identificado."}

    try:
        return WellbeingModel.toggle_favorite_music(int(id_usuario), track_id)
    except Exception as error:
        return {"success": False, "favorite": False, "message": str(error)}
