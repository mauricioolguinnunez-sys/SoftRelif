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
from utils.i18n import Lang
from utils.app_state import AppState


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

        user_lang = self.user.get("idioma") if self.user else None
        Lang.set(user_lang or AppState.load_language())

        self.category_keys = [
            ("all", "micro_filter_all"),
            ("relax", "micro_filter_relax"),
            ("focus", "micro_filter_focus"),
            ("energy", "micro_filter_energy"),
            ("creativity", "micro_filter_creativity"),
        ]
        self.selected_category = "all"
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
                "lang_key": "pause",
                "category_key": "relax",
                "duration": 5,
                "icon": "☕",
                "color": "#8EDCC7",
                "description": "Una pausa corta para soltar la tensión acumulada, respirar y reconectar contigo.",
                "benefits": ["Reduce el estrés", "Aclara tu mente", "Mejora tu enfoque"],
                "benefit_keys": ["stress", "mind", "focus"],
                "steps": [
                    "Siéntate con la espalda cómoda.",
                    "Inhala lentamente durante 4 segundos.",
                    "Exhala sin prisa durante 5 segundos.",
                    "Repite el ciclo hasta terminar la pausa."
                ],
            },
            {
                "title": "Observa y crece",
                "lang_key": "grow",
                "category_key": "energy",
                "duration": 7,
                "icon": "🌱",
                "color": "#B78BFA",
                "description": "Riega el estanque y observa cómo florece el entorno mientras tu mente se sereniza.",
                "benefits": ["Relaja la mente", "Fomenta calma", "Mejora la atención"],
                "benefit_keys": ["relax", "calm", "attention"],
                "steps": [
                    "Abre el juego de observación y crecimiento.",
                    "Riega poco a poco para ver la escena cambiar.",
                    "Respira con la calma del paisaje.",
                    "Disfruta el momento sin prisa."
                ],
            },
            {
                "title": "Patrones visuales",
                "lang_key": "patterns",
                "category_key": "focus",
                "duration": 4,
                "icon": "👁",
                "color": "#8FB8FF",
                "description": "Observa, relaja tu mente y mejora tu enfoque con patrones calmantes.",
                "benefits": ["Descansa la vista", "Mejora atención", "Baja saturación"],
                "benefit_keys": ["rest_eyes", "attention", "lower_saturation"],
                "steps": [
                    "Mira un punto fijo.",
                    "Sigue un patrón visual simple.",
                    "Evita forzar la vista.",
                    "Respira lentamente."
                ],
            },
            {
                "title": "Toque consciente",
                "lang_key": "touch",
                "category_key": "relax",
                "duration": 3,
                "icon": "☝",
                "color": "#8EDCC7",
                "description": "Pequeñas interacciones para anclar tu atención en el momento presente.",
                "benefits": ["Vuelve al presente", "Reduce ansiedad", "Regula atención"],
                "benefit_keys": ["present", "anxiety", "regulate"],
                "steps": [
                    "Toca suavemente la mesa.",
                    "Nota la textura.",
                    "Respira mientras observas la sensación.",
                    "Repite sin juzgar."
                ],
            },
            {
                "title": "Memoria ligera",
                "lang_key": "memory",
                "category_key": "creativity",
                "duration": 6,
                "icon": "🧠",
                "color": "#C59BFF",
                "description": "Ejercita tu memoria de forma amable con una actividad breve y sencilla.",
                "benefits": ["Activa memoria", "Estimula creatividad", "Rompe rutina"],
                "benefit_keys": ["memory", "creativity", "routine"],
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

    def normalize_microbreak(self, microbreak):
        return {
            "title": microbreak.get("title", microbreak.get("nombre", "Microdescanso")),
            "category": microbreak.get("category", microbreak.get("categoria", microbreak.get("category_key", "General"))),
            "duration": microbreak.get("duration", microbreak.get("duracion", 5)),
            "description": microbreak.get("description", microbreak.get("descripcion", "Actividad breve de bienestar.")),
            "icon": microbreak.get("icon", microbreak.get("icono", "☕")),
            "color": microbreak.get("color", "#8EDCC7"),
            "lang_key": microbreak.get("lang_key", "pause"),
            "steps": microbreak.get("steps", []),
        }

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
            Lang.get("micro_title"),
            size=34,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title_box,
            Lang.get("micro_subtitle"),
            size=15,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(2, 0))

        user_box = ctk.CTkFrame(header, fg_color="transparent")
        user_box.grid(row=0, column=1, sticky="e")

        SmallLabel(
            user_box,
            Lang.get("micro_hello", name=self.get_user_name()),
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="e")

        SmallLabel(
            user_box,
            Lang.get("micro_balance"),
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

        for index, (key, lang_key) in enumerate(self.category_keys):
            btn = SecondaryButton(
                filters,
                text=Lang.get(lang_key),
                height=38,
                command=lambda k=key: self.select_category(k)
            )
            btn.grid(row=0, column=index, padx=(0, 10), sticky="ew")
            filters.grid_columnconfigure(index, weight=1)
            self.category_buttons[key] = btn

        self.refresh_category_buttons()

    def render_break_cards(self):
        for widget in self.cards_area.winfo_children():
            widget.destroy()

        self.break_cards.clear()

        visible_items = [
            item for item in self.microbreaks
            if self.selected_category == "all" or item["category_key"] == self.selected_category
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
            Lang.get(f"micro_breaks_{item['lang_key']}"),
            size=19,
            text_color=self.c("text", "#1E1B4B")
        ).grid(row=0, column=1, sticky="w", padx=(0, 22), pady=(26, 4))

        SmallLabel(
            card,
            Lang.get("micro_duration", min=item["duration"]),
            text_color=self.c("text_soft", "#6B7280")
        ).grid(row=1, column=1, sticky="w", padx=(0, 22))

        BodyLabel(
            card,
            Lang.get(f"micro_breaks_{item['lang_key']}_desc"),
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
            Lang.get("micro_preview_title"),
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
            text=Lang.get("micro_start"),
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
        self.selected_break = self.normalize_microbreak(item)
        self.refresh_break_cards()
        self.update_preview()

    def refresh_category_buttons(self):
        for key, button in self.category_buttons.items():
            selected = key == self.selected_category

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

        self.preview_title.configure(text=Lang.get(f"micro_breaks_{item['lang_key']}"))
        self.preview_duration.configure(text=Lang.get("micro_duration", min=item["duration"]))
        self.preview_description.configure(text=Lang.get(f"micro_breaks_{item['lang_key']}_desc"))

        for widget in self.preview_benefits.winfo_children():
            widget.destroy()

        benefit_keys = item.get("benefit_keys", [])
        for index, bk in enumerate(benefit_keys):
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
                Lang.get(f"micro_benefits_{bk}"),
                text_color=self.c("text_soft", "#6B7280")
            ).pack(padx=10, pady=12)

    # =====================================================
    # REALIZAR MICRODESCANSO
    # =====================================================

    def start_microbreak(self):
        if not self.selected_break:
            messagebox.showwarning(
                Lang.get("micro_warning_title"),
                Lang.get("micro_warning_msg")
            )
            return

        title = self.selected_break.get("title", "Microdescanso")
        category = self.selected_break.get("category", "General")
        duration = self.selected_break.get("duration", 5)
        description = self.selected_break.get("description", "Actividad breve de bienestar.")

        payload = {
            "user_id": self.user.get("id_usuario") if self.user else None,
            "title": title,
            "category": category,
            "duration": duration,
            "description": description,
            "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "completed": True,
        }

        if self.app is not None:
            self.app.last_microbreak = payload

            if not hasattr(self.app, "microbreak_history"):
                self.app.microbreak_history = []

            self.app.microbreak_history.append(payload)

        launcher = get_game_launcher_for_title(self.selected_break.get("title", ""))
        if launcher is not None:
            try:
                parent_window = self.winfo_toplevel()
                game_window = launcher(parent_window)
                if hasattr(game_window, "transient") and parent_window is not None:
                    game_window.transient(parent_window)
                game_window.focus()
            except Exception as error:
                messagebox.showerror(
                    Lang.get("micro_game_error"),
                    Lang.get("micro_game_error_msg", error=error)
                )
            return

        self.show_microbreak_steps(payload)

    def show_microbreak_steps(self, payload):
        steps_lines = []
        for index, step in enumerate(self.selected_break.get("steps", [])):
            steps_lines.append(Lang.get("micro_steps_format", number=index + 1, step=step))
        steps = "\n".join(steps_lines)

        parts = [
            Lang.get("micro_started"),
            Lang.get("micro_duration_suggested", duration=payload.get("duration", 5)),
            steps,
            Lang.get("micro_saved"),
        ]
        messagebox.showinfo(
            payload.get("title", "Microdescanso"),
            "\n\n".join(parts)
        )