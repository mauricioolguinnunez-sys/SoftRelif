import customtkinter as ctk
from utils.theme_manager import ThemeManager


class SoftCard(ctk.CTkFrame):
    """
    Tarjeta general de SoftRelief.
    Uso: bloques de contenido, secciones del Home, historial, configuración.

    Importante:
    No se envía width=None ni height=None a CTkFrame,
    porque CustomTkinter requiere valores numéricos.
    """

    def __init__(self, master, width=None, height=None, **kwargs):
        colors = ThemeManager.get_colors()

        frame_options = {
            "master": master,
            "corner_radius": kwargs.pop("corner_radius", 22),
            "fg_color": kwargs.pop("fg_color", colors.get("card_bg", "#FFFFFF")),
            "border_width": kwargs.pop("border_width", 0),
            "border_color": kwargs.pop(
                "border_color",
                colors.get("card_border", colors.get("border", "#E5E7EB"))
            ),
        }

        if width is not None:
            frame_options["width"] = width

        if height is not None:
            frame_options["height"] = height

        frame_options.update(kwargs)

        super().__init__(**frame_options)

        if width is not None or height is not None:
            self.pack_propagate(False)
            self.grid_propagate(False)


class FormCard(ctk.CTkFrame):
    """
    Tarjeta para formularios.
    Uso: login, registro, formularios de check-in, configuración.
    """

    def __init__(self, master, width=430, height=560, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=kwargs.pop("corner_radius", 28),
            fg_color=kwargs.pop("fg_color", colors.get("card_bg", "#FFFFFF")),
            border_width=kwargs.pop("border_width", 0),
            border_color=kwargs.pop(
                "border_color",
                colors.get("card_border", colors.get("border", "#E5E7EB"))
            ),
            **kwargs
        )

        self.pack_propagate(False)
        self.grid_propagate(False)


class StatCard(ctk.CTkFrame):
    """
    Tarjeta pequeña para mostrar datos rápidos.
    Uso: estrés, energía, check-in reciente, estado actual.
    """

    def __init__(self, master, title="", value="", **kwargs):
        colors = ThemeManager.get_colors()

        width = kwargs.pop("width", 210)
        height = kwargs.pop("height", 120)

        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=kwargs.pop("corner_radius", 20),
            fg_color=kwargs.pop("fg_color", colors.get("card_bg", "#FFFFFF")),
            border_width=kwargs.pop("border_width", 0),
            border_color=kwargs.pop(
                "border_color",
                colors.get("card_border", colors.get("border", "#E5E7EB"))
            ),
            **kwargs
        )

        self.pack_propagate(False)
        self.grid_propagate(False)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 13),
            text_color=colors.get("text_soft", colors.get("muted_text", "#64748B"))
        )
        self.title_label.pack(anchor="w", padx=18, pady=(16, 4))

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=("Arial", 26, "bold"),
            text_color=colors.get("text", "#1E1B4B")
        )
        self.value_label.pack(anchor="w", padx=18)

    def set_value(self, value):
        self.value_label.configure(text=value)