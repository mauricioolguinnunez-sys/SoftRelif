import customtkinter as ctk
from tkinter import messagebox

from components import TitleLabel, SubtitleLabel
from components.checkin_components import (
    MetricsCard,
    MoodCard,
    PhraseCard,
    RecommendationPanel,
)

from utils.theme_manager import ThemeManager


class CheckinView(ctk.CTkFrame):
    """
    Check-in emocional de SoftRelief.

    RF cubiertos:
    RF-007 Registrar check-in emocional.
    RF-008 Seleccionar estado de ánimo.
    RF-009 Escribir frase motivacional.
    RF-010 Visualizar frase en Home.
    RF-011 Visualizar estado actual.
    RF-012 Generar recomendaciones automáticas.
    """

    def __init__(self, master, app=None, user=None):
        self.app = app
        self.user = user

        self.theme_name = "light"

        if self.user:
            self.theme_name = self.user.get("tema_visual", "light")

        self.theme = ThemeManager.get_theme(self.theme_name)

        super().__init__(
            master,
            fg_color=self.theme.get("app_bg", "#F6F7FB"),
            corner_radius=0
        )

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.metrics_card = None
        self.mood_card = None
        self.phrase_card = None
        self.recommendation_panel = None

        self.build_view()

    # =====================================================
    # BUILD
    # =====================================================

    def build_view(self):
        self.build_header()
        self.build_content()
        self.update_recommendation()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=30,
            pady=(24, 16)
        )

        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        TitleLabel(
            left,
            "Check-in",
            size=34,
            text_color=self.theme.get("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            left,
            "Identifica cómo te sientes hoy",
            size=15,
            text_color=self.theme.get("text_soft", "#6B7280")
        ).pack(anchor="w")

    def build_content(self):
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(30, 15),
            pady=(0, 24)
        )

        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(15, 30),
            pady=(0, 24)
        )

        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(2, weight=1)

        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)

        self.metrics_card = MetricsCard(
            left_panel,
            theme=self.theme,
            command=self.update_recommendation
        )
        self.metrics_card.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        self.mood_card = MoodCard(
            left_panel,
            theme=self.theme,
            command=self.update_recommendation
        )
        self.mood_card.grid(row=1, column=0, sticky="ew", pady=(0, 18))

        self.phrase_card = PhraseCard(
            left_panel,
            theme=self.theme,
            default_text="Hoy puedo dar un pequeño paso por mi bienestar."
        )
        self.phrase_card.grid(row=2, column=0, sticky="nsew")

        self.recommendation_panel = RecommendationPanel(
            right_panel,
            theme=self.theme,
            save_command=self.save_checkin
        )
        self.recommendation_panel.grid(row=0, column=0, sticky="nsew")

    # =====================================================
    # DATA
    # =====================================================

    def get_user_name(self):
        if self.user:
            return self.user.get("nombre", "Usuario")

        return "Usuario"

    def generate_recommendation(self):
        values = self.metrics_card.get_values()
        mood = self.mood_card.get_selected()

        stress = values["stress"]
        energy = values["energy"]
        focus = values["focus"]
        fatigue = values["mental_fatigue"]

        if stress >= 7 or mood == "Ansioso":
            return (
                "Modo Calma · 7 min",
                "Relaja tu mente y reduce el estrés con una pausa guiada y respiración consciente."
            )

        if fatigue >= 7 or mood == "Cansado":
            return (
                "Microdescanso · 5 min",
                "Tómate una pausa breve para reducir la fatiga cognitiva y recuperar claridad."
            )

        if focus <= 4 or mood == "Saturado":
            return (
                "Sonidos ambientales · 10 min",
                "Usa un sonido suave de fondo para bajar la saturación mental y recuperar enfoque."
            )

        if energy <= 4:
            return (
                "Microdescanso activo · 5 min",
                "Una pausa breve y consciente puede ayudarte a recuperar energía de forma gradual."
            )

        if mood == "Motivado":
            return (
                "Continuar en equilibrio",
                "Tu estado actual es favorable. Mantén el ritmo y reserva unos minutos para cuidarte."
            )

        return (
            "Modo Calma · 5 min",
            "Estás en un punto estable. Una pequeña pausa guiada puede ayudarte a conservar ese equilibrio."
        )

    def update_recommendation(self):
        if not self.metrics_card or not self.recommendation_panel:
            return

        title, text = self.generate_recommendation()
        self.recommendation_panel.update(title, text)

    def build_payload(self):
        values = self.metrics_card.get_values()
        mood = self.mood_card.get_selected()
        phrase = self.phrase_card.get_text()

        recommendation_title, recommendation_text = self.generate_recommendation()

        return {
            "user_id": self.user.get("id_usuario") if self.user else None,
            "user_name": self.get_user_name(),
            "stress": values["stress"],
            "energy": values["energy"],
            "focus": values["focus"],
            "mental_fatigue": values["mental_fatigue"],
            "mood": mood,
            "phrase": phrase,
            "recommendation_title": recommendation_title,
            "recommendation_text": recommendation_text,
        }

    # =====================================================
    # SAVE
    # =====================================================

    def save_checkin(self):
        mood = self.mood_card.get_selected()
        phrase = self.phrase_card.get_text()

        if not mood:
            messagebox.showwarning(
                "Check-in incompleto",
                "Selecciona un estado de ánimo antes de guardar."
            )
            return

        if not phrase:
            messagebox.showwarning(
                "Check-in incompleto",
                "Escribe una frase motivacional antes de guardar."
            )
            return

        payload = self.build_payload()

        if self.app is not None:
            self.app.last_checkin = payload

            if self.app.current_user is not None:
                self.app.current_user["ultimo_checkin"] = payload
                self.app.current_user["frase_hoy"] = payload["phrase"]

        print("CHECK-IN GUARDADO:", payload)

        messagebox.showinfo(
            "Check-in guardado",
            "Tu check-in se guardó correctamente."
        )