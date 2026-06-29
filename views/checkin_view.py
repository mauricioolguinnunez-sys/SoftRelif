import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from components import (
    SoftCard,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    SmallLabel,
    PrimaryButton,
)

from utils.theme_manager import ThemeManager


class CheckinView(ctk.CTkFrame):
    """
    Vista Check-in.

    RF cubiertos:
    - RF-007 Registrar check-in emocional.
    - RF-008 Seleccionar estado de ánimo.
    - RF-009 Escribir frase motivacional.
    - RF-010 Visualizar frase en Home.
    - RF-011 Visualizar estado actual.
    - RF-012 Generar recomendaciones automáticas.
    """

    def __init__(self, master, app=None, user=None):
        self.app = app
        self.user = user
        self.theme_name = self.get_theme_name()
        self.theme = ThemeManager.get_theme(self.theme_name)

        super().__init__(
            master,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=0
        )

        self.metric_vars = {}
        self.metric_value_labels = {}
        self.mood_buttons = {}
        self.selected_mood = None

        self.recommendation_title = None
        self.recommendation_text = None
        self.phrase_box = None
        self.counter_label = None

        self.metrics = [
            ("stress", "Estrés", "Nivel de tensión", "⚡", 4, "#9B7CF3"),
            ("energy", "Energía", "Vitalidad física y mental", "🍃", 7, "#62C79A"),
            ("focus", "Enfoque", "Concentración actual", "🎯", 6, "#7DA7FF"),
            ("mental_fatigue", "Cansancio mental", "Fatiga cognitiva", "🧠", 8, "#A97DF5"),
        ]

        self.moods = [
            ("Tranquilo", "🙂", "#62C79A"),
            ("Saturado", "😵", "#F0AE7A"),
            ("Ansioso", "😟", "#B78BFA"),
            ("Cansado", "😴", "#7DA7FF"),
            ("Motivado", "⭐", "#F0C95D"),
        ]

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_view()

    # =====================================================
    # HELPERS
    # =====================================================

    def c(self, key, default):
        return self.theme.get(key, default)

    def get_theme_name(self):
        if self.user:
            return self.user.get("tema_visual", "light")
        return "light"

    def user_name(self):
        if self.user:
            return self.user.get("nombre", "Usuario")
        return "Usuario"

    def value(self, key):
        return int(round(float(self.metric_vars[key].get())))

    def make_card(self, parent, radius=22):
        return SoftCard(
            parent,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=radius
        )

    def range_label(self, value, kind):
        if kind == "stress" or kind == "mental_fatigue":
            if value <= 3:
                return "Bajo"
            if value <= 6:
                return "Moderado"
            return "Alto"

        if value <= 3:
            return "Baja"
        if value <= 6:
            return "Media"
        return "Buena"

    # =====================================================
    # BUILD
    # =====================================================

    def build_view(self):
        self.header()
        self.left_panel()
        self.right_panel()
        self.update_recommendation()

    def header(self):
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=30,
            pady=(24, 16)
        )

        box.grid_columnconfigure(0, weight=1)

        title = ctk.CTkFrame(box, fg_color="transparent")
        title.grid(row=0, column=0, sticky="w")

        TitleLabel(
            title,
            "Check-in",
            size=34,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title,
            "Identifica cómo te sientes hoy",
            size=15,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w")

        user = ctk.CTkFrame(box, fg_color="transparent")
        user.grid(row=0, column=1, sticky="e")

        SmallLabel(
            user,
            f"Hola, {self.user_name()}",
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="e")

        SmallLabel(
            user,
            "Todo en equilibrio",
            size=12,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="e")

    def left_panel(self):
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(30, 15),
            pady=(0, 26)
        )

        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        self.metrics_card(left)
        self.mood_card(left)
        self.phrase_card(left)

    def right_panel(self):
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(15, 30),
            pady=(0, 26)
        )

        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)

        self.recommendation_card(right)
        self.action_card(right)
        self.tip_card(right)

        PrimaryButton(
            right,
            text="Guardar check-in",
            height=48,
            command=self.save_checkin
        ).grid(row=3, column=0, sticky="ew")

    # =====================================================
    # METRICS
    # =====================================================

    def metrics_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        TitleLabel(
            card,
            "1. ¿Cómo estás en estas áreas hoy?",
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 4))

        SmallLabel(
            card,
            "Valora del 1 al 10, donde 1 es muy bajo y 10 es excelente.",
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 14))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=24, pady=(0, 20))

        for item in self.metrics:
            self.metric_row(body, *item)

    def metric_row(self, parent, key, title, subtitle, icon, start_value, color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=8)

        row.grid_columnconfigure(1, weight=0)
        row.grid_columnconfigure(2, weight=1)
        row.grid_columnconfigure(3, weight=0)

        ctk.CTkLabel(
            row,
            text=icon,
            width=46,
            height=46,
            corner_radius=23,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=color,
            font=("Arial", 24)
        ).grid(row=0, column=0, padx=(0, 14))

        text = ctk.CTkFrame(row, fg_color="transparent")
        text.grid(row=0, column=1, sticky="w", padx=(0, 18))

        TitleLabel(
            text,
            title,
            size=16,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        SmallLabel(
            text,
            subtitle,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w")

        self.metric_vars[key] = ctk.DoubleVar(value=start_value)

        slider = ctk.CTkSlider(
            row,
            from_=1,
            to=10,
            number_of_steps=9,
            variable=self.metric_vars[key],
            fg_color=self.c("card_border", "#E5E7EB"),
            progress_color=color,
            button_color="#FFFFFF",
            button_hover_color=color,
            command=lambda _=None: self.on_metric_change()
        )
        slider.grid(row=0, column=2, sticky="ew", padx=(0, 16))

        value_label = ctk.CTkLabel(
            row,
            text=str(start_value),
            width=34,
            height=34,
            corner_radius=17,
            fg_color=color,
            text_color="white",
            font=("Arial", 14, "bold")
        )
        value_label.grid(row=0, column=3)

        self.metric_value_labels[key] = value_label

    def on_metric_change(self):
        for key, label in self.metric_value_labels.items():
            label.configure(text=str(self.value(key)))

        self.update_recommendation()

    # =====================================================
    # MOODS
    # =====================================================

    def mood_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 18))

        TitleLabel(
            card,
            "2. ¿Cómo describirías tu estado de ánimo?",
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 4))

        SmallLabel(
            card,
            "Selecciona la emoción que mejor te representa hoy.",
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 16))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=18, pady=(0, 20))

        for col, (mood, icon, color) in enumerate(self.moods):
            btn = ctk.CTkButton(
                body,
                text=f"{icon}  {mood}",
                height=44,
                corner_radius=14,
                fg_color=self.c("app_bg", "#F6F7FB"),
                hover_color=color,
                text_color=self.c("text", "#1E1B4B"),
                border_width=1,
                border_color=self.c("card_border", "#E5E7EB"),
                command=lambda m=mood: self.select_mood(m)
            )
            btn.grid(row=0, column=col, sticky="ew", padx=5)
            body.grid_columnconfigure(col, weight=1)
            self.mood_buttons[mood] = (btn, color)

    def select_mood(self, mood):
        self.selected_mood = mood

        for name, (button, color) in self.mood_buttons.items():
            selected = name == mood

            button.configure(
                fg_color=color if selected else self.c("app_bg", "#F6F7FB"),
                text_color="white" if selected else self.c("text", "#1E1B4B"),
                border_color=color if selected else self.c("card_border", "#E5E7EB")
            )

        self.update_recommendation()

    # =====================================================
    # PHRASE
    # =====================================================

    def phrase_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=2, column=0, sticky="nsew")

        TitleLabel(
            card,
            "3. Escribe una frase motivacional",
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 4))

        SmallLabel(
            card,
            "Esta frase se mostrará después como frase para hoy.",
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 14))

        self.phrase_box = ctk.CTkTextbox(
            card,
            height=128,
            corner_radius=15,
            fg_color=self.c("app_bg", "#F6F7FB"),
            text_color=self.c("text", "#1E1B4B"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            font=("Arial", 14)
        )
        self.phrase_box.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        self.phrase_box.insert("1.0", "Hoy puedo dar un pequeño paso por mi bienestar.")
        self.phrase_box.bind("<KeyRelease>", self.update_counter)

        self.counter_label = SmallLabel(
            card,
            "0/250",
            text_color=self.c("text_soft", "#6B7280")
        )
        self.counter_label.pack(anchor="e", padx=24, pady=(0, 18))

        self.update_counter()

    def phrase(self):
        if not self.phrase_box:
            return ""
        return self.phrase_box.get("1.0", "end-1c").strip()

    def update_counter(self, event=None):
        text = self.phrase()

        if len(text) > 250:
            text = text[:250]
            self.phrase_box.delete("1.0", "end")
            self.phrase_box.insert("1.0", text)

        if self.counter_label:
            self.counter_label.configure(text=f"{len(text)}/250")

    # =====================================================
    # RIGHT CARDS
    # =====================================================

    def recommendation_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        ctk.CTkLabel(
            card,
            text="🌿",
            width=82,
            height=82,
            corner_radius=41,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#7C3AED"),
            font=("Arial", 38)
        ).pack(anchor="center", pady=(24, 10))

        TitleLabel(
            card,
            "Recomendación para ti",
            size=21,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(0, 4))

        SmallLabel(
            card,
            "Basado en tu estado actual",
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 12))

        self.recommendation_title = TitleLabel(
            card,
            "",
            size=18,
            text_color=self.c("text", "#1E1B4B")
        )
        self.recommendation_title.pack(anchor="w", padx=24, pady=(0, 4))

        self.recommendation_text = BodyLabel(
            card,
            "",
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=310
        )
        self.recommendation_text.pack(anchor="w", padx=24, pady=(0, 24))

    def action_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        TitleLabel(
            card,
            "Acción sugerida",
            size=18,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 6))

        BodyLabel(
            card,
            "También puedes iniciar Modo Calma, escuchar sonidos o hacer un microdescanso.",
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=310
        ).pack(anchor="w", padx=24, pady=(0, 20))

    def tip_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=2, column=0, sticky="nsew", pady=(0, 16))

        TitleLabel(
            card,
            "Pequeño paso, gran cambio",
            size=18,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 6))

        BodyLabel(
            card,
            "Dedicar unos minutos a tu bienestar puede ayudarte a recuperar equilibrio durante el día.",
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=310
        ).pack(anchor="w", padx=24, pady=(0, 20))

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    def generate_recommendation(self):
        stress = self.value("stress")
        energy = self.value("energy")
        focus = self.value("focus")
        fatigue = self.value("mental_fatigue")

        if stress >= 7 or self.selected_mood == "Ansioso":
            return (
                "Modo Calma · 7 min",
                "Relaja tu mente y reduce el estrés con una pausa guiada."
            )

        if fatigue >= 7 or self.selected_mood == "Cansado":
            return (
                "Microdescanso · 5 min",
                "Tómate una pausa breve para reducir la fatiga mental."
            )

        if focus <= 4 or self.selected_mood == "Saturado":
            return (
                "Sonidos ambientales · 10 min",
                "Usa un sonido suave para bajar la saturación y recuperar enfoque."
            )

        if energy <= 4:
            return (
                "Pausa activa · 5 min",
                "Una pausa breve puede ayudarte a recuperar energía gradualmente."
            )

        if self.selected_mood == "Motivado":
            return (
                "Continuar en equilibrio",
                "Tu estado actual es favorable. Mantén el ritmo y cuida tus pausas."
            )

        return (
            "Modo Calma · 5 min",
            "Estás en un punto estable. Una pausa breve puede conservar ese equilibrio."
        )

    def update_recommendation(self):
        if not self.recommendation_title or not self.recommendation_text:
            return

        title, text = self.generate_recommendation()
        self.recommendation_title.configure(text=title)
        self.recommendation_text.configure(text=text)

    # =====================================================
    # SAVE
    # =====================================================

    def build_payload(self):
        title, text = self.generate_recommendation()

        return {
            "user_id": self.user.get("id_usuario") if self.user else None,
            "user_name": self.user_name(),
            "stress": self.value("stress"),
            "energy": self.value("energy"),
            "focus": self.value("focus"),
            "mental_fatigue": self.value("mental_fatigue"),
            "stress_range": self.range_label(self.value("stress"), "stress"),
            "energy_range": self.range_label(self.value("energy"), "energy"),
            "focus_range": self.range_label(self.value("focus"), "focus"),
            "mental_fatigue_range": self.range_label(self.value("mental_fatigue"), "mental_fatigue"),
            "mood": self.selected_mood,
            "phrase": self.phrase(),
            "recommendation_title": title,
            "recommendation_text": text,
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def save_checkin(self):
        if not self.selected_mood:
            messagebox.showwarning(
                "Check-in incompleto",
                "Selecciona un estado de ánimo antes de guardar."
            )
            return

        if not self.phrase():
            messagebox.showwarning(
                "Check-in incompleto",
                "Escribe una frase motivacional antes de guardar."
            )
            return

        payload = self.build_payload()

        if self.app is not None:
            self.app.last_checkin = payload

            if not hasattr(self.app, "checkin_history"):
                self.app.checkin_history = []

            self.app.checkin_history.insert(0, payload)

            if self.app.current_user is not None:
                self.app.current_user["ultimo_checkin"] = payload
                self.app.current_user["frase_hoy"] = payload["phrase"]

        print("CHECK-IN GUARDADO:", payload)

        messagebox.showinfo(
            "Check-in guardado",
            "Tu check-in se guardó correctamente."
        )