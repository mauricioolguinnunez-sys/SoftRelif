import customtkinter as ctk
from utils.theme_manager import ThemeManager


class PrimaryButton(ctk.CTkButton):
    """
    Botón principal de SoftRelief.
    Uso: acciones principales como iniciar sesión, guardar, continuar.
    """

    def __init__(self, master, text, command=None, width=220, height=42, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=kwargs.pop("corner_radius", 14),
            fg_color=kwargs.pop("fg_color", colors.get("button", "#7C3AED")),
            hover_color=kwargs.pop("hover_color", colors.get("button_hover", "#6D28D9")),
            text_color=kwargs.pop("text_color", "#FFFFFF"),
            font=kwargs.pop("font", ("Arial", 14, "bold")),
            **kwargs
        )


class SecondaryButton(ctk.CTkButton):
    """
    Botón secundario.
    Uso: crear cuenta, volver, cancelar, acciones menos importantes.
    """

    def __init__(self, master, text, command=None, width=160, height=36, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=kwargs.pop("corner_radius", 12),
            fg_color=kwargs.pop("fg_color", "transparent"),
            hover_color=kwargs.pop("hover_color", colors.get("hover", "#EDE9FE")),
            text_color=kwargs.pop("text_color", colors.get("accent", "#7C3AED")),
            font=kwargs.pop("font", ("Arial", 13, "bold")),
            **kwargs
        )


class DangerButton(ctk.CTkButton):
    """
    Botón de acciones peligrosas.
    Uso: eliminar cuenta, restringir usuario, borrar datos.
    """

    def __init__(self, master, text, command=None, width=180, height=40, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=kwargs.pop("corner_radius", 12),
            fg_color=kwargs.pop("fg_color", colors.get("danger", "#DC2626")),
            hover_color=kwargs.pop("hover_color", "#B91C1C"),
            text_color=kwargs.pop("text_color", "#FFFFFF"),
            font=kwargs.pop("font", ("Arial", 13, "bold")),
            **kwargs
        )


class SidebarButton(ctk.CTkButton):
    """
    Botón para menú lateral.
    Uso: Home, Check-in, Modo Calma, Sonidos, Microdescansos, Historial, Configuración.
    """

    def __init__(self, master, text, command=None, active=False, width=190, height=38, **kwargs):
        colors = ThemeManager.get_colors()

        fg = colors.get("accent", "#7C3AED") if active else "transparent"
        hover = colors.get("button_hover", "#6D28D9") if active else colors.get("hover", "#EDE9FE")
        txt = "#FFFFFF" if active else colors.get("text", "#1E1B4B")

        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            anchor="w",
            corner_radius=12,
            fg_color=kwargs.pop("fg_color", fg),
            hover_color=kwargs.pop("hover_color", hover),
            text_color=kwargs.pop("text_color", txt),
            font=kwargs.pop("font", ("Arial", 13, "bold")),
            **kwargs
        )
