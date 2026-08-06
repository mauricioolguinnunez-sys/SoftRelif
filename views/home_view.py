import os
import re
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
from utils.i18n import Lang
from controllers.checkin_controller import CheckinController


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
DARK_LOGO_PATH = os.path.join(BASE_DIR, "assets", "dark_logo.png")

# Stable navigation keys
NAV_HOME = "nav_home"
NAV_CHECKIN = "nav_checkin"
NAV_CALM_MODE = "nav_calm_mode"
NAV_SOUNDS = "nav_sounds"
NAV_MICROBREAKS = "nav_microbreaks"
NAV_HISTORY = "nav_history"
NAV_SETTINGS = "nav_settings"
NAV_SUPERUSER = "nav_superuser"
NAV_SPECIALIST = "nav_specialist"
NAV_TRAJECTORY = "nav_trajectory"
NAV_ASSIGN_RECOMMENDATION = "nav_assign_recommendation"
NAV_MARK_FOLLOWUP = "nav_mark_followup"
NAV_LOAD_RESOURCE = "nav_load_resource"


class HomeView(ctk.CTkFrame):

    def __init__(self, master, app):
        self.app = app
        self.current_user = app.current_user
        self.theme_name = self.get_theme_name()
        self.theme = ThemeManager.get_theme(self.theme_name)

        self.safe_apply_theme()
        AppState.save_last_theme(self.theme_name)

        user_lang = self.current_user.get("idioma") if self.current_user else None
        Lang.set(user_lang or AppState.load_language())

        super().__init__(
            master,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=0
        )

        self.sidebar = None
        self.content = None
        self.logo_image = None
        self.nav_buttons = {}
        self.lang_frame = None
        self.current_view_key = NAV_HOME

        self.build_layout()
        self.show_default_view()

    def c(self, key, default=None):
        fallback = {
            "app_bg": "#F6F7FB",
            "sidebar_bg": "#FFFFFF",
            "card_bg": "#FFFFFF",
            "card_border": "#E5E7EB",
            "text": "#1E1B4B",
            "text_soft": "#6B7280",
            "accent": "#8B5CF6",
            "accent_soft": "#EDE9FE",
            "button_hover": "#7C3AED",
            "menu_hover": "#F3F4F6",
            "danger": "#DC2626",
        }
        if default is None:
            default = fallback.get(key, "#000000")
        return self.theme.get(key, default)

    def get_theme_name(self):
        if self.current_user:
            return self.current_user.get("tema_visual", "light")
        return AppState.load_last_theme()

    def user_name(self):
        if self.current_user:
            return self.current_user.get("nombre", Lang.get("username"))
        return Lang.get("username")

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

    def allowed_views(self):
        role = self.user_role()
        if role == "superuser":
            return {NAV_SUPERUSER, NAV_SETTINGS}
        if role == "especialista":
            return {NAV_SPECIALIST, NAV_TRAJECTORY, NAV_ASSIGN_RECOMMENDATION,
                    NAV_MARK_FOLLOWUP, NAV_LOAD_RESOURCE, NAV_SETTINGS}
        return {NAV_HOME, NAV_CHECKIN, NAV_CALM_MODE, NAV_SOUNDS,
                NAV_MICROBREAKS, NAV_HISTORY, NAV_SETTINGS}

    def can_open(self, key):
        return key in self.allowed_views()

    def get_role_menu(self):
        role = self.user_role()
        if role == "superuser":
            return [
                (NAV_SUPERUSER, "\u25c6", lambda: self.open_view(
                    NAV_SUPERUSER, "views.superuser_view", "SuperuserView"
                )),
                (NAV_SETTINGS, "\u2699", lambda: self.open_view(
                    NAV_SETTINGS, "views.settings_view", "SettingsView"
                )),
            ]
        if role == "especialista":
            return [
                (NAV_SPECIALIST, "\u271a", lambda: self.open_view(
                    NAV_SPECIALIST, "views.specialist_view", "SpecialistView"
                )),
                (NAV_SETTINGS, "\u2699", lambda: self.open_view(
                    NAV_SETTINGS, "views.settings_view", "SettingsView"
                )),
            ]
        return [
            (NAV_HOME, "\u2302", self.show_home_content),
            (NAV_CHECKIN, "\u2661", lambda: self.open_view(
                NAV_CHECKIN, "views.checkin_view", "CheckinView"
            )),
            (NAV_CALM_MODE, "\u263e", self.show_calm_mode),
            (NAV_SOUNDS, "\u266b", self.show_sounds),
            (NAV_MICROBREAKS, "\u2615", lambda: self.open_view(
                NAV_MICROBREAKS, "views.microbreaks_view", "MicrobreaksView"
            )),
            (NAV_HISTORY, "\u25d4", lambda: self.open_view(
                NAV_HISTORY, "views.history_view", "HistoryView"
            )),
            (NAV_SETTINGS, "\u2699", lambda: self.open_view(
                NAV_SETTINGS, "views.settings_view", "SettingsView"
            )),
        ]

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
        self.sidebar_language_selector()

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

    def sidebar_header(self):
        box = self.frame(self.sidebar)
        box.grid(row=0, column=0, sticky="ew", padx=22, pady=(26, 18))

        logo = self.load_logo()

        if logo:
            ctk.CTkLabel(box, text="", image=logo).pack(anchor="center", pady=(0, 8))
        else:
            ctk.CTkLabel(
                box,
                text="\u2726",
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
            Lang.get("sidebar_digital_wellness"),
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
        self.nav_buttons = {}

        for row, (key, icon, command) in enumerate(self.get_role_menu()):
            text = Lang.get(key)
            button = SidebarButton(
                nav,
                text=f"{icon}   {text}",
                command=command,
                fg_color="transparent",
                hover_color=self.c("menu_hover", "#F0F0F0"),
                text_color=self.c("text", "#30384F")
            )
            button.grid(row=row, column=0, sticky="ew", pady=4)
            self.nav_buttons[key] = button

    def sidebar_user_card(self):
        box = self.frame(self.sidebar)
        box.grid(row=2, column=0, sticky="sew", padx=18, pady=(18, 8))

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

    def sidebar_language_selector(self):
        container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        container.grid(row=3, column=0, sticky="ew", padx=18, pady=(4, 24))
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        SmallLabel(
            container,
            Lang.get("sidebar_language"),
            text_color=self.c("text_soft", "#7E86A3")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 6))

        current = Lang.current()
        es_selected = current == "es"
        en_selected = current == "en"

        btn_es = ctk.CTkButton(
            container,
            text=Lang.get("language_es"),
            height=32,
            corner_radius=12,
            fg_color=self.c("accent_soft", "#EDE9FE") if es_selected else self.c("card_bg", "#FFFFFF"),
            text_color=self.c("accent", "#8B5CF6") if es_selected else self.c("text_soft", "#6B7280"),
            border_width=1,
            border_color=self.c("accent", "#8B5CF6") if es_selected else self.c("card_border", "#E5E7EB"),
            command=lambda: self.set_language("es")
        )
        btn_es.grid(row=1, column=0, sticky="ew", padx=(0, 4))

        btn_en = ctk.CTkButton(
            container,
            text=Lang.get("language_en"),
            height=32,
            corner_radius=12,
            fg_color=self.c("accent_soft", "#EDE9FE") if en_selected else self.c("card_bg", "#FFFFFF"),
            text_color=self.c("accent", "#8B5CF6") if en_selected else self.c("text_soft", "#6B7280"),
            border_width=1,
            border_color=self.c("accent", "#8B5CF6") if en_selected else self.c("card_border", "#E5E7EB"),
            command=lambda: self.set_language("en")
        )
        btn_en.grid(row=1, column=1, sticky="ew", padx=(4, 0))

    def set_language(self, lang):
        if lang not in ["es", "en"]:
            return

        Lang.set(lang)
        AppState.save_language(lang)

        if self.current_user:
            self.current_user["idioma"] = lang
            from controllers.user_controller import UserController
            UserController.update_language(self.current_user, lang)

        self.rebuild_sidebar()
        self.reload_current_view()

    def rebuild_sidebar(self):
        if self.sidebar:
            for widget in self.sidebar.winfo_children():
                widget.destroy()
        self.sidebar_header()
        self.sidebar_nav()
        self.sidebar_user_card()
        self.sidebar_language_selector()

    def reload_current_view(self):
        key = self.current_view_key
        menu_map = {
            NAV_HOME: ("show_home_content", None, None),
            NAV_CALM_MODE: ("show_calm_mode", None, None),
            NAV_SOUNDS: ("show_sounds", None, None),
            NAV_CHECKIN: ("open_view", "views.checkin_view", "CheckinView"),
            NAV_MICROBREAKS: ("open_view", "views.microbreaks_view", "MicrobreaksView"),
            NAV_HISTORY: ("open_view", "views.history_view", "HistoryView"),
            NAV_SETTINGS: ("open_view", "views.settings_view", "SettingsView"),
            NAV_SUPERUSER: ("open_view", "views.superuser_view", "SuperuserView"),
            NAV_SPECIALIST: ("open_view", "views.specialist_view", "SpecialistView"),
            NAV_TRAJECTORY: ("open_view", "views.specialist_view", "SpecialistView"),
            NAV_ASSIGN_RECOMMENDATION: ("open_view", "views.specialist_view", "SpecialistView"),
            NAV_MARK_FOLLOWUP: ("open_view", "views.specialist_view", "SpecialistView"),
            NAV_LOAD_RESOURCE: ("open_view", "views.specialist_view", "SpecialistView"),
        }
        action, module, cls = menu_map.get(key, ("show_home_content", None, None))
        if action == "show_home_content":
            self.show_home_content()
        elif action == "show_calm_mode":
            self.show_calm_mode()
        elif action == "show_sounds":
            self.show_sounds()
        elif action == "open_view" and module and cls:
            self.open_view(key, module, cls)

    def set_active(self, active_key):
        for key, button in self.nav_buttons.items():
            selected = key == active_key
            button.configure(
                fg_color=self.c("accent_soft", "#F4F1FF") if selected else "transparent",
                text_color=self.c("accent", "#7462D4") if selected else self.c("text", "#30384F"),
                hover_color=self.c("menu_hover", "#F0F0F0")
            )

    def show_default_view(self):
        role = self.user_role()
        if role == "superuser":
            self.open_view(NAV_SUPERUSER, "views.superuser_view", "SuperuserView")
            return
        if role == "especialista":
            self.open_view(NAV_SPECIALIST, "views.specialist_view", "SpecialistView")
            return
        self.show_home_content()

    def open_view(self, key, module_path, class_name):
        if not self.can_open(key):
            self.error_view(
                Lang.get("specialist_access_denied"),
                Lang.get("specialist_access_denied_msg")
            )
            return

        self.current_view_key = key
        self.set_active(key)
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
                    sticky="nsew",
                    padx=0,
                    pady=0
                )

        except Exception as error:
            self.error_view(Lang.get("specialist_access_denied"), str(error))

    def show_calm_mode(self):
        if not self.can_open(NAV_CALM_MODE):
            self.error_view(
                Lang.get("specialist_access_denied"),
                Lang.get("specialist_access_denied_msg")
            )
            return
        self.open_view(NAV_CALM_MODE, "views.calm_mode_view", "CalmModeView")

    def show_sounds(self):
        if not self.can_open(NAV_SOUNDS):
            self.error_view(
                Lang.get("specialist_access_denied"),
                Lang.get("specialist_access_denied_msg")
            )
            return
        self.open_view(NAV_SOUNDS, "views.sounds_view", "SoundsView")

    def show_home_content(self):
        if not self.can_open(NAV_HOME):
            self.error_view(
                Lang.get("specialist_access_denied"),
                Lang.get("specialist_access_denied_msg")
            )
            return

        self.current_view_key = NAV_HOME
        self.set_active(NAV_HOME)
        self.clear_content()
        self.configure_content_grid()

        self.home_header()
        self.home_stats()
        self.home_actions()
        self.home_phrase()
        self.home_activity()
        self.home_recomendacion_especialista()
        self.home_recursos_especialista()

    def last_checkin(self):
        latest = CheckinController.get_latest_checkin(self.current_user)
        if latest:
            return latest
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
            return Lang.get("home_no_detail")
        texto = str(descripcion)
        texto = texto.replace("RECOMENDACION", "")
        texto = texto.replace("T\u00edtulo:", "T\u00edtulo:")
        texto = texto.replace("Detalle:", "\nDetalle:")
        return texto.strip()

    def home_recomendacion_especialista(self):
        recomendacion = self.obtener_recomendacion_especialista()

        card = self.card(self.content)
        card.grid(
            row=4, column=0, columnspan=3, sticky="ew", padx=30, pady=(0, 28)
        )

        TitleLabel(
            card,
            Lang.get("home_specialist_recommendation"),
            size=22,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        if not recomendacion:
            BodyLabel(
                card,
                Lang.get("home_no_recommendations"),
                size=14,
                text_color=self.c("text_soft", "#7E86A3"),
                wraplength=820
            ).pack(anchor="w", padx=24, pady=(0, 22))
            return

        especialista = recomendacion.get("especialista_nombre") or Lang.get("super_role_specialist")
        fecha = recomendacion.get("fecha_evento", "-")
        detalle = self.limpiar_texto_recomendacion(recomendacion.get("descripcion", ""))

        SmallLabel(
            card,
            Lang.get("home_assigned_by", especialista=especialista, fecha=fecha),
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

    def obtener_recursos_especialista(self):
        if not self.current_user:
            return []
        id_usuario = self.current_user.get("id_usuario")
        if not id_usuario:
            return []
        try:
            from models.user_model import UserModel
            return UserModel.get_resources_for_user(id_usuario) or []
        except Exception:
            return []

    def parsear_recurso(self, descripcion):
        descripcion = str(descripcion)

        patrones = [
            ("nuevo", r"TIPO:\s*(.*?)\s*\nTITULO:\s*(.*?)\s*\nCONTENIDO:\s*([\s\S]*)"),
            ("legacy", r"Título:\s*(.*?)\s*\nTipo:\s*(.*?)\s*\nContenido:\s*([\s\S]*)"),
            ("legacy", r"Title:\s*(.*?)\s*\nType:\s*(.*?)\s*\nContent:\s*([\s\S]*)"),
        ]

        for formato, patron in patrones:
            match = re.search(patron, descripcion)
            if match:
                if formato == "nuevo":
                    return {
                        "titulo": match.group(2).strip(),
                        "tipo": match.group(1).strip(),
                        "contenido": match.group(3).strip(),
                    }
                return {
                    "titulo": match.group(1).strip(),
                    "tipo": match.group(2).strip(),
                    "contenido": match.group(3).strip(),
                }

        return None

    def icono_recurso(self, tipo):
        iconos = {
            "texto": "📄",
            "enlace": "🔗",
            "documento": "📑",
            "audio": "🎵",
            "video": "🎬",
        }
        return iconos.get(tipo, "📄")

    def home_recursos_especialista(self):
        recursos = self.obtener_recursos_especialista()

        card = self.card(self.content)
        card.grid(
            row=5, column=0, columnspan=3, sticky="ew", padx=30, pady=(0, 28)
        )

        TitleLabel(
            card,
            Lang.get("home_resources"),
            size=22,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        if not recursos:
            BodyLabel(
                card,
                Lang.get("home_no_resources"),
                size=14,
                text_color=self.c("text_soft", "#7E86A3"),
                wraplength=820
            ).pack(anchor="w", padx=24, pady=(0, 22))
            return

        for recurso in recursos:
            datos = self.parsear_recurso(recurso.get("descripcion", ""))

            if not datos:
                continue

            especialista = recurso.get("especialista_nombre") or Lang.get("super_role_specialist")
            fecha = recurso.get("fecha_evento", "-")

            fila = ctk.CTkFrame(card, fg_color="transparent")
            fila.pack(fill="x", padx=24, pady=(0, 14))

            ctk.CTkLabel(
                fila,
                text=self.icono_recurso(datos["tipo"]),
                font=("Arial", 20),
                text_color=self.c("text", "#30384F")
            ).pack(side="left", padx=(0, 12))

            cuerpo = ctk.CTkFrame(fila, fg_color="transparent")
            cuerpo.pack(side="left", fill="x", expand=True)

            TitleLabel(
                cuerpo,
                datos["titulo"],
                size=15,
                text_color=self.c("text", "#30384F")
            ).pack(anchor="w")

            SmallLabel(
                cuerpo,
                Lang.get(
                    "home_resource_meta",
                    tipo=Lang.t(f"resource_type_{datos['tipo']}", datos["tipo"]),
                    especialista=especialista,
                    fecha=fecha
                ),
                size=11,
                text_color=self.c("text_soft", "#7E86A3")
            ).pack(anchor="w", pady=(2, 4))

            BodyLabel(
                cuerpo,
                datos["contenido"],
                size=13,
                text_color=self.c("text", "#30384F"),
                wraplength=760
            ).pack(anchor="w")

    def home_header(self):
        card = self.card(self.content)
        card.grid(row=0, column=0, columnspan=3, sticky="ew", padx=30, pady=(24, 18))
        card.grid_columnconfigure(0, weight=1)

        left = self.frame(card)
        left.grid(row=0, column=0, sticky="w", padx=26, pady=24)

        TitleLabel(
            left,
            Lang.get("home_hello", name=self.user_name()),
            size=32,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w")

        SubtitleLabel(
            left,
            Lang.get("home_welcome"),
            size=15,
            text_color=self.c("text_soft", "#7E86A3")
        ).pack(anchor="w", pady=(3, 0))

        self.secondary_button(
            card,
            Lang.get("home_logout"),
            command=self.logout
        ).grid(row=0, column=1, sticky="e", padx=26, pady=24)

    def home_stats(self):
        data = self.last_checkin()

        stats = self.frame(self.content)
        stats.grid(row=1, column=0, columnspan=3, sticky="ew", padx=30, pady=(0, 18))

        for col in range(4):
            stats.grid_columnconfigure(col, weight=1)

        metricas = data.get("resumen_metricas", {})
        estres_val = metricas.get("estres", data.get("estres", "-"))
        energia_val = metricas.get("energia", data.get("energia", "-"))

        items = [
            (Lang.get("home_stress"), f"{estres_val}/10"),
            (Lang.get("home_energy"), f"{energia_val}/10"),
            (Lang.get("home_status"), data.get("estado_animo_general") or data.get("estado_animo") or data.get("mood", Lang.get("home_no_record"))),
            (Lang.get("home_recommendation"), data.get("recomendacion_automatica", {}).get("titulo", Lang.get("home_pending"))),
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
            Lang.get("home_quick_actions"),
            size=22,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 10))

        box = self.frame(card)
        box.pack(fill="x", padx=24, pady=(0, 24))

        for col in range(3):
            box.grid_columnconfigure(col, weight=1)

        actions = [
            (Lang.get("nav_checkin"), Lang.get("home_checkin_register"), lambda: self.open_view(
                NAV_CHECKIN, "views.checkin_view", "CheckinView"
            )),
            (Lang.get("nav_calm_mode"), Lang.get("home_calm_mode_desc"), self.show_calm_mode),
            (Lang.get("nav_microbreaks"), Lang.get("home_microbreak_desc"), lambda: self.open_view(
                NAV_MICROBREAKS, "views.microbreaks_view", "MicrobreaksView"
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
            Lang.get("home_open"),
            height=34,
            command=command
        ).pack(fill="x", padx=18, pady=(0, 18))

    def home_phrase(self):
        data = self.last_checkin()
        phrase = data.get("frase") or data.get("phrase")
        if not phrase:
            for r in data.get("respuestas", []):
                if r.get("tipo") == "texto" and r.get("valor"):
                    phrase = r["valor"]
                    break
        if not phrase and self.current_user:
            phrase = self.current_user.get("frase_hoy")
        phrase = phrase or Lang.get("home_default_phrase")

        card = self.card(self.content)
        card.grid(row=2, column=2, sticky="nsew", padx=(12, 30), pady=(0, 18))

        TitleLabel(
            card,
            Lang.get("home_phrase_today"),
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
            Lang.get("home_recent_activity"),
            size=22,
            text_color=self.c("text", "#30384F")
        ).pack(anchor="w", padx=24, pady=(22, 12))

        rec = data.get("recomendacion_automatica", {})
        self.activity_row(
            card,
            rec.get("titulo", Lang.get("home_no_recent_activity")),
            data.get("estado_animo_general") or data.get("estado_animo") or data.get("mood", Lang.get("home_do_checkin"))
        )

    def activity_row(self, parent, title, detail):
        row = self.card(parent, radius=16, bg=self.c("app_bg", "#F6F7FB"))
        row.pack(fill="x", padx=24, pady=(0, 24))
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row,
            text="\u2713",
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
