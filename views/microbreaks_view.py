import importlib.util
from pathlib import Path
from datetime import datetime, timezone

import customtkinter as ctk
from tkinter import messagebox

from components import (
    SoftCard,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    SmallLabel,
    PrimaryButton,
    SecondaryButton,
)

from utils.theme_manager import ThemeManager


def get_game_launcher_for_title(title):
    mappings = {
        "Patrones visuales": ("games/acomodar_cosas.py", "LibreriaZen"),
        "Toque consciente": ("games/toque inteligente.py", "PaisajeBurbujasPastel"),
        "Memoria ligera": ("games/memorama.py", "MemoramaEsteticoApp"),
        "Observa y crece": ("games/regar.py", "RefugioEstudiantil"),
    }

    module_path, class_name = mappings.get(title, (None, None))
    if not module_path or not class_name:
        return None

    file_path = Path(__file__).resolve().parents[1] / module_path
    if not file_path.exists():
        return None

    module_name = f"softrelief_game_{Path(module_path).stem.replace(' ', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, class_name)


class MicrobreaksView(ctk.CTkFrame):
    """
    Vista de Microdescansos de SoftRelief.

    RF principal:
    - RF-015 Realizar microdescansos.

    Conexión futura:
    - RF-016 Consultar historial del usuario.
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

        self.selected_category = "Todos"
        self.selected_break = None
        self.category_buttons = {}
        self.break_cards = []

        self.preview_title = None
        self.preview_duration = None
        self.preview_description = None
        self.preview_benefits = None
        self.start_button = None

        self.microbreaks = [
            {
                "title": "Pausa breve",
                "category": "Relajación",
                "duration": 5,
                "icon": "☕",
                "color": "#8EDCC7",
                "description": "Una pausa corta para soltar la tensión acumulada, respirar y reconectar contigo.",
                "benefits": ["Reduce el estrés", "Aclara tu mente", "Mejora tu enfoque"],
                "steps": [
                    "Siéntate con la espalda cómoda.",
                    "Inhala lentamente durante 4 segundos.",
                    "Exhala sin prisa durante 5 segundos.",
                    "Repite el ciclo hasta terminar la pausa."
                ],
            },
            {
                "title": "Observa y crece",
                "category": "Energía",
                "duration": 7,
                "icon": "🌱",
                "color": "#B78BFA",
                "description": "Riega el estanque y observa cómo florece el entorno mientras tu mente se sereniza.",
                "benefits": ["Relaja la mente", "Fomenta calma", "Mejora la atención"],
                "steps": [
                    "Abre el juego de observación y crecimiento.",
                    "Riega poco a poco para ver la escena cambiar.",
                    "Respira con la calma del paisaje.",
                    "Disfruta el momento sin prisa."
                ],
            },
            {
                "title": "Patrones visuales",
                "category": "Enfoque",
                "duration": 4,
                "icon": "👁",
                "color": "#8FB8FF",
                "description": "Observa, relaja tu mente y mejora tu enfoque con patrones calmantes.",
                "benefits": ["Descansa la vista", "Mejora atención", "Baja saturación"],
                "steps": [
                    "Mira un punto fijo.",
                    "Sigue un patrón visual simple.",
                    "Evita forzar la vista.",
                    "Respira lentamente."
                ],
            },
            {
                "title": "Toque consciente",
                "category": "Relajación",
                "duration": 3,
                "icon": "☝",
                "color": "#8EDCC7",
                "description": "Pequeñas interacciones para anclar tu atención en el momento presente.",
                "benefits": ["Vuelve al presente", "Reduce ansiedad", "Regula atención"],
                "steps": [
                    "Toca suavemente la mesa.",
                    "Nota la textura.",
                    "Respira mientras observas la sensación.",
                    "Repite sin juzgar."
                ],
            },
            {
                "title": "Memoria ligera",
                "category": "Creatividad",
                "duration": 6,
                "icon": "🧠",
                "color": "#C59BFF",
                "description": "Ejercita tu memoria de forma amable con una actividad breve y sencilla.",
                "benefits": ["Activa memoria", "Estimula creatividad", "Rompe rutina"],
                "steps": [
                    "Observa 4 elementos cercanos.",
                    "Cierra los ojos unos segundos.",
                    "Recuerda el orden.",
                    "Repite con calma."
                ],
            },
        ]

        self.selected_break = self.microbreaks[0]

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

    def get_user_name(self):
        if self.user:
            return self.user.get("nombre", "Usuario")
        return "Usuario"

    # =====================================================
    # BUILD
    # =====================================================

    def build_view(self):
        self.build_header()
        self.build_left_panel()
        self.build_preview_panel()

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
        header.grid_columnconfigure(1, weight=0)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        TitleLabel(
            title_box,
            "Microdescansos y minijuegos",
            size=34,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title_box,
            "Pequeñas pausas para recargar tu mente y volver al presente.",
            size=15,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(2, 0))

        user_box = ctk.CTkFrame(header, fg_color="transparent")
        user_box.grid(row=0, column=1, sticky="e")

        SmallLabel(
            user_box,
            f"Hola, {self.get_user_name()}",
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="e")

        SmallLabel(
            user_box,
            "Todo en equilibrio",
            size=12,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="e")

    def build_left_panel(self):
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(30, 15),
            pady=(0, 26)
        )

        left.grid_columnconfigure(0, weight=1)
        left.grid_columnconfigure(1, weight=1)
        left.grid_rowconfigure(1, weight=1)

        self.build_filters(left)
        self.cards_area = ctk.CTkFrame(left, fg_color="transparent")
        self.cards_area.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.render_break_cards()

    def build_filters(self, parent):
        filters = ctk.CTkFrame(parent, fg_color="transparent")
        filters.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))

        categories = ["Todos", "Relajación", "Enfoque", "Energía", "Creatividad"]

        for index, category in enumerate(categories):
            btn = SecondaryButton(
                filters,
                text=category,
                height=38,
                command=lambda c=category: self.select_category(c)
            )
            btn.grid(row=0, column=index, padx=(0, 10), sticky="ew")
            filters.grid_columnconfigure(index, weight=1)
            self.category_buttons[category] = btn

        self.refresh_category_buttons()

    def render_break_cards(self):
        for widget in self.cards_area.winfo_children():
            widget.destroy()

        self.break_cards.clear()

        visible_items = [
            item for item in self.microbreaks
            if self.selected_category == "Todos" or item["category"] == self.selected_category
        ]

        for index, item in enumerate(visible_items):
            row = index // 2
            col = index % 2

            card = self.create_break_card(self.cards_area, item)
            card.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=(0, 16) if col == 0 else (0, 0),
                pady=(0, 18)
            )

            self.cards_area.grid_columnconfigure(col, weight=1)
            self.break_cards.append((card, item))

        self.refresh_break_cards()

    def create_break_card(self, parent, item):
        selected = item == self.selected_break

        card = SoftCard(
            parent,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=2 if selected else 1,
            border_color=item["color"] if selected else self.c("card_border", "#E5E7EB"),
            corner_radius=20
        )

        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)

        icon = ctk.CTkLabel(
            card,
            text=item["icon"],
            width=86,
            height=86,
            corner_radius=43,
            fg_color=item["color"],
            text_color="white",
            font=("Arial", 36)
        )
        icon.grid(row=0, column=0, rowspan=3, padx=22, pady=26)

        TitleLabel(
            card,
            item["title"],
            size=19,
            text_color=self.c("text", "#1E1B4B")
        ).grid(row=0, column=1, sticky="w", padx=(0, 22), pady=(26, 4))

        SmallLabel(
            card,
            f"◷ {item['duration']} min",
            text_color=self.c("text_soft", "#6B7280")
        ).grid(row=1, column=1, sticky="w", padx=(0, 22))

        BodyLabel(
            card,
            item["description"],
            size=13,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=230
        ).grid(row=2, column=1, sticky="w", padx=(0, 22), pady=(10, 26))

        card.bind("<Button-1>", lambda event, i=item: self.select_break(i))
        icon.bind("<Button-1>", lambda event, i=item: self.select_break(i))

        return card

    def build_preview_panel(self):
        self.preview = SoftCard(
            self,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=22
        )
        self.preview.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(15, 30),
            pady=(0, 26)
        )

        self.preview.grid_columnconfigure(0, weight=1)
        self.preview.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self.preview, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 10))
        top.grid_columnconfigure(0, weight=1)

        TitleLabel(
            top,
            "Vista previa",
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).grid(row=0, column=0, sticky="w")

        SmallLabel(
            top,
            "ⓘ",
            size=15,
            text_color=self.c("text_soft", "#6B7280")
        ).grid(row=0, column=1, sticky="e")

        self.preview_image = ctk.CTkFrame(
            self.preview,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=20
        )
        self.preview_image.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))
        self.preview_image.grid_columnconfigure(0, weight=1)
        self.preview_image.grid_rowconfigure(0, weight=1)

        self.preview_icon = ctk.CTkLabel(
            self.preview_image,
            text="☕",
            width=120,
            height=120,
            corner_radius=60,
            fg_color="#8EDCC7",
            text_color="white",
            font=("Arial", 52)
        )
        self.preview_icon.grid(row=0, column=0, pady=38)

        info = ctk.CTkFrame(self.preview, fg_color="transparent")
        info.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))
        info.grid_columnconfigure(0, weight=1)

        self.preview_title = TitleLabel(
            info,
            "",
            size=21,
            text_color=self.c("text", "#1E1B4B")
        )
        self.preview_title.grid(row=0, column=0, sticky="w")

        self.preview_duration = SmallLabel(
            info,
            "",
            text_color=self.c("accent", "#7C3AED")
        )
        self.preview_duration.grid(row=0, column=1, sticky="e")

        self.preview_description = BodyLabel(
            info,
            "",
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=360
        )
        self.preview_description.grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))

        self.preview_benefits = ctk.CTkFrame(self.preview, fg_color="transparent")
        self.preview_benefits.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 20))

        self.start_button = PrimaryButton(
            self.preview,
            text="▶  Comenzar",
            height=48,
            command=self.start_microbreak
        )
        self.start_button.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 24))

        self.update_preview()

    # =====================================================
    # EVENTS
    # =====================================================

    def select_category(self, category):
        self.selected_category = category
        self.refresh_category_buttons()
        self.render_break_cards()

    def select_break(self, item):
        self.selected_break = item
        self.refresh_break_cards()
        self.update_preview()

    def refresh_category_buttons(self):
        for category, button in self.category_buttons.items():
            selected = category == self.selected_category

            button.configure(
                fg_color=self.c("accent_soft", "#EDE9FE") if selected else self.c("card_bg", "#FFFFFF"),
                text_color=self.c("accent", "#7C3AED") if selected else self.c("text", "#1E1B4B"),
                border_color=self.c("accent", "#7C3AED") if selected else self.c("card_border", "#E5E7EB")
            )

    def refresh_break_cards(self):
        for card, item in self.break_cards:
            selected = item == self.selected_break
            card.configure(
                border_width=2 if selected else 1,
                border_color=item["color"] if selected else self.c("card_border", "#E5E7EB")
            )

    def update_preview(self):
        item = self.selected_break

        if not item:
            return

        self.preview_icon.configure(
            text=item["icon"],
            fg_color=item["color"]
        )

        self.preview_title.configure(text=item["title"])
        self.preview_duration.configure(text=f"◷ Duración {item['duration']} min")
        self.preview_description.configure(text=item["description"])

        for widget in self.preview_benefits.winfo_children():
            widget.destroy()

        for index, benefit in enumerate(item["benefits"]):
            badge = SoftCard(
                self.preview_benefits,
                fg_color=self.c("app_bg", "#F6F7FB"),
                border_width=0,
                corner_radius=16
            )
            badge.grid(row=0, column=index, sticky="ew", padx=5)
            self.preview_benefits.grid_columnconfigure(index, weight=1)

            SmallLabel(
                badge,
                benefit,
                text_color=self.c("text_soft", "#6B7280")
            ).pack(padx=10, pady=12)

    # =====================================================
    # RF-015: REALIZAR MICRODESCANSO
    # =====================================================

    def start_microbreak(self):
        if not self.selected_break:
            messagebox.showwarning(
                "Microdescanso",
                "Selecciona un microdescanso antes de comenzar."
            )
            return

        payload = {
            "user_id": self.user.get("id_usuario") if self.user else None,
            "title": self.selected_break["title"],
            "category": self.selected_break["category"],
            "duration": self.selected_break["duration"],
            "description": self.selected_break["description"],
            "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "completed": True,
        }

        if self.app is not None:
            self.app.last_microbreak = payload

            if not hasattr(self.app, "microbreak_history"):
                self.app.microbreak_history = []

            self.app.microbreak_history.append(payload)

        launcher = get_game_launcher_for_title(self.selected_break["title"])
        if launcher is not None:
            try:
                parent_window = self.winfo_toplevel()
                game_window = launcher(parent_window)
                if hasattr(game_window, "transient") and parent_window is not None:
                    game_window.transient(parent_window)
                game_window.focus()
            except Exception as error:
                messagebox.showerror(
                    "No se pudo abrir el juego",
                    f"Hubo un problema al iniciar el juego: {error}"
                )
            return

        self.show_microbreak_steps(payload)

    def show_microbreak_steps(self, payload):
        steps = "\n".join(
            [f"{index + 1}. {step}" for index, step in enumerate(self.selected_break["steps"])]
        )

        messagebox.showinfo(
            payload["title"],
            f"Microdescanso iniciado.\n\n"
            f"Duración sugerida: {payload['duration']} minutos.\n\n"
            f"{steps}\n\n"
            f"Registro guardado para el historial."
        )