import customtkinter as ctk

from controllers.user_controller import UserController
from utils.theme_manager import ThemeManager
from utils.app_state import AppState


class SettingsView(ctk.CTkFrame):

    def __init__(self, master, app):
        self.app = app
        self.current_user = app.current_user
        self.theme_name = self.current_user.get("tema_visual", "light")
        self.theme = ThemeManager.get_theme(self.theme_name)

        super().__init__(
            master,
            corner_radius=0,
            fg_color=self.theme["app_bg"]
        )

        self.pack(fill="both", expand=True)

        self.create_widgets()

    # =====================================================
    # WIDGETS
    # =====================================================

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=35,
            pady=(30, 20)
        )

        self.title = ctk.CTkLabel(
            self.header,
            text="Configuración",
            font=("Segoe UI", 34),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        self.title.pack(anchor="w")

        self.subtitle = ctk.CTkLabel(
            self.header,
            text="Personaliza tu experiencia y administra tu cuenta.",
            font=("Segoe UI", 15),
            text_color=self.theme["text_soft"],
            fg_color="transparent"
        )
        self.subtitle.pack(anchor="w")

        self.create_theme_card()
        self.create_account_card()

        self.message_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 14),
            text_color=self.theme["text_soft"],
            fg_color="transparent"
        )
        self.message_label.grid(
            row=3,
            column=0,
            sticky="w",
            padx=35,
            pady=10
        )

    def create_theme_card(self):
        self.theme_card = ctk.CTkFrame(
            self,
            height=190,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        self.theme_card.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=35,
            pady=10
        )
        self.theme_card.grid_propagate(False)
        self.theme_card.grid_columnconfigure(0, weight=1)

        self.theme_title = ctk.CTkLabel(
            self.theme_card,
            text="Apariencia",
            font=("Segoe UI", 22),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        self.theme_title.place(x=25, y=20)

        self.theme_description = ctk.CTkLabel(
            self.theme_card,
            text="Elige cómo quieres visualizar SoftRelief.",
            font=("Segoe UI", 14),
            text_color=self.theme["text_soft"],
            fg_color="transparent"
        )
        self.theme_description.place(x=25, y=58)

        current_theme_text = (
            "Modo actual: oscuro"
            if self.theme_name == "dark"
            else "Modo actual: normal"
        )

        self.current_theme_label = ctk.CTkLabel(
            self.theme_card,
            text=current_theme_text,
            font=("Segoe UI", 13),
            text_color=self.theme["text_soft"],
            fg_color="transparent"
        )
        self.current_theme_label.place(x=25, y=95)

        self.visual_note = ctk.CTkLabel(
            self.theme_card,
            text="El modo oscuro utiliza la estética blueprint darkmode de SoftRelief.",
            font=("Segoe UI", 12),
            text_color=self.theme["text_soft"],
            fg_color="transparent"
        )
        self.visual_note.place(x=25, y=125)

        self.light_button = ctk.CTkButton(
            self.theme_card,
            text="Modo normal",
            width=160,
            height=38,
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            command=lambda: self.change_theme("light")
        )
        self.light_button.place(relx=0.62, y=75, anchor="center")

        self.dark_button = ctk.CTkButton(
            self.theme_card,
            text="Modo oscuro",
            width=160,
            height=38,
            fg_color="#17243A" if self.theme_name == "light" else "#3A5FBC",
            hover_color="#243654",
            text_color="#FFFFFF",
            command=lambda: self.change_theme("dark")
        )
        self.dark_button.place(relx=0.82, y=75, anchor="center")

    def create_account_card(self):
        self.account_card = ctk.CTkFrame(
            self,
            height=210,
            corner_radius=18,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
        )
        self.account_card.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=35,
            pady=20
        )
        self.account_card.grid_propagate(False)

        self.account_title = ctk.CTkLabel(
            self.account_card,
            text="Cuenta",
            font=("Segoe UI", 22),
            text_color=self.theme["text"],
            fg_color="transparent"
        )
        self.account_title.place(x=25, y=20)

        self.account_info = ctk.CTkLabel(
            self.account_card,
            text=(
                f"Usuario actual: {self.current_user['usuario']}\n"
                f"Nombre: {self.current_user['nombre']}\n"
                f"Rol: {self.current_user['rol']}"
            ),
            font=("Segoe UI", 14),
            text_color=self.theme["text_soft"],
            justify="left",
            fg_color="transparent"
        )
        self.account_info.place(x=25, y=65)

        self.delete_account_button = ctk.CTkButton(
            self.account_card,
            text="Eliminar mi cuenta",
            width=190,
            height=40,
            fg_color=self.theme["danger"],
            hover_color=self.theme["danger_hover"],
            text_color="#FFFFFF",
            command=self.confirm_delete_account
        )
        self.delete_account_button.place(relx=0.78, y=95, anchor="center")

        if self.current_user["rol"] == "superuser":
            self.delete_account_button.configure(
                state="disabled",
                text="Superuser protegido"
            )

    # =====================================================
    # CAMBIO DE TEMA
    # =====================================================

    def change_theme(self, theme):
        result = UserController.update_theme(self.current_user, theme)

        if result["success"]:
            self.current_user["tema_visual"] = theme
            self.app.login_theme = theme
            AppState.save_last_theme(theme)
            ThemeManager.apply_mode(theme)
            self.app.show_home()
        else:
            self.message_label.configure(
                text=result["message"],
                text_color=self.theme["danger"]
            )

    # =====================================================
    # ELIMINAR CUENTA
    # =====================================================

    def confirm_delete_account(self):
        confirm_window = ctk.CTkToplevel(self)
        confirm_window.title("Confirmar eliminación")
        confirm_window.geometry("430x250")
        confirm_window.resizable(False, False)
        confirm_window.grab_set()

        title = ctk.CTkLabel(
            confirm_window,
            text="¿Eliminar cuenta?",
            font=("Segoe UI", 24)
        )
        title.pack(pady=(25, 10))

        message = ctk.CTkLabel(
            confirm_window,
            text=(
                "Esta acción eliminará tu cuenta de forma permanente.\n"
                "No podrás recuperar esta información.\n\n"
                "¿Deseas continuar?"
            ),
            font=("Segoe UI", 14),
            justify="center"
        )
        message.pack(pady=10)

        button_frame = ctk.CTkFrame(
            confirm_window,
            fg_color="transparent"
        )
        button_frame.pack(pady=15)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            width=130,
            command=confirm_window.destroy
        )
        cancel_button.grid(row=0, column=0, padx=10)

        delete_button = ctk.CTkButton(
            button_frame,
            text="Sí, eliminar",
            width=130,
            fg_color=self.theme["danger"],
            hover_color=self.theme["danger_hover"],
            text_color="#FFFFFF",
            command=lambda: self.delete_account(confirm_window)
        )
        delete_button.grid(row=0, column=1, padx=10)

    def delete_account(self, window):
        result = UserController.delete_own_account(self.current_user)

        if result["success"]:
            window.destroy()
            self.app.current_user = None
            self.app.login_theme = "light"
            AppState.save_last_theme("light")
            self.app.show_login()
        else:
            self.message_label.configure(
                text=result["message"],
                text_color=self.theme["danger"]
            )
            window.destroy()