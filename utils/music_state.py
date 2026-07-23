import json
from pathlib import Path


STATE_PATH = Path(__file__).resolve().parent.parent / "softrelief_music_state.json"


def load_music_state():
    if not STATE_PATH.exists():
        return {}

    try:
        with open(STATE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_music_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4, ensure_ascii=False)


def get_user_music_settings(id_usuario):
    state = load_music_state()
    key = str(id_usuario)

    return state.get(key, {
        "calm_mode_track": None,
        "background_track": None,
        "favorites": []
    })


def update_user_music_setting(id_usuario, setting_name, track_id):
    state = load_music_state()
    key = str(id_usuario)

    if key not in state:
        state[key] = {
            "calm_mode_track": None,
            "background_track": None,
            "favorites": []
        }

    state[key][setting_name] = track_id
    save_music_state(state)

    return {
        "success": True,
        "message": "Selección musical actualizada correctamente."
    }


def toggle_favorite_track(id_usuario, track_id):
    state = load_music_state()
    key = str(id_usuario)

    if key not in state:
        state[key] = {
            "calm_mode_track": None,
            "background_track": None,
            "favorites": []
        }

    favorites = state[key].get("favorites", [])

    if track_id in favorites:
        favorites.remove(track_id)
        is_favorite = False
    else:
        favorites.append(track_id)
        is_favorite = True

    state[key]["favorites"] = favorites
    save_music_state(state)

    return {
        "success": True,
        "favorite": is_favorite,
        "message": "Favorito actualizado."
    }