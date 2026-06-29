import os
import customtkinter as ctk
from PIL import Image

from components import (
    SoftCard,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    SmallLabel,
    SidebarButton,
    PrimaryButton,
    SecondaryButton,
)

from views.settings_view import SettingsView
from views.superuser_view import SuperuserView
from views.checkin_view import CheckinView

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
    """
    HomeView experimental usando components/.

    Esta versión:
    - Usa componentes reutilizables.
    - Quita Respiración como vista independiente.
    - Conecta Check-in con CheckinView.
    - Usa CTkFrame normal para evitar pantalla en blanco.
    """

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
     self.content = None

     self.create_layout()
     self.create_content_area()
     self.create_sidebar()
     self.show_home_content()
    # =====================================================
    # UTILIDADES
    # =====================================================

    def get_logo_path(self):
        if self.theme_name == "dark" and os.path.exists(DARK_LOGO_PATH):
            return DARK_LOGO_PATH

        return LOGO_PATH

    def get_user_name(self):
        if self.current_user:
            return self.current_user.get("nombre", "Usuario")

        return "Usuario"

    def get_user_role(self):
        if self.current_user:
            return self.current_user.get("rol", "usuario")

        return "Cuenta local"

    def get_initials(self, name):
        parts = name.strip().split()

        if len(parts) >= 2:
            return parts[0][0].upper() + parts[1][0].upper()

        if len(parts) == 1 and len(parts[0]) > 0:
            return parts[0][0].upper()

        return "U"

    def clear_content(self):
     if not hasattr(self, "content") or self.content is None:
        self.create_content_area()
        return

     for widget in self.content.winfo_children():
        widget.destroy()
     for widget in self.content.winfo_children():
        widget.destroy()

    def configure_content_grid(self):
       if not hasattr(self, "content") or self.content is None:
        return

       for col in range(3):
        self.content.grid_columnconfigure(col, weight=1)

       for row in range(20):
        self.content.grid_rowconfigure(row, weight=0)
    def get_column_padding(self, column):
        if column == 0:
            return (35, 10)

        if column == 1:
            return (10, 10)

        return (10, 35)

    # =====================================================
    # LAYOUT PRINCIPAL
    # =====================================================

    def create_layout(self):
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

    def create_content_area(self):
     self.content = ctk.CTkScrollableFrame(
        self.main_area,
        fg_color=self.theme["app_bg"],
        corner_radius=0,
        scrollbar_button_color=self.theme.get("accent", "#7C3AED"),
        scrollbar_button_hover_color=self.theme.get("button_hover", "#6D28D9")
    )

     self.content.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

     self.configure_content_grid()
    # =====================================================
    # SIDEBAR
    # =====================================================

    def create_sidebar(self):
        self.sidebar.grid_rowconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=0)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.create_sidebar_header()
        self.create_sidebar_menu()
        self.create_user_card()

    def create_sidebar_header(self):
        header = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=(25, 10)
        )

        self.logo_image = load_ctk_image(self.get_logo_path(), (105, 105))

        if self.logo_image:
            logo = ctk.CTkLabel(
                header,
                text="",
                image=self.logo_image,
                fg_color="transparent"
            )
        else:
            logo = ctk.CTkLabel(
                header,
                text="[ LOGO ]",
                font=("Segoe UI", 18),
                text_color=self.theme["text"],
                fg_color="transparent"
            )

        logo.pack(pady=(0, 5))

        TitleLabel(
            header,
            "SoftRelief",
            size=28,
            text_color=self.theme["text"]
        ).pack()

        SmallLabel(
            header,
            "Bienestar digital al alcance",
            text_color=self.theme["text_soft"]
        ).pack(pady=(0, 10))

    def create_sidebar_menu(self):
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
            ("Check-in", self.show_checkin),
            ("Modo Calma", self.show_calm_mode),
            ("Sonidos", self.show_sounds),
            ("Microdescansos", self.show_microbreaks),
            ("Historial", self.show_history),
            ("Configuración", self.show_settings),
        ]

        if self.current_user and self.current_user.get("rol") == "superuser":
            self.menu_items.append(("Superuser", self.show_superuser_panel))

        for text, command in self.menu_items:
            SidebarButton(
                self.menu_frame,
                text=text,
                command=command,
                width=180,
                height=38
            ).pack(fill="x", pady=4)

    def create_user_card(self):
        user_name = self.get_user_name()
        user_role = self.get_user_role()
        initials = self.get_initials(user_name)

        card = SoftCard(
            self.sidebar,
            height=75,
            corner_radius=16,
            fg_color=self.theme["user_card"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        card.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=15,
            pady=(10, 20)
        )
        card.grid_propagate(False)

        avatar = ctk.CTkLabel(
            card,
            text=initials,
            width=38,
            height=38,
            corner_radius=19,
            fg_color=self.theme["avatar_bg"],
            text_color=self.theme["avatar_text"],
            font=("Segoe UI", 13)
        )
        avatar.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(12, 8),
            pady=16
        )

        user_label = ctk.CTkLabel(
            card,
            text=user_name,
            font=("Segoe UI", 12),
            text_color=self.theme["text"],
            fg_color="transparent",
            anchor="w"
        )
        user_label.grid(
            row=0,
            column=1,
            sticky="w",
            pady=(15, 0)
        )

        role_label = ctk.CTkLabel(
            card,
            text=user_role,
            font=("Segoe UI", 10),
            text_color=self.theme["text_soft"],
            fg_color="transparent",
            anchor="w"
        )
        role_label.grid(
            row=1,
            column=1,
            sticky="w",
            pady=(0, 15)
        )

    # =====================================================
    # HOME
    # =====================================================

    def show_home_content(self):
        self.clear_content()
        self.configure_content_grid()

        self.create_home_header()
        self.create_home_top_cards()
        self.create_quick_actions()
        self.create_bottom_cards()

    def create_home_header(self):
        header = SoftCard(
            self.content,
            height=120,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        header.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=35,
            pady=(30, 15)
        )
        header.grid_propagate(False)

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
            sticky="w",
            padx=28,
            pady=18
        )

        TitleLabel(
            title_box,
            "Inicio",
            size=34,
            text_color=self.theme["text"]
        ).pack(anchor="w")

        SubtitleLabel(
            title_box,
            "Tu bienestar, tu momento, tu equilibrio.",
            size=15,
            text_color=self.theme["text_soft"]
        ).pack(anchor="w")

        SmallLabel(
            header,
            f"Hola, {self.get_user_name()}",
            size=14,
            text_color=self.theme["text"]
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=(10, 10)
        )

        SecondaryButton(
            header,
            text="Cerrar sesión",
            width=120,
            height=32,
            fg_color=self.theme["card_bg"],
            hover_color=self.theme["menu_hover"],
            text_color=self.theme["text"],
            border_width=1,
            border_color=self.theme["card_border"],
            command=self.logout
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=(0, 25)
        )

    def create_home_top_cards(self):
        welcome_card = SoftCard(
            self.content,
            height=220,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        welcome_card.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=(35, 15),
            pady=10
        )
        welcome_card.grid_propagate(False)

        SubtitleLabel(
            welcome_card,
            "Bienvenido a",
            size=20,
            text_color=self.theme["text"]
        ).pack(anchor="w", padx=30, pady=(30, 0))

        TitleLabel(
            welcome_card,
            "SoftRelief",
            size=42,
            text_color=self.theme["text"]
        ).pack(anchor="w", padx=30)

        BodyLabel(
            welcome_card,
            "Herramientas simples para cuidar tu mente,\n"
            "realizar pausas y recuperar enfoque durante el día.",
            size=15,
            text_color=self.theme["text_soft"],
            wraplength=580
        ).pack(anchor="w", padx=30, pady=(15, 0))

        status_card = SoftCard(
            self.content,
            height=220,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        status_card.grid(
            row=1,
            column=2,
            sticky="nsew",
            padx=(15, 35),
            pady=10
        )
        status_card.grid_propagate(False)

        TitleLabel(
            status_card,
            "Tu estado de hoy",
            size=20,
            text_color=self.theme["text"]
        ).pack(anchor="w", padx=25, pady=(25, 5))

        last_checkin = getattr(self.app, "last_checkin", None)

        if last_checkin:
            status_text = (
                f"Estrés: {last_checkin.get('stress', '-')}/10\n"
                f"Energía: {last_checkin.get('energy', '-')}/10\n"
                f"Ánimo: {last_checkin.get('mood', '-')}"
            )
        else:
            status_text = "Sin check-in registrado"

        BodyLabel(
            status_card,
            status_text,
            size=15,
            text_color=self.theme["text_soft"],
            wraplength=260
        ).pack(anchor="w", padx=25, pady=(10, 20))

        PrimaryButton(
            status_card,
            text="Realizar Check-in",
            width=180,
            height=36,
            command=self.show_checkin
        ).pack(anchor="w", padx=25)

    def create_quick_actions(self):
        TitleLabel(
            self.content,
            "Acciones rápidas",
            size=18,
            text_color=self.theme["text"]
        ).grid(
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
            title="Modo Calma",
            description="Relaja tu mente y reduce la tensión.",
            command=self.show_calm_mode
        )

        self.create_action_card(
            row=3,
            column=1,
            title="Check-in",
            description="Registra cómo te sientes hoy.",
            command=self.show_checkin
        )

        self.create_action_card(
            row=3,
            column=2,
            title="Microdescanso",
            description="Tómate una pausa breve.",
            command=self.show_microbreaks
        )

    def create_action_card(self, row, column, title, description, command):
        card = SoftCard(
            self.content,
            height=95,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
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

        TitleLabel(
            text_box,
            title,
            size=15,
            text_color=self.theme["text"]
        ).pack(anchor="w")

        SmallLabel(
            text_box,
            description,
            size=12,
            text_color=self.theme["text_soft"]
        ).pack(anchor="w", pady=(5, 0))

        SecondaryButton(
            card,
            text=">",
            width=36,
            height=36,
            corner_radius=18,
            fg_color=self.theme["accent_soft"],
            hover_color=self.theme["menu_hover"],
            text_color=self.theme["accent"],
            command=command
        ).grid(
            row=0,
            column=1,
            padx=(0, 18),
            pady=30
        )

    def create_bottom_cards(self):
        self.create_info_card(
            row=4,
            column=0,
            title="Sesión recomendada",
            text="Modo Calma con respiración suave\n7 min · Pausa guiada",
            button_text="Iniciar sesión",
            command=self.show_calm_mode
        )

        self.create_info_card(
            row=4,
            column=1,
            title="Sesiones recientes",
            text="Modo Calma · 5 min\n"
                 "Sonidos de lluvia · 20 min\n"
                 "Pausa breve · 5 min"
        )

        last_checkin = getattr(self.app, "last_checkin", None)

        if last_checkin and last_checkin.get("phrase"):
            quote_text = f"“{last_checkin.get('phrase')}”"
        else:
            quote_text = (
                "“No se trata de tener tiempo,\n"
                "sino de tomarte el tiempo\n"
                "para lo que te hace bien.”"
            )

        self.create_info_card(
            row=4,
            column=2,
            title="Frase para hoy",
            text=quote_text
        )

    def create_info_card(self, row, column, title, text, button_text=None, command=None):
        card = SoftCard(
            self.content,
            height=185,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=self.get_column_padding(column),
            pady=(25, 35)
        )
        card.grid_propagate(False)

        TitleLabel(
            card,
            title,
            size=16,
            text_color=self.theme["text"]
        ).pack(anchor="w", padx=20, pady=(18, 10))

        BodyLabel(
            card,
            text,
            size=13,
            text_color=self.theme["text_soft"],
            wraplength=280
        ).pack(anchor="w", padx=20)

        if button_text and command:
            PrimaryButton(
                card,
                text=button_text,
                width=160,
                height=34,
                command=command
            ).pack(anchor="w", padx=20, pady=(20, 0))

    # =====================================================
    # VISTAS INTERNAS
    # =====================================================

    def show_checkin(self):
        print("Abriendo Check-in experimental")
        self.clear_content()
        self.configure_content_grid()

        try:
            view = CheckinView(
                master=self.content,
                app=self.app,
                user=self.current_user
            )

            if not view.winfo_manager():
                view.grid(
                    row=0,
                    column=0,
                    columnspan=3,
                    sticky="nsew",
                    padx=35,
                    pady=30
                )

        except Exception as error:
            self.show_error_screen(
                "Error al abrir Check-in",
                str(error)
            )

    def show_settings(self):
        self.clear_content()
        self.configure_content_grid()

        try:
            view = SettingsView(self.content, self.app)

            if hasattr(view, "winfo_manager") and not view.winfo_manager():
                view.grid(
                    row=0,
                    column=0,
                    columnspan=3,
                    sticky="nsew",
                    padx=35,
                    pady=30
                )

        except Exception as error:
            self.show_error_screen(
                "Error al abrir Configuración",
                str(error)
            )

    def show_superuser_panel(self):
        self.clear_content()
        self.configure_content_grid()

        try:
            view = SuperuserView(self.content, self.app)

            if hasattr(view, "winfo_manager") and not view.winfo_manager():
                view.grid(
                    row=0,
                    column=0,
                    columnspan=3,
                    sticky="nsew",
                    padx=35,
                    pady=30
                )

        except Exception as error:
            self.show_error_screen(
                "Error al abrir Superuser",
                str(error)
            )

    def show_calm_mode(self):
        self.show_placeholder(
            "Modo Calma",
            "Pausa guiada para recuperar equilibrio. La respiración guiada forma parte de este módulo."
        )

    def show_sounds(self):
        self.show_placeholder(
            "Sonidos",
            "Ambientes sonoros para concentración y relajación."
        )

    def show_microbreaks(self):
        self.clear_content()
        self.configure_content_grid()
        from views.microbreaks_view import MicrobreaksView
        view = MicrobreaksView(
            master = self.content,
            app = self.app,
            user = self.current_user
        )
        view.grid(
            row = 0,
            column= 0,
            columnspan = 3,
            sticky = "nsnew"
        )

    def show_history(self):
        self.clear_content()
        self.configure_content_grid()

        from views.history_view import HistoryView

        view = HistoryView(
        master=self.content,
        app=self.app,
        user=self.current_user
        )

        view.grid(
        row=0,
        column=0,
        columnspan=3,
        sticky="nsew"
    )

    # =====================================================
    # PLACEHOLDERS Y ERRORES
    # =====================================================

    def show_placeholder(self, title, subtitle):
        self.clear_content()
        self.configure_content_grid()

        header = SoftCard(
            self.content,
            height=120,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        header.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=35,
            pady=(30, 20)
        )
        header.grid_propagate(False)

        TitleLabel(
            header,
            title,
            size=34,
            text_color=self.theme["text"]
        ).pack(anchor="w", padx=28, pady=(18, 0))

        SubtitleLabel(
            header,
            subtitle,
            size=15,
            text_color=self.theme["text_soft"]
        ).pack(anchor="w", padx=28)

        card = SoftCard(
            self.content,
            height=400,
            corner_radius=20,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
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

        BodyLabel(
            card,
            f"Pantalla '{title}' pendiente de implementar.\n\n"
            "Aquí se cargarán los componentes finales,\n"
            "gráficos, animaciones y lógica correspondiente.",
            size=20,
            text_color=self.theme["text"],
            wraplength=520,
            justify="center"
        ).place(relx=0.5, rely=0.5, anchor="center")

        PrimaryButton(
            self.content,
            text="Volver a Inicio",
            width=160,
            height=38,
            command=self.show_home_content
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=35,
            pady=20
        )

    def show_error_screen(self, title, error):
        self.clear_content()
        self.configure_content_grid()

        card = SoftCard(
            self.content,
            height=320,
            corner_radius=20,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        card.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="nsew",
            padx=35,
            pady=35
        )
        card.grid_propagate(False)

        TitleLabel(
            card,
            title,
            size=24,
            text_color="#DC2626"
        ).pack(anchor="w", padx=25, pady=(25, 10))

        BodyLabel(
            card,
            error,
            size=14,
            text_color=self.theme["text"],
            wraplength=760
        ).pack(anchor="w", padx=25, pady=10)

        PrimaryButton(
            card,
            text="Volver a Inicio",
            width=160,
            command=self.show_home_content
        ).pack(anchor="w", padx=25, pady=20)

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