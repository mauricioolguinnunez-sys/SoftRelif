import math
import tkinter as tk


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
