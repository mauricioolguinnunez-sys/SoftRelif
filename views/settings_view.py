import customtkinter as ctk
from tkinter import messagebox

from controllers.user_controller import UserController
from components import TitleLabel, SubtitleLabel, SmallLabel
from components.settings_components import (
    ThemeOptionCard,
    PersistenceCard,
    AccountSummaryCard,
    DangerAccountCard,
    VisualPreviewCard,
)

from utils.theme_manager import ThemeManager
from utils.app_state import AppState


class SettingsView(ctk.CTkFrame):
    """
    Vista de Configuración de SoftRelief.

    RF relacionados:
    - RF-017. Configurar visualización.
    - RF-018. Guardar persistencia del tema por cuenta.

    Funciones:
    - Cambiar tema claro/oscuro.
    - Guardar tema en el usuario actual.
    - Guardar último tema en AppState.
    - Solicitar eliminación de cuenta.
    """

    def __init__(self, master, app=None):
        self.app = app
        self.user = getattr(app, "current_user", None)

        self.theme_name = self.get_current_theme()
        self.theme = ThemeManager.get_theme(self.theme_name)

        super().__init__(
            master,
            fg_color=self.theme.get("app_bg", "#F6F7FB"),
            corner_radius=0
        )

        self.selected_theme = self.theme_name
        self.persist_theme = True

        self.light_card = None
        self.dark_card = None
        self.message_label = None

        self.pack(fill="both", expand=True)

        self.build_view()

    # =====================================================
    # HELPERS
    # =====================================================

    def get_current_theme(self):
        if self.user:
            return self.user.get("tema_visual", "light")

        return AppState.load_last_theme()

    def get_user_name(self):
        if self.user:
            return self.user.get("nombre", "Usuario")

        return "Usuario"

    def get_user_role(self):
        if self.user:
            return self.user.get("rol", "usuario")

        return "Cuenta local"

    # =====================================================
    # BUILD
    # =====================================================

    def build_view(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_header()
        self.build_left_content()
        self.build_right_content()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=30,
            pady=(26, 18)
        )

        header.grid_columnconfigure(0, weight=0)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=0)

        icon = ctk.CTkLabel(
            header,
            text="⚙",
            width=74,
            height=74,
            corner_radius=37,
            fg_color=self.theme.get("accent_soft", "#EDE9FE"),
            text_color=self.theme.get("accent", "#7C3AED"),
            font=("Arial", 34)
        )
        icon.grid(row=0, column=0, padx=(0, 20))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=1, sticky="w")

        TitleLabel(
            title_box,
            "Configuración",
            size=34,
            text_color=self.theme.get("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title_box,
            "Personaliza tu experiencia",
            size=16,
            text_color=self.theme.get("text_soft", "#6B7280")
        ).pack(anchor="w")

        user_box = ctk.CTkFrame(header, fg_color="transparent")
        user_box.grid(row=0, column=2, sticky="e")

        SmallLabel(
            user_box,
            f"Hola, {self.get_user_name()}",
            size=14,
            text_color=self.theme.get("text", "#1E1B4B")
        ).pack(anchor="e")

        SmallLabel(
            user_box,
            self.get_user_role(),
            size=12,
            text_color=self.theme.get("text_soft", "#6B7280")
        ).pack(anchor="e")

    def build_left_content(self):
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(30, 15),
            pady=(0, 30)
        )

        left.grid_columnconfigure(0, weight=1)
        left.grid_columnconfigure(1, weight=1)

        self.light_card = ThemeOptionCard(
            left,
            theme=self.theme,
            title="Claro",
            subtitle="Interfaz luminosa y suave.",
            mode="light",
            selected=self.selected_theme == "light",
            command=self.change_theme
        )
        self.light_card.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 10),
            pady=(0, 18)
        )

        self.dark_card = ThemeOptionCard(
            left,
            theme=self.theme,
            title="Oscuro",
            subtitle="Interfaz cómoda en baja luz.",
            mode="dark",
            selected=self.selected_theme == "dark",
            command=self.change_theme
        )
        self.dark_card.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(10, 0),
            pady=(0, 18)
        )

        PersistenceCard(
            left,
            theme=self.theme,
            enabled=True,
            command=self.set_persistence
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 18)
        )

        DangerAccountCard(
            left,
            theme=self.theme,
            command=self.confirm_delete_account
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 18)
        )

        self.message_label = SmallLabel(
            left,
            "",
            text_color=self.theme.get("text_soft", "#6B7280")
        )
        self.message_label.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(4, 0)
        )

    def build_right_content(self):
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(15, 30),
            pady=(0, 30)
        )

        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        AccountSummaryCard(
            right,
            theme=self.theme,
            user=self.user
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        VisualPreviewCard(
            right,
            theme=self.theme
        ).grid(
            row=1,
            column=0,
            sticky="nsew"
        )

    # =====================================================
    # CAMBIO DE TEMA
    # =====================================================

    def change_theme(self, theme):
        """
        Cambia el tema visual del usuario y reconstruye HomeView.

        Backend usado:
        UserController.update_theme(current_user, theme)
        """

        if theme not in ["light", "dark"]:
            self.show_message("Tema no válido.", error=True)
            return

        if not self.user:
            self.show_message("No hay usuario activo para actualizar el tema.", error=True)
            return

        result = UserController.update_theme(self.user, theme)

        if not result.get("success"):
            self.show_message(result.get("message", "No se pudo actualizar el tema."), error=True)
            return

        self.selected_theme = theme
        self.user["tema_visual"] = theme

        if self.app:
            self.app.current_user = self.user
            self.app.login_theme = theme

        if self.persist_theme:
            AppState.save_last_theme(theme)

        ThemeManager.apply_mode(theme)

        self.show_message("Tema actualizado correctamente.")

        if self.light_card:
            self.light_card.set_selected(theme == "light")

        if self.dark_card:
            self.dark_card.set_selected(theme == "dark")

        # Reconstruye toda la interfaz para que sidebar, cards y colores cambien.
        if self.app:
            self.after(250, self.app.show_home)

    def set_persistence(self, enabled):
        self.persist_theme = enabled

        if enabled:
            AppState.save_last_theme(self.selected_theme)
            self.show_message("Persistencia del tema activada.")
        else:
            self.show_message("Persistencia del tema desactivada.")

    # =====================================================
    # ELIMINAR CUENTA
    # =====================================================

    def confirm_delete_account(self):
        if not self.user:
            self.show_message("No hay usuario activo.", error=True)
            return

        if self.user.get("rol") == "superuser":
            messagebox.showwarning(
                "Cuenta protegida",
                "La cuenta superuser no se puede eliminar."
            )
            return

        confirm = messagebox.askyesno(
            "Eliminar cuenta",
            "¿Seguro que deseas solicitar la eliminación de esta cuenta?\n\n"
            "Esta acción eliminará tu cuenta de forma permanente."
        )

        if confirm:
            self.delete_account()

    def delete_account(self):
        """
        Elimina la cuenta propia usando el backend original:
        UserController.delete_own_account(current_user)
        """

        result = UserController.delete_own_account(self.user)

        if result.get("success"):
            messagebox.showinfo(
                "Cuenta eliminada",
                "La cuenta fue eliminada correctamente."
            )

            if self.app:
                self.app.current_user = None
                self.app.login_theme = "light"

            AppState.save_last_theme("light")
            ThemeManager.apply_mode("light")

            if self.app:
                self.app.show_login()

        else:
            self.show_message(
                result.get("message", "No se pudo eliminar la cuenta."),
                error=True
            )

    # =====================================================
    # MENSAJES
    # =====================================================

    def show_message(self, text, error=False):
        if self.message_label:
            self.message_label.configure(
                text=text,
                text_color=self.theme.get("danger", "#DC2626")
                if error
                else self.theme.get("text_soft", "#6B7280")
            )