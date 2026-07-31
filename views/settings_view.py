import customtkinter as ctk
from tkinter import messagebox

from controllers.user_controller import UserController

from components import (
    TitleLabel,
    SubtitleLabel,
    SmallLabel,
    BodyLabel,
    PrimaryButton,
    SecondaryButton,
)

from components.settings_components import (
    ThemeOptionCard,
    PersistenceCard,
    AccountSummaryCard,
    DangerAccountCard,
    VisualPreviewCard,
)

from utils.theme_manager import ThemeManager
from utils.app_state import AppState
from utils.i18n import Lang


class SettingsView(ctk.CTkFrame):
    """
    Vista de Configuración de SoftRelief.

    Mantiene la visualización original:
    - Header con ícono.
    - Opciones visuales a la izquierda.
    - Resumen de cuenta y preview a la derecha.

    Agregado:
    - Opción "Cambiar datos de cuenta".
    - Subvista interna en el mismo archivo para cambiar:
        - nombre visible
        - nombre de usuario, solo si existe columna usuario
        - correo
        - contraseña
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

        Lang.set(AppState.load_language())

        self.selected_theme = self.theme_name
        self.persist_theme = True

        self.light_card = None
        self.dark_card = None
        self.message_label = None

        self.nombre_entry = None
        self.usuario_entry = None
        self.correo_entry = None

        self.password_actual_entry = None
        self.password_nueva_entry = None
        self.password_confirmar_entry = None

        self.username_supported = False
        self.username_note = None

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

    def get_user_email(self):
        if self.user:
            return self.user.get("correo", "Sin correo")

        return "Sin correo"

    def clear_view(self):
        for widget in self.winfo_children():
            widget.destroy()

    def c(self, key, default):
        return self.theme.get(key, default)

    def create_entry(self, parent, placeholder, show=None):
        return ctk.CTkEntry(
            parent,
            height=38,
            corner_radius=12,
            placeholder_text=placeholder,
            show=show,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_color=self.c("card_border", "#E5E7EB"),
            text_color=self.c("text", "#1E1B4B")
        )

    def create_field_label(self, parent, text, row):
        SmallLabel(
            parent,
            text,
            size=12,
            text_color=self.c("text_soft", "#6B7280")
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=22,
            pady=(8, 4)
        )

    # =====================================================
    # MAIN VIEW
    # =====================================================

    def build_view(self):
        self.clear_view()

        self.configure(
            fg_color=self.theme.get("app_bg", "#F6F7FB")
        )

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
            Lang.get("settings_title"),
            size=34,
            text_color=self.theme.get("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title_box,
            Lang.get("settings_subtitle"),
            size=16,
            text_color=self.theme.get("text_soft", "#6B7280")
        ).pack(anchor="w")

        user_box = ctk.CTkFrame(header, fg_color="transparent")
        user_box.grid(row=0, column=2, sticky="e")

        SmallLabel(
            user_box,
            Lang.get("settings_hello", name=self.get_user_name()),
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
            title=Lang.get("settings_light"),
            subtitle=Lang.get("settings_light_desc"),
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
            title=Lang.get("settings_dark"),
            subtitle=Lang.get("settings_dark_desc"),
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

        self.build_account_options_card(left).grid(
            row=2,
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
            row=3,
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
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(4, 0)
        )

    def build_account_options_card(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme.get("card_bg", "#FFFFFF"),
            corner_radius=22,
            border_width=1,
            border_color=self.theme.get("card_border", "#E5E7EB")
        )

        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(2, weight=0)

        icon = ctk.CTkLabel(
            card,
            text="👤",
            width=54,
            height=54,
            corner_radius=27,
            fg_color=self.theme.get("accent_soft", "#EDE9FE"),
            text_color=self.theme.get("accent", "#7C3AED"),
            font=("Arial", 25)
        )
        icon.grid(
            row=0,
            column=0,
            padx=(22, 16),
            pady=22
        )

        text_box = ctk.CTkFrame(card, fg_color="transparent")
        text_box.grid(
            row=0,
            column=1,
            sticky="w",
            pady=22
        )

        TitleLabel(
            text_box,
            Lang.get("settings_account_data"),
            size=19,
            text_color=self.theme.get("text", "#1E1B4B")
        ).pack(anchor="w")

        SmallLabel(
            text_box,
            Lang.get("settings_account_data_desc"),
            size=12,
            text_color=self.theme.get("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(3, 0))

        PrimaryButton(
            card,
            text=Lang.get("settings_change_data"),
            width=140,
            height=36,
            command=self.build_account_view
        ).grid(
            row=0,
            column=2,
            padx=(16, 22),
            pady=22,
            sticky="e"
        )

        return card

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
    # SUBVIEW DATOS DE CUENTA
    # =====================================================

    def build_account_view(self):
        self.clear_view()

        self.configure(
            fg_color=self.theme.get("app_bg", "#F6F7FB")
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_account_header()
        self.build_account_form()
        self.build_password_form()

        self.message_label = SmallLabel(
            self,
            "",
            text_color=self.theme.get("text_soft", "#6B7280")
        )
        self.message_label.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            padx=34,
            pady=(0, 20)
        )

        self.load_account_data()

    def build_account_header(self):
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
            text="👤",
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
            Lang.get("settings_account_title"),
            size=34,
            text_color=self.theme.get("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title_box,
            Lang.get("settings_account_subtitle"),
            size=16,
            text_color=self.theme.get("text_soft", "#6B7280")
        ).pack(anchor="w")

        SecondaryButton(
            header,
            text=Lang.get("settings_back"),
            width=120,
            height=36,
            fg_color=self.theme.get("card_bg", "#FFFFFF"),
            hover_color=self.theme.get("menu_hover", "#F3F4F6"),
            text_color=self.theme.get("text", "#1E1B4B"),
            border_width=1,
            border_color=self.theme.get("card_border", "#E5E7EB"),
            command=self.build_view
        ).grid(
            row=0,
            column=2,
            sticky="e"
        )

    def build_account_form(self):
        card = ctk.CTkFrame(
            self,
            fg_color=self.theme.get("card_bg", "#FFFFFF"),
            corner_radius=24,
            border_width=1,
            border_color=self.theme.get("card_border", "#E5E7EB")
        )
        card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(30, 15),
            pady=(0, 30)
        )

        card.grid_columnconfigure(0, weight=1)

        TitleLabel(
            card,
            Lang.get("settings_personal_info"),
            size=22,
            text_color=self.theme.get("text", "#1E1B4B")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(24, 6)
        )

        BodyLabel(
            card,
            Lang.get("settings_personal_info_desc"),
            size=13,
            text_color=self.theme.get("text_soft", "#6B7280"),
            wraplength=460
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 12)
        )

        self.create_field_label(card, Lang.get("settings_field_name"), 2)
        self.nombre_entry = self.create_entry(card, Lang.get("settings_name_placeholder"))
        self.nombre_entry.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 8)
        )

        self.create_field_label(card, Lang.get("settings_field_username"), 4)
        self.usuario_entry = self.create_entry(card, Lang.get("settings_field_username"))
        self.usuario_entry.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 4)
        )

        self.username_note = SmallLabel(
            card,
            "",
            size=11,
            text_color=self.theme.get("text_soft", "#6B7280")
        )
        self.username_note.grid(
            row=6,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 8)
        )

        self.create_field_label(card, Lang.get("settings_field_email"), 7)
        self.correo_entry = self.create_entry(card, Lang.get("settings_email_placeholder"))
        self.correo_entry.grid(
            row=8,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 16)
        )

        PrimaryButton(
            card,
            text=Lang.get("settings_save_data"),
            height=38,
            command=self.save_account_data
        ).grid(
            row=9,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 24)
        )

    def build_password_form(self):
        card = ctk.CTkFrame(
            self,
            fg_color=self.theme.get("card_bg", "#FFFFFF"),
            corner_radius=24,
            border_width=1,
            border_color=self.theme.get("card_border", "#E5E7EB")
        )
        card.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(15, 30),
            pady=(0, 30)
        )

        card.grid_columnconfigure(0, weight=1)

        TitleLabel(
            card,
            Lang.get("settings_security"),
            size=22,
            text_color=self.theme.get("text", "#1E1B4B")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(24, 6)
        )

        BodyLabel(
            card,
            Lang.get("settings_security_desc"),
            size=13,
            text_color=self.theme.get("text_soft", "#6B7280"),
            wraplength=460
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 12)
        )

        self.create_field_label(card, Lang.get("settings_current_password"), 2)
        self.password_actual_entry = self.create_entry(
            card,
            Lang.get("settings_current_password"),
            show="*"
        )
        self.password_actual_entry.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 8)
        )

        self.create_field_label(card, Lang.get("settings_new_password"), 4)
        self.password_nueva_entry = self.create_entry(
            card,
            Lang.get("settings_new_password"),
            show="*"
        )
        self.password_nueva_entry.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 8)
        )

        self.create_field_label(card, Lang.get("settings_confirm_password"), 6)
        self.password_confirmar_entry = self.create_entry(
            card,
            Lang.get("settings_confirm_password"),
            show="*"
        )
        self.password_confirmar_entry.grid(
            row=7,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 16)
        )

        PrimaryButton(
            card,
            text=Lang.get("settings_change_password"),
            height=38,
            command=self.change_password
        ).grid(
            row=8,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 24)
        )

    # =====================================================
    # CAMBIO DE TEMA
    # =====================================================

    def change_theme(self, theme):
        if theme not in ["light", "dark"]:
            self.show_message(Lang.get("settings_no_theme"), error=True)
            return

        if not self.user:
            self.show_message(Lang.get("settings_no_user"), error=True)
            return

        result = UserController.update_theme(self.user, theme)

        if not result.get("success"):
            self.show_message(
                result.get("message", Lang.get("settings_update_error")),
                error=True
            )
            return

        self.selected_theme = theme
        self.theme_name = theme
        self.theme = ThemeManager.get_theme(theme)
        self.user["tema_visual"] = theme

        if self.app:
            self.app.current_user = self.user
            self.app.login_theme = theme

        if self.persist_theme:
            AppState.save_last_theme(theme)

        ThemeManager.apply_mode(theme)

        self.show_message(Lang.get("settings_theme_updated"))

        if self.light_card:
            self.light_card.set_selected(theme == "light")

        if self.dark_card:
            self.dark_card.set_selected(theme == "dark")

        if self.app:
            self.after(250, self.app.show_home)

    def set_persistence(self, enabled):
        self.persist_theme = enabled

        if enabled:
            AppState.save_last_theme(self.selected_theme)
            self.show_message(Lang.get("settings_persistence_on"))
        else:
            self.show_message(Lang.get("settings_persistence_off"))

    # =====================================================
    # DATOS DE CUENTA
    # =====================================================

    def load_account_data(self):
        if not hasattr(UserController, "get_account_settings"):
            self.show_message(
                "Falta UserController.get_account_settings().",
                error=True
            )
            return

        result = UserController.get_account_settings(self.user)

        if not result.get("success"):
            self.show_message(
                result.get("message", "No se pudieron cargar los datos."),
                error=True
            )
            return

        user_data = result.get("user")
        self.username_supported = result.get("username_supported", False)

        if not user_data:
            self.show_message("No se encontraron datos de cuenta.", error=True)
            return

        self.nombre_entry.delete(0, "end")
        self.nombre_entry.insert(0, user_data.get("nombre", ""))

        self.usuario_entry.configure(state="normal")
        self.usuario_entry.delete(0, "end")
        self.usuario_entry.insert(0, user_data.get("nombre_usuario", ""))

        self.correo_entry.delete(0, "end")
        self.correo_entry.insert(0, user_data.get("correo", ""))

        if self.username_supported:
            self.usuario_entry.configure(state="normal")
            self.username_note.configure(
                text=Lang.get("settings_username_note")
            )
        else:
            self.usuario_entry.configure(state="disabled")
            self.username_note.configure(
                text=Lang.get("settings_username_note_alt")
            )

    def save_account_data(self):
        if not hasattr(UserController, "update_account_settings"):
            self.show_message(
                "Falta UserController.update_account_settings().",
                error=True
            )
            return

        nombre = self.nombre_entry.get().strip()
        correo = self.correo_entry.get().strip()

        if self.username_supported:
            nombre_usuario = self.usuario_entry.get().strip()
        else:
            nombre_usuario = ""

        result = UserController.update_account_settings(
            self.user,
            nombre,
            nombre_usuario,
            correo
        )

        if not result.get("success"):
            self.show_message(
                result.get("message", "No se pudieron actualizar los datos."),
                error=True
            )
            return

        updated_user = result.get("user")

        if updated_user:
            self.user.update({
                "nombre": updated_user.get("nombre", self.user.get("nombre")),
                "correo": updated_user.get("correo", self.user.get("correo")),
                "usuario": updated_user.get("nombre_usuario", updated_user.get("correo")),
                "tema_visual": updated_user.get("tema_visual", self.user.get("tema_visual")),
                "rol": updated_user.get("rol", self.user.get("rol")),
                "estado": updated_user.get("estado", self.user.get("estado")),
            })

            if self.app:
                self.app.current_user = self.user

        self.load_account_data()
        self.show_message(Lang.get("settings_data_updated"))

    def change_password(self):
        if not hasattr(UserController, "update_password"):
            self.show_message(
                "Falta UserController.update_password().",
                error=True
            )
            return

        actual = self.password_actual_entry.get().strip()
        nueva = self.password_nueva_entry.get().strip()
        confirmar = self.password_confirmar_entry.get().strip()

        result = UserController.update_password(
            self.user,
            actual,
            nueva,
            confirmar
        )

        if not result.get("success"):
            self.show_message(
                result.get("message", "No se pudo cambiar la contraseña."),
                error=True
            )
            return

        self.password_actual_entry.delete(0, "end")
        self.password_nueva_entry.delete(0, "end")
        self.password_confirmar_entry.delete(0, "end")

        self.show_message(Lang.get("settings_password_updated"))

    # =====================================================
    # ELIMINAR CUENTA
    # =====================================================

    def confirm_delete_account(self):
        if not self.user:
            self.show_message(Lang.get("settings_no_user_active"), error=True)
            return

        if self.user.get("rol") == "superuser":
            messagebox.showwarning(
                Lang.get("settings_protected_account"),
                Lang.get("settings_protected_msg")
            )
            return

        confirm = messagebox.askyesno(
            Lang.get("settings_delete_confirm_title"),
            Lang.get("settings_delete_confirm_msg")
        )

        if confirm:
            self.delete_account()

    def delete_account(self):
        result = UserController.delete_own_account(self.user)

        if result.get("success"):
            messagebox.showinfo(
                Lang.get("settings_account_deleted_title"),
                Lang.get("settings_account_deleted_msg")
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