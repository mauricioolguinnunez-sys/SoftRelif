import customtkinter as ctk

from components.cards import SoftCard
from components.labels import TitleLabel, SubtitleLabel, BodyLabel, SmallLabel
from components.buttons import PrimaryButton


class MetricSlider(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title,
        subtitle,
        value=5,
        color="#7C3AED",
        theme=None,
        command=None
    ):
        super().__init__(master, fg_color="transparent")

        self.theme = theme or {}
        self.color = color
        self.command = command
        self.var = ctk.DoubleVar(value=value)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        text_box = ctk.CTkFrame(self, fg_color="transparent")
        text_box.grid(row=0, column=0, sticky="w", padx=(0, 18))

        ctk.CTkLabel(
            text_box,
            text=title,
            font=("Arial", 16, "bold"),
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_box,
            text=subtitle,
            font=("Arial", 12),
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w")

        slider_box = ctk.CTkFrame(self, fg_color="transparent")
        slider_box.grid(row=0, column=1, sticky="ew")
        slider_box.grid_columnconfigure(0, weight=1)

        number_box = ctk.CTkFrame(slider_box, fg_color="transparent")
        number_box.grid(row=0, column=0, sticky="ew")

        for i in range(1, 11):
            ctk.CTkLabel(
                number_box,
                text=str(i),
                font=("Arial", 10),
                text_color=self.c("text_soft", "#6B7280")
            ).grid(row=0, column=i - 1, padx=8)

        self.slider = ctk.CTkSlider(
            slider_box,
            from_=1,
            to=10,
            number_of_steps=9,
            variable=self.var,
            progress_color=color,
            button_color="#FFFFFF",
            button_hover_color=color,
            fg_color="#E6E9F2",
            command=self.on_change
        )
        self.slider.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        self.value_label = ctk.CTkLabel(
            self,
            text=str(self.get_value()),
            width=34,
            height=34,
            corner_radius=17,
            fg_color=color,
            text_color="white",
            font=("Arial", 14, "bold")
        )
        self.value_label.grid(row=0, column=2, padx=(16, 0))

    def c(self, key, default):
        return self.theme.get(key, default)

    def get_value(self):
        return int(round(float(self.var.get())))

    def on_change(self, _=None):
        self.value_label.configure(text=str(self.get_value()))

        if self.command:
            self.command()


class MetricsCard(SoftCard):
    def __init__(self, master, theme, command=None):
        super().__init__(
            master,
            fg_color=theme.get("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=theme.get("card_border", "#E5E7EB"),
            corner_radius=20
        )

        self.theme = theme
        self.command = command
        self.metrics = {}

        TitleLabel(
            self,
            "1. ¿Cómo estás en estas áreas hoy?",
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 4))

        SmallLabel(
            self,
            "Valora del 1 al 10, donde 1 es muy bajo y 10 es excelente.",
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 14))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="x", padx=24, pady=(0, 20))

        self.add_metric(
            body,
            key="stress",
            title="Estrés",
            subtitle="Nivel de tensión",
            value=4,
            color="#9B7CF3"
        )

        self.add_metric(
            body,
            key="energy",
            title="Energía",
            subtitle="Vitalidad física y mental",
            value=7,
            color="#62C79A"
        )

        self.add_metric(
            body,
            key="focus",
            title="Enfoque",
            subtitle="Concentración actual",
            value=6,
            color="#7DA7FF"
        )

        self.add_metric(
            body,
            key="mental_fatigue",
            title="Cansancio mental",
            subtitle="Fatiga cognitiva",
            value=8,
            color="#A97DF5"
        )

    def c(self, key, default):
        return self.theme.get(key, default)

    def add_metric(self, parent, key, title, subtitle, value, color):
        metric = MetricSlider(
            parent,
            title=title,
            subtitle=subtitle,
            value=value,
            color=color,
            theme=self.theme,
            command=self.command
        )
        metric.pack(fill="x", pady=9)

        self.metrics[key] = metric

    def get_values(self):
        return {
            key: metric.get_value()
            for key, metric in self.metrics.items()
        }


class MoodCard(SoftCard):
    def __init__(self, master, theme, command=None):
        super().__init__(
            master,
            fg_color=theme.get("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=theme.get("card_border", "#E5E7EB"),
            corner_radius=20
        )

        self.theme = theme
        self.command = command
        self.selected_mood = None
        self.buttons = {}

        TitleLabel(
            self,
            "2. ¿Cómo describirías tu estado de ánimo?",
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 4))

        SmallLabel(
            self,
            "Selecciona la emoción que mejor te representa hoy.",
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 16))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=(0, 20))

        moods = [
            ("Tranquilo", "#62C79A"),
            ("Saturado", "#F0AE7A"),
            ("Ansioso", "#B78BFA"),
            ("Cansado", "#7DA7FF"),
            ("Motivado", "#F0C95D"),
        ]

        for index, (mood, color) in enumerate(moods):
            button = ctk.CTkButton(
                body,
                text=mood,
                height=42,
                corner_radius=14,
                fg_color=self.c("app_bg", "#F6F7FB"),
                hover_color=color,
                text_color=self.c("text", "#1E1B4B"),
                border_width=1,
                border_color=self.c("card_border", "#D9DEEA"),
                command=lambda m=mood: self.select_mood(m)
            )
            button.grid(row=0, column=index, padx=6, sticky="ew")
            body.grid_columnconfigure(index, weight=1)

            self.buttons[mood] = {
                "button": button,
                "color": color
            }

    def c(self, key, default):
        return self.theme.get(key, default)

    def select_mood(self, mood):
        self.selected_mood = mood

        for name, data in self.buttons.items():
            button = data["button"]
            color = data["color"]

            if name == mood:
                button.configure(
                    fg_color=color,
                    text_color="white",
                    border_color=color
                )
            else:
                button.configure(
                    fg_color=self.c("app_bg", "#F6F7FB"),
                    text_color=self.c("text", "#1E1B4B"),
                    border_color=self.c("card_border", "#D9DEEA")
                )

        if self.command:
            self.command()

    def get_selected(self):
        return self.selected_mood


class PhraseCard(SoftCard):
    def __init__(self, master, theme, default_text=""):
        super().__init__(
            master,
            fg_color=theme.get("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=theme.get("card_border", "#E5E7EB"),
            corner_radius=20
        )

        self.theme = theme

        TitleLabel(
            self,
            "3. Escribe una frase motivacional",
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 4))

        SmallLabel(
            self,
            "Esta frase se mostrará en tu Home como “Frase para hoy”.",
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 14))

        self.textbox = ctk.CTkTextbox(
            self,
            height=130,
            corner_radius=14,
            fg_color=self.c("app_bg", "#F6F7FB"),
            text_color=self.c("text", "#1E1B4B"),
            border_width=1,
            border_color=self.c("card_border", "#D9DEEA"),
            font=("Arial", 14)
        )
        self.textbox.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        self.textbox.insert("1.0", default_text)
        self.textbox.bind("<KeyRelease>", self.update_counter)

        self.counter = SmallLabel(
            self,
            "0/250",
            text_color=self.c("text_soft", "#6B7280")
        )
        self.counter.pack(anchor="e", padx=24, pady=(0, 18))

        self.update_counter()

    def c(self, key, default):
        return self.theme.get(key, default)

    def get_text(self):
        return self.textbox.get("1.0", "end-1c").strip()

    def update_counter(self, event=None):
        text = self.get_text()

        if len(text) > 250:
            text = text[:250]
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", text)

        self.counter.configure(text=f"{len(text)}/250")


class RecommendationPanel(ctk.CTkFrame):
    def __init__(self, master, theme, save_command=None):
        super().__init__(master, fg_color="transparent")

        self.theme = theme
        self.save_command = save_command

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.build_main_card()
        self.build_secondary_card()
        self.build_tip_card()
        self.build_button()

    def c(self, key, default):
        return self.theme.get(key, default)

    def build_main_card(self):
        card = SoftCard(
            self,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=20
        )
        card.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        TitleLabel(
            card,
            "Recomendación para ti",
            size=22,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(22, 6))

        SmallLabel(
            card,
            "Basado en tu estado actual",
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 10))

        self.title_label = TitleLabel(
            card,
            "Modo Calma · 7 min",
            size=18,
            text_color=self.c("text", "#1E1B4B")
        )
        self.title_label.pack(anchor="w", padx=24, pady=(8, 4))

        self.body_label = BodyLabel(
            card,
            "Relaja tu mente y reduce el estrés con una pausa guiada.",
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=300
        )
        self.body_label.pack(anchor="w", padx=24, pady=(0, 22))

    def build_secondary_card(self):
        card = SoftCard(
            self,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=20
        )
        card.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        TitleLabel(
            card,
            "Acción sugerida",
            size=18,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 6))

        BodyLabel(
            card,
            "También puedes usar sonidos ambientales o iniciar un microdescanso breve.",
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=300
        ).pack(anchor="w", padx=24, pady=(0, 20))

    def build_tip_card(self):
        card = SoftCard(
            self,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=20
        )
        card.grid(row=2, column=0, sticky="nsew", pady=(0, 16))

        TitleLabel(
            card,
            "Pequeño paso, gran cambio",
            size=18,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 6))

        BodyLabel(
            card,
            "Dedicar unos minutos a tu bienestar hoy puede transformar tu día.",
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=300
        ).pack(anchor="w", padx=24, pady=(0, 20))

    def build_button(self):
        PrimaryButton(
            self,
            text="Guardar check-in",
            height=46,
            command=self.save_command
        ).grid(row=3, column=0, sticky="ew")

    def update(self, title, text):
        self.title_label.configure(text=title)
        self.body_label.configure(text=text)