import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

from controllers.auth_controller import AuthController
from utils.theme_manager import ThemeManager
from utils.app_state import AppState
from utils.i18n import Lang


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LIGHT_LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
DARK_LOGO_PATH = os.path.join(BASE_DIR, "assets", "dark_logo.png")

LIGHT_LOGIN_BACKGROUND_PATH = os.path.join(BASE_DIR, "assets", "login_background.png")
DARK_LOGIN_BACKGROUND_PATH = os.path.join(BASE_DIR, "assets", "dark_login_background.png")

LIGHT_REGISTER_BACKGROUND_PATH = os.path.join(BASE_DIR, "assets", "sing-in_background.png")
DARK_REGISTER_BACKGROUND_PATH = os.path.join(BASE_DIR, "assets", "dark_sing-in_background.png")


class LoginView(ctk.CTkFrame):

    def __init__(self, master, app):
        super().__init__(
            master,
            corner_radius=0,
            fg_color="#F8FAFC"
        )

        self.app = app
        self.pack(fill="both", expand=True)

        self.theme_name = getattr(self.app, "login_theme", "light")
        self.theme = ThemeManager.get_theme(self.theme_name)

        self.login_bg_original = None
        self.register_bg_original = None
        self.bg_original = None
        self.logo_original = None

        self.bg_photo = None
        self.logo_photo = None

        self.mode = "login"

        Lang.set(AppState.load_language())

        self.load_images()
        self.create_canvas()
        self.create_language_selector()
        self.create_login_card()
        self.bind_resize_events()

    # =====================================================
    # SELECCIÓN DE ASSETS POR TEMA
    # =====================================================

    def get_asset_paths_by_theme(self):
        if self.theme_name == "dark":
            return {
                "logo": DARK_LOGO_PATH,
                "login_bg": DARK_LOGIN_BACKGROUND_PATH,
                "register_bg": DARK_REGISTER_BACKGROUND_PATH
            }

        return {
            "logo": LIGHT_LOGO_PATH,
            "login_bg": LIGHT_LOGIN_BACKGROUND_PATH,
            "register_bg": LIGHT_REGISTER_BACKGROUND_PATH
        }

    def load_images(self):
        paths = self.get_asset_paths_by_theme()

        if os.path.exists(paths["login_bg"]):
            self.login_bg_original = Image.open(paths["login_bg"]).convert("RGB")

        if os.path.exists(paths["register_bg"]):
            self.register_bg_original = Image.open(paths["register_bg"]).convert("RGB")

        if os.path.exists(paths["logo"]):
            self.logo_original = Image.open(paths["logo"]).convert("RGBA")

        self.bg_original = self.login_bg_original

    # =====================================================
    # CANVAS RESPONSIVE
    # =====================================================

    def create_canvas(self):
        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bd=0,
            bg=self.theme["app_bg"]
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

    def create_language_selector(self):
        self.lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lang_frame.place(relx=1.0, rely=0.0, x=-20, y=16, anchor="ne")

        self.lang_btn_es = ctk.CTkButton(
            self.lang_frame,
            text="ES",
            width=40,
            height=28,
            corner_radius=8,
            font=("Segoe UI", 11, "bold"),
            fg_color=self.theme["accent"] if Lang.current() == "es" else self.theme["card_bg"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF" if Lang.current() == "es" else self.theme["text"],
            border_width=1,
            border_color=self.theme["accent"],
            command=lambda: self.set_language("es")
        )
        self.lang_btn_es.grid(row=0, column=0, padx=(0, 4))

        self.lang_btn_en = ctk.CTkButton(
            self.lang_frame,
            text="EN",
            width=40,
            height=28,
            corner_radius=8,
            font=("Segoe UI", 11, "bold"),
            fg_color=self.theme["accent"] if Lang.current() == "en" else self.theme["card_bg"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF" if Lang.current() == "en" else self.theme["text"],
            border_width=1,
            border_color=self.theme["accent"],
            command=lambda: self.set_language("en")
        )
        self.lang_btn_en.grid(row=0, column=1)

    def set_language(self, lang):
        Lang.set(lang)
        AppState.save_language(lang)
        self.lang_btn_es.configure(
            fg_color=self.theme["accent"] if lang == "es" else self.theme["card_bg"],
            text_color="#FFFFFF" if lang == "es" else self.theme["text"]
        )
        self.lang_btn_en.configure(
            fg_color=self.theme["accent"] if lang == "en" else self.theme["card_bg"],
            text_color="#FFFFFF" if lang == "en" else self.theme["text"]
        )
        self.reload_login()

    def bind_resize_events(self):
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        if event.width < 100 or event.height < 100:
            return

        self.draw_background(event.width, event.height)
        self.position_elements(event.width, event.height)

    def switch_background(self, mode="login"):
        self.mode = mode

        if mode == "register" and self.register_bg_original is not None:
            self.bg_original = self.register_bg_original
        else:
            self.bg_original = self.login_bg_original

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 100 or height < 100:
            width = 1200
            height = 700

        self.draw_background(width, height)
        self.position_elements(width, height)

    def draw_background(self, width, height):
        self.canvas.delete("background")
        self.canvas.delete("text")

        if self.bg_original:
            resized_bg = self.cover_resize(self.bg_original, width, height)
            self.bg_photo = ImageTk.PhotoImage(resized_bg)

            self.canvas.create_image(
                0,
                0,
                image=self.bg_photo,
                anchor="nw",
                tags="background"
            )
        else:
            self.canvas.create_rectangle(
                0,
                0,
                width,
                height,
                fill=self.theme["app_bg"],
                outline="",
                tags="background"
            )

        self.draw_header_text(width, height)
        self.draw_footer_text(width, height)

    def draw_header_text(self, width, height):
        logo_size = self.scale_value(
            width,
            height,
            base=135,
            minimum=85,
            maximum=150
        )

        if self.logo_original:
            resized_logo = self.logo_original.resize(
                (logo_size, logo_size),
                Image.LANCZOS
            )

            self.logo_photo = ImageTk.PhotoImage(resized_logo)

            self.canvas.create_image(
                width / 2,
                height * 0.13,
                image=self.logo_photo,
                anchor="center",
                tags="text"
            )
        else:
            self.canvas.create_text(
                width / 2,
                height * 0.13,
                text="[ LOGO ]",
                font=("Segoe UI", 22),
                fill=self.theme["text"],
                tags="text"
            )

        title_size = self.scale_value(
            width,
            height,
            base=46,
            minimum=32,
            maximum=52
        )

        slogan_size = self.scale_value(
            width,
            height,
            base=15,
            minimum=12,
            maximum=17
        )

        if self.mode == "register":
            title_text = Lang.get("register_title")
            slogan_text = Lang.get("register_slogan")
        else:
            title_text = Lang.get("app_title")
            slogan_text = Lang.get("slogan")

        self.canvas.create_text(
            width / 2,
            height * 0.26,
            text=title_text,
            font=("Segoe UI Light", title_size),
            fill=self.theme["text"],
            tags="text"
        )

        self.canvas.create_text(
            width / 2,
            height * 0.31,
            text=slogan_text,
            font=("Segoe UI", slogan_size),
            fill=self.theme["text_soft"],
            tags="text"
        )

    def draw_footer_text(self, width, height):
        footer_size = self.scale_value(
            width,
            height,
            base=13,
            minimum=11,
            maximum=14
        )

        self.canvas.create_text(
            max(30, width * 0.04),
            height - 35,
            text=Lang.get("version"),
            font=("Segoe UI", footer_size),
            fill=self.theme["text_soft"],
            anchor="w",
            tags="text"
        )

        self.canvas.create_text(
            width - max(30, width * 0.04),
            height - 35,
            text=Lang.get("footer_credits"),
            font=("Segoe UI", footer_size),
            fill=self.theme["text"],
            anchor="e",
            tags="text"
        )

        if self.mode == "login":
            forgot_item = self.canvas.create_text(
                width / 2,
                height * 0.84,
                text=Lang.get("forgot_password"),
                font=("Segoe UI", footer_size),
                fill=self.theme["accent"],
                tags="text"
            )

            self.canvas.tag_bind(
                forgot_item,
                "<Enter>",
                lambda e: self.canvas.config(cursor="hand2")
            )
            self.canvas.tag_bind(
                forgot_item,
                "<Leave>",
                lambda e: self.canvas.config(cursor="")
            )
            self.canvas.tag_bind(
                forgot_item,
                "<Button-1>",
                lambda e: self.show_message(Lang.get("pending_function"))
            )

    def cover_resize(self, image, target_width, target_height):
        img_width, img_height = image.size

        scale = max(
            target_width / img_width,
            target_height / img_height
        )

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        resized = image.resize(
            (new_width, new_height),
            Image.LANCZOS
        )

        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        return resized.crop((left, top, right, bottom))

    def scale_value(self, width, height, base, minimum, maximum):
        scale = min(width / 1200, height / 700)
        value = int(base * scale)

        return max(minimum, min(value, maximum))

    # =====================================================
    # CARD LOGIN
    # =====================================================

    def create_login_card(self):
        self.card = ctk.CTkFrame(
            self,
            width=420,
            height=330,
            corner_radius=26,
            fg_color=self.theme["card_bg"],
            border_width=1,
            border_color=self.theme["card_border"]
        )

        self.user_entry = ctk.CTkEntry(
            self.card,
            width=320,
            height=46,
            corner_radius=14,
            placeholder_text=Lang.get("username"),
            font=("Segoe UI", 15),
            fg_color=self.theme["input_bg"],
            border_width=1,
            border_color=self.theme["card_border"],
            text_color=self.theme["text"],
            placeholder_text_color=self.theme["text_soft"]
        )

        self.password_entry = ctk.CTkEntry(
            self.card,
            width=320,
            height=46,
            corner_radius=14,
            placeholder_text=Lang.get("password"),
            show="●",
            font=("Segoe UI", 15),
            fg_color=self.theme["input_bg"],
            border_width=1,
            border_color=self.theme["card_border"],
            text_color=self.theme["text"],
            placeholder_text_color=self.theme["text_soft"]
        )

        self.login_button = ctk.CTkButton(
            self.card,
            text=Lang.get("login_button"),
            width=320,
            height=46,
            corner_radius=14,
            font=("Segoe UI", 15),
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            command=self.login
        )

        self.separator_label = ctk.CTkLabel(
            self.card,
            text=Lang.get("or"),
            font=("Segoe UI", 14),
            text_color=self.theme["text_soft"],
            fg_color=self.theme["card_bg"]
        )

        self.create_account_button = ctk.CTkButton(
            self.card,
            text=Lang.get("create_account"),
            width=320,
            height=42,
            corner_radius=14,
            font=("Segoe UI", 15),
            fg_color=self.theme["card_bg"],
            hover_color=self.theme["menu_hover"],
            border_width=1,
            border_color=self.theme["accent"],
            text_color=self.theme["accent"],
            command=self.show_register_form
        )

        self.message_label = ctk.CTkLabel(
            self.card,
            text="",
            font=("Segoe UI", 13),
            text_color=self.theme["danger"],
            fg_color=self.theme["card_bg"]
        )

        self.place_login_widgets()

    def place_login_widgets(self):
        self.user_entry.place(relx=0.5, rely=0.17, anchor="center")
        self.password_entry.place(relx=0.5, rely=0.36, anchor="center")
        self.login_button.place(relx=0.5, rely=0.56, anchor="center")
        self.separator_label.place(relx=0.5, rely=0.70, anchor="center")
        self.create_account_button.place(relx=0.5, rely=0.82, anchor="center")
        self.message_label.place(relx=0.5, rely=0.95, anchor="center")

    def position_elements(self, width, height):
        if self.mode == "register":
            card_width = self.scale_value(
                width,
                height,
                base=430,
                minimum=360,
                maximum=460
            )

            card_height = self.scale_value(
                width,
                height,
                base=410,
                minimum=380,
                maximum=430
            )

            self.card.configure(
                width=card_width,
                height=card_height
            )

            self.card.place(
                relx=0.5,
                rely=0.61,
                anchor="center"
            )

        else:
            card_width = self.scale_value(
                width,
                height,
                base=420,
                minimum=360,
                maximum=460
            )

            card_height = self.scale_value(
                width,
                height,
                base=330,
                minimum=300,
                maximum=350
            )

            self.card.configure(
                width=card_width,
                height=card_height
            )

            self.card.place(
                relx=0.5,
                rely=0.59,
                anchor="center"
            )

        entry_width = int(card_width * 0.76)
        entry_height = self.scale_value(
            width,
            height,
            base=46,
            minimum=38,
            maximum=48
        )

        self.update_widget_sizes(entry_width, entry_height)

    def update_widget_sizes(self, entry_width, entry_height):
        widgets = [
            "user_entry",
            "password_entry",
            "login_button",
            "create_account_button",
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

    # =====================================================
    # LOGIN
    # =====================================================

    def login(self):
        usuario = self.user_entry.get().strip()
        password = self.password_entry.get().strip()

        result = AuthController.login(usuario, password)

        if result["success"]:
            self.app.current_user = result["user"]

            user_theme = result["user"].get("tema_visual", "light")
            self.app.login_theme = user_theme
            AppState.save_last_theme(user_theme)
            ThemeManager.apply_mode(user_theme)

            self.app.show_home()
        else:
            self.show_message(result["message"])

    def show_message(self, text):
        if hasattr(self, "message_label"):
            self.message_label.configure(
                text=text,
                text_color=self.theme["danger"]
            )

    # =====================================================
    # FORMULARIO DE REGISTRO
    # =====================================================

    def show_register_form(self):
        self.switch_background("register")

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
            command=self.reload_login
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

        width = self.winfo_width()
        height = self.winfo_height()

        if width > 100 and height > 100:
            self.position_elements(width, height)

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
            self.reload_login()
        else:
            self.register_message.configure(
                text=result["message"],
                text_color=self.theme["danger"]
            )

    def reload_login(self):
        self.app.show_login()