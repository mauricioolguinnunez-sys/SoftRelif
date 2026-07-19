import customtkinter as ctk

from components import (
    SoftCard,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    SmallLabel,
    PrimaryButton,
)

from utils.theme_manager import ThemeManager


class SpecialistView(ctk.CTkFrame):
    """
    Panel del especialista.

    RF relacionados:
    - RF-005 Visualizar panel de especialista.
    - RF-020 Asignar recomendación.
    - RF-021 Marcar seguimiento.
    - RF-022 Cargar recurso.
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
            return self.user.get("nombre", "Especialista")
        return "Especialista"

    def card(self, parent, radius=22):
        return SoftCard(
            parent,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=radius
        )

    def build_view(self):
        self.build_header()
        self.build_main_panel()
        self.build_side_panel()

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

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        TitleLabel(
            title_box,
            "Panel especialista",
            size=34,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title_box,
            "Seguimiento, recomendaciones y recursos de apoyo.",
            size=15,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w")

        user_box = ctk.CTkFrame(header, fg_color="transparent")
        user_box.grid(row=0, column=1, sticky="e")

        SmallLabel(
            user_box,
            f"Hola, {self.user_name()}",
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="e")

        SmallLabel(
            user_box,
            "Rol especialista",
            size=12,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="e")

    def build_main_panel(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(30, 15),
            pady=(0, 26)
        )

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        modules = [
            (
                "Trayectoria del usuario",
                "Consultar evolución, historial emocional y actividad registrada.",
                "RF-005",
                "◔"
            ),
            (
                "Asignar recomendación",
                "Registrar una recomendación personalizada para un usuario.",
                "RF-020",
                "➕"
            ),
            (
                "Marcar seguimiento",
                "Indicar que un caso fue revisado o atendido.",
                "RF-021",
                "✓"
            ),
            (
                "Cargar recurso",
                "Agregar material de apoyo para el bienestar del usuario.",
                "RF-022",
                "⬆"
            ),
        ]

        for index, module in enumerate(modules):
            row = index // 2
            col = index % 2
            self.module_card(main, module, row, col)

    def module_card(self, parent, data, row, col):
        title, description, rf, icon = data

        card = self.card(parent, radius=20)
        card.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=(0, 14) if col == 0 else (14, 0),
            pady=(0, 18)
        )

        ctk.CTkLabel(
            card,
            text=icon,
            width=58,
            height=58,
            corner_radius=29,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#7C3AED"),
            font=("Arial", 28)
        ).pack(anchor="w", padx=24, pady=(22, 12))

        TitleLabel(
            card,
            title,
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(0, 6))

        BodyLabel(
            card,
            description,
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=300
        ).pack(anchor="w", padx=24, pady=(0, 10))

        SmallLabel(
            card,
            rf,
            text_color=self.c("accent", "#7C3AED")
        ).pack(anchor="w", padx=24, pady=(0, 18))

    def build_side_panel(self):
        side = ctk.CTkFrame(self, fg_color="transparent")
        side.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(15, 30),
            pady=(0, 26)
        )

        side.grid_columnconfigure(0, weight=1)

        summary = self.card(side)
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        TitleLabel(
            summary,
            "Resumen del rol",
            size=22,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        BodyLabel(
            summary,
            "El especialista no utiliza las funciones de bienestar como usuario final. Su función es dar seguimiento, asignar recomendaciones y gestionar recursos de apoyo.",
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=310
        ).pack(anchor="w", padx=24, pady=(0, 22))

        notice = self.card(side)
        notice.grid(row=1, column=0, sticky="ew")

        TitleLabel(
            notice,
            "Acceso controlado",
            size=20,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(22, 8))

        BodyLabel(
            notice,
            "Este panel está limitado a funciones de asesoría y seguimiento conforme a los requerimientos funcionales del sistema.",
            size=14,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=310
        ).pack(anchor="w", padx=24, pady=(0, 22))