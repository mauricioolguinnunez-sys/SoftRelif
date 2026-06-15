import customtkinter as ctk

from database.schema import create_tables
from views.login_view import LoginView
from views.home_view import HomeView
from utils.theme_manager import ThemeManager
from utils.app_state import AppState


class SoftReliefApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SoftRelief")
        self.geometry("1200x700")
        self.resizable(True, True)
        self.minsize(900, 600)

        self.current_user = None
        self.login_theme = AppState.load_last_theme()

        create_tables()
        ThemeManager.apply_mode(self.login_theme)

        self.show_login()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()

        self.login_theme = AppState.load_last_theme()
        ThemeManager.apply_mode(self.login_theme)

        LoginView(self, self)

    def show_home(self):
        self.clear_window()

        if self.current_user:
            theme = self.current_user.get("tema_visual", "light")
            self.login_theme = theme
            AppState.save_last_theme(theme)
            ThemeManager.apply_mode(theme)

        HomeView(self, self)


if __name__ == "__main__":
    app = SoftReliefApp()
    app.mainloop()