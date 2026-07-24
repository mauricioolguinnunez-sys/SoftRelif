import customtkinter as ctk

from utils.theme_manager import ThemeManager


class CalmModeView(ctk.CTkFrame):
    def __init__(self, master, app=None, user=None):
        self.app = app
        self.user = user
        self.theme_name = self.get_theme_name()
        self.theme = ThemeManager.get_theme(self.theme_name)

        super().__init__(
            master,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=0,
        )

        self.modes = [
            {"id": "uniforme", "nombre": "Respiración uniforme", "fases": [4, 0, 4, 0]},
            {"id": "478", "nombre": "Técnica 4-7-8", "fases": [4, 7, 8, 0]},
            {"id": "box", "nombre": "Box breathing", "fases": [4, 4, 4, 4]},
        ]
        self.mode_index = 0
        self.current_cycle = self.modes[0]["fases"]
        self.phase_index = 0
        self.phase_elapsed = 0.0
        self.is_running = False
        self.bubble_scale = 0.9
        self.breath_label = "Listo para comenzar"

        self.build_view()
        self.update_breathing_display()

    def c(self, key, default):
        return self.theme.get(key, default)

    def get_theme_name(self):
        if self.user:
            return self.user.get("tema_visual", "light")
        return "light"

    def build_view(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=24)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            container,
            text="Modo calma",
            font=("Arial", 28, "bold"),
            text_color=self.c("text", "#1E1B4B"),
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 10))

        subtitle = ctk.CTkLabel(
            container,
            text="Una pausa guiada para respirar, soltar la tensión y volver a ti.",
            font=("Arial", 14),
            text_color=self.c("text_soft", "#6B7280"),
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 20))

        main = ctk.CTkFrame(container, fg_color=self.c("card_bg", "#FFFFFF"), corner_radius=24)
        main.grid(row=2, column=0, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(0, weight=1)

        content = ctk.CTkFrame(main, fg_color="transparent")
        content.grid(row=0, column=0, sticky="nsew", padx=26, pady=24)
        content.grid_columnconfigure(0, weight=1)

        self.bubble = ctk.CTkFrame(
            content,
            width=220,
            height=220,
            corner_radius=110,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            border_width=2,
            border_color=self.c("accent", "#7C3AED"),
        )
        self.bubble.grid(row=0, column=0, pady=(0, 20))
        self.bubble.grid_propagate(False)
        self.bubble.columnconfigure(0, weight=1)
        self.bubble.rowconfigure(0, weight=1)

        self.bubble_label = ctk.CTkLabel(
            self.bubble,
            text="Respira",
            font=("Arial", 22, "bold"),
            text_color=self.c("accent", "#7C3AED"),
        )
        self.bubble_label.place(relx=0.5, rely=0.5, anchor="center")

        self.phase_label = ctk.CTkLabel(
            content,
            text="Listo para comenzar",
            font=("Arial", 18, "bold"),
            text_color=self.c("text", "#1E1B4B"),
        )
        self.phase_label.grid(row=1, column=0, pady=(0, 10))

        self.timer_label = ctk.CTkLabel(
            content,
            text="--",
            font=("Arial", 28, "bold"),
            text_color=self.c("accent", "#7C3AED"),
        )
        self.timer_label.grid(row=2, column=0, pady=(0, 16))

        controls = ctk.CTkFrame(content, fg_color="transparent")
        controls.grid(row=3, column=0)
        controls.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_button = ctk.CTkButton(controls, text="Iniciar", command=self.start_session)
        self.start_button.grid(row=0, column=0, padx=6)

        self.pause_button = ctk.CTkButton(controls, text="Pausar", command=self.pause_session)
        self.pause_button.grid(row=0, column=1, padx=6)

        self.reset_button = ctk.CTkButton(controls, text="Reiniciar", command=self.reset_session)
        self.reset_button.grid(row=0, column=2, padx=6)

        mode_row = ctk.CTkFrame(content, fg_color="transparent")
        mode_row.grid(row=4, column=0, pady=(20, 8))
        ctk.CTkLabel(mode_row, text="Modo:", font=("Arial", 13), text_color=self.c("text_soft", "#6B7280")).grid(row=0, column=0, padx=(0, 8))

        self.mode_combo = ctk.CTkComboBox(
            mode_row,
            values=[mode["nombre"] for mode in self.modes],
            command=self.change_mode,
        )
        self.mode_combo.grid(row=0, column=1)
        self.mode_combo.set(self.modes[0]["nombre"])

    def change_mode(self, value):
        for index, mode in enumerate(self.modes):
            if mode["nombre"] == value:
                self.mode_index = index
                self.current_cycle = mode["fases"]
                self.phase_index = 0
                self.phase_elapsed = 0.0
                self.update_breathing_display()
                break

    def start_session(self):
        self.is_running = True
        self.after(100, self.tick)

    def pause_session(self):
        self.is_running = False

    def reset_session(self):
        self.is_running = False
        self.phase_index = 0
        self.phase_elapsed = 0.0
        self.bubble_scale = 0.9
        self.breath_label = "Listo para comenzar"
        self.update_breathing_display()

    def tick(self):
        if not self.is_running:
            return

        self.phase_elapsed += 0.1
        duration = self.current_cycle[self.phase_index]

        if duration == 0:
            self.phase_index = (self.phase_index + 1) % len(self.current_cycle)
            self.phase_elapsed = 0.0
            self.after(100, self.tick)
            return

        if self.phase_elapsed >= duration:
            self.phase_index = (self.phase_index + 1) % len(self.current_cycle)
            self.phase_elapsed = 0.0
            self.after(100, self.tick)
            return

        self.update_breathing_display()
        self.after(100, self.tick)

    def update_breathing_display(self):
        duration = self.current_cycle[self.phase_index]
        labels = ["Inhala", "Sostén", "Exhala", "Pausa"]
        current_label = labels[self.phase_index]
        self.phase_label.configure(text=current_label)

        if duration == 0:
            self.timer_label.configure(text="0s")
            self.bubble_scale = 0.9
            self.bubble_label.configure(text="Respira")
            self.bubble.configure(width=220, height=220)
            return

        remaining = max(0, int(duration - self.phase_elapsed))
        self.timer_label.configure(text=f"{remaining}s")

        if self.phase_index == 0:
            self.bubble_scale = 0.9 + min(0.35, self.phase_elapsed / duration * 0.35)
        elif self.phase_index == 2:
            self.bubble_scale = 1.25 - min(0.35, self.phase_elapsed / duration * 0.35)
        else:
            self.bubble_scale = 1.1

        size = int(220 * self.bubble_scale)
        self.bubble.configure(width=size, height=size)
        self.bubble_label.configure(text=current_label)


if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    root = ctk.CTk()
    root.geometry("980x720")
    CalmModeView(root)
    root.mainloop()