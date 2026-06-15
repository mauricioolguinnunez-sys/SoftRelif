import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE_DIR, "softrelief_state.json")


class AppState:

    @staticmethod
    def save_last_theme(theme):
        data = {
            "last_theme": theme
        }

        with open(STATE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def load_last_theme():
        if not os.path.exists(STATE_PATH):
            return "light"

        try:
            with open(STATE_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data.get("last_theme", "light")

        except Exception:
            return "light"