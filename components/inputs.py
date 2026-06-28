import customtkinter as ctk
from utils.theme_manager import ThemeManager


class SoftEntry(ctk.CTkEntry):
    """
    Entrada de texto estándar.
    Uso: usuario, correo, nombres, formularios generales.
    """

    def __init__(self, master, placeholder="", width=330, height=45, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=kwargs.pop("corner_radius", 14),
            placeholder_text=placeholder,
            fg_color=kwargs.pop("fg_color", colors.get("input_bg", "#F8FAFC")),
            border_color=kwargs.pop("border_color", colors.get("border", "#CBD5E1")),
            text_color=kwargs.pop("text_color", colors.get("text", "#1E1B4B")),
            placeholder_text_color=kwargs.pop("placeholder_text_color", colors.get("muted_text", "#64748B")),
            **kwargs
        )


class PasswordEntry(SoftEntry):
    """
    Entrada de contraseña.
    Uso: login, registro, cambio de contraseña.
    """

    def __init__(self, master, placeholder="Contraseña", width=330, height=45, **kwargs):
        super().__init__(
            master,
            placeholder=placeholder,
            width=width,
            height=height,
            show="*",
            **kwargs
        )


class SoftTextbox(ctk.CTkTextbox):
    """
    Caja de texto larga.
    Uso: frase motivacional, descripción, recursos o notas del especialista.
    """

    def __init__(self, master, width=330, height=100, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=kwargs.pop("corner_radius", 14),
            fg_color=kwargs.pop("fg_color", colors.get("input_bg", "#F8FAFC")),
            border_color=kwargs.pop("border_color", colors.get("border", "#CBD5E1")),
            text_color=kwargs.pop("text_color", colors.get("text", "#1E1B4B")),
            **kwargs
        )
