import os
from importlib import import_module

import customtkinter as ctk
from PIL import Image

from components import (
    SoftCard,
    StatCard,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    SmallLabel,
    PrimaryButton,
    SecondaryButton,
    SidebarButton,
)

from utils.theme_manager import ThemeManager
from utils.app_state import AppState


class HomeView(ctk.CTkFrame):
    """
    Home principal de SoftRelief.

    Función:
    - Contenedor general de la app.
    - Sidebar.
    - Área scrollable.
    - Navegación entre vistas.
    """

    def __init__(self, master, app):
        self.app = app
        self.current_user = app.current_user
        self.theme_name = self.get_theme_name()
        self.theme = ThemeManager.get_theme(self.theme_name)

        self.safe_apply_theme()
        AppState.save_last_theme(self.theme_name)

        super().__init__(
            master,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=0
        )

        self.sidebar = None
        self.content = None
        self.logo_image = None
        self.nav_buttons = {}

        self.pack(fill="both", expand=True)
        self.build()
        self.show_home_content()

    # =====================================================
    # HELPERS
    # =====================================================

    def c(self, key, default):
        return self.theme.get(key, default)

    def get_theme_name(self):
        if self.current_user:
            return self.current_user.get("tema_visual", "light")
        return AppState.load_last_theme()

    def user_name(self):
        if self.current_user:
            return self.current_user.get("nombre", "Usuario")
        return "Usuario"

    def user_role(self):
        if self.current_user:
            return self.current_user.get("rol", "usuario")
        return "usuario"

    def user_initials(self):
        name = self.user_name().strip().split()

        if len(name) >= 2:
            return f"{name[0][0]}{name[1][0]}".upper()

        if len(name) == 1 and name[0]:
            return name[0][0].upper()

        return "U"

    def safe_apply_theme(self):
        try:
            ThemeManager.apply_mode(self.theme_name)
        except Exception:
            ctk.set_appearance_mode(self.theme_name)

    def frame(self, parent):
        return ctk.CTkFrame(parent, fg_color="transparent")

    def card(self, parent, radius=22, bg=None, border=True):
        return SoftCard(
            parent,
            fg_color=bg or self.c("card_bg", "#FFFFFF"),
            border_width=1 if border else 0,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=radius
        )

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def configure_content_grid(self):
        for col in range(3):
            self.content.grid_columnconfigure(col, weight=1)

    def set_active(self, active_text):
        for text, button in self.nav_buttons.items():
            selected = text == active_text

            button.configure(
                fg_color=self.c("accent_soft", "#EDE9FE") if selected else "transparent",
                text_color=self.c("accent", "#7C3AED") if selected else self.c("text", "#1E1B4B"),
                hover_color=self.c("accent_soft", "#EDE9FE")
            )

    # =====================================================
    # BUILD BASE
    # =====================================================

    def build(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.build_content_area()

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=self.c("sidebar_bg", "#FFFFFF")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=1)

        self.sidebar_logo()
        self.sidebar_nav()
        self.sidebar_user_card()

    def build_content_area(self):
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=0,
            scrollbar_button_color=self.c("accent", "#7C3AED"),
            scrollbar_button_hover_color=self.c("button_hover", "#6D28D9")
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.configure_content_grid()

    # =====================================================
    # SIDEBAR
    # =====================================================

    def sidebar_logo(self):
        box = self.frame(self.sidebar)
        box.grid(row=0, column=0, sticky="ew", padx=24, pady=(28, 22))

        logo = self.load_logo()

        if logo:
            ctk.CTkLabel(box, text="", image=logo).pack(anchor="center", pady=(0, 8))
        else:
            ctk.CTkLabel(
                box,
                text="✦",
                width=78,
                height=78,
                corner_radius=39,
                fg_color=self.c("accent_soft", "#EDE9FE"),
                text_color=self.c("accent", "#7C3AED"),
                font=("Arial", 40, "bold")
            ).pack(anchor="center", pady=(0, 8))

        TitleLabel(
            box,
            "SoftRelief",
            size=28,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="center")

        SmallLabel(
            box,
            "Bienestar digital al alcance",
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="center")

    def load_logo(self):
        candidates = [
            f"assets/{self.theme_name}_logo.png",
            f"assets/{self.theme_name}_logo.jpg",
            "assets/logo.png",
            "assets/logo.jpg",
            "assets/logo.jpeg",
        ]

        for path in candidates:
            if os.path.exists(path):
                image = Image.open(path)
                self.logo_image = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(120, 120)
                )
                return self.logo_image

        return None

    def sidebar_nav(self):
        nav = self.frame(self.sidebar)
        nav.grid(row=1, column=0, sticky="new", padx=18, pady=(4, 0))
        nav.grid_columnconfigure(0, weight=1)

        items = [
            ("Inicio", "⌂", self.show_home_content),
            ("Check-in", "♡", lambda: self.open_view("Check-in", "views.checkin_view", "CheckinView")),
            ("Modo Calma", "☾", self.show_calm_mode),
            ("Sonidos", "♫", self.show_sounds),
            ("Microdescansos", "☕", lambda: self.open_view("Microdescansos", "views.microbreaks_view", "MicrobreaksView")),
            ("Historial", "◔", lambda: self.open_view("Historial", "views.history_view", "HistoryView")),
            ("Configuración", "⚙", lambda: self.open_view("Configuración", "views.settings_view", "SettingsView")),
        ]

        if self.user_role() == "superuser":
            items.append(
                ("Superuser", "◆", lambda: self.open_view("Superuser", "views.superuser_view", "SuperuserView"))
            )

        for row, (text, icon, command) in enumerate(items):
            button = SidebarButton(
                nav,
                text=f"{icon}   {text}",
                command=command
            )
            button.grid(row=row, column=0, sticky="ew", pady=4)
            self.nav_buttons[text] = button

    def sidebar_user_card(self):
        box = self.frame(self.sidebar)
        box.grid(row=3, column=0, sticky="sew", padx=18, pady=(18, 24))

        user_card = self.card(box, radius=18)
        user_card.pack(fill="x")

        user_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            user_card,
            text=self.user_initials(),
            width=44,
            height=44,
            corner_radius=22,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#7C3AED"),
            font=("Arial", 15, "bold")
        ).grid(row=0, column=0, rowspan=2, padx=14, pady=14)

        TitleLabel(
            user_card,
            self.user_name(),
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).grid(row=0, column=1, sticky="w", pady=(14, 0))

        SmallLabel(
            user_card,
            self.user_role(),
            text_color=self.c("text_soft", "#6B7280")
        ).grid(row=1, column=1, sticky="w", pady=(0, 14))

    # =====================================================
    # NAVEGACIÓN
    # =====================================================

    def open_view(self, nav_name, module_path, class_name):
        self.set_active(nav_name)
        self.clear_content()
        self.configure_content_grid()

        try:
            module = import_module(module_path)
            view_class = getattr(module, class_name)

            try:
                view = view_class(
                    master=self.content,
                    app=self.app,
                    user=self.current_user
                )
            except TypeError:
                view = view_class(
                    master=self.content,
                    app=self.app
                )

            view.grid(
                row=0,
                column=0,
                columnspan=3,
                sticky="new",
                padx=0,
                pady=0
            )

        except Exception as error:
            self.error_view("No se pudo abrir la vista", str(error))

    def show_calm_mode(self):
        try:
            self.open_view("Modo Calma", "views.calm_mode_view", "CalmModeView")
        except Exception:
            self.placeholder(
                "Modo Calma",
                "Pausa guiada para recuperar equilibrio y reducir tensión."
            )

    def show_sounds(self):
        try:
            self.open_view("Sonidos", "views.sounds_view", "SoundsView")
        except Exception:
            self.placeholder(
                "Sonidos",
                "Ambientes sonoros para concentración y relajación."
            )

    def placeholder(self, title, description):
        self.clear_content()
        self.configure_content_grid()

        card = self.card(self.content)
        card.grid(row=0, column=0, columnspan=3, sticky="ew", padx=30, pady=30)

        TitleLabel(
            card,
            title,
            size=30,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=26, pady=(24, 8))

        BodyLabel(
            card,
            description,
            size=15,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=720
        ).pack(anchor="w", padx=26, pady=(0, 24))

    def error_view(self, title, detail):
        self.clear_content()

        card = self.card(self.content)
        card.grid(row=0, column=0, columnspan=3, sticky="ew", padx=30, pady=30)

        TitleLabel(
            card,
            title,
            size=24,
            text_color=self.c("danger", "#DC2626")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        BodyLabel(
            card,
            detail,
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=720
        ).pack(anchor="w", padx=24, pady=(0, 22))

    # =====================================================
    # HOME
    # =====================================================

    def show_home_content(self):
        self.set_active("Inicio")
        self.clear_content()
        self.configure_content_grid()

        self.home_header()
        self.home_stats()
        self.home_actions()
        self.home_phrase_and_activity()

    def last_checkin(self):
        if self.app and getattr(self.app, "last_checkin", None):
            return self.app.last_checkin

        if self.current_user and self.current_user.get("ultimo_checkin"):
            return self.current_user["ultimo_checkin"]

        return {}

    def home_header(self):
        card = self.card(self.content)
        card.grid(row=0, column=0, columnspan=3, sticky="ew", padx=30, pady=(24, 18))
        card.grid_columnconfigure(0, weight=1)

        left = self.frame(card)
        left.grid(row=0, column=0, sticky="w", padx=26, pady=24)

        TitleLabel(
            left,
            f"Hola, {self.user_name()}",
            size=32,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            left,
            "Bienvenido de nuevo a tu espacio de bienestar digital.",
            size=15,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(3, 0))

        SecondaryButton(
            card,
            text="Cerrar sesión",
            command=self.logout
        ).grid(row=0, column=1, sticky="e", padx=26, pady=24)

    def home_stats(self):
        data = self.last_checkin()

        stats = self.frame(self.content)
        stats.grid(row=1, column=0, columnspan=3, sticky="ew", padx=30, pady=(0, 18))

        for col in range(4):
            stats.grid_columnconfigure(col, weight=1)

        items = [
            ("Estrés", f"{data.get('stress', '-')}/10"),
            ("Energía", f"{data.get('energy', '-')}/10"),
            ("Estado", data.get("mood", "Sin registro")),
            ("Recomendación", data.get("recommendation_title", "Pendiente")),
        ]

        for col, (title, value) in enumerate(items):
            StatCard(stats, title=title, value=value).grid(
                row=0,
                column=col,
                sticky="ew",
                padx=6
            )

    def home_actions(self):
        card = self.card(self.content)
        card.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(30, 12), pady=(0, 18))

        TitleLabel(
            card,
            "Acciones rápidas",
            size=22,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(22, 10))

        actions = self.frame(card)
        actions.pack(fill="x", padx=24, pady=(0, 24))

        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)
        actions.grid_columnconfigure(2, weight=1)

        self.action_button(
            actions,
            "Check-in",
            "Registra cómo te sientes hoy.",
            lambda: self.open_view("Check-in", "views.checkin_view", "CheckinView"),
            0
        )

        self.action_button(
            actions,
            "Modo Calma",
            "Pausa guiada para recuperar equilibrio.",
            self.show_calm_mode,
            1
        )

        self.action_button(
            actions,
            "Microdescanso",
            "Actividad breve de baja carga cognitiva.",
            lambda: self.open_view("Microdescansos", "views.microbreaks_view", "MicrobreaksView"),
            2
        )

    def action_button(self, parent, title, detail, command, col):
        card = self.card(parent, radius=18, bg=self.c("app_bg", "#F6F7FB"))
        card.grid(row=0, column=col, sticky="nsew", padx=6)

        TitleLabel(
            card,
            title,
            size=17,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=18, pady=(18, 4))

        SmallLabel(
            card,
            detail,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=18, pady=(0, 14))

        PrimaryButton(
            card,
            text="Abrir",
            height=34,
            command=command
        ).pack(fill="x", padx=18, pady=(0, 18))

    def home_phrase_and_activity(self):
        data = self.last_checkin()

        phrase = data.get("phrase")
        if not phrase and self.current_user:
            phrase = self.current_user.get("frase_hoy")

        phrase = phrase or "Hoy es un buen día para cuidar de ti."

        phrase_card = self.card(self.content)
        phrase_card.grid(row=2, column=2, sticky="nsew", padx=(12, 30), pady=(0, 18))

        TitleLabel(
            phrase_card,
            "Frase para hoy",
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        BodyLabel(
            phrase_card,
            phrase,
            size=15,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=300
        ).pack(anchor="w", padx=24, pady=(0, 22))

        activity = self.card(self.content)
        activity.grid(row=3, column=0, columnspan=3, sticky="ew", padx=30, pady=(0, 28))

        TitleLabel(
            activity,
            "Actividad reciente",
            size=22,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(22, 12))

        self.activity_row(
            activity,
            data.get("recommendation_title", "Sin actividad reciente"),
            data.get("mood", "Realiza un check-in para comenzar.")
        )

    def activity_row(self, parent, title, detail):
        row = self.card(parent, radius=16, bg=self.c("app_bg", "#F6F7FB"))
        row.pack(fill="x", padx=24, pady=(0, 24))
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row,
            text="✓",
            width=36,
            height=36,
            corner_radius=18,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#7C3AED"),
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, rowspan=2, padx=14, pady=12)

        TitleLabel(
            row,
            title,
            size=15,
            text_color=self.c("text", "#1E1B4B")
        ).grid(row=0, column=1, sticky="w", pady=(12, 0))

        SmallLabel(
            row,
            detail,
            text_color=self.c("text_soft", "#6B7280")
        ).grid(row=1, column=1, sticky="w", pady=(0, 12))

    # =====================================================
    # SESSION
    # =====================================================

    def logout(self):
        AppState.save_last_theme(self.theme_name)

        if self.app:
            self.app.current_user = None
            self.app.show_login()