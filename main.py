import traceback
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from database.schema import create_tables
from utils.app_state import AppState
from utils.theme_manager import ThemeManager
from utils.sound_player import SoundPlayer
from utils.i18n import Lang

from views.login_view import LoginView
from views.home_view import HomeView


class SoftReliefApp(ctk.CTk):
    """
    Clase principal de la aplicación SoftRelief.

    Responsabilidades:
    - Inicializar base de datos.
    - Aplicar tema visual.
    - Controlar sesión actual.
    - Cambiar entre LoginView y HomeView.
    - Detener música al cerrar sesión o regresar al login.
    """

    def report_callback_exception(self, exc, val, tb):
        if isinstance(val, tk.TclError) and "bad window path name" in str(val):
            return
        traceback.print_exception(exc, val, tb)

    def __init__(self):
        super().__init__()

        self.title("SoftRelief")
        self.geometry("1180x720")
        self.minsize(980, 620)

        self.current_user = None
        self.login_theme = AppState.load_last_theme()
        Lang.set(AppState.load_language())

        self.configure_app()
        self.initialize_database()
        self.show_login()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # =====================================================
    # CONFIGURACIÓN GENERAL
    # =====================================================

    def configure_app(self):
        """
        Aplica el tema inicial de la app.
        """

        if self.login_theme not in ["light", "dark"]:
            self.login_theme = "light"

        ThemeManager.apply_mode(self.login_theme)

        theme = ThemeManager.get_theme(self.login_theme)

        self.configure(
            fg_color=theme.get("app_bg", "#F6F7FB")
        )

    def initialize_database(self):
        """
        Crea/verifica las tablas del modelo relacional.
        """

        try:
            create_tables()

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudo inicializar la base de datos:\n\n{error}"
            )

    def clear_window(self):
        """
        Limpia todos los widgets actuales de la ventana.
        """

        for widget in self.winfo_children():
            widget.destroy()

    # =====================================================
    # NAVEGACIÓN PRINCIPAL
    # =====================================================

    def show_login(self):
        """
        Muestra LoginView.

        También se usa como cierre de sesión, por eso detiene cualquier música
        activa antes de regresar al login.
        """

        try:
            SoundPlayer.stop()
        except Exception:
            pass

        self.current_user = None

        self.clear_window()

        theme_name = self.login_theme or AppState.load_last_theme()

        if theme_name not in ["light", "dark"]:
            theme_name = "light"

        ThemeManager.apply_mode(theme_name)

        theme = ThemeManager.get_theme(theme_name)

        self.configure(
            fg_color=theme.get("app_bg", "#F6F7FB")
        )

        view = LoginView(self, self)
        view.pack(fill="both", expand=True)

    def show_home(self):
        """
        Muestra HomeView después de iniciar sesión o después de reconstruir
        la interfaz por cambio de tema.
        """

        if not self.current_user:
            self.show_login()
            return

        theme_name = self.current_user.get("tema_visual", "light")

        if theme_name not in ["light", "dark"]:
            theme_name = "light"

        self.login_theme = theme_name

        ThemeManager.apply_mode(theme_name)
        AppState.save_last_theme(theme_name)

        theme = ThemeManager.get_theme(theme_name)

        self.configure(
            fg_color=theme.get("app_bg", "#F6F7FB")
        )

        self.clear_window()

        view = HomeView(self, self)
        view.pack(fill="both", expand=True)

    def logout(self):
        """
        Cierre de sesión centralizado.
        Cualquier vista puede llamar self.app.logout().
        """

        try:
            SoundPlayer.stop()
        except Exception:
            pass

        if self.current_user:
            theme_name = self.current_user.get("tema_visual", "light")

            if theme_name in ["light", "dark"]:
                self.login_theme = theme_name
                AppState.save_last_theme(theme_name)

        self.current_user = None
        self.show_login()

    # =====================================================
    # SESIÓN
    # =====================================================

    def set_current_user(self, user):
        """
        Guarda usuario actual después de login.
        Compatible con LoginView si usa app.current_user directamente.
        """

        self.current_user = user

        if self.current_user:
            theme_name = self.current_user.get("tema_visual", "light")

            if theme_name not in ["light", "dark"]:
                theme_name = "light"

            self.current_user["tema_visual"] = theme_name
            self.login_theme = theme_name

            ThemeManager.apply_mode(theme_name)
            AppState.save_last_theme(theme_name)

            idioma = self.current_user.get("idioma", "es")

            if idioma not in ["es", "en"]:
                idioma = "es"

            Lang.set(idioma)
            AppState.save_language(idioma)

    # =====================================================
    # CIERRE DE APP
    # =====================================================

    def on_close(self):
        """
        Cierra la aplicación y detiene audio activo.
        """

        try:
            SoundPlayer.stop()
        except Exception:
            pass

        self.destroy()


if __name__ == "__main__":
    app = SoftReliefApp()
    app.mainloop()