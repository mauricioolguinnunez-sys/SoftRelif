import json
import os

from utils.paths import app_base_dir


BASE_DIR = app_base_dir()
STATE_PATH = os.path.join(BASE_DIR, "softrelief_state.json")


class AppState:

    @staticmethod
    def save_state(key, value):
        data = {}

        if os.path.exists(STATE_PATH):
            try:
                with open(STATE_PATH, "r", encoding="utf-8") as file:
                    data = json.load(file)
            except Exception:
                data = {}

        data[key] = value

        with open(STATE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def load_state(key, default=None):
        if not os.path.exists(STATE_PATH):
            return default

        try:
            with open(STATE_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data.get(key, default)

        except Exception:
            return default

    @staticmethod
    def save_last_theme(theme):
        AppState.save_state("last_theme", theme)

    @staticmethod
    def load_last_theme():
        return AppState.load_state("last_theme", "light")

    @staticmethod
    def save_language(lang):
        AppState.save_state("language", lang)

    @staticmethod
    def load_language():
        return AppState.load_state("language", "es")