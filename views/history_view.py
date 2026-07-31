import customtkinter as ctk
from datetime import datetime

from components import (
    SoftCard,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    SmallLabel,
    SecondaryButton,
)

from utils.theme_manager import ThemeManager
from utils.i18n import Lang
from controllers.wellbeing_controller import WellbeingController


class HistoryView(ctk.CTkFrame):
    """
    Vista Historial.
    Los datos de check-in se obtienen desde MongoDB vía WellbeingController.
    """

    def __init__(self, master, app=None, user=None):
        self.app = app
        self.current_user = getattr(app, "current_user", None)
        self.user = user or self.current_user
        self.theme_name = self.get_theme_name()
        self.theme = ThemeManager.get_theme(self.theme_name)

        super().__init__(
            master,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=0
        )

        self.checkins = []
        self.microbreaks = self.load_microbreaks()
        self.summary = {}

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1, minsize=240)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        self.load_data()
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

    def user_role(self):
        if self.user:
            return self.user.get("rol", "usuario")
        return "usuario"

    def make_card(self, parent, bg=None, radius=22, border=True):
        return SoftCard(
            parent,
            fg_color=bg or self.c("card_bg", "#FFFFFF"),
            border_width=1 if border else 0,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=radius
        )

    def load_data(self):
        result = WellbeingController.get_history(self.user)
        if result.get("success"):
            self.checkins = result.get("checkins", [])
            self.summary = result.get("summary", {})
        else:
            self.checkins = []
            self.summary = {}

    def load_microbreaks(self):
        if self.app and hasattr(self.app, "microbreak_history"):
            return self.app.microbreak_history
        return []

    def avg_from_summary(self, key):
        promedios = self.summary.get("promedios", {})
        return promedios.get(key, 0)

    def status_from_value(self, value, kind):
        if value == 0:
            return Lang.get("history_no_data_status")

        if kind in ("stress", "agotamiento", "presion", "cansancio_mental", "irritabilidad", "saturacion", "desconexion"):
            if value <= 3:
                return Lang.get("history_low")
            if value <= 6:
                return Lang.get("history_moderate")
            return Lang.get("history_high")

        if value <= 3:
            return Lang.get("history_low_f")
        if value <= 6:
            return Lang.get("history_medium")
        return Lang.get("history_good")

    def mood_color(self, mood):
        return {
            Lang.get("checkin_mood_tranquilo"): "#62C79A",
            Lang.get("checkin_mood_saturado"): "#F0AE7A",
            Lang.get("checkin_mood_ansioso"): "#F0AE7A",
            Lang.get("checkin_mood_cansado"): "#7DA7FF",
            Lang.get("checkin_mood_motivado"): "#F0C95D",
        }.get(mood, self.c("accent", "#7C3AED"))

    def mood_icon(self, mood):
        return {
            Lang.get("checkin_mood_tranquilo"): "🙂",
            Lang.get("checkin_mood_saturado"): "😵",
            Lang.get("checkin_mood_ansioso"): "😟",
            Lang.get("checkin_mood_cansado"): "😴",
            Lang.get("checkin_mood_motivado"): "⭐",
        }.get(mood, "☁")

    def main_phrase(self):
        if self.checkins:
            latest = self.checkins[0]
            if latest.get("frase"):
                return latest["frase"]
            respuestas = latest.get("respuestas", [])
            for r in respuestas:
                if r.get("tipo") == "texto" and r.get("valor"):
                    return r["valor"]

        if self.user and self.user.get("frase_hoy"):
            return self.user["frase_hoy"]

        return Lang.get("history_default_phrase")

    def format_date(self, item):
        raw = item.get("fecha") or item.get("started_at") or item.get("created_at")

        if not raw:
            return "Hoy, registro reciente"

        try:
            return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").strftime("%d/%m, %H:%M")
        except Exception:
            return str(raw)

    # =====================================================
    # BUILD
    # =====================================================

    def build_view(self):
        self.build_header()
        self.build_stats()
        self.build_left_panel()
        self.build_right_panel()

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

        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="◔",
            width=72,
            height=72,
            corner_radius=36,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#7C3AED"),
            font=("Arial", 34, "bold")
        ).grid(row=0, column=0, padx=(0, 18))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=1, sticky="w")

        TitleLabel(
            title_box,
            Lang.get("history_title"),
            size=34,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title_box,
            Lang.get("history_subtitle"),
            size=15,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w")

        user_box = ctk.CTkFrame(header, fg_color="transparent")
        user_box.grid(row=0, column=2, sticky="e")

        SmallLabel(
            user_box,
            Lang.get("history_hello", name=self.user_name()),
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="e")

        SmallLabel(
            user_box,
            self.user_role(),
            size=12,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="e")

    def build_stats(self):
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=30,
            pady=(0, 18)
        )

        for col in range(4):
            stats.grid_columnconfigure(col, weight=1)

        total_sessions = len(self.checkins) + len(self.microbreaks)
        total_minutes = sum(item.get("duration", 0) for item in self.microbreaks)
        streak = min(total_sessions, 7)
        last_type = self.summary.get("ultimo_tipo_checkin", "-")

        items = [
            (Lang.get("history_sessions"), total_sessions),
            (Lang.get("history_minutes"), total_minutes),
            (Lang.get("history_streak"), Lang.get("history_streak_days", count=streak)),
            (Lang.get("history_last_checkin"), last_type),
        ]

        for col, (title, value) in enumerate(items):
            self.stat_card(stats, title, value, col)

    def stat_card(self, parent, title, value, col):
        card = self.make_card(parent, radius=18)
        card.grid(row=0, column=col, sticky="ew", padx=6)

        SmallLabel(
            card,
            title,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="center", pady=(16, 4))

        TitleLabel(
            card,
            str(value),
            size=24,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="center", pady=(0, 16))

    def build_left_panel(self):
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(30, 15),
            pady=(0, 26)
        )

        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        self.recent_checkins(left)
        self.week_summary(left)

    def build_right_panel(self):
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(
            row=2,
            column=1,
            sticky="nsew",
            padx=(15, 30),
            pady=(0, 26)
        )

        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        self.phrase_card(right)
        self.activity_card(right)

    # =====================================================
    # CHECKINS
    # =====================================================

    def recent_checkins(self, parent):
        card = self.make_card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        TitleLabel(
            card,
            Lang.get("history_recent"),
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=22, pady=(20, 12))

        if not self.checkins:
            self.empty(card, Lang.get("history_no_checkins"))
            return

        for item in self.checkins[:4]:
            self.checkin_row(card, item)

        SecondaryButton(
            card,
            text=Lang.get("history_view_all"),
            height=36,
            command=self.show_total_checkins
        ).pack(fill="x", padx=22, pady=(10, 20))

    def checkin_row(self, parent, item):
        mood = item.get("estado_animo_general") or item.get("estado_animo") or item.get("mood", "Sin estado")
        title = item.get("titulo_checkin") or item.get("tipo_checkin", "Check-in")
        respuestas = item.get("respuestas", [])
        metricas = item.get("resumen_metricas", {})

        row = self.make_card(parent, bg=self.c("app_bg", "#F6F7FB"), radius=15)
        row.pack(fill="x", padx=22, pady=5)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row,
            text=self.mood_icon(mood),
            width=42,
            height=42,
            corner_radius=21,
            fg_color=self.mood_color(mood),
            text_color="white",
            font=("Arial", 20)
        ).grid(row=0, column=0, rowspan=2, padx=14, pady=10)

        TitleLabel(
            row,
            f"{title} · {self.format_date(item)}",
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).grid(row=0, column=1, sticky="w", pady=(10, 0))

        resumen_parts = []
        for clave, val in list(metricas.items())[:2]:
            resumen_parts.append(f"{clave.capitalize()} {val}/10")
        if respuestas:
            text_resp = [r.get("valor", "") for r in respuestas if r.get("tipo") == "texto" and r.get("valor")]
            if text_resp:
                resumen_parts.append(f"'{text_resp[0][:40]}'")

        SmallLabel(
            row,
            " • ".join(resumen_parts) if resumen_parts else "Sin datos detallados",
            text_color=self.c("text_soft", "#6B7280")
        ).grid(row=1, column=1, sticky="w", pady=(0, 10))

        ctk.CTkLabel(
            row,
            text=mood,
            height=26,
            corner_radius=13,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.mood_color(mood),
            font=("Arial", 12, "bold")
        ).grid(row=0, column=2, rowspan=2, padx=14)

    # =====================================================
    # WEEK SUMMARY
    # =====================================================

    def week_summary(self, parent):
        card = self.make_card(parent)
        card.grid(row=1, column=0, sticky="nsew")

        TitleLabel(
            card,
            Lang.get("history_metrics_title"),
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=22, pady=(20, 4))

        SmallLabel(
            card,
            Lang.get("history_metrics_subtitle"),
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", padx=22, pady=(0, 16))

        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(fill="x", padx=22)

        promedios = self.summary.get("promedios", {})
        if promedios:
            for col, (key, val) in enumerate(list(promedios.items())[:4]):
                self.avg_block(box, Lang.get("history_avg_prefix", key=key.capitalize()), val, key, col)
                box.grid_columnconfigure(col, weight=1)
        else:
            SmallLabel(
                box,
                Lang.get("history_no_data"),
                text_color=self.c("text_soft", "#6B7280")
            ).pack(anchor="w", pady=8)

        self.chart(card)

    def avg_block(self, parent, title, value, kind, col):
        block = ctk.CTkFrame(parent, fg_color="transparent")
        block.grid(row=0, column=col, sticky="ew", padx=8)

        SmallLabel(
            block,
            title,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="center")

        TitleLabel(
            block,
            f"{value} /10",
            size=24,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="center", pady=(4, 0))

        SmallLabel(
            block,
            self.status_from_value(value, kind),
            text_color=self.c("accent", "#7C3AED")
        ).pack(anchor="center")

    def chart(self, parent):
        chart = ctk.CTkFrame(parent, fg_color="transparent")
        chart.pack(fill="both", expand=True, padx=22, pady=(14, 22))

        days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        values = self.chart_values()

        for col in range(7):
            chart.grid_columnconfigure(col, weight=1)

        for index, day in enumerate(days):
            column = ctk.CTkFrame(chart, fg_color="transparent")
            column.grid(row=0, column=index, sticky="ns", padx=5)

            height = max(14, int((values[index] / 10) * 110))

            ctk.CTkFrame(
                column,
                height=110 - height,
                fg_color="transparent"
            ).pack()

            ctk.CTkFrame(
                column,
                width=24,
                height=height,
                fg_color=self.c("accent", "#7C3AED"),
                corner_radius=8
            ).pack()

            SmallLabel(
                chart,
                day,
                text_color=self.c("text_soft", "#6B7280")
            ).grid(row=1, column=index, pady=(8, 0))

    def chart_values(self):
        first_metric = None
        for item in self.checkins:
            rm = item.get("resumen_metricas", {})
            if rm:
                first_metric = list(rm.keys())[0]
                break

        if first_metric:
            values = []
            for item in self.checkins:
                rm = item.get("resumen_metricas", {})
                val = rm.get(first_metric)
                if isinstance(val, (int, float)):
                    values.append(val)
        else:
            values = []

        if not values:
            return [0, 0, 0, 0, 0, 0, 0]

        values = values[:7]
        while len(values) < 7:
            values.append(values[-1])

        return values

    # =====================================================
    # RIGHT PANEL
    # =====================================================

    def phrase_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        TitleLabel(
            card,
            Lang.get("history_phrase_title"),
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=22, pady=(20, 8))

        box = ctk.CTkFrame(
            card,
            fg_color=self.c("app_bg", "#F6F7FB"),
            corner_radius=18
        )
        box.pack(fill="x", padx=22, pady=(0, 22))

        ctk.CTkLabel(
            box,
            text="“",
            font=("Arial", 42, "bold"),
            text_color=self.c("accent", "#7C3AED")
        ).pack(anchor="center", pady=(18, 0))

        BodyLabel(
            box,
            self.main_phrase(),
            size=15,
            text_color=self.c("text", "#1E1B4B"),
            wraplength=300
        ).pack(anchor="center", padx=24, pady=(0, 18))

    def activity_card(self, parent):
        card = self.make_card(parent)
        card.grid(row=1, column=0, sticky="nsew")

        TitleLabel(
            card,
            Lang.get("history_activity_title"),
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=22, pady=(20, 12))

        activities = self.activities()

        if not activities:
            self.empty(card, Lang.get("history_no_activity"))
            return

        for item in activities[:6]:
            self.activity_row(card, item)

    def activities(self):
        data = []

        for item in self.checkins:
            mood = item.get("estado_animo_general") or item.get("estado_animo") or Lang.get("history_no_data_status")
            titulo = item.get("titulo_checkin") or Lang.get("checkin_title")
            metricas = item.get("resumen_metricas", {})
            detail_parts = [f"{k.capitalize()} {v}/10" for k, v in list(metricas.items())[:2]]
            data.append({
                "title": f"{titulo}: {mood}",
                "detail": " • ".join(detail_parts) if detail_parts else Lang.get("history_completed"),
            })

        for item in self.microbreaks:
            data.append({
                "title": Lang.get("history_microbreak", title=item.get("title", "Actividad")),
                "detail": f"{item.get('duration', '-')} min • {item.get('category', 'General')}",
            })

        return data

    def activity_row(self, parent, item):
        row = self.make_card(parent, bg=self.c("app_bg", "#F6F7FB"), radius=14)
        row.pack(fill="x", padx=22, pady=5)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row,
            text="✓",
            width=34,
            height=34,
            corner_radius=17,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#7C3AED"),
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, rowspan=2, padx=12, pady=10)

        TitleLabel(
            row,
            item["title"],
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).grid(row=0, column=1, sticky="w", pady=(10, 0))

        SmallLabel(
            row,
            item["detail"],
            text_color=self.c("text_soft", "#6B7280")
        ).grid(row=1, column=1, sticky="w", pady=(0, 10))

    # =====================================================
    # MISC
    # =====================================================

    def empty(self, parent, text):
        BodyLabel(
            parent,
            text,
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=420
        ).pack(anchor="w", padx=22, pady=(6, 22))

    def show_total_checkins(self):
        from tkinter import messagebox

        total = self.summary.get("total_checkins", len(self.checkins))
        ultimo_tipo = self.summary.get("ultimo_tipo_checkin", "N/A")
        messagebox.showinfo(
            Lang.get("history_title"),
            Lang.get("history_checkin_info", total=total, ultimo=ultimo_tipo)
        )