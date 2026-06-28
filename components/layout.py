import customtkinter as ctk
from utils.theme_manager import ThemeManager
from .buttons import SidebarButton
from .labels import TitleLabel, SmallLabel


class BaseView(ctk.CTkFrame):
    """
    Vista base para pantallas de SoftRelief.
    Todas las views pueden heredar de esta clase para mantener estilo uniforme.
    """

    def __init__(self, master, app=None, **kwargs):
        colors = ThemeManager.get_colors()

        super().__init__(
            master,
            fg_color=kwargs.pop("fg_color", colors.get("app_bg", "#F8FAFC")),
            **kwargs
        )

        self.app = app
        self.colors = colors

    def refresh_theme(self):
        self.colors = ThemeManager.get_colors()
        self.configure(fg_color=self.colors.get("app_bg", "#F8FAFC"))


class SidebarLayout(BaseView):
    """
    Layout con sidebar lateral.
    Uso recomendado: Home, Check-in, Modo Calma, Sonidos, Microdescansos, Historial, Configuración.
    """

    def __init__(self, master, app=None, active_page="Home", title="SoftRelief", **kwargs):
        super().__init__(master, app=app, **kwargs)

        self.active_page = active_page
        self.title = title

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=self.colors.get("sidebar_bg", "#FFFFFF")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.colors.get("app_bg", "#F8FAFC")
        )
        self.content.grid(row=0, column=1, sticky="nsew")

        self.build_sidebar()

    def build_sidebar(self):
        TitleLabel(
            self.sidebar,
            self.title,
            size=24
        ).pack(anchor="w", padx=22, pady=(28, 4))

        SmallLabel(
            self.sidebar,
            "Bienestar académico"
        ).pack(anchor="w", padx=24, pady=(0, 22))

        buttons = [
            ("Home", getattr(self.app, "show_home", None)),
            ("Check-in", getattr(self.app, "show_checkin", None)),
            ("Modo Calma", getattr(self.app, "show_calm_mode", None)),
            ("Sonidos", getattr(self.app, "show_sounds", None)),
            ("Microdescansos", getattr(self.app, "show_microbreaks", None)),
            ("Historial", getattr(self.app, "show_history", None)),
            ("Configuración", getattr(self.app, "show_settings", None)),
        ]

        for name, command in buttons:
            SidebarButton(
                self.sidebar,
                text=name,
                active=(name == self.active_page),
                command=command
            ).pack(padx=18, pady=5)

        ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        ).pack(fill="both", expand=True)

        SidebarButton(
            self.sidebar,
            text="Cerrar sesión",
            command=getattr(self.app, "logout", None),
            active=False
        ).pack(padx=18, pady=(5, 24))
