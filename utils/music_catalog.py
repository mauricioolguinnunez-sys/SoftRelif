from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_PATH = PROJECT_ROOT / "assets"

SUPPORTED_AUDIO = [
    ".mp3",
    ".wav",
    ".ogg",
    ".m4a",
    ".flac",
]


def normalize_id(text):
    text = str(text).lower().strip()

    replacements = {
        " ": "_",
        "-": "_",
        ".": "_",
        "(": "",
        ")": "",
        "[": "",
        "]": "",
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    while "__" in text:
        text = text.replace("__", "_")

    return text.strip("_")


def audio_files():
    if not ASSETS_PATH.exists():
        return []

    files = []

    for file_path in ASSETS_PATH.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_AUDIO:
            continue

        files.append(file_path)

    return sorted(files)


def infer_category(file_path):
    name = f"{file_path.stem} {file_path.parent.name}".lower()

    if any(word in name for word in [
        "focus",
        "concentracion",
        "concentración",
        "cafe",
        "cafeteria",
        "coffee",
        "ruido",
        "white",
        "study",
        "work"
    ]):
        return "concentracion"

    if any(word in name for word in [
        "sleep",
        "sueno",
        "sueño",
        "night",
        "noche",
        "viento",
        "wind",
        "dream"
    ]):
        return "sueno"

    if any(word in name for word in [
        "lluvia",
        "rain",
        "bosque",
        "forest",
        "mar",
        "olas",
        "ocean",
        "sea",
        "piano",
        "calm",
        "relax",
        "relajacion",
        "relajación"
    ]):
        return "relajacion"

    return "relajacion"


def infer_icon(file_path):
    name = f"{file_path.stem} {file_path.parent.name}".lower()

    if any(word in name for word in ["lluvia", "rain"]):
        return "🌧"

    if any(word in name for word in ["bosque", "forest"]):
        return "🌲"

    if any(word in name for word in ["olas", "mar", "ocean", "sea"]):
        return "🌊"

    if any(word in name for word in ["cafe", "cafeteria", "coffee"]):
        return "☕"

    if any(word in name for word in ["viento", "wind", "night", "noche"]):
        return "🌙"

    if any(word in name for word in ["piano"]):
        return "🎹"

    if any(word in name for word in ["white", "ruido"]):
        return "◌"

    return "♪"


def infer_title(file_path):
    name = file_path.stem.replace("_", " ").replace("-", " ").strip()
    lower = name.lower()

    if "lluvia" in lower or "rain" in lower:
        return "Lluvia suave"

    if "bosque" in lower or "forest" in lower:
        return "Bosque"

    if "olas" in lower or "mar" in lower or "ocean" in lower or "sea" in lower:
        return "Olas del mar"

    if "cafe" in lower or "cafeteria" in lower or "coffee" in lower:
        return "Cafetería"

    if "viento" in lower or "wind" in lower or "night" in lower or "noche" in lower:
        return "Viento nocturno"

    if "piano" in lower:
        return "Piano calmado"

    if "white" in lower or "ruido" in lower:
        return "Ruido blanco"

    return name.title()


def infer_description(file_path):
    title = infer_title(file_path)

    descriptions = {
        "Lluvia suave": "La lluvia suave ayuda a reducir el estrés y mejorar la concentración.",
        "Bosque": "Sonidos del bosque para conectar con la calma natural.",
        "Olas del mar": "El sonido del mar favorece la relajación profunda y el descanso mental.",
        "Cafetería": "Ambiente de cafetería para mantenerte enfocado y productivo.",
        "Viento nocturno": "El viento suave de la noche acompaña tu mente hacia la tranquilidad.",
        "Piano calmado": "Música suave para acompañar ejercicios de calma.",
        "Ruido blanco": "Sonido constante para bloquear distracciones externas.",
    }

    return descriptions.get(
        title,
        "Sonido ambiental disponible en la biblioteca local de SoftRelief."
    )


def get_all_music():
    tracks = []

    for file_path in audio_files():
        category = infer_category(file_path)

        track = {
            "id": normalize_id(file_path.stem),
            "title": infer_title(file_path),
            "category": category,
            "description": infer_description(file_path),
            "duration": "30 min",
            "icon": infer_icon(file_path),
            "file": file_path,
            "relative_path": str(file_path.relative_to(PROJECT_ROOT)),
            "calm_mode": category in ["relajacion", "sueno"],
            "background_sound": category in ["relajacion", "concentracion", "sueno"],
        }

        tracks.append(track)

    return tracks


def get_music_by_id(track_id):
    track_id = str(track_id).strip()

    for track in get_all_music():
        if track["id"] == track_id:
            return track

    return None


def get_calm_mode_music():
    return [
        track for track in get_all_music()
        if track.get("calm_mode")
    ]


def get_background_music():
    return [
        track for track in get_all_music()
        if track.get("background_sound")
    ]