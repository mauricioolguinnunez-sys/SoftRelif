import customtkinter as ctk

from utils.theme_manager import ThemeManager


class BaseFrame(ctk.CTkFrame):
    """
    Clase base para todas las vistas principales de SoftRelief.

    Centraliza:
    - app
    - usuario actual
    - tema visual
    - limpieza de contenido
    - configuración de grid
    - creación básica de frames, labels y botones
    """

    def __init__(self, master, app=None, usuario=None, tema=None, **kwargs):
        self.app = app
        self.usuario = usuario
        self.tema = tema or ThemeManager.get_colors()

        color_fondo = kwargs.pop(
            "fg_color",
            self.tema.get("app_bg", "#F8FAFC")
        )

        super().__init__(
            master,
            fg_color=color_fondo,
            **kwargs
        )

    # =====================================================
    # LIMPIEZA
    # =====================================================

    def limpiar_widgets(self, contenedor=None):
        """
        Elimina todos los widgets hijos de un contenedor.
        """
        contenedor = contenedor or self

        for widget in contenedor.winfo_children():
            widget.destroy()

    # =====================================================
    # GRID
    # =====================================================

    def configurar_columnas(self, contenedor, cantidad=1, peso=1):
        """
        Configura columnas de un contenedor.
        """
        for columna in range(cantidad):
            contenedor.grid_columnconfigure(columna, weight=peso)

    def configurar_filas(self, contenedor, cantidad=1, peso=0):
        """
        Configura filas de un contenedor.
        """
        for fila in range(cantidad):
            contenedor.grid_rowconfigure(fila, weight=peso)

    def configurar_expansion(self, contenedor):
        """
        Configura una expansión básica en fila 0 y columna 0.
        """
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

    # =====================================================
    # FACTORY METHODS / DEFS INSTANCIABLES
    # =====================================================

    def crear_frame(self, padre, color="transparent", radio=0, **kwargs):
        """
        Crea un CTkFrame.
        """
        return ctk.CTkFrame(
            padre,
            fg_color=color,
            corner_radius=radio,
            **kwargs
        )

    def crear_scroll_frame(self, padre, color="transparent", radio=0, **kwargs):
        """
        Crea un CTkScrollableFrame.
        """
        return ctk.CTkScrollableFrame(
            padre,
            fg_color=color,
            corner_radius=radio,
            scrollbar_button_color=self.tema.get("accent", "#7C3AED"),
            scrollbar_button_hover_color=self.tema.get("button_hover", "#6D28D9"),
            **kwargs
        )

    def crear_label(
        self,
        padre,
        texto,
        tamano=14,
        color=None,
        peso="normal",
        anchor="w",
        **kwargs
    ):
        """
        Crea un CTkLabel reutilizable.
        """
        return ctk.CTkLabel(
            padre,
            text=texto,
            font=("Segoe UI", tamano, peso),
            text_color=color or self.tema.get("text", "#111827"),
            fg_color="transparent",
            anchor=anchor,
            **kwargs
        )

    def crear_boton(
        self,
        padre,
        texto,
        comando,
        ancho=140,
        alto=36,
        color=None,
        hover=None,
        color_texto="#FFFFFF",
        **kwargs
    ):
        """
        Crea un CTkButton reutilizable.
        """
        return ctk.CTkButton(
            padre,
            text=texto,
            command=comando,
            width=ancho,
            height=alto,
            fg_color=color or self.tema.get("accent", "#7C3AED"),
            hover_color=hover or self.tema.get("button_hover", "#6D28D9"),
            text_color=color_texto,
            **kwargs
        )


class BaseView(BaseFrame):
    """
    Compatibilidad con vistas anteriores que ya usaban BaseView.
    """

    def __init__(self, master, app=None, **kwargs):
        super().__init__(
            master,
            app=app,
            **kwargs
        )

        self.colors = self.tema

    def refresh_theme(self):
        self.colors = ThemeManager.get_colors()
        self.tema = self.colors
        self.configure(
            fg_color=self.colors.get("app_bg", "#F8FAFC")
        )


class SidebarLayout(BaseView):
    """
    Layout base con barra lateral.
    Puede usarse para vistas que necesiten sidebar.
    """

    def __init__(
        self,
        master,
        app=None,
        active_page="Home",
        title="SoftRelief",
        **kwargs
    ):
        super().__init__(
            master,
            app=app,
            **kwargs
        )

        self.active_page = active_page
        self.title = title

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=self.colors.get("sidebar_bg", "#FFFFFF")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.colors.get("app_bg", "#F8FAFC")
        )
        self.content.grid(row=0, column=1, sticky="nsew")

        self.configurar_expansion(self.content)