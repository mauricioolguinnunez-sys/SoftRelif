import customtkinter as ctk

from controllers.auth_controller import AuthController
from utils.app_state import AppState
from utils.i18n import Lang


class RegisterForm:
    """
    Formulario de registro de SoftRelief.

    Encapsula la UI de creación de cuenta dentro de una tarjeta contenedora.
    Recibe la tarjeta, un proveedor de tema y callbacks de navegación.
    """

    def __init__(self, card, theme_provider, on_back, on_success):
        self.card = card
        self.theme_provider = theme_provider
        self.on_back = on_back
        self.on_success = on_success

        self.register_title = None
        self.nombre_entry = None
        self.new_user_entry = None
        self.email_entry = None
        self.new_password_entry = None
        self.confirm_password_entry = None
        self.register_button = None
        self.back_button = None
        self.register_message = None

        Lang.set(AppState.load_language())

    @property
    def theme(self):
        return self.theme_provider()

    def show(self):
        for widget in self.card.winfo_children():
            widget.destroy()

        self.card.configure(
            fg_color=self.theme["card_bg"],
            border_color=self.theme["card_border"]
        )

        self.register_title = ctk.CTkLabel(
            self.card,
            text=Lang.get("register_title"),
            font=("Segoe UI", 22),
            text_color=self.theme["text"],
            fg_color=self.theme["card_bg"]
        )
        self.register_title.place(relx=0.5, rely=0.08, anchor="center")

        self.nombre_entry = self.create_register_entry(Lang.get("full_name"), 0.19)
        self.new_user_entry = self.create_register_entry(Lang.get("username"), 0.30)
        self.email_entry = self.create_register_entry(Lang.get("email"), 0.41)

        self.new_password_entry = self.create_register_entry(Lang.get("password"), 0.52)
        self.new_password_entry.configure(show="●")

        self.confirm_password_entry = self.create_register_entry(Lang.get("confirm_password"), 0.63)
        self.confirm_password_entry.configure(show="●")

        self.register_button = ctk.CTkButton(
            self.card,
            text=Lang.get("register_button"),
            width=320,
            height=40,
            corner_radius=14,
            font=("Segoe UI", 14),
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            command=self.register
        )
        self.register_button.place(relx=0.5, rely=0.76, anchor="center")

        self.back_button = ctk.CTkButton(
            self.card,
            text=Lang.get("back"),
            width=130,
            height=32,
            corner_radius=12,
            fg_color=self.theme["card_bg"],
            hover_color=self.theme["menu_hover"],
            border_width=1,
            border_color=self.theme["accent"],
            text_color=self.theme["accent"],
            command=self.on_back
        )
        self.back_button.place(relx=0.5, rely=0.87, anchor="center")

        self.register_message = ctk.CTkLabel(
            self.card,
            text="",
            font=("Segoe UI", 12),
            text_color=self.theme["danger"],
            fg_color=self.theme["card_bg"]
        )
        self.register_message.place(relx=0.5, rely=0.95, anchor="center")

    def create_register_entry(self, placeholder, rely):
        entry = ctk.CTkEntry(
            self.card,
            width=320,
            height=38,
            corner_radius=13,
            placeholder_text=placeholder,
            font=("Segoe UI", 14),
            fg_color=self.theme["input_bg"],
            border_width=1,
            border_color=self.theme["card_border"],
            text_color=self.theme["text"],
            placeholder_text_color=self.theme["text_soft"]
        )
        entry.place(relx=0.5, rely=rely, anchor="center")
        return entry

    def register(self):
        nombre = self.nombre_entry.get().strip()
        usuario = self.new_user_entry.get().strip()
        correo = self.email_entry.get().strip()
        password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        result = AuthController.register(
            nombre,
            usuario,
            correo,
            password,
            confirm_password
        )

        if result["success"]:
            self.on_success()
        else:
            self.register_message.configure(
                text=result["message"],
                text_color=self.theme["danger"]
            )

    def resize(self, entry_width, entry_height):
        widgets = [
            "nombre_entry",
            "new_user_entry",
            "email_entry",
            "new_password_entry",
            "confirm_password_entry",
            "register_button"
        ]

        for widget_name in widgets:
            if hasattr(self, widget_name):
                widget = getattr(self, widget_name)

                try:
                    widget.configure(
                        width=entry_width,
                        height=entry_height
                    )
                except Exception:
                    pass
