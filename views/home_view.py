import os
import customtkinter as ctk
from PIL import Image

from views.settings_view import SettingsView
from views.superuser_view import SuperuserView
from utils.theme_manager import ThemeManager
from utils.app_state import AppState


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
DARK_LOGO_PATH = os.path.join(BASE_DIR, "assets", "dark_logo.png")


def load_ctk_image(path, size):
    try:
        if os.path.exists(path):
            image = Image.open(path)
            return ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=size
            )
    except Exception as error:
        print(f"Error al cargar imagen {path}: {error}")

    return None


class HomeView(ctk.CTkFrame):

    def __init__(self, master, app):
        self.app = app
        self.current_user = app.current_user

        self.theme_name = "light"

        if self.current_user:
            self.theme_name = self.current_user.get("tema_visual", "light")

        self.theme = ThemeManager.get_theme(self.theme_name)

        super().__init__(
            master,
            corner_radius=0,
            fg_color=self.theme["app_bg"]
        )

        self.pack(fill="both", expand=True)

        self.logo_image = None

        self.create_responsive_layout()
        self.create_sidebar()
        self.create_content_area()
        self.show_home_content()

    # =====================================================
    # ESTILOS
    # =====================================================

    def card_style(self):
        return {
            "fg_color": self.theme["card_bg"],
            "border_width": 1,
            "border_color": self.theme["card_border"]
        }

    def get_logo_path(self):
        if self.theme_name == "dark" and os.path.exists(DARK_LOGO_PATH):
            return DARK_LOGO_PATH
        return LOGO_PATH

    # =====================================================
    # LAYOUT PRINCIPAL
    # =====================================================

    def create_responsive_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=self.theme["sidebar_bg"]
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.main_area = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.theme["app_bg"]
        )
        self.main_area.grid(row=0, column=1, sticky="nsew")

        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

    # =====================================================
    # SIDEBAR
    # =====================================================

    def create_sidebar(self):
        self.sidebar.grid_rowconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=0)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.sidebar_header = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        self.sidebar_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=(25, 10)
        )

        self.logo_image = load_ctk_image(self.get_logo_path(), (105, 105))

        if self.logo_image:
            self.logo_label = ctk.CTkLabel(
                self.sidebar_header,
                text="",
                image=self.logo_image,
                fg_color="transparent"
            )
        else:
            self.logo_label = ctk.CTkLabel(
                self.sidebar_header,
                text="[ LOGO ]",
                font=("Segoe UI", 18),
                text_color=self.theme["text"],
                fg_color="transparent"
            )

        self.logo_label.pack(pady=(0, 5))

        self.app_title = ctk.CTkLabel(
            self.sidebar_header,
            text="SoftRelief",
            font=("Segoe UI Light", 30),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        self.app_title.pack()

        self.app_slogan = ctk.CTkLabel(
            self.sidebar_header,
            text="Bienestar digital al alcance",
            font=("Segoe UI", 11),
            text_color=self.theme["text_soft"],
            fg_color="transparent"
        )
        self.app_slogan.pack(pady=(0, 10))

        self.menu_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color=self.theme["card_border"],
            scrollbar_button_hover_color=self.theme["accent"]
        )
        self.menu_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=14,
            pady=5
        )

        self.menu_items = [
            ("Inicio", self.show_home_content),
            ("Check-in", lambda: self.show_placeholder("Check-in", "Registra tu estado de ánimo y nivel de agotamiento.")),
            ("Modo Calma", lambda: self.show_placeholder("Modo Calma", "Pausa guiada para recuperar equilibrio.")),
            ("Respiración", lambda: self.show_placeholder("Respiración", "Ejercicios para respirar y centrarte.")),
            ("Sonidos", lambda: self.show_placeholder("Sonidos", "Ambientes sonoros para concentración y relajación.")),
            ("Microdescansos", lambda: self.show_placeholder("Microdescansos", "Pausas breves y actividades de baja carga cognitiva.")),
            ("Historial", lambda: self.show_placeholder("Historial", "Consulta tus sesiones, pausas y progreso.")),
            ("Configuración", self.show_settings),
        ]

        if self.current_user and self.current_user.get("rol") == "superuser":
            self.menu_items.append(("Superuser", self.show_superuser_panel))

        for text, command in self.menu_items:
            button = ctk.CTkButton(
                self.menu_frame,
                text=text,
                width=180,
                height=38,
                corner_radius=12,
                anchor="w",
                font=("Segoe UI", 14),
                fg_color="transparent",
                hover_color=self.theme["menu_hover"],
                text_color=self.theme["text"],
                command=command
            )
            button.pack(fill="x", pady=4)

        self.create_user_card()

    def create_user_card(self):
        self.user_card = ctk.CTkFrame(
            self.sidebar,
            height=75,
            corner_radius=16,
            fg_color=self.theme["user_card"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        self.user_card.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=15,
            pady=(10, 20)
        )
        self.user_card.grid_propagate(False)

        user_name = "Usuario"
        user_role = "Cuenta local"

        if self.current_user:
            user_name = self.current_user.get("nombre", "Usuario")
            user_role = self.current_user.get("rol", "usuario")

        initials = self.get_initials(user_name)

        self.avatar = ctk.CTkLabel(
            self.user_card,
            text=initials,
            width=38,
            height=38,
            corner_radius=19,
            fg_color=self.theme["avatar_bg"],
            text_color=self.theme["avatar_text"],
            font=("Segoe UI", 13)
        )
        self.avatar.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(12, 8),
            pady=16
        )

        self.user_name_label = ctk.CTkLabel(
            self.user_card,
            text=user_name,
            font=("Segoe UI", 12),
            text_color=self.theme["text"],
            fg_color="transparent",
            anchor="w"
        )
        self.user_name_label.grid(
            row=0,
            column=1,
            sticky="w",
            pady=(15, 0)
        )

        self.user_role_label = ctk.CTkLabel(
            self.user_card,
            text=user_role,
            font=("Segoe UI", 10),
            text_color=self.theme["text_soft"],
            fg_color="transparent",
            anchor="w"
        )
        self.user_role_label.grid(
            row=1,
            column=1,
            sticky="w",
            pady=(0, 15)
        )

    def get_initials(self, name):
        parts = name.strip().split()

        if len(parts) >= 2:
            return parts[0][0].upper() + parts[1][0].upper()

        if len(parts) == 1 and len(parts[0]) > 0:
            return parts[0][0].upper()

        return "U"

    # =====================================================
    # ÁREA DE CONTENIDO
    # =====================================================

    def create_content_area(self):
        self.content = ctk.CTkScrollableFrame(
            self.main_area,
            fg_color=self.theme["app_bg"],
            corner_radius=0
        )
        self.content.grid(row=0, column=0, sticky="nsew")

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_columnconfigure(2, weight=1)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # =====================================================
    # HOME CONTENT
    # =====================================================

    def show_home_content(self):
        self.clear_content()

        user_name = "Usuario"

        if self.current_user:
            user_name = self.current_user.get("nombre", "Usuario")

        header = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        header.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=35,
            pady=(30, 15)
        )
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)
        header.grid_columnconfigure(2, weight=0)

        title_box = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )
        title_box.grid(
            row=0,
            column=0,
            sticky="w"
        )

        title = ctk.CTkLabel(
            title_box,
            text="Inicio",
            font=("Segoe UI", 34),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_box,
            text="Tu bienestar, tu momento, tu equilibrio.",
            font=("Segoe UI", 15),
            text_color=self.theme["text_soft"],
            fg_color="transparent"
        )
        subtitle.pack(anchor="w")

        greeting = ctk.CTkLabel(
            header,
            text=f"Hola, {user_name}",
            font=("Segoe UI", 15),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        greeting.grid(
            row=0,
            column=1,
            padx=(10, 10),
            sticky="e"
        )

        logout_button = ctk.CTkButton(
            header,
            text="Cerrar sesión",
            width=120,
            height=32,
            corner_radius=12,
            fg_color=self.theme["card_bg"],
            hover_color=self.theme["menu_hover"],
            border_width=1,
            border_color=self.theme["card_border"],
            text_color=self.theme["text"],
            command=self.logout
        )
        logout_button.grid(
            row=0,
            column=2,
            sticky="e"
        )

        self.create_welcome_card(row=1, column=0)
        self.create_status_card(row=1, column=2)

        actions_title = ctk.CTkLabel(
            self.content,
            text="Acciones rápidas",
            font=("Segoe UI", 16),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        actions_title.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="w",
            padx=35,
            pady=(25, 10)
        )

        self.create_action_card(
            row=3,
            column=0,
            title="Iniciar Modo Calma",
            description="Relaja tu mente y reduce la tensión.",
            command=lambda: self.show_placeholder("Modo Calma", "Pausa guiada para recuperar equilibrio.")
        )

        self.create_action_card(
            row=3,
            column=1,
            title="Respiración guiada",
            description="Ejercicios para respirar y centrarte.",
            command=lambda: self.show_placeholder("Respiración", "Ejercicios para respirar y centrarte.")
        )

        self.create_action_card(
            row=3,
            column=2,
            title="Pausa breve",
            description="Tómate 5 minutos para ti.",
            command=lambda: self.show_placeholder("Microdescansos", "Pausas breves y actividades de baja carga cognitiva.")
        )

        self.create_recommended_card(row=4, column=0)
        self.create_recent_card(row=4, column=1)
        self.create_quote_card(row=4, column=2)

    # =====================================================
    # CARDS
    # =====================================================

    def create_welcome_card(self, row, column):
        card = ctk.CTkFrame(
            self.content,
            height=220,
            corner_radius=18,
            **self.card_style()
        )
        card.grid(
            row=row,
            column=column,
            columnspan=2,
            sticky="nsew",
            padx=(35, 15),
            pady=10
        )
        card.grid_propagate(False)

        label = ctk.CTkLabel(
            card,
            text="Bienvenido a",
            font=("Segoe UI", 20),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        label.pack(anchor="w", padx=30, pady=(30, 0))

        title = ctk.CTkLabel(
            card,
            text="SoftRelief",
            font=("Segoe UI Light", 42),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        title.pack(anchor="w", padx=30)

        text = ctk.CTkLabel(
            card,
            text="Herramientas simples para cuidar tu mente,\n"
                 "realizar pausas y recuperar enfoque durante el día.",
            font=("Segoe UI", 15),
            text_color=self.theme["text_soft"],
            justify="left",
            fg_color="transparent"
        )
        text.pack(anchor="w", padx=30, pady=(15, 0))

    def create_status_card(self, row, column):
        card = ctk.CTkFrame(
            self.content,
            height=220,
            corner_radius=18,
            **self.card_style()
        )
        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=(15, 35),
            pady=10
        )
        card.grid_propagate(False)

        title = ctk.CTkLabel(
            card,
            text="Tu estado de hoy",
            font=("Segoe UI", 20),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        title.pack(anchor="w", padx=25, pady=(20, 0))

        subtitle = ctk.CTkLabel(
            card,
            text="Actualizado ahora",
            font=("Segoe UI", 12),
            text_color=self.theme["text_soft"],
            fg_color="transparent"
        )
        subtitle.pack(anchor="w", padx=25)

        info_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        info_frame.pack(
            expand=True,
            fill="both",
            padx=25,
            pady=20
        )
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)

        stress = ctk.CTkLabel(
            info_frame,
            text="Estrés\n4/10\nModerado",
            font=("Segoe UI", 18),
            justify="center",
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        stress.grid(row=0, column=0, sticky="nsew")

        energy = ctk.CTkLabel(
            info_frame,
            text="Energía\n7/10\nBuena",
            font=("Segoe UI", 18),
            justify="center",
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        energy.grid(row=0, column=1, sticky="nsew")

    def create_action_card(self, row, column, title, description, command):
        card = ctk.CTkFrame(
            self.content,
            height=95,
            corner_radius=18,
            **self.card_style()
        )
        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=self.get_column_padding(column),
            pady=10
        )
        card.grid_propagate(False)

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)

        text_box = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        text_box.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=20,
            pady=15
        )

        title_label = ctk.CTkLabel(
            text_box,
            text=title,
            font=("Segoe UI", 15),
            text_color=self.theme["text"],
            fg_color="transparent",
            anchor="w"
        )
        title_label.pack(anchor="w")

        desc_label = ctk.CTkLabel(
            text_box,
            text=description,
            font=("Segoe UI", 12),
            text_color=self.theme["text_soft"],
            justify="left",
            fg_color="transparent",
            anchor="w"
        )
        desc_label.pack(anchor="w", pady=(5, 0))

        open_button = ctk.CTkButton(
            card,
            text=">",
            width=36,
            height=36,
            corner_radius=18,
            fg_color=self.theme["accent_soft"],
            hover_color=self.theme["menu_hover"],
            text_color=self.theme["accent"],
            command=command
        )
        open_button.grid(
            row=0,
            column=1,
            padx=(0, 18),
            pady=30
        )

    def create_recommended_card(self, row, column):
        self.create_info_card(
            row=row,
            column=column,
            title="Sesión recomendada",
            text="Respiración para volver al centro\n7 min · Respiración",
            button_text="Iniciar sesión",
            command=lambda: self.show_placeholder("Respiración", "Ejercicios para respirar y centrarte.")
        )

    def create_recent_card(self, row, column):
        self.create_info_card(
            row=row,
            column=column,
            title="Sesiones recientes",
            text="Respiración consciente · 5 min\n"
                 "Sonidos de lluvia · 20 min\n"
                 "Pausa breve · 5 min"
        )

    def create_quote_card(self, row, column):
        self.create_info_card(
            row=row,
            column=column,
            title="Frase para hoy",
            text="“No se trata de tener tiempo,\n"
                 "sino de tomarte el tiempo\n"
                 "para lo que te hace bien.”"
        )

    def create_info_card(self, row, column, title, text, button_text=None, command=None):
        card = ctk.CTkFrame(
            self.content,
            height=185,
            corner_radius=18,
            **self.card_style()
        )
        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=self.get_column_padding(column),
            pady=(25, 35)
        )
        card.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 16),
            text_color=self.theme["text"],
            fg_color="transparent",
            anchor="w"
        )
        title_label.pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        text_label = ctk.CTkLabel(
            card,
            text=text,
            font=("Segoe UI", 13),
            text_color=self.theme["text_soft"],
            justify="left",
            fg_color="transparent",
            anchor="w"
        )
        text_label.pack(
            anchor="w",
            padx=20
        )

        if button_text and command:
            button = ctk.CTkButton(
                card,
                text=button_text,
                width=160,
                height=34,
                corner_radius=12,
                fg_color=self.theme["button"],
                hover_color=self.theme["button_hover"],
                text_color="#FFFFFF",
                command=command
            )
            button.pack(
                anchor="w",
                padx=20,
                pady=(20, 0)
            )

    def get_column_padding(self, column):
        if column == 0:
            return (35, 10)
        if column == 1:
            return (10, 10)
        return (10, 35)

    # =====================================================
    # SETTINGS Y SUPERUSER
    # =====================================================

    def show_settings(self):
        self.clear_content()
        SettingsView(self.content, self.app)

    def show_superuser_panel(self):
        self.clear_content()
        SuperuserView(self.content, self.app)

    # =====================================================
    # PLACEHOLDERS
    # =====================================================

    def show_placeholder(self, title, subtitle):
        self.clear_content()

        header = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        header.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=35,
            pady=(30, 20)
        )

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=("Segoe UI", 34),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header,
            text=subtitle,
            font=("Segoe UI", 15),
            text_color=self.theme["text_soft"],
            fg_color="transparent"
        )
        subtitle_label.pack(anchor="w")

        card = ctk.CTkFrame(
            self.content,
            height=400,
            corner_radius=20,
            **self.card_style()
        )
        card.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="nsew",
            padx=35,
            pady=10
        )
        card.grid_propagate(False)

        text = ctk.CTkLabel(
            card,
            text=f"Pantalla '{title}' pendiente de implementar.\n\n"
                 "Aquí se cargarán los componentes finales,\n"
                 "gráficos, animaciones y lógica correspondiente.",
            font=("Segoe UI", 20),
            text_color=self.theme["text"],
            justify="center",
            fg_color="transparent"
        )
        text.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        back_button = ctk.CTkButton(
            self.content,
            text="Volver a Inicio",
            width=160,
            height=38,
            corner_radius=12,
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            command=self.show_home_content
        )
        back_button.grid(
            row=2,
            column=0,
            sticky="w",
            padx=35,
            pady=20
        )

    # =====================================================
    # SESIÓN
    # =====================================================

    def logout(self):
        if self.app.current_user:
            theme = self.app.current_user.get("tema_visual", "light")
            self.app.login_theme = theme
            AppState.save_last_theme(theme)

        self.app.current_user = None
        self.app.show_login()