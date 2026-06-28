import customtkinter as ctk
from components.cards import SoftCard
from components.labels import TitleLabel, SubtitleLabel, BodyLabel, SmallLabel
from components.buttons import PrimaryButton, DangerButton


class ThemeOptionCard(SoftCard):
    def __init__(self, master, theme, title, subtitle, mode, selected=False, command=None):
        super().__init__(
            master,
            fg_color=theme.get("card_bg", "#FFFFFF"),
            border_width=2 if selected else 1,
            border_color=theme.get("accent", "#7C3AED") if selected else theme.get("card_border", "#E5E7EB"),
            corner_radius=18
        )

        self.theme = theme
        self.mode = mode
        self.command = command

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=22, pady=20)

        TitleLabel(
            left,
            title,
            size=18,
            text_color=theme.get("text", "#1E1B4B")
        ).pack(anchor="w")

        SmallLabel(
            left,
            subtitle,
            text_color=theme.get("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(4, 0))

        self.indicator = ctk.CTkLabel(
            self,
            text="●" if selected else "○",
            font=("Arial", 26, "bold"),
            text_color=theme.get("accent", "#7C3AED") if selected else theme.get("card_border", "#D9DEEA")
        )
        self.indicator.grid(row=0, column=1, padx=(0, 22), pady=20)

        self.bind("<Button-1>", self.select)
        left.bind("<Button-1>", self.select)
        self.indicator.bind("<Button-1>", self.select)

    def select(self, event=None):
        if self.command:
            self.command(self.mode)

    def set_selected(self, selected):
        self.configure(
            border_width=2 if selected else 1,
            border_color=self.theme.get("accent", "#7C3AED") if selected else self.theme.get("card_border", "#E5E7EB")
        )

        self.indicator.configure(
            text="●" if selected else "○",
            text_color=self.theme.get("accent", "#7C3AED") if selected else self.theme.get("card_border", "#D9DEEA")
        )


class PersistenceCard(SoftCard):
    def __init__(self, master, theme, enabled=True, command=None):
        super().__init__(
            master,
            fg_color=theme.get("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=theme.get("card_border", "#E5E7EB"),
            corner_radius=20
        )

        self.theme = theme
        self.command = command

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=24, pady=22)

        TitleLabel(
            left,
            "Persistencia del tema",
            size=20,
            text_color=theme.get("text", "#1E1B4B")
        ).pack(anchor="w")

        BodyLabel(
            left,
            "Guardar mi preferencia visual para mantenerla en la aplicación.",
            size=14,
            text_color=theme.get("text_soft", "#6B7280"),
            wraplength=480
        ).pack(anchor="w", pady=(5, 0))

        self.switch = ctk.CTkSwitch(
            self,
            text="",
            command=self.toggle,
            progress_color=theme.get("accent", "#7C3AED"),
            button_color="#FFFFFF",
            fg_color=theme.get("card_border", "#D9DEEA")
        )
        self.switch.grid(row=0, column=1, padx=(0, 24), pady=22)

        if enabled:
            self.switch.select()
        else:
            self.switch.deselect()

    def toggle(self):
        if self.command:
            self.command(self.is_enabled())

    def is_enabled(self):
        return self.switch.get() == 1


class AccountSummaryCard(SoftCard):
    def __init__(self, master, theme, user=None):
        super().__init__(
            master,
            fg_color=theme.get("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=theme.get("card_border", "#E5E7EB"),
            corner_radius=20
        )

        user = user or {}
        name = user.get("nombre", "Usuario")
        role = user.get("rol", "Cuenta local")
        email = user.get("correo", "Sin correo registrado")

        initials = self.get_initials(name)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkLabel(
            self,
            text=initials,
            width=58,
            height=58,
            corner_radius=29,
            fg_color=theme.get("accent_soft", "#EDE9FE"),
            text_color=theme.get("accent", "#7C3AED"),
            font=("Arial", 18, "bold")
        )
        avatar.grid(row=0, column=0, rowspan=3, padx=24, pady=24)

        TitleLabel(
            self,
            name,
            size=19,
            text_color=theme.get("text", "#1E1B4B")
        ).grid(row=0, column=1, sticky="w", padx=(0, 24), pady=(24, 0))

        SmallLabel(
            self,
            role,
            text_color=theme.get("text_soft", "#6B7280")
        ).grid(row=1, column=1, sticky="w", padx=(0, 24))

        SmallLabel(
            self,
            email,
            text_color=theme.get("text_soft", "#6B7280")
        ).grid(row=2, column=1, sticky="w", padx=(0, 24), pady=(0, 24))

    def get_initials(self, name):
        parts = name.strip().split()

        if len(parts) >= 2:
            return parts[0][0].upper() + parts[1][0].upper()

        if len(parts) == 1 and parts[0]:
            return parts[0][0].upper()

        return "U"


class DangerAccountCard(SoftCard):
    def __init__(self, master, theme, command=None):
        super().__init__(
            master,
            fg_color=theme.get("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=theme.get("card_border", "#E5E7EB"),
            corner_radius=20
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=24, pady=22)

        TitleLabel(
            left,
            "Eliminar cuenta",
            size=20,
            text_color=theme.get("danger", "#DC2626")
        ).pack(anchor="w")

        BodyLabel(
            left,
            "Solicitar la eliminación de la cuenta y sus datos asociados.",
            size=14,
            text_color=theme.get("text_soft", "#6B7280"),
            wraplength=480
        ).pack(anchor="w", pady=(5, 0))

        DangerButton(
            self,
            text="Solicitar eliminación",
            width=190,
            command=command
        ).grid(row=0, column=1, padx=(0, 24), pady=22)


class VisualPreviewCard(SoftCard):
    def __init__(self, master, theme):
        super().__init__(
            master,
            fg_color=theme.get("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=theme.get("card_border", "#E5E7EB"),
            corner_radius=20
        )

        TitleLabel(
            self,
            "Vista previa visual",
            size=20,
            text_color=theme.get("text", "#1E1B4B")
        ).pack(anchor="w", padx=24, pady=(22, 6))

        SmallLabel(
            self,
            "Representación del estilo actual de SoftRelief.",
            text_color=theme.get("text_soft", "#6B7280")
        ).pack(anchor="w", padx=24, pady=(0, 16))

        preview = ctk.CTkFrame(
            self,
            fg_color=theme.get("app_bg", "#F6F7FB"),
            corner_radius=18,
            border_width=1,
            border_color=theme.get("card_border", "#E5E7EB")
        )
        preview.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        ctk.CTkFrame(
            preview,
            width=80,
            fg_color=theme.get("sidebar_bg", "#FFFFFF"),
            corner_radius=14
        ).pack(side="left", fill="y", padx=18, pady=18)

        body = ctk.CTkFrame(preview, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, padx=(0, 18), pady=18)

        for _ in range(3):
            ctk.CTkFrame(
                body,
                height=42,
                fg_color=theme.get("card_bg", "#FFFFFF"),
                corner_radius=12,
                border_width=1,
                border_color=theme.get("card_border", "#E5E7EB")
            ).pack(fill="x", pady=6)