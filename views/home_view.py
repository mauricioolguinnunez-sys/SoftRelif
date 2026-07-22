import os
from importlib import import_module

import customtkinter as ctk
from PIL import Image

from components import (
    SoftCard,
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


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
DARK_LOGO_PATH = os.path.join(BASE_DIR, "assets", "dark_logo.png")


class HomeView(ctk.CTkFrame):
    """
    HomeView principal de SoftRelief.

    Control de acceso por rol:
    - usuario: funciones de bienestar personal.
    - especialista: seguimiento, recomendaciones y recursos.
    - superuser: administración del sistema.
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
        self.build_layout()
        self.show_default_view()

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
        parts = self.user_name().strip().split()

        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()

        if len(parts) == 1 and parts[0]:
            return parts[0][0].upper()

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

    def primary_button(self, parent, text, command=None, height=40):
        return PrimaryButton(
            parent,
            text=text,
            height=height,
            fg_color=self.c("button", "#7BAFD4"),
            hover_color=self.c("button_hover", "#6A9FC5"),
            text_color="#FFFFFF",
            command=command
        )

    def secondary_button(self, parent, text, command=None, height=36):
        return SecondaryButton(
            parent,
            text=text,
            height=height,
            fg_color=self.c("card_bg", "#FFFFFF"),
            hover_color=self.c("menu_hover", "#F0F0F0"),
            text_color=self.c("text", "#30384F"),
            border_width=1,
            border_color=self.c("card_border", "#E8ECF5"),
            command=command
        )

    def clear_content(self):
        if not self.content:
            return

        for widget in self.content.winfo_children():
            widget.destroy()

    def configure_content_grid(self):
        if not self.content:
            return

        for col in range(3):
            self.content.grid_columnconfigure(col, weight=1)

    # =====================================================
    # ACCESS CONTROL
    # =====================================================

    def allowed_views(self):
        role = self.user_role()

        if role == "superuser":
            return {
                "Panel superuser",
                "Configuración",
            }

        if role == "especialista":
            return {
                "Panel especialista",
                "Trayectoria",
                "Asignar recomendación",
                "Marcar seguimiento",
                "Cargar recurso",
                "Configuración",
            }

        return {
            "Inicio",
            "Check-in",
            "Modo Calma",
            "Sonidos",
            "Microdescansos",
            "Historial",
            "Configuración",
        }

    def can_open(self, view_name):
        return view_name in self.allowed_views()

    def get_role_menu(self):
        role = self.user_role()

        if role == "superuser":
            return [
                ("Panel superuser", "◆", lambda: self.open_view(
                    "Panel superuser",
                    "views.superuser_view",
                    "SuperuserView"
                )),
                ("Configuración", "⚙", lambda: self.open_view(
                    "Configuración",
                    "views.settings_view",
                    "SettingsView"
                )),
            ]

        if role == "especialista":
            return [
                ("Panel especialista", "✚", lambda: self.open_view(
                    "Panel especialista",
                    "views.specialist_view",
                    "SpecialistView"
                )),
                ("Configuración", "⚙", lambda: self.open_view(
                    "Configuración",
                    "views.settings_view",
                    "SettingsView"
                )),
            ]

        return [
            ("Inicio", "⌂", self.show_home_content),
            ("Check-in", "♡", lambda: self.open_view(
                "Check-in",
                "views.checkin_view",
                "CheckinView"
            )),
            ("Modo Calma", "☾", self.show_calm_mode),
            ("Sonidos", "♫", self.show_sounds),
            ("Microdescansos", "☕", lambda: self.open_view(
                "Microdescansos",
                "views.microbreaks_view",
                "MicrobreaksView"
            )),
            ("Historial", "◔", lambda: self.open_view(
                "Historial",
                "views.history_view",
                "HistoryView"
            )),
            ("Configuración", "⚙", lambda: self.open_view(
                "Configuración",
                "views.settings_view",
                "SettingsView"
            )),
        ]

    # =====================================================
    # LAYOUT
    # =====================================================

    def build_layout(self):
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
        self.sidebar.grid_rowconfigure(1, weight=1)

        self.sidebar_header()
        self.sidebar_nav()
        self.sidebar_user_card()

    def build_content_area(self):
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=0,
            scrollbar_button_color=self.c("accent", "#7462D4"),
            scrollbar_button_hover_color=self.c("button_hover", "#6A9FC5")
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.configure_content_grid()

    # =====================================================
    # SIDEBAR
    # =====================================================

    def sidebar_header(self):
        box = self.frame(self.sidebar)
        box.grid(row=0, column=0, sticky="ew", padx=22, pady=(26, 18))

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
                fg_color=self.c("accent_soft", "#F4F1FF"),
                text_color=self.c("accent", "#7462D4"),
                font=("Arial", 40, "bold")
            ).pack(anchor="center", pady=(0, 8))

        TitleLabel(
            box,
            "SoftRelief",
            size=28,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="center")

        SmallLabel(
            box,
            "Bienestar digital al alcance",
            text_color=self.c("text_soft", "#7E86A3")
        ).pack(anchor="center")

    def load_logo(self):
        candidates = []

        if self.theme_name == "dark":
            candidates.append(DARK_LOGO_PATH)

        candidates.extend([
            LOGO_PATH,
            os.path.join(BASE_DIR, "assets", "logo.jpg"),
            os.path.join(BASE_DIR, "assets", "logo.jpeg"),
        ])

        for path in candidates:
            if os.path.exists(path):
                image = Image.open(path)
                self.logo_image = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(115, 115)
                )
                return self.logo_image

        return None

    def sidebar_nav(self):
        nav = self.frame(self.sidebar)
        nav.grid(row=1, column=0, sticky="new", padx=18, pady=(4, 0))
        nav.grid_columnconfigure(0, weight=1)

        for row, (text, icon, command) in enumerate(self.get_role_menu()):
            button = SidebarButton(
                nav,
                text=f"{icon}   {text}",
                command=command,
                fg_color="transparent",
                hover_color=self.c("menu_hover", "#F0F0F0"),
                text_color=self.c("text", "#30384F")
            )
            button.grid(row=row, column=0, sticky="ew", pady=4)
            self.nav_buttons[text] = button

    def sidebar_user_card(self):
        box = self.frame(self.sidebar)
        box.grid(row=2, column=0, sticky="sew", padx=18, pady=(18, 24))

        card = self.card(box, radius=18, bg=self.c("user_card", "#F7F7F7"))
        card.pack(fill="x")
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text=self.user_initials(),
            width=44,
            height=44,
            corner_radius=22,
            fg_color=self.c("avatar_bg", "#E8E2FF"),
            text_color=self.c("avatar_text", "#7462D4"),
            font=("Arial", 15, "bold")
        ).grid(row=0, column=0, rowspan=2, padx=14, pady=14)

        TitleLabel(
            card,
            self.user_name(),
            size=14,
            text_color=self.c("text", "#30384F")
        ).grid(row=0, column=1, sticky="w", pady=(14, 0))

        SmallLabel(
            card,
            self.user_role(),
            text_color=self.c("text_soft", "#7E86A3")
        ).grid(row=1, column=1, sticky="w", pady=(0, 14))

    def set_active(self, active_text):
        for text, button in self.nav_buttons.items():
            selected = text == active_text

            button.configure(
                fg_color=self.c("accent_soft", "#F4F1FF") if selected else "transparent",
                text_color=self.c("accent", "#7462D4") if selected else self.c("text", "#30384F"),
                hover_color=self.c("menu_hover", "#F0F0F0")
            )

    # =====================================================
    # NAVIGATION
    # =====================================================

    def show_default_view(self):
        role = self.user_role()

        if role == "superuser":
            self.open_view(
                "Panel superuser",
                "views.superuser_view",
                "SuperuserView"
            )
            return

        if role == "especialista":
            self.open_view(
                "Panel especialista",
                "views.specialist_view",
                "SpecialistView"
            )
            return

        self.show_home_content()

    def open_view(self, nav_name, module_path, class_name):
        if not self.can_open(nav_name):
            self.error_view(
                "Acceso no permitido",
                "Tu rol no tiene permisos para acceder a esta sección."
            )
            return

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

            if not view.winfo_manager():
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
        if not self.can_open("Modo Calma"):
            self.error_view(
                "Acceso no permitido",
                "Tu rol no tiene permisos para acceder a esta sección."
            )
            return

        self.open_view("Modo Calma", "views.calm_mode_view", "CalmModeView")

    def show_sounds(self):
        if not self.can_open("Sonidos"):
            self.error_view(
                "Acceso no permitido",
                "Tu rol no tiene permisos para acceder a esta sección."
            )
            return

        self.open_view("Sonidos", "views.sounds_view", "SoundsView")

    # =====================================================
    # HOME USUARIO NORMAL
    # =====================================================

    def show_home_content(self):
        if not self.can_open("Inicio"):
            self.error_view(
                "Acceso no permitido",
                "Tu rol no tiene permisos para acceder a esta sección."
            )
            return

        self.set_active("Inicio")
        self.clear_content()
        self.configure_content_grid()

        self.home_header()
        self.home_stats()
        self.home_actions()
        self.home_phrase()
        self.home_activity()
        self.home_recomendacion_especialista()

    def last_checkin(self):
        if self.app and getattr(self.app, "last_checkin", None):
            return self.app.last_checkin

        if self.current_user and self.current_user.get("ultimo_checkin"):
            return self.current_user["ultimo_checkin"]

        return {}

    def obtener_recomendacion_especialista(self):
        if not self.current_user:
            return None

        id_usuario = self.current_user.get("id_usuario")

        if not id_usuario:
            return None

        try:
            from models.user_model import UserModel
            return UserModel.get_latest_recommendation_for_user(id_usuario)

        except Exception:
            return None

    def limpiar_texto_recomendacion(self, descripcion):
        if not descripcion:
            return "No hay detalle disponible."

        texto = str(descripcion)

        texto = texto.replace("RECOMENDACION", "")
        texto = texto.replace("Título:", "Título:")
        texto = texto.replace("Detalle:", "\nDetalle:")
        texto = texto.replace("Mongo ID:", "\nReferencia Mongo:")

        return texto.strip()

    def home_recomendacion_especialista(self):
        recomendacion = self.obtener_recomendacion_especialista()

        card = self.card(self.content)
        card.grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=30,
            pady=(0, 28)
        )

        TitleLabel(
            card,
            "Recomendación del especialista",
            size=22,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        if not recomendacion:
            BodyLabel(
                card,
                "Aún no tienes recomendaciones asignadas por un especialista.",
                size=14,
                text_color=self.c("text_soft", "#7E86A3"),
                wraplength=820
            ).pack(anchor="w", padx=24, pady=(0, 22))
            return

        especialista = recomendacion.get("especialista_nombre") or "Especialista"
        fecha = recomendacion.get("fecha_evento", "-")
        detalle = self.limpiar_texto_recomendacion(recomendacion.get("descripcion", ""))

        SmallLabel(
            card,
            f"Asignada por: {especialista} · {fecha}",
            size=12,
            text_color=self.c("text_soft", "#7E86A3")
        ).pack(anchor="w", padx=24, pady=(0, 8))

        BodyLabel(
            card,
            detalle,
            size=14,
            text_color=self.c("text", "#30384F"),
            wraplength=820
        ).pack(anchor="w", padx=24, pady=(0, 22))

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
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w")

        SubtitleLabel(
            left,
            "Bienvenido de nuevo a tu espacio de bienestar digital.",
            size=15,
            text_color=self.c("text_soft", "#7E86A3")
        ).pack(anchor="w", pady=(3, 0))

        self.secondary_button(
            card,
            "Cerrar sesión",
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
            self.stat_card(stats, title, value, col)

    def stat_card(self, parent, title, value, col):
        card = self.card(parent, radius=18)
        card.grid(row=0, column=col, sticky="ew", padx=6)

        SmallLabel(
            card,
            title,
            text_color=self.c("text_soft", "#7E86A3")
        ).pack(anchor="center", pady=(16, 4))

        TitleLabel(
            card,
            str(value),
            size=21,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="center", pady=(0, 16))

    def home_actions(self):
        card = self.card(self.content)
        card.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(30, 12), pady=(0, 18))

        TitleLabel(
            card,
            "Acciones rápidas",
            size=22,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 10))

        box = self.frame(card)
        box.pack(fill="x", padx=24, pady=(0, 24))

        for col in range(3):
            box.grid_columnconfigure(col, weight=1)

        actions = [
            ("Check-in", "Registra cómo te sientes hoy.", lambda: self.open_view(
                "Check-in",
                "views.checkin_view",
                "CheckinView"
            )),
            ("Modo Calma", "Pausa guiada para recuperar equilibrio.", self.show_calm_mode),
            ("Microdescanso", "Actividad breve de baja carga cognitiva.", lambda: self.open_view(
                "Microdescansos",
                "views.microbreaks_view",
                "MicrobreaksView"
            )),
        ]

        for col, (title, detail, command) in enumerate(actions):
            self.action_card(box, title, detail, command, col)

    def action_card(self, parent, title, detail, command, col):
        card = self.card(parent, radius=18, bg=self.c("app_bg", "#F6F7FB"))
        card.grid(row=0, column=col, sticky="nsew", padx=6)

        TitleLabel(
            card,
            title,
            size=17,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=18, pady=(18, 4))

        SmallLabel(
            card,
            detail,
            text_color=self.c("text_soft", "#7E86A3")
        ).pack(anchor="w", padx=18, pady=(0, 14))

        self.primary_button(
            card,
            "Abrir",
            height=34,
            command=command
        ).pack(fill="x", padx=18, pady=(0, 18))

    def home_phrase(self):
        data = self.last_checkin()

        phrase = data.get("phrase")

        if not phrase and self.current_user:
            phrase = self.current_user.get("frase_hoy")

        phrase = phrase or "Hoy es un buen día para cuidar de ti."

        card = self.card(self.content)
        card.grid(row=2, column=2, sticky="nsew", padx=(12, 30), pady=(0, 18))

        TitleLabel(
            card,
            "Frase para hoy",
            size=20,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        BodyLabel(
            card,
            phrase,
            size=15,
            text_color=self.c("text_soft", "#7E86A3"),
            wraplength=300
        ).pack(anchor="w", padx=24, pady=(0, 22))

    def home_activity(self):
        data = self.last_checkin()

        card = self.card(self.content)
        card.grid(row=3, column=0, columnspan=3, sticky="ew", padx=30, pady=(0, 28))

        TitleLabel(
            card,
            "Actividad reciente",
            size=22,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 12))

        self.activity_row(
            card,
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
            fg_color=self.c("accent_soft", "#F4F1FF"),
            text_color=self.c("accent", "#7462D4"),
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, rowspan=2, padx=14, pady=12)

        TitleLabel(
            row,
            title,
            size=15,
            text_color=self.c("text", "#30384F")
        ).grid(row=0, column=1, sticky="w", pady=(12, 0))

        SmallLabel(
            row,
            detail,
            text_color=self.c("text_soft", "#7E86A3")
        ).grid(row=1, column=1, sticky="w", pady=(0, 12))

    # =====================================================
    # ESPECIALISTA
    # =====================================================

    def show_specialist_panel(self):
        if not self.can_open("Panel especialista"):
            self.error_view(
                "Acceso no permitido",
                "Tu rol no tiene permisos para acceder a esta sección."
            )
            return

        self.set_active("Panel especialista")
        self.clear_content()
        self.configure_content_grid()

        self.specialist_header()
        self.specialist_modules()
        self.specialist_side_panel()

    def specialist_header(self):
        card = self.card(self.content)
        card.grid(row=0, column=0, columnspan=3, sticky="ew", padx=30, pady=(24, 18))
        card.grid_columnconfigure(0, weight=1)

        left = self.frame(card)
        left.grid(row=0, column=0, sticky="w", padx=26, pady=24)

        TitleLabel(
            left,
            "Panel especialista",
            size=32,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w")

        SubtitleLabel(
            left,
            "Seguimiento, recomendaciones y recursos de apoyo.",
            size=15,
            text_color=self.c("text_soft", "#7E86A3")
        ).pack(anchor="w", pady=(3, 0))

        self.secondary_button(
            card,
            "Cerrar sesión",
            command=self.logout
        ).grid(row=0, column=1, sticky="e", padx=26, pady=24)

    def specialist_modules(self):
        box = self.frame(self.content)
        box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(30, 12), pady=(0, 26))

        box.grid_columnconfigure(0, weight=1)
        box.grid_columnconfigure(1, weight=1)

        modules = [
            ("Trayectoria", "Consultar evolución, historial emocional y actividad registrada.", "RF-005", "◔"),
            ("Asignar recomendación", "Registrar una recomendación personalizada para un usuario.", "RF-020", "➕"),
            ("Marcar seguimiento", "Indicar que un caso fue revisado o atendido.", "RF-021", "✓"),
            ("Cargar recurso", "Agregar material de apoyo para el bienestar del usuario.", "RF-022", "⬆"),
        ]

        for index, data in enumerate(modules):
            row = index // 2
            col = index % 2
            self.specialist_module_card(box, data, row, col)

    def specialist_module_card(self, parent, data, row, col):
        title, description, rf, icon = data

        card = self.card(parent, radius=20)
        card.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=(0, 12) if col == 0 else (12, 0),
            pady=(0, 18)
        )

        ctk.CTkLabel(
            card,
            text=icon,
            width=58,
            height=58,
            corner_radius=29,
            fg_color=self.c("accent_soft", "#F4F1FF"),
            text_color=self.c("accent", "#7462D4"),
            font=("Arial", 28)
        ).pack(anchor="w", padx=24, pady=(22, 12))

        TitleLabel(
            card,
            title,
            size=20,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(0, 6))

        BodyLabel(
            card,
            description,
            size=14,
            text_color=self.c("text_soft", "#7E86A3"),
            wraplength=300
        ).pack(anchor="w", padx=24, pady=(0, 10))

        SmallLabel(
            card,
            rf,
            text_color=self.c("accent", "#7462D4")
        ).pack(anchor="w", padx=24, pady=(0, 10))

        self.primary_button(
            card,
            "Abrir módulo",
            height=36,
            command=lambda t=title, d=description: self.show_specialist_section(t, d)
        ).pack(fill="x", padx=24, pady=(0, 22))

    def specialist_side_panel(self):
        side = self.frame(self.content)
        side.grid(row=1, column=2, sticky="nsew", padx=(12, 30), pady=(0, 26))

        summary = self.card(side)
        summary.pack(fill="x", pady=(0, 18))

        TitleLabel(
            summary,
            "Resumen del rol",
            size=22,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        BodyLabel(
            summary,
            "El especialista no utiliza las funciones de bienestar como usuario final. Su función es dar seguimiento, asignar recomendaciones y gestionar recursos de apoyo.",
            size=14,
            text_color=self.c("text_soft", "#7E86A3"),
            wraplength=310
        ).pack(anchor="w", padx=24, pady=(0, 22))

        notice = self.card(side)
        notice.pack(fill="x")

        TitleLabel(
            notice,
            "Acceso controlado",
            size=20,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        BodyLabel(
            notice,
            "Este panel está limitado a funciones de asesoría y seguimiento conforme a los requerimientos funcionales del sistema.",
            size=14,
            text_color=self.c("text_soft", "#7E86A3"),
            wraplength=310
        ).pack(anchor="w", padx=24, pady=(0, 22))

    def show_specialist_section(self, title, description):
        if not self.can_open(title):
            self.error_view(
                "Acceso no permitido",
                "Tu rol no tiene permisos para acceder a esta sección."
            )
            return

        self.set_active(title)
        self.clear_content()
        self.configure_content_grid()

        card = self.card(self.content)
        card.grid(row=0, column=0, columnspan=3, sticky="ew", padx=30, pady=(24, 18))

        TitleLabel(
            card,
            title,
            size=32,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=26, pady=(24, 8))

        BodyLabel(
            card,
            description,
            size=15,
            text_color=self.c("text_soft", "#7E86A3"),
            wraplength=820
        ).pack(anchor="w", padx=26, pady=(0, 16))

        BodyLabel(
            card,
            "Módulo en desarrollo. Esta sección corresponde a las funciones definidas para el rol especialista.",
            size=14,
            text_color=self.c("text_soft", "#7E86A3"),
            wraplength=820
        ).pack(anchor="w", padx=26, pady=(0, 24))

    # =====================================================
    # ERRORS / SESSION
    # =====================================================

    def error_view(self, title, detail):
        self.clear_content()
        self.configure_content_grid()

        card = self.card(self.content)
        card.grid(row=0, column=0, columnspan=3, sticky="ew", padx=30, pady=30)

        TitleLabel(
            card,
            title,
            size=24,
            text_color=self.c("danger", "#D9534F")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        BodyLabel(
            card,
            detail,
            size=14,
            text_color=self.c("text_soft", "#7E86A3"),
            wraplength=720
        ).pack(anchor="w", padx=24, pady=(0, 22))

    def logout(self):
        if self.app.current_user:
            theme = self.app.current_user.get("tema_visual", "light")
            self.app.login_theme = theme
            AppState.save_last_theme(theme)

        self.app.current_user = None
        self.app.show_login()