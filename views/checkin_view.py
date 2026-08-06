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
from utils.app_state import AppState
from utils.i18n import Lang
from controllers.checkin_controller import CheckinController
from utils.checkin_questions import get_today_checkin_template


class CheckinView(ctk.CTkFrame):
    def __init__(self, master, app=None, user=None):
        self.app = app
        self.user = user
        self.theme_name = self.get_theme_name()
        self.theme = ThemeManager.get_theme(self.theme_name)

        user_lang = self.user.get("idioma") if self.user else None
        Lang.set(user_lang or AppState.load_language())

        super().__init__(
            master,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=0
        )

        id_usuario = user.get("id_usuario", 0) if user else 0
        self.template = get_today_checkin_template(id_usuario)

        self.slider_vars = {}
        self.slider_labels = {}
        self.option_vars = {}
        self.option_buttons = {}
        self.text_boxes = {}
        self.text_counters = {}

        self.selected_mood = None
        self.mood_buttons = {}

        self.recommendation_title = None
        self.recommendation_text = None

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_view()

    def c(self, key, default):
        return self.theme.get(key, default)

    def get_theme_name(self):
        if self.user:
            return self.user.get("tema_visual", "light")
        return "light"

    def user_name(self):
        if self.user:
            return self.user.get("nombre", Lang.get("username"))
        return Lang.get("username")

    def make_card(self, parent, radius=22):
        return SoftCard(
            parent,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=radius
        )

    def build_view(self):
        self.header()
        self.left_panel()
        self.right_panel()
        self.update_recommendation()

    def header(self):
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.grid(row=0, column=0, columnspan=2, sticky="ew", padx=30, pady=(24, 16))
        box.grid_columnconfigure(0, weight=1)

        title = ctk.CTkFrame(box, fg_color="transparent")
        title.grid(row=0, column=0, sticky="w")

        TitleLabel(
            title,
            Lang.get("checkin_title"),
            size=34,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title,
            self.template.get("titulo", Lang.get("checkin_question_desc")),
            size=15,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w")

        user = ctk.CTkFrame(box, fg_color="transparent")
        user.grid(row=0, column=1, sticky="e")

        SmallLabel(
            user,
            Lang.get("checkin_hello", name=self.user_name()),
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="e")

        SmallLabel(
            user,
            Lang.get("checkin_balance"),
            size=12,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="e")

    def left_panel(self):
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=1, column=0, sticky="nsew", padx=(30, 15), pady=(0, 26))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        self.questions_card(left)
        self.mood_card(left)

    def right_panel(self):
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1, column=1, sticky="nsew", padx=(15, 30), pady=(0, 26))
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

    def slider_color(self, index):
        colors = ["#9B7CF3", "#62C79A", "#7DA7FF", "#A97DF5", "#F0AE7A", "#F0C95D", "#B78BFA", "#E8846B"]
        return colors[index % len(colors)]

    def questions_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        TitleLabel(
            card,
            Lang.get("checkin_question_1"),
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 4))

        SmallLabel(
            card,
            Lang.get("checkin_question_desc"),
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 14))

        body = ctk.CTkScrollableFrame(card, fg_color="transparent", height=360)
        body.pack(fill="x", padx=24, pady=(0, 20))

        for idx, pregunta in enumerate(self.template.get("preguntas", [])):
            self.render_question(body, pregunta, idx)

    def render_question(self, parent, pregunta, idx):
        tipo = pregunta.get("tipo")
        clave = pregunta.get("clave")
        texto = pregunta.get("texto", "")

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(10, 4))

        BodyLabel(
            frame,
            texto,
            size=15,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        if tipo == "escala":
            self.render_escala(frame, pregunta, idx)
        elif tipo == "opcion":
            self.render_opcion(frame, pregunta, idx)
        elif tipo == "texto":
            self.render_texto(frame, pregunta, idx)

    def render_escala(self, parent, pregunta, idx):
        clave = pregunta.get("clave")
        min_val = pregunta.get("min", 1)
        max_val = pregunta.get("max", 10)
        color = self.slider_color(idx)

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)

        self.slider_vars[clave] = ctk.DoubleVar(value=5)

        slider = ctk.CTkSlider(
            row,
            from_=min_val,
            to=max_val,
            number_of_steps=max_val - min_val,
            variable=self.slider_vars[clave],
            fg_color=self.c("card_border", "#E5E7EB"),
            progress_color=color,
            button_color="#FFFFFF",
            button_hover_color=color,
            command=lambda _=None: self.on_slider_change(clave)
        )
        slider.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        value_label = ctk.CTkLabel(
            row,
            text="5",
            width=30,
            height=30,
            corner_radius=15,
            fg_color=color,
            text_color="white",
            font=("Arial", 13, "bold")
        )
        value_label.grid(row=0, column=1)
        self.slider_labels[clave] = value_label

    def on_slider_change(self, clave):
        if clave in self.slider_labels:
            val = int(round(float(self.slider_vars[clave].get())))
            self.slider_labels[clave].configure(text=str(val))
        self.update_recommendation()

    def render_opcion(self, parent, pregunta, idx):
        clave = pregunta.get("clave")
        opciones = pregunta.get("opciones", [])

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=6)

        var = ctk.StringVar(value="")
        self.option_vars[clave] = var
        self.option_buttons[clave] = []

        for col, opcion in enumerate(opciones):
            btn = ctk.CTkButton(
                row,
                text=opcion,
                height=34,
                corner_radius=12,
                fg_color=self.c("app_bg", "#F6F7FB"),
                hover_color=self.c("accent", "#7C3AED"),
                text_color=self.c("text", "#1E1B4B"),
                border_width=1,
                border_color=self.c("card_border", "#E5E7EB"),
                command=lambda o=opcion, k=clave: self.select_option(k, o)
            )
            btn.grid(row=0, column=col, sticky="ew", padx=3)
            row.grid_columnconfigure(col, weight=1)
            self.option_buttons[clave].append((opcion, btn))

    def select_option(self, clave, opcion):
        if clave in self.option_vars:
            self.option_vars[clave].set(opcion)
        for opt, btn in self.option_buttons.get(clave, []):
            selected = opt == opcion
            btn.configure(
                fg_color=self.c("accent", "#7C3AED") if selected else self.c("app_bg", "#F6F7FB"),
                text_color="white" if selected else self.c("text", "#1E1B4B"),
                border_color=self.c("accent", "#7C3AED") if selected else self.c("card_border", "#E5E7EB")
            )
        self.update_recommendation()

    def render_texto(self, parent, pregunta, idx):
        clave = pregunta.get("clave")

        textbox = ctk.CTkTextbox(
            parent,
            height=90,
            corner_radius=12,
            fg_color=self.c("app_bg", "#F6F7FB"),
            text_color=self.c("text", "#1E1B4B"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            font=("Arial", 13)
        )
        textbox.pack(fill="x", pady=(4, 2))
        self.text_boxes[clave] = textbox

        counter = SmallLabel(
            parent,
            "0/250",
            text_color=self.c("text_soft", "#6B7280")
        )
        counter.pack(anchor="e", padx=4, pady=(0, 4))
        self.text_counters[clave] = counter

        textbox.bind("<KeyRelease>", lambda e, k=clave: self.update_text_counter(k))

    def update_text_counter(self, clave):
        textbox = self.text_boxes.get(clave)
        counter = self.text_counters.get(clave)
        if not textbox or not counter:
            return
        text = textbox.get("1.0", "end-1c").strip()
        if len(text) > 250:
            text = text[:250]
            textbox.delete("1.0", "end")
            textbox.insert("1.0", text)
        counter.configure(text=f"{len(text)}/250")

    def mood_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 18))

        TitleLabel(
            card,
            Lang.get("checkin_mood_title"),
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 4))

        SmallLabel(
            card,
            Lang.get("checkin_mood_desc"),
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 16))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=18, pady=(0, 20))

        moods = [
            (Lang.get("checkin_mood_tranquilo"), "🙂", "#62C79A"),
            (Lang.get("checkin_mood_saturado"), "😵", "#F0AE7A"),
            (Lang.get("checkin_mood_ansioso"), "😟", "#B78BFA"),
            (Lang.get("checkin_mood_cansado"), "😴", "#7DA7FF"),
            (Lang.get("checkin_mood_motivado"), "⭐", "#F0C95D"),
        ]

        for col, (mood, icon, color) in enumerate(moods):
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

    def recommendation_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        ctk.CTkLabel(
            card,
            text="🌿",
            width=82, height=82,
            corner_radius=41,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#7C3AED"),
            font=("Arial", 38)
        ).pack(anchor="center", pady=(24, 10))

        TitleLabel(
            card,
            Lang.get("checkin_recommendation_title"),
            size=21,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(0, 4))

        SmallLabel(
            card,
            Lang.get("checkin_recommendation_subtitle"),
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 12))

        self.recommendation_title = TitleLabel(
            card, "", size=18,
            text_color=self.c("text", "#1E1B4B")
        )
        self.recommendation_title.pack(anchor="w", padx=24, pady=(0, 4))

        self.recommendation_text = BodyLabel(
            card, "", size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=310
        )
        self.recommendation_text.pack(anchor="w", padx=24, pady=(0, 24))

    def action_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        TitleLabel(
            card,
            Lang.get("checkin_suggested_action"),
            size=18,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 6))

        BodyLabel(
            card,
            Lang.get("checkin_suggested_action_desc"),
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=310
        ).pack(anchor="w", padx=24, pady=(0, 20))

    def tip_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=2, column=0, sticky="nsew", pady=(0, 16))

        TitleLabel(
            card, Lang.get("checkin_tip_title"),
            size=18,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(20, 6))

        BodyLabel(
            card,
            Lang.get("checkin_tip_desc"),
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=310
        ).pack(anchor="w", padx=24, pady=(0, 20))

    def get_slider_value(self, clave):
        if clave in self.slider_vars:
            return int(round(float(self.slider_vars[clave].get())))
        return None

    def get_option_value(self, clave):
        if clave in self.option_vars:
            return self.option_vars[clave].get()
        return None

    def get_text_value(self, clave):
        tb = self.text_boxes.get(clave)
        if tb:
            return tb.get("1.0", "end-1c").strip()
        return ""

    def generate_recommendation(self):
        escala_values = {}
        for clave in self.slider_vars:
            escala_values[clave] = self.get_slider_value(clave)

        mood_tranquilo = Lang.get("checkin_mood_tranquilo")
        mood_saturado = Lang.get("checkin_mood_saturado")
        mood_ansioso = Lang.get("checkin_mood_ansioso")
        mood_cansado = Lang.get("checkin_mood_cansado")
        mood_motivado = Lang.get("checkin_mood_motivado")

        if escala_values.get("estres") and escala_values["estres"] >= 7:
            return (Lang.get("checkin_rec_calm"), Lang.get("checkin_rec_calm_desc"))

        agotamiento = escala_values.get("agotamiento")
        if agotamiento and agotamiento >= 7:
            return (Lang.get("checkin_rec_micro"), Lang.get("checkin_rec_micro_desc"))

        cansancio = escala_values.get("cansancio_mental")
        if cansancio and cansancio >= 7:
            return (Lang.get("checkin_rec_micro"), Lang.get("checkin_rec_micro_desc"))

        saturacion = escala_values.get("saturacion")
        if saturacion and saturacion >= 7:
            return (Lang.get("checkin_rec_sounds"), Lang.get("checkin_rec_sounds_desc"))

        presion = escala_values.get("presion")
        if presion and presion >= 7:
            return (Lang.get("checkin_rec_calm_pressure"), Lang.get("checkin_rec_calm_pressure_desc"))

        if self.selected_mood in (mood_saturado, mood_ansioso):
            return (Lang.get("checkin_rec_calm_anxious"), Lang.get("checkin_rec_calm_anxious_desc"))

        if self.selected_mood == mood_cansado:
            return (Lang.get("checkin_rec_micro_tired"), Lang.get("checkin_rec_micro_tired_desc"))

        if self.selected_mood == mood_motivado:
            return (Lang.get("checkin_rec_continue"), Lang.get("checkin_rec_continue_desc"))

        return (Lang.get("checkin_rec_stable"), Lang.get("checkin_rec_stable_desc"))

    def update_recommendation(self):
        if not self.recommendation_title or not self.recommendation_text:
            return
        title, text = self.generate_recommendation()
        self.recommendation_title.configure(text=title)
        self.recommendation_text.configure(text=text)

    def build_payload(self):
        title, text = self.generate_recommendation()
        respuestas = []

        for pregunta in self.template.get("preguntas", []):
            clave = pregunta["clave"]
            tipo = pregunta["tipo"]
            respuesta = {
                "clave": clave,
                "pregunta": pregunta["texto"],
                "tipo": tipo,
            }
            if tipo == "escala":
                respuesta["valor"] = self.get_slider_value(clave)
                respuesta["min"] = pregunta.get("min", 1)
                respuesta["max"] = pregunta.get("max", 10)
            elif tipo == "opcion":
                respuesta["valor"] = self.get_option_value(clave)
            elif tipo == "texto":
                respuesta["valor"] = self.get_text_value(clave)

            if respuesta["valor"] is not None and respuesta["valor"] != "":
                respuestas.append(respuesta)

        return {
            "tipo_checkin": self.template["tipo_checkin"],
            "titulo_checkin": self.template["titulo"],
            "estado_animo_general": self.selected_mood or Lang.get("history_no_state"),
            "respuestas": respuestas,
            "recomendacion_automatica": {
                "titulo": title,
                "descripcion": text,
                "tipo": self.selected_mood.lower() if self.selected_mood else "general"
            }
        }

    def save_checkin(self):
        if not self.selected_mood:
            messagebox.showwarning(
                Lang.get("checkin_save_warning"),
                Lang.get("checkin_save_warning_msg")
            )
            return

        has_text = False
        for pregunta in self.template.get("preguntas", []):
            if pregunta["tipo"] == "texto":
                val = self.get_text_value(pregunta["clave"])
                if val:
                    has_text = True
                    break

        payload = self.build_payload()
        result = CheckinController.save_checkin(self.user, payload)

        if result.get("success"):
            checkin = result.get("checkin", {})

            if self.app is not None:
                self.app.last_checkin = checkin
                if not hasattr(self.app, "checkin_history"):
                    self.app.checkin_history = []
                self.app.checkin_history.insert(0, checkin)
                if self.app.current_user is not None:
                    self.app.current_user["ultimo_checkin"] = checkin
                    for r in checkin.get("respuestas", []):
                        if r.get("tipo") == "texto" and r.get("valor"):
                            self.app.current_user["frase_hoy"] = r["valor"]
                            break

            print("CHECK-IN GUARDADO EN MONGO:", checkin)
            messagebox.showinfo(
                Lang.get("checkin_saved_title"),
                Lang.get("checkin_saved_msg")
            )
        else:
            messagebox.showerror(
                Lang.get("checkin_error_title"),
                result.get("message", Lang.get("checkin_error_title"))
            )
