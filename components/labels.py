import customtkinter as ctk
from utils.theme_manager import ThemeManager


class TitleLabel(ctk.CTkLabel):
    """
    Título principal de pantalla.
    """

    def __init__(self, master, text, size=30, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            text=text,
            font=kwargs.pop("font", ("Arial", size, "bold")),
            text_color=kwargs.pop("text_color", colors.get("text", "#1E1B4B")),
            **kwargs
        )


class SubtitleLabel(ctk.CTkLabel):
    """
    Subtítulo o descripción breve.
    """

    def __init__(self, master, text, size=15, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            text=text,
            font=kwargs.pop("font", ("Arial", size)),
            text_color=kwargs.pop("text_color", colors.get("muted_text", "#475569")),
            **kwargs
        )


class BodyLabel(ctk.CTkLabel):
    """
    Texto normal de contenido.
    """

    def __init__(self, master, text, size=14, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            text=text,
            font=kwargs.pop("font", ("Arial", size)),
            text_color=kwargs.pop("text_color", colors.get("text", "#1E1B4B")),
            wraplength=kwargs.pop("wraplength", 420),
            justify=kwargs.pop("justify", "left"),
            **kwargs
        )


class SmallLabel(ctk.CTkLabel):
    """
    Texto pequeño auxiliar.
    """

    def __init__(self, master, text, size=12, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            text=text,
            font=kwargs.pop("font", ("Arial", size)),
            text_color=kwargs.pop("text_color", colors.get("muted_text", "#64748B")),
            **kwargs
        )


class ErrorLabel(ctk.CTkLabel):
    """
    Label para errores o mensajes de validación.
    """

    def __init__(self, master, text="", size=13, **kwargs):
        super().__init__(
            master,
            text=text,
            font=kwargs.pop("font", ("Arial", size)),
            text_color=kwargs.pop("text_color", "#DC2626"),
            **kwargs
        )

    def show_error(self, text):
        self.configure(text=text, text_color="#DC2626")

    def show_success(self, text):
        self.configure(text=text, text_color="#16A34A")

    def clear(self):
        self.configure(text="")
