import customtkinter as ctk


class ThemeManager:
    LIGHT = {
        "mode": "light",
        "app_bg": "#F5F5F5",
        "sidebar_bg": "#FFFFFF",
        "card_bg": "#FFFFFF",
        "card_border": "#E8ECF5",
        "text": "#30384F",
        "text_soft": "#7E86A3",
        "button": "#7BAFD4",
        "button_hover": "#6A9FC5",
        "accent": "#7462D4",
        "accent_soft": "#F4F1FF",
        "danger": "#D9534F",
        "danger_hover": "#C9433F",
        "user_card": "#F7F7F7",
        "input_bg": "#FFFFFF",
        "menu_hover": "#F0F0F0",
        "avatar_bg": "#E8E2FF",
        "avatar_text": "#7462D4"
    }

    DARK = {
        "mode": "dark",
        "app_bg": "#07101F",
        "sidebar_bg": "#0B1324",
        "card_bg": "#0F1A2E",
        "card_border": "#253653",
        "text": "#F4F7FB",
        "text_soft": "#A7B3C8",
        "button": "#3A5FBC",
        "button_hover": "#4C6FD1",
        "accent": "#7C64B8",
        "accent_soft": "#18233A",
        "danger": "#D9534F",
        "danger_hover": "#C9433F",
        "user_card": "#101C31",
        "input_bg": "#111D32",
        "menu_hover": "#17243A",
        "avatar_bg": "#17243A",
        "avatar_text": "#A8D5BA"
    }

    @staticmethod
    def get_theme(theme_name):
        if theme_name == "dark":
            return ThemeManager.DARK
        return ThemeManager.LIGHT

    @staticmethod
    def apply_mode(theme_name):
        if theme_name == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")