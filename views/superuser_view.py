import customtkinter as ctk
from utils.app_state import AppState

from components import (
    SoftCard,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    SmallLabel,
    PrimaryButton,
    SecondaryButton,
)

from controllers.user_controller import UserController
from utils.theme_manager import ThemeManager


class BaseVistaComponentes(ctk.CTkFrame):
    """
    Base local para vistas administrativas.
    Usa componentes del proyecto sin modificar la carpeta components/.
    """

    def __init__(self, master, app, **kwargs):
        self.app = app
        self.usuario_actual = getattr(app, "current_user", None)

        nombre_tema = "light"

        if self.usuario_actual:
            nombre_tema = self.usuario_actual.get("tema_visual", "light")

        self.tema = ThemeManager.get_theme(nombre_tema)

        super().__init__(
            master,
            fg_color="transparent",
            corner_radius=0,
            **kwargs
        )

    def color(self, clave, defecto):
        return self.tema.get(clave, defecto)

    def limpiar(self, contenedor):
        for widget in contenedor.winfo_children():
            widget.destroy()

    def tarjeta(self, padre, alto=None, radio=18, **kwargs):
        opciones = {
            "corner_radius": radio,
            "fg_color": self.color("card_bg", "#FFFFFF"),
            "border_width": 1,
            "border_color": self.color("card_border", "#E5E7EB"),
        }

        if alto:
            opciones["height"] = alto

        opciones.update(kwargs)

        return SoftCard(padre, **opciones)

    def marco(self, padre, color="transparent", **kwargs):
        return ctk.CTkFrame(
            padre,
            fg_color=color,
            **kwargs
        )

    def etiqueta_estado(self, padre, estado):
        estado_normalizado = str(estado).lower()

        if estado_normalizado == "activa":
            texto = "Activa"
            fondo = "#DCFCE7"
            color_texto = "#166534"
        else:
            texto = "Restringida"
            fondo = "#FEE2E2"
            color_texto = "#991B1B"

        return ctk.CTkLabel(
            padre,
            text=texto,
            width=92,
            height=26,
            corner_radius=13,
            fg_color=fondo,
            text_color=color_texto,
            font=("Segoe UI", 11, "bold")
        )

    def boton_secundario(self, padre, texto, comando, ancho=100):
        return SecondaryButton(
            padre,
            text=texto,
            width=ancho,
            height=30,
            fg_color=self.color("card_bg", "#FFFFFF"),
            hover_color=self.color("menu_hover", "#F3F4F6"),
            text_color=self.color("text", "#111827"),
            border_width=1,
            border_color=self.color("card_border", "#E5E7EB"),
            command=comando
        )

    def boton_peligro(self, padre, texto, comando, ancho=95):
        return ctk.CTkButton(
            padre,
            text=texto,
            width=ancho,
            height=30,
            corner_radius=10,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            text_color="#FFFFFF",
            font=("Segoe UI", 12, "bold"),
            command=comando
        )


class SuperuserView(BaseVistaComponentes):
    """
    Panel profesional para administrar usuarios de SoftRelief.

    Funciones:
    - Listar usuarios.
    - Buscar por nombre, usuario, correo, rol o estado.
    - Restringir usuarios.
    - Activar usuarios.
    - Eliminar usuarios.
    - Proteger cuentas superuser.
    """

    def __init__(self, master, app):
        super().__init__(
            master,
            app,
            width=980,
            height=700
        )

        self.usuarios = []
        self.usuarios_filtrados = []

        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace_add("write", self.filtrar_usuarios)

        self.tabla = None
        self.mensaje = None
        self.total_label = None
        self.activos_label = None
        self.restringidos_label = None

        self.crear_interfaz()
        self.cargar_usuarios()

    # =====================================================
    # INTERFAZ PRINCIPAL
    # =====================================================

    def crear_interfaz(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.crear_encabezado()
        self.crear_metricas()
        self.crear_panel_tabla()
        self.crear_mensaje()

    def crear_encabezado(self):
        header = self.tarjeta(
            self,
            alto=115
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=35,
            pady=(28, 14)
        )
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        caja_texto = self.marco(header)
        caja_texto.grid(
            row=0,
            column=0,
            sticky="w",
            padx=28,
            pady=18
        )

        TitleLabel(
            caja_texto,
            "Panel Superuser",
            size=32,
            text_color=self.color("text", "#111827")
        ).pack(anchor="w")

        SubtitleLabel(
            caja_texto,
            "Administra cuentas registradas, estados de acceso y permisos básicos.",
            size=14,
            text_color=self.color("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(4, 0))

        PrimaryButton(
            header,
            text="Cerrar Sesion",
            width=130,
            height=36,
            command=self.cerrar_sesion
        ).grid(
            row=0,
            column=1,
            padx=28,
            pady=38,
            sticky="e"
        )

    def crear_metricas(self):
        contenedor = self.marco(self)
        contenedor.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=35,
            pady=(0, 14)
        )

        for columna in range(3):
            contenedor.grid_columnconfigure(columna, weight=1)

        metricas = [
            ("Usuarios totales", "0", "total_label"),
            ("Cuentas activas", "0", "activos_label"),
            ("Cuentas restringidas", "0", "restringidos_label"),
        ]

        for columna, (titulo, valor, atributo) in enumerate(metricas):
            tarjeta = self.tarjeta(
                contenedor,
                alto=92
            )
            tarjeta.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=self.padding_metrica(columna)
            )
            tarjeta.grid_propagate(False)

            SmallLabel(
                tarjeta,
                titulo,
                size=12,
                text_color=self.color("text_soft", "#6B7280")
            ).pack(anchor="w", padx=20, pady=(16, 0))

            label_valor = TitleLabel(
                tarjeta,
                valor,
                size=28,
                text_color=self.color("text", "#111827")
            )
            label_valor.pack(anchor="w", padx=20, pady=(4, 0))

            setattr(self, atributo, label_valor)

    def crear_panel_tabla(self):
        panel = self.tarjeta(self)
        panel.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=35,
            pady=(0, 12)
        )

        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        barra = self.marco(panel)
        barra.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(18, 12)
        )
        barra.grid_columnconfigure(0, weight=1)

        BodyLabel(
            barra,
            "Cuentas registradas",
            size=17,
            text_color=self.color("text", "#111827")
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        buscador = ctk.CTkEntry(
            barra,
            textvariable=self.busqueda_var,
            width=280,
            height=34,
            corner_radius=12,
            placeholder_text="Buscar usuario...",
            fg_color=self.color("app_bg", "#F8FAFC"),
            border_color=self.color("card_border", "#E5E7EB"),
            text_color=self.color("text", "#111827")
        )
        buscador.grid(
            row=0,
            column=1,
            sticky="e"
        )

        self.tabla = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.color("card_border", "#E5E7EB"),
            scrollbar_button_hover_color=self.color("accent", "#7C3AED")
        )
        self.tabla.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20)
        )

    def crear_mensaje(self):
        self.mensaje = SmallLabel(
            self,
            "",
            size=13,
            text_color=self.color("text_soft", "#6B7280")
        )
        self.mensaje.grid(
            row=3,
            column=0,
            sticky="w",
            padx=40,
            pady=(0, 15)
        )

    # =====================================================
    # DATOS
    # =====================================================
    def cargar_usuarios(self):
     """
    Carga los usuarios desde la base de datos y actualiza la tabla.
    """

    resultado = UserController.get_users(self.usuario_actual)

    if not resultado["success"]:
        self.usuarios = []
        self.usuarios_filtrados = []
        self.actualizar_metricas()
        self.dibujar_tabla()
        self.mostrar_mensaje(resultado["message"], error=True)
        return

    self.usuarios = resultado["users"]
    self.usuarios_filtrados = self.usuarios[:]

    self.actualizar_metricas()
    self.dibujar_tabla()
    self.mostrar_mensaje("Usuarios cargados correctamente.")
    def cerrar_sesion(self):
     """
    Cierra la sesión actual y regresa al login.
    """

     if self.usuario_actual:
        tema = self.usuario_actual.get("tema_visual", "light")
        self.app.login_theme = tema
        AppState.save_last_theme(tema)

     self.app.current_user = None

     if hasattr(self.app, "show_login"):
        self.app.show_login()

   

    def filtrar_usuarios(self, *args):
        texto = self.busqueda_var.get().strip().lower()

        if not texto:
            self.usuarios_filtrados = self.usuarios[:]
        else:
            self.usuarios_filtrados = [
                usuario for usuario in self.usuarios
                if self.coincide_busqueda(usuario, texto)
            ]

        self.dibujar_tabla()

    def coincide_busqueda(self, usuario, texto):
        campos = [
            usuario.get("nombre", ""),
            usuario.get("usuario", ""),
            usuario.get("correo", ""),
            usuario.get("rol", ""),
            usuario.get("estado", ""),
        ]

        return any(texto in str(campo).lower() for campo in campos)

    def actualizar_metricas(self):
        total = len(self.usuarios)
        activos = sum(1 for u in self.usuarios if u.get("estado") == "activa")
        restringidos = total - activos

        self.total_label.configure(text=str(total))
        self.activos_label.configure(text=str(activos))
        self.restringidos_label.configure(text=str(restringidos))

    def mostrar_mensaje(self, texto, error=False):
        color = "#DC2626" if error else self.color("text_soft", "#6B7280")
        self.mensaje.configure(text=texto, text_color=color)

    # =====================================================
    # TABLA
    # =====================================================

    def dibujar_tabla(self):
        self.limpiar(self.tabla)
        self.configurar_columnas_tabla()
        self.crear_encabezados_tabla()

        if not self.usuarios_filtrados:
            self.crear_tabla_vacia()
            return

        for fila, usuario in enumerate(self.usuarios_filtrados, start=1):
            self.crear_fila_usuario(fila, usuario)

    def configurar_columnas_tabla(self):
        pesos = [0, 1, 1, 2, 1, 1, 2]

        for columna, peso in enumerate(pesos):
            self.tabla.grid_columnconfigure(columna, weight=peso)

    def crear_encabezados_tabla(self):
        encabezados = [
            "ID",
            "Nombre",
            "Usuario",
            "Correo",
            "Rol",
            "Estado",
            "Acciones"
        ]

        for columna, texto in enumerate(encabezados):
            SmallLabel(
                self.tabla,
                texto,
                size=12,
                text_color=self.color("text_soft", "#6B7280")
            ).grid(
                row=0,
                column=columna,
                padx=10,
                pady=(6, 12),
                sticky="w"
            )

    def crear_tabla_vacia(self):
        BodyLabel(
            self.tabla,
            "No se encontraron usuarios con ese filtro.",
            size=14,
            text_color=self.color("text_soft", "#6B7280")
        ).grid(
            row=1,
            column=0,
            columnspan=7,
            sticky="w",
            padx=10,
            pady=25
        )

    def crear_fila_usuario(self, fila, usuario):
        datos = [
            usuario.get("id_usuario", "-"),
            usuario.get("nombre", "-"),
            usuario.get("usuario", "-"),
            usuario.get("correo", "-"),
            usuario.get("rol", "-"),
        ]

        for columna, valor in enumerate(datos):
            SmallLabel(
                self.tabla,
                str(valor),
                size=12,
                text_color=self.color("text", "#111827")
            ).grid(
                row=fila,
                column=columna,
                padx=10,
                pady=8,
                sticky="w"
            )

        self.etiqueta_estado(
            self.tabla,
            usuario.get("estado", "-")
        ).grid(
            row=fila,
            column=5,
            padx=10,
            pady=8,
            sticky="w"
        )

        self.crear_acciones_fila(fila, usuario)

    def crear_acciones_fila(self, fila, usuario):
        acciones = self.marco(self.tabla)
        acciones.grid(
            row=fila,
            column=6,
            padx=10,
            pady=8,
            sticky="w"
        )

        if usuario.get("rol") == "superuser":
            ctk.CTkLabel(
                acciones,
                text="Protegido",
                width=100,
                height=28,
                corner_radius=10,
                fg_color=self.color("accent_soft", "#EDE9FE"),
                text_color=self.color("accent", "#7C3AED"),
                font=("Segoe UI", 11, "bold")
            ).pack()
            return

        id_usuario = usuario.get("id_usuario")
        estado = usuario.get("estado")

        if estado == "activa":
            self.boton_secundario(
                acciones,
                "Restringir",
                lambda uid=id_usuario: self.restringir_usuario(uid),
                ancho=95
            ).grid(
                row=0,
                column=0,
                padx=(0, 6)
            )
        else:
            self.boton_secundario(
                acciones,
                "Activar",
                lambda uid=id_usuario: self.activar_usuario(uid),
                ancho=95
            ).grid(
                row=0,
                column=0,
                padx=(0, 6)
            )

        self.boton_peligro(
            acciones,
            "Eliminar",
            lambda uid=id_usuario: self.confirmar_eliminacion(uid),
            ancho=90
        ).grid(
            row=0,
            column=1
        )

    # =====================================================
    # ACCIONES DE USUARIO
    # =====================================================

    def restringir_usuario(self, id_usuario):
        self.ejecutar_accion(
            lambda: UserController.restrict_user(
                self.usuario_actual,
                id_usuario
            )
        )

    def activar_usuario(self, id_usuario):
        self.ejecutar_accion(
            lambda: UserController.activate_user(
                self.usuario_actual,
                id_usuario
            )
        )

    def eliminar_usuario(self, id_usuario, ventana):
        resultado = UserController.delete_user(
            self.usuario_actual,
            id_usuario
        )

        ventana.destroy()
        self.mostrar_mensaje(resultado["message"], error=not resultado["success"])
        self.cargar_usuarios()

    def ejecutar_accion(self, accion):
        resultado = accion()
        self.mostrar_mensaje(resultado["message"], error=not resultado["success"])
        self.cargar_usuarios()

    # =====================================================
    # MODAL DE CONFIRMACIÓN
    # =====================================================

    def confirmar_eliminacion(self, id_usuario):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Confirmar eliminación")
        ventana.geometry("460x250")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.configure(
            fg_color=self.color("app_bg", "#F8FAFC")
        )

        tarjeta = self.tarjeta(
            ventana,
            alto=210
        )
        tarjeta.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )
        tarjeta.pack_propagate(False)

        TitleLabel(
            tarjeta,
            "¿Eliminar usuario?",
            size=24,
            text_color=self.color("text", "#111827")
        ).pack(
            pady=(28, 8)
        )

        BodyLabel(
            tarjeta,
            "Esta acción eliminará la cuenta seleccionada.\n"
            "No podrás recuperarla después.",
            size=14,
            text_color=self.color("text_soft", "#6B7280"),
            justify="center"
        ).pack(
            pady=(0, 18)
        )

        botones = self.marco(tarjeta)
        botones.pack()

        self.boton_secundario(
            botones,
            "Cancelar",
            ventana.destroy,
            ancho=130
        ).grid(
            row=0,
            column=0,
            padx=8
        )

        self.boton_peligro(
            botones,
            "Sí, eliminar",
            lambda: self.eliminar_usuario(id_usuario, ventana),
            ancho=130
        ).grid(
            row=0,
            column=1,
            padx=8
        )

    # =====================================================
    # UTILIDADES
    # =====================================================

    def padding_metrica(self, columna):
        if columna == 0:
            return (0, 8)

        if columna == 1:
            return (8, 8)

        return (8, 0)

    # =====================================================
    # ALIAS PARA COMPATIBILIDAD
    # =====================================================

    def load_users(self):
        self.cargar_usuarios()

    def restrict_user(self, id_usuario):
        self.restringir_usuario(id_usuario)

    def activate_user(self, id_usuario):
        self.activar_usuario(id_usuario)

    def confirm_delete_user(self, id_usuario):
        self.confirmar_eliminacion(id_usuario)

    def delete_user(self, id_usuario, window):
        self.eliminar_usuario(id_usuario, window)