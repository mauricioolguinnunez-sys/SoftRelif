import math
import tkinter as tk

import customtkinter as ctk

from utils.music_catalog import get_all_music, get_music_by_id
from utils.music_state import get_user_music_settings
from utils.sound_player import SoundPlayer


class BreathingCanvas(tk.Canvas):
    """Lienzo animado que recrea la burbuja y la flor del diseño original."""

    def __init__(self, master, view):
        super().__init__(
            master,
            bg="#101A32",
            highlightthickness=0,
            bd=0,
        )
        self.view = view

    def redraw(self):
        if not self.winfo_exists():
            return

        self.delete("all")

        width = max(self.winfo_width(), 460)
        height = max(self.winfo_height(), 380)
        center_x = width / 2
        center_y = height / 2 - 16

        self.create_oval(
            12,
            12,
            width - 12,
            height - 12,
            fill="#101A32",
            outline="#24324F",
            width=1,
        )

        for index in range(18):
            x = (index * 83 + 31) % width
            y = (index * 47 + 24) % max(height - 60, 1)
            radius = 2 + index % 3
            self.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="#FFFFFF",
                outline="",
                stipple="gray50",
            )

        base_radius = min(width, height) * 0.245
        radius = base_radius * self.view.bubble_scale

        bubble_layers = (
            (1.18, "#172D4D"),
            (1.10, "#1C3A5D"),
            (1.03, "#285276"),
            (1.00, "#386F91"),
            (0.94, "#183C61"),
        )

        for scale, color in bubble_layers:
            current = radius * scale
            self.create_oval(
                center_x - current,
                center_y - current,
                center_x + current,
                center_y + current,
                fill=color,
                outline="",
            )

        self.create_arc(
            center_x - radius * 0.72,
            center_y - radius * 0.82,
            center_x + radius * 0.38,
            center_y - radius * 0.20,
            start=35,
            extent=115,
            style=tk.ARC,
            outline="#D7F4FF",
            width=5,
        )

        time_value = self.view.animation_time
        flower_x = center_x + math.cos(time_value * 0.75) * 8
        flower_y = center_y + math.sin(time_value * 1.05) * 10
        flower_scale = max(radius / 115, 0.65)
        self.draw_flower(flower_x, flower_y, flower_scale)

        timer_text = self.view.timer_text
        instruction = self.view.instruction_text

        self.create_text(
            center_x,
            center_y + radius * 0.48,
            text=timer_text,
            fill="#F9E076",
            font=("Segoe UI", max(24, int(radius * 0.28)), "bold"),
        )
        self.create_text(
            center_x,
            center_y + radius * 0.74,
            text=instruction,
            fill="#FFFFFF",
            font=("Segoe UI", max(12, int(radius * 0.105))),
        )

    def draw_flower(self, x, y, scale):
        petal_colors = ["#E8DDFF", "#D7F1FF", "#BBD9FA", "#F1E8FF"]

        for index in range(8):
            angle = math.radians(index * 45 + math.sin(self.view.animation_time) * 4)
            distance = 25 * scale
            petal_x = x + math.cos(angle) * distance
            petal_y = y + math.sin(angle) * distance
            width = 42 * scale
            height = 22 * scale

            self.create_oval(
                petal_x - width / 2,
                petal_y - height / 2,
                petal_x + width / 2,
                petal_y + height / 2,
                fill=petal_colors[index % len(petal_colors)],
                outline="#FFFFFF",
                width=1,
            )

        center_radius = 12 * scale
        self.create_oval(
            x - center_radius,
            y - center_radius,
            x + center_radius,
            y + center_radius,
            fill="#F9E076",
            outline="#FFF8C4",
            width=2,
        )


class CalmModeView(ctk.CTkFrame):
    """Modo Calma integrado a la navegación y al audio de SoftRelief."""

    BACKGROUND = "#101A32"
    CARD = "#192642"
    CARD_HOVER = "#213253"
    TEXT = "#FFFFFF"
    TEXT_SOFT = "#B9C6DC"
    GOLD = "#F9E076"
    BLUE = "#69B6D5"

    def __init__(self, master, app=None, user=None):
        super().__init__(master, fg_color=self.BACKGROUND, corner_radius=0)

        self.app = app
        self.user = user or getattr(app, "current_user", None)

        self.modes = [
            {
                "id": "uniforme",
                "nombre": "Respiración uniforme",
                "fases": [5, 0, 5, 0],
            },
            {
                "id": "478",
                "nombre": "Técnica 4-7-8",
                "fases": [4, 7, 8, 0],
            },
            {
                "id": "box",
                "nombre": "Box breathing",
                "fases": [4, 4, 4, 4],
            },
        ]
        self.phase_names = ["Inhala...", "Mantén...", "Exhala...", "Pausa..."]
        self.mode_index = 0
        self.phase_index = 0
        self.phase_elapsed = 0.0
        self.animation_time = 0.0
        self.is_started = False
        self.is_paused = True
        self.bubble_scale = 0.80
        self.timer_text = "--"
        self.instruction_text = "Listo para comenzar"
        self.animation_job = None

        self.tracks = get_all_music()
        self.track_by_name = {track["title"]: track for track in self.tracks}
        self.selected_track = self.get_saved_track()

        self.build_view()
        self.start_animation_loop()
        self.bind("<Destroy>", self.on_destroy, add="+")

    @property
    def current_phases(self):
        return self.modes[self.mode_index]["fases"]

    def user_id(self):
        if not self.user:
            return None
        return self.user.get("id_usuario")

    def get_saved_track(self):
        if not self.user_id():
            return self.tracks[0] if self.tracks else None

        try:
            settings = get_user_music_settings(self.user_id())
            track = get_music_by_id(settings.get("calm_mode_track"))
            if track:
                return track
        except Exception:
            pass

        return self.tracks[0] if self.tracks else None

    def build_view(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=34, pady=(24, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Modo calma",
            font=("Segoe UI", 32, "bold"),
            text_color=self.TEXT,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Respira, baja el ritmo y recupera tu equilibrio.",
            font=("Segoe UI", 14),
            text_color=self.TEXT_SOFT,
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=34, pady=(0, 26))
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=5, uniform="calm")
        body.grid_columnconfigure(1, weight=4, uniform="calm")

        self.build_animation_column(body)
        self.build_options_column(body)

    def build_animation_column(self, parent):
        left = ctk.CTkFrame(
            parent,
            fg_color="#101A32",
            border_width=1,
            border_color="#283755",
            corner_radius=24,
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(0, weight=1)

        self.canvas = BreathingCanvas(left, self)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 0))

        controls = ctk.CTkFrame(left, fg_color="transparent")
        controls.grid(row=1, column=0, pady=(4, 12))

        self.back_button = self.bubble_button(
            controls,
            "↶",
            56,
            self.reset_phase,
        )
        self.back_button.grid(row=0, column=0, padx=12)

        self.play_button = self.bubble_button(
            controls,
            "▶",
            76,
            self.toggle_session,
        )
        self.play_button.grid(row=0, column=1, padx=12)

        self.next_button = self.bubble_button(
            controls,
            "↷",
            56,
            self.next_phase,
        )
        self.next_button.grid(row=0, column=2, padx=12)

        volume = ctk.CTkFrame(left, fg_color="transparent")
        volume.grid(row=2, column=0, sticky="ew", padx=56, pady=(0, 20))
        volume.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            volume,
            text="🔊",
            font=("Segoe UI Emoji", 18),
            text_color=self.TEXT,
        ).grid(row=0, column=0, padx=(0, 12))

        self.volume_slider = ctk.CTkSlider(
            volume,
            from_=0,
            to=1,
            number_of_steps=100,
            button_color="#FFFFFF",
            button_hover_color="#D7F4FF",
            progress_color=self.GOLD,
            fg_color="#52617B",
            command=self.change_volume,
        )
        self.volume_slider.grid(row=0, column=1, sticky="ew")
        self.volume_slider.set(SoundPlayer.get_status().get("volume", 0.65))

    def bubble_button(self, master, text, size, command):
        return ctk.CTkButton(
            master,
            text=text,
            width=size,
            height=size,
            corner_radius=size // 2,
            fg_color="#315D7D",
            hover_color="#4E86A5",
            border_width=2,
            border_color="#BCEBFA",
            text_color="#FFFFFF",
            font=("Segoe UI Symbol", 22, "bold"),
            command=command,
        )

    def build_options_column(self, parent):
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(3, weight=1)

        mode_card = self.option_card(right)
        mode_card.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        self.card_title(mode_card, "Modo de respiración").pack(
            anchor="w",
            padx=20,
            pady=(18, 8),
        )

        self.mode_combo = ctk.CTkComboBox(
            mode_card,
            values=[mode["nombre"] for mode in self.modes],
            command=self.change_mode,
            height=40,
            corner_radius=10,
            fg_color="#111C32",
            border_color="#3D4E6C",
            button_color="#315D7D",
            button_hover_color="#4E86A5",
            dropdown_fg_color="#182642",
            dropdown_hover_color="#315D7D",
            text_color=self.TEXT,
        )
        self.mode_combo.pack(fill="x", padx=20, pady=(0, 18))
        self.mode_combo.set(self.modes[0]["nombre"])

        sound_card = self.option_card(right)
        sound_card.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        self.card_title(sound_card, "Sonido ambiental").pack(
            anchor="w",
            padx=20,
            pady=(18, 8),
        )

        track_names = list(self.track_by_name) or ["Sin sonidos disponibles"]
        self.sound_combo = ctk.CTkComboBox(
            sound_card,
            values=track_names,
            command=self.change_track,
            height=40,
            corner_radius=10,
            fg_color="#111C32",
            border_color="#3D4E6C",
            button_color="#315D7D",
            button_hover_color="#4E86A5",
            dropdown_fg_color="#182642",
            dropdown_hover_color="#315D7D",
            text_color=self.TEXT,
        )
        self.sound_combo.pack(fill="x", padx=20, pady=(0, 18))
        if self.selected_track:
            self.sound_combo.set(self.selected_track["title"])

        quote_card = self.option_card(right)
        quote_card.grid(row=2, column=0, sticky="ew", pady=(0, 14))

        self.card_title(quote_card, "Recomendación de hoy").pack(
            anchor="w",
            padx=20,
            pady=(18, 6),
        )
        ctk.CTkLabel(
            quote_card,
            text=(
                "“Cierra los ojos y concéntrate en tu respiración.\n"
                "Este momento es solo para ti; recupera tu energía\n"
                "antes de volver a tus actividades.”"
            ),
            justify="left",
            anchor="w",
            font=("Segoe UI", 14, "italic"),
            text_color=self.TEXT_SOFT,
        ).pack(fill="x", padx=20, pady=(0, 18))

        self.status_label = ctk.CTkLabel(
            right,
            text="Elige un patrón y comienza cuando estés listo.",
            justify="left",
            anchor="w",
            font=("Segoe UI", 12),
            text_color=self.TEXT_SOFT,
        )
        self.status_label.grid(row=3, column=0, sticky="new", padx=4)

        ctk.CTkButton(
            right,
            text="Finalizar sesión  🍃",
            height=44,
            corner_radius=22,
            fg_color="#243450",
            hover_color="#5A3445",
            border_width=1,
            border_color="#64738D",
            text_color=self.TEXT,
            font=("Segoe UI", 14, "bold"),
            command=self.finish_session,
        ).grid(row=4, column=0, sticky="e", pady=(12, 0))

    def option_card(self, master):
        return ctk.CTkFrame(
            master,
            fg_color=self.CARD,
            border_width=1,
            border_color="#354663",
            corner_radius=18,
        )

    def card_title(self, master, text):
        return ctk.CTkLabel(
            master,
            text=text,
            font=("Segoe UI", 14, "bold"),
            text_color=self.GOLD,
        )

    def change_mode(self, selected_name):
        for index, mode in enumerate(self.modes):
            if mode["nombre"] == selected_name:
                self.mode_index = index
                self.reset_phase()
                self.status_label.configure(
                    text=f"Patrón seleccionado: {mode['nombre']}."
                )
                break

    def change_track(self, selected_name):
        track = self.track_by_name.get(selected_name)
        if not track:
            return

        self.selected_track = track
        if self.is_started and not self.is_paused:
            self.play_selected_audio()

    def change_volume(self, value):
        SoundPlayer.set_volume(float(value))

    def toggle_session(self):
        if not self.is_started:
            self.is_started = True
            self.is_paused = False
            self.play_button.configure(text="Ⅱ")
            self.instruction_text = self.phase_names[self.phase_index]
            self.play_selected_audio()
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            self.play_button.configure(text="▶")
            self.instruction_text = "Sesión pausada"
            SoundPlayer.pause()
            self.status_label.configure(text="La sesión está en pausa.")
        else:
            self.play_button.configure(text="Ⅱ")
            self.instruction_text = self.phase_names[self.phase_index]
            status = SoundPlayer.get_status()
            if status.get("paused"):
                SoundPlayer.resume()
            else:
                self.play_selected_audio()
            self.status_label.configure(text="Sesión de calma en curso.")

    def play_selected_audio(self):
        if not self.selected_track:
            self.status_label.configure(
                text="La respiración inició sin sonido ambiental."
            )
            return

        result = SoundPlayer.play_calm_mode(self.selected_track["file"])
        self.status_label.configure(
            text=result.get("message", "Sonido ambiental iniciado."),
            text_color=self.TEXT_SOFT if result.get("success") else "#FFB4B4",
        )

    def reset_phase(self):
        self.phase_index = 0
        self.phase_elapsed = 0.0
        self.bubble_scale = 0.80
        self.timer_text = "--"
        self.instruction_text = (
            self.phase_names[0]
            if self.is_started and not self.is_paused
            else "Listo para comenzar"
        )

    def next_phase(self):
        self.phase_index = (self.phase_index + 1) % len(self.current_phases)
        self.phase_elapsed = 0.0
        self.skip_empty_phases()
        self.instruction_text = self.phase_names[self.phase_index]

    def skip_empty_phases(self):
        attempts = 0
        while self.current_phases[self.phase_index] == 0 and attempts < 4:
            self.phase_index = (self.phase_index + 1) % 4
            attempts += 1

    def start_animation_loop(self):
        if not self.winfo_exists():
            return

        self.animation_time += 0.04

        if self.is_started and not self.is_paused:
            self.update_breathing(0.04)

        self.canvas.redraw()
        self.animation_job = self.after(40, self.start_animation_loop)

    def update_breathing(self, delta):
        self.skip_empty_phases()
        duration = self.current_phases[self.phase_index]

        if duration <= 0:
            return

        self.phase_elapsed += delta

        if self.phase_elapsed >= duration:
            self.phase_index = (self.phase_index + 1) % 4
            self.phase_elapsed = 0.0
            self.skip_empty_phases()
            duration = self.current_phases[self.phase_index]

        progress = min(self.phase_elapsed / max(duration, 0.01), 1.0)

        if self.phase_index == 0:
            self.bubble_scale = 0.80 + 0.38 * progress
        elif self.phase_index == 1:
            self.bubble_scale = 1.18
        elif self.phase_index == 2:
            self.bubble_scale = 1.18 - 0.38 * progress
        else:
            self.bubble_scale = 0.80

        remaining = max(1, math.ceil(duration - self.phase_elapsed))
        self.timer_text = str(remaining)
        self.instruction_text = self.phase_names[self.phase_index]

    def finish_session(self):
        self.is_started = False
        self.is_paused = True
        self.play_button.configure(text="▶")
        SoundPlayer.stop()
        self.reset_phase()
        self.status_label.configure(
            text="Sesión finalizada. Tómate un momento antes de continuar.",
            text_color=self.TEXT_SOFT,
        )

    def on_destroy(self, event):
        if event.widget is not self:
            return

        if self.animation_job:
            try:
                self.after_cancel(self.animation_job)
            except Exception:
                pass
            self.animation_job = None


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.geometry("1100x750")
    root.minsize(980, 620)
    CalmModeView(root).pack(fill="both", expand=True)
    root.mainloop()