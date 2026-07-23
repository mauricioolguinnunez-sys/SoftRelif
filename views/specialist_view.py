import customtkinter as ctk

from components import (
    SoftCard,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    SmallLabel,
    PrimaryButton,
    SecondaryButton,
)

from database.connection import get_connection
from utils.theme_manager import ThemeManager
from utils.app_state import AppState
from models.user_model import UserModel


class SpecialistView(ctk.CTkFrame):
    """
    Vista única del especialista.

    RF:
    - RF-005 Visualizar panel de especialista.
    - RF-020 Asignar recomendación.
    - RF-022 Cargar recurso.
    - Trayectoria: consultar historial relacional del usuario atendido.

    Nota:
    Se elimina la función de marcar seguimiento.
    """

    def __init__(self, master, app=None, user=None):
        self.app = app
        self.usuario_actual = user or getattr(app, "current_user", None)

        self.tema_nombre = self.usuario_actual.get("tema_visual", "light") if self.usuario_actual else "light"
        self.tema = ThemeManager.get_theme(self.tema_nombre)

        super().__init__(master, fg_color="transparent", corner_radius=0)

        self.usuarios = []
        self.usuarios_filtrados = []
        self.usuario_seleccionado = None
        self.historial_usuario = []

        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace_add("write", self.filtrar_usuarios)

        self.total_label = None
        self.activos_label = None
        self.recomendados_label = None
        self.mongo_label = None

        self.lista_usuarios = None
        self.detalle_card = None
        self.historial_frame = None
        self.mensaje_label = None

        self.recomendacion_titulo = None
        self.recomendacion_descripcion = None

        self.recurso_titulo = None
        self.recurso_tipo_var = ctk.StringVar(value="texto")
        self.recurso_contenido = None

        self.crear_interfaz()

        if self.es_especialista():
            self.cargar_usuarios()
        else:
            self.mostrar_acceso_denegado()

    # =====================================================
    # HELPERS VISUALES
    # =====================================================

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

        if alto is not None:
            opciones["height"] = alto

        opciones.update(kwargs)
        return SoftCard(padre, **opciones)

    def marco(self, padre, color="transparent", **kwargs):
        return ctk.CTkFrame(padre, fg_color=color, **kwargs)

    def normalizar_usuario_para_vista(self, usuario):
        if not isinstance(usuario, dict):
            return {}

        datos = dict(usuario)

        def texto(valor, defecto="-"):
            if valor is None:
                return defecto

            valor_str = str(valor).strip()
            return valor_str if valor_str else defecto

        datos["id_usuario"] = texto(datos.get("id_usuario"), "-")
        datos["nombre"] = texto(datos.get("nombre"), "Sin nombre")
        datos["correo"] = texto(datos.get("correo"), texto(datos.get("usuario"), "Sin correo"))
        datos["usuario"] = texto(datos.get("usuario"), datos.get("correo", "Sin usuario"))

        rol = str(datos.get("rol") or "").strip().lower()
        if rol == "usuario":
            rol_texto = "Usuario"
        elif rol == "especialista":
            rol_texto = "Especialista"
        elif rol == "superuser":
            rol_texto = "Superuser"
        else:
            rol_texto = texto(datos.get("rol"), "Sin rol")
        datos["rol"] = rol_texto

        estado = str(datos.get("estado") or "").strip().lower()
        if estado == "activa":
            estado_texto = "activa"
        elif estado == "restringida":
            estado_texto = "restringida"
        else:
            estado_texto = texto(datos.get("estado"), "sin_estado")
        datos["estado"] = estado_texto

        tema = str(datos.get("tema_visual") or "").strip().lower()
        if tema in {"light", "claro", "", "default"}:
            tema_texto = "light"
        elif tema in {"dark", "oscuro"}:
            tema_texto = "dark"
        else:
            tema_texto = texto(datos.get("tema_visual"), "light")
        datos["tema_visual"] = tema_texto

        datos["mongo_id"] = texto(datos.get("mongo_id"), "-")
        datos["coleccion"] = texto(datos.get("coleccion"), "-")
        datos["acciones_especialista"] = datos.get("acciones_especialista") or 0
        datos["ultima_recomendacion"] = datos.get("ultima_recomendacion")

        return datos

    def entrada(self, padre, placeholder):
        return ctk.CTkEntry(
            padre,
            height=36,
            corner_radius=12,
            placeholder_text=placeholder,
            fg_color=self.color("app_bg", "#F8FAFC"),
            border_color=self.color("card_border", "#E5E7EB"),
            text_color=self.color("text", "#111827")
        )

    def area_texto(self, padre, alto=95):
        return ctk.CTkTextbox(
            padre,
            height=alto,
            corner_radius=12,
            fg_color=self.color("app_bg", "#F8FAFC"),
            border_color=self.color("card_border", "#E5E7EB"),
            border_width=1,
            text_color=self.color("text", "#111827")
        )

    def boton_secundario(self, padre, texto, comando, ancho=120):
        return SecondaryButton(
            padre,
            text=texto,
            width=ancho,
            height=34,
            fg_color=self.color("card_bg", "#FFFFFF"),
            hover_color=self.color("menu_hover", "#F3F4F6"),
            text_color=self.color("text", "#111827"),
            border_width=1,
            border_color=self.color("card_border", "#E5E7EB"),
            command=comando
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
            width=95,
            height=26,
            corner_radius=13,
            fg_color=fondo,
            text_color=color_texto,
            font=("Segoe UI", 11, "bold")
        )

    # =====================================================
    # CONTROL DE ROL
    # =====================================================

    def es_especialista(self):
        return self.usuario_actual and self.usuario_actual.get("rol") == "especialista"

    def mostrar_acceso_denegado(self):
        self.limpiar(self)

        card = self.tarjeta(self, alto=220)
        card.grid(row=0, column=0, sticky="ew", padx=35, pady=35)
        card.grid_propagate(False)

        TitleLabel(
            card,
            "Acceso no permitido",
            size=28,
            text_color="#DC2626"
        ).pack(anchor="w", padx=28, pady=(32, 8))

        BodyLabel(
            card,
            "Esta vista está reservada para usuarios con rol especialista.",
            size=15,
            text_color=self.color("text_soft", "#6B7280"),
            wraplength=700
        ).pack(anchor="w", padx=28, pady=(0, 20))

        PrimaryButton(
            card,
            text="Cerrar sesión",
            width=140,
            height=36,
            command=self.cerrar_sesion
        ).pack(anchor="w", padx=28)

    # =====================================================
    # INTERFAZ PRINCIPAL
    # =====================================================

    def crear_interfaz(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(3, weight=1)

        self.crear_encabezado()
        self.crear_metricas()
        self.crear_panel_usuarios()
        self.crear_panel_trabajo()
        self.crear_mensaje()

    def crear_encabezado(self):
        header = self.tarjeta(self, alto=120)
        header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=35,
            pady=(28, 14)
        )
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        caja_texto = self.marco(header)
        caja_texto.grid(row=0, column=0, sticky="w", padx=28, pady=18)

        TitleLabel(
            caja_texto,
            "Panel Especialista",
            size=32,
            text_color=self.color("text", "#111827")
        ).pack(anchor="w")

        SubtitleLabel(
            caja_texto,
            "Usuarios comunes, recomendaciones, recursos y trayectoria de atención.",
            size=14,
            text_color=self.color("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(4, 0))

        acciones = self.marco(header)
        acciones.grid(row=0, column=1, sticky="e", padx=28, pady=34)

        SecondaryButton(
            acciones,
            text="Actualizar",
            width=115,
            height=36,
            fg_color=self.color("card_bg", "#FFFFFF"),
            hover_color=self.color("menu_hover", "#F3F4F6"),
            text_color=self.color("text", "#111827"),
            border_width=1,
            border_color=self.color("card_border", "#E5E7EB"),
            command=self.cargar_usuarios
        ).grid(row=0, column=0, padx=(0, 10))

        PrimaryButton(
            acciones,
            text="Cerrar sesión",
            width=130,
            height=36,
            command=self.cerrar_sesion
        ).grid(row=0, column=1)

    def crear_metricas(self):
        contenedor = self.marco(self)
        contenedor.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=35,
            pady=(0, 14)
        )

        for columna in range(4):
            contenedor.grid_columnconfigure(columna, weight=1)

        metricas = [
            ("Usuarios comunes", "0", "total_label"),
            ("Activos", "0", "activos_label"),
            ("Recomendados", "0", "recomendados_label"),
            ("Vinculados Mongo", "0", "mongo_label"),
        ]

        for columna, (titulo, valor, atributo) in enumerate(metricas):
            tarjeta = self.tarjeta(contenedor, alto=92)
            tarjeta.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=self.padding_metrica(columna, 4)
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
                size=27,
                text_color=self.color("text", "#111827")
            )
            label_valor.pack(anchor="w", padx=20, pady=(4, 0))

            setattr(self, atributo, label_valor)

    def crear_panel_usuarios(self):
        panel = self.tarjeta(self)
        panel.grid(
            row=2,
            column=0,
            rowspan=2,
            sticky="nsew",
            padx=(35, 12),
            pady=(0, 12)
        )

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        BodyLabel(
            panel,
            "Usuarios comunes existentes",
            size=18,
            text_color=self.color("text", "#111827")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        buscador = ctk.CTkEntry(
            panel,
            textvariable=self.busqueda_var,
            height=36,
            corner_radius=12,
            placeholder_text="Buscar por nombre, correo, estado o Mongo ID...",
            fg_color=self.color("app_bg", "#F8FAFC"),
            border_color=self.color("card_border", "#E5E7EB"),
            text_color=self.color("text", "#111827")
        )
        buscador.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))

        self.lista_usuarios = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.color("card_border", "#E5E7EB"),
            scrollbar_button_hover_color=self.color("accent", "#7C3AED")
        )
        self.lista_usuarios.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 20))
        self.lista_usuarios.grid_columnconfigure(0, weight=1)

    def crear_panel_trabajo(self):
        self.panel_trabajo = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.color("card_border", "#E5E7EB"),
            scrollbar_button_hover_color=self.color("accent", "#7C3AED")
        )

        self.panel_trabajo.grid(
            row=2,
            column=1,
            rowspan=2,
            sticky="nsew",
            padx=(12, 35),
            pady=(0, 12)
        )

        self.panel_trabajo.grid_columnconfigure(0, weight=1)
        self.panel_trabajo.grid_columnconfigure(1, weight=1)

        self.crear_detalle_usuario()
        self.crear_form_recomendacion()
        self.crear_form_recurso()
        self.crear_historial()

    def crear_mensaje(self):
        self.mensaje_label = SmallLabel(
            self,
            "",
            size=13,
            text_color=self.color("text_soft", "#6B7280")
        )
        self.mensaje_label.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            padx=40,
            pady=(0, 15)
        )

    # =====================================================
    # TARJETAS DE TRABAJO
    # =====================================================

    def crear_detalle_usuario(self):
        self.detalle_card = self.tarjeta(self.panel_trabajo, alto=170)
        self.detalle_card.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=0,
            pady=(0, 14)
        )
        self.detalle_card.grid_propagate(False)
        self.dibujar_detalle_usuario()

    def crear_form_recomendacion(self):
        card = self.tarjeta(self.panel_trabajo)
        card.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 14))
        card.grid_columnconfigure(0, weight=1)

        TitleLabel(
            card,
            "RF-020 Asignar recomendación",
            size=19,
            text_color=self.color("text", "#111827")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 6))

        SmallLabel(
            card,
            "La recomendación aparecerá en el Home del usuario seleccionado.",
            size=12,
            text_color=self.color("text_soft", "#6B7280")
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        self.recomendacion_titulo = self.entrada(card, "Título de la recomendación")
        self.recomendacion_titulo.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        self.recomendacion_descripcion = self.area_texto(card, alto=120)
        self.recomendacion_descripcion.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 12))

        PrimaryButton(
            card,
            text="Guardar recomendación",
            height=36,
            command=self.guardar_recomendacion
        ).grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))

    def crear_form_recurso(self):
        card = self.tarjeta(self.panel_trabajo)
        card.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(0, 14))
        card.grid_columnconfigure(0, weight=1)

        TitleLabel(
            card,
            "RF-022 Cargar recurso",
            size=19,
            text_color=self.color("text", "#111827")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 6))

        SmallLabel(
            card,
            "Registra un recurso de apoyo vinculado al usuario seleccionado.",
            size=12,
            text_color=self.color("text_soft", "#6B7280")
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        self.recurso_titulo = self.entrada(card, "Título del recurso")
        self.recurso_titulo.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        tipo = ctk.CTkOptionMenu(
            card,
            variable=self.recurso_tipo_var,
            values=["texto", "enlace", "documento", "audio", "video"],
            height=34,
            fg_color=self.color("button", "#7C3AED"),
            button_color=self.color("button_hover", "#6D28D9"),
            button_hover_color=self.color("accent", "#7C3AED")
        )
        tipo.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

        self.recurso_contenido = self.area_texto(card, alto=95)
        self.recurso_contenido.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 12))

        PrimaryButton(
            card,
            text="Guardar recurso",
            height=36,
            command=self.guardar_recurso
        ).grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))

    def crear_historial(self):
        card = self.tarjeta(self.panel_trabajo)
        card.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=0,
            pady=(0, 14)
        )

        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        TitleLabel(
            card,
            "Trayectoria del usuario",
            size=20,
            text_color=self.color("text", "#111827")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 6))

        SmallLabel(
            card,
            "Historial de recomendaciones y recursos registrados por este especialista.",
            size=12,
            text_color=self.color("text_soft", "#6B7280")
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        self.historial_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent",
            corner_radius=0,
            height=300
        )
        self.historial_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.historial_frame.grid_columnconfigure(0, weight=1)

        self.dibujar_historial()

    # =====================================================
    # CONSULTAS
    # =====================================================

    def cargar_usuarios(self):
        if not self.es_especialista():
            self.mostrar_acceso_denegado()
            return

        try:
            usuarios_brutos = self.consultar_usuarios_comunes()
            self.usuarios = [
                self.normalizar_usuario_para_vista(usuario)
                for usuario in usuarios_brutos
            ]

            for usuario in self.usuarios:
                if not usuario.get("mongo_id") or usuario.get("mongo_id") == "-":
                    self.asegurar_conexion_mongo(usuario.get("id_usuario"))

            self.usuarios = [
                self.normalizar_usuario_para_vista(usuario)
                for usuario in self.consultar_usuarios_comunes()
            ]
            self.usuarios_filtrados = self.usuarios[:]

            self.actualizar_metricas()
            self.dibujar_lista_usuarios()

            if self.usuarios:
                id_actual = self.usuario_seleccionado.get("id_usuario") if self.usuario_seleccionado else None
                self.seleccionar_usuario(id_actual or self.usuarios[0].get("id_usuario"))
            else:
                self.usuario_seleccionado = None
                self.historial_usuario = []
                self.dibujar_detalle_usuario()
                self.dibujar_historial()

            self.mostrar_mensaje("Usuarios comunes cargados correctamente.")

        except Exception as error:
            self.usuarios = []
            self.usuarios_filtrados = []
            self.actualizar_metricas()
            self.dibujar_lista_usuarios()
            self.mostrar_mensaje(f"No se pudieron cargar usuarios: {error}", error=True)

    def consultar_usuarios_comunes(self):
        id_especialista = self.usuario_actual.get("id_usuario")
        return UserModel.get_common_users_for_specialist(id_especialista)

    def consultar_usuario_por_id(self, id_usuario):
        usuario = UserModel.get_user_detail(id_usuario)

        if not usuario:
            return None

        if usuario.get("rol") != "usuario":
            return None

        return usuario

    def consultar_historial_usuario(self, id_usuario):
        id_especialista = self.usuario_actual.get("id_usuario")

        return UserModel.get_history_for_specialist(
            id_usuario=id_usuario,
            id_especialista=id_especialista
        )

    def asegurar_conexion_mongo(self, id_usuario):
        UserModel.ensure_mongo_link(id_usuario)

    # =====================================================
    # LISTA Y SELECCIÓN
    # =====================================================

    def filtrar_usuarios(self, *args):
        texto = self.busqueda_var.get().strip().lower()

        if not texto:
            self.usuarios_filtrados = self.usuarios[:]
        else:
            self.usuarios_filtrados = [
                usuario for usuario in self.usuarios
                if self.coincide_busqueda(usuario, texto)
            ]

        self.dibujar_lista_usuarios()

    def coincide_busqueda(self, usuario, texto):
        campos = [
            usuario.get("nombre", ""),
            usuario.get("correo", ""),
            usuario.get("estado", ""),
            usuario.get("tema_visual", ""),
            usuario.get("mongo_id", ""),
        ]

        return any(texto in str(campo).lower() for campo in campos)

    def dibujar_lista_usuarios(self):
        if not self.lista_usuarios:
            return

        self.limpiar(self.lista_usuarios)

        if not self.usuarios_filtrados:
            BodyLabel(
                self.lista_usuarios,
                "No hay usuarios comunes registrados.",
                size=14,
                text_color=self.color("text_soft", "#6B7280"),
                wraplength=300
            ).grid(row=0, column=0, sticky="w", padx=8, pady=18)
            return

        for fila, usuario in enumerate(self.usuarios_filtrados):
            self.crear_fila_usuario(usuario, fila)

    def crear_fila_usuario(self, usuario, fila):
        seleccionado = (
            self.usuario_seleccionado
            and str(self.usuario_seleccionado.get("id_usuario")) == str(usuario.get("id_usuario"))
        )

        fondo = self.color("accent_soft", "#EDE9FE") if seleccionado else self.color("card_bg", "#FFFFFF")
        borde = self.color("accent", "#7C3AED") if seleccionado else self.color("card_border", "#E5E7EB")

        card = ctk.CTkFrame(
            self.lista_usuarios,
            fg_color=fondo,
            corner_radius=16,
            border_width=1,
            border_color=borde
        )
        card.grid(row=fila, column=0, sticky="ew", padx=4, pady=6)
        card.grid_columnconfigure(0, weight=1)

        texto_estado = usuario.get("estado", "-")
        acciones = usuario.get("acciones_especialista", 0)
        ultima = usuario.get("ultima_recomendacion") or "Sin recomendación"

        boton = ctk.CTkButton(
            card,
            text=(
                f"{usuario.get('nombre', '-')}\n"
                f"{usuario.get('correo', '-')}\n"
                f"Acciones contigo: {acciones} · Última rec.: {ultima}"
            ),
            height=78,
            corner_radius=14,
            fg_color="transparent",
            hover_color=self.color("menu_hover", "#F3F4F6"),
            text_color=self.color("text", "#111827"),
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            command=lambda uid=usuario.get("id_usuario"): self.seleccionar_usuario(uid)
        )
        boton.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        self.etiqueta_estado(card, texto_estado).grid(row=0, column=1, padx=(0, 8), pady=8)

    def seleccionar_usuario(self, id_usuario):
        self.asegurar_conexion_mongo(id_usuario)

        usuario = self.consultar_usuario_por_id(id_usuario)

        if not usuario:
            self.mostrar_mensaje("Usuario no encontrado.", error=True)
            return

        self.usuario_seleccionado = usuario
        self.historial_usuario = self.consultar_historial_usuario(id_usuario)

        self.dibujar_lista_usuarios()
        self.dibujar_detalle_usuario()
        self.dibujar_historial()

        self.mostrar_mensaje(f"Usuario seleccionado: {usuario.get('nombre')}.")

    # =====================================================
    # DETALLE E HISTORIAL
    # =====================================================

    def dibujar_detalle_usuario(self):
        if not self.detalle_card:
            return

        self.limpiar(self.detalle_card)

        if not self.usuario_seleccionado:
            TitleLabel(
                self.detalle_card,
                "Selecciona un usuario",
                size=24,
                text_color=self.color("text", "#111827")
            ).pack(anchor="w", padx=24, pady=(28, 8))

            BodyLabel(
                self.detalle_card,
                "Elige un usuario común para ver trayectoria, asignar recomendaciones o cargar recursos.",
                size=14,
                text_color=self.color("text_soft", "#6B7280"),
                wraplength=720
            ).pack(anchor="w", padx=24)
            return

        usuario = self.usuario_seleccionado

        self.detalle_card.grid_columnconfigure(0, weight=1)
        self.detalle_card.grid_columnconfigure(1, weight=0)

        caja = self.marco(self.detalle_card)
        caja.grid(row=0, column=0, sticky="w", padx=24, pady=24)

        TitleLabel(
            caja,
            usuario.get("nombre", "-"),
            size=25,
            text_color=self.color("text", "#111827")
        ).pack(anchor="w")

        BodyLabel(
            caja,
            usuario.get("correo", "-"),
            size=14,
            text_color=self.color("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(2, 8))

        SmallLabel(
            caja,
            (
                f"ID relacional: {usuario.get('id_usuario')}   |   "
                f"Mongo ID: {usuario.get('mongo_id', '-')}   |   "
                f"Tema: {usuario.get('tema_visual', '-')}"
            ),
            size=12,
            text_color=self.color("text_soft", "#6B7280")
        ).pack(anchor="w")

        estado_box = self.marco(self.detalle_card)
        estado_box.grid(row=0, column=1, sticky="e", padx=24, pady=24)

        self.etiqueta_estado(estado_box, usuario.get("estado", "-")).pack(anchor="e", pady=(0, 8))

        self.boton_secundario(
            estado_box,
            "Actualizar trayectoria",
            lambda: self.seleccionar_usuario(usuario.get("id_usuario")),
            ancho=170
        ).pack(anchor="e")

    def dibujar_historial(self):
        if not self.historial_frame:
            return

        self.limpiar(self.historial_frame)

        if not self.usuario_seleccionado:
            SmallLabel(
                self.historial_frame,
                "Selecciona un usuario para ver su trayectoria.",
                size=12,
                text_color=self.color("text_soft", "#6B7280")
            ).grid(row=0, column=0, sticky="w", padx=4, pady=12)
            return

        if not self.historial_usuario:
            SmallLabel(
                self.historial_frame,
                "Todavía no hay recomendaciones ni recursos registrados para este usuario por este especialista.",
                size=12,
                text_color=self.color("text_soft", "#6B7280")
            ).grid(row=0, column=0, sticky="w", padx=4, pady=12)
            return

        for fila, registro in enumerate(self.historial_usuario):
            self.crear_fila_historial(registro, fila)

    def crear_fila_historial(self, registro, fila):
        card = ctk.CTkFrame(
            self.historial_frame,
            fg_color=self.color("app_bg", "#F8FAFC"),
            corner_radius=14,
            border_width=1,
            border_color=self.color("card_border", "#E5E7EB")
        )
        card.grid(row=fila, column=0, sticky="ew", padx=4, pady=5)
        card.grid_columnconfigure(0, weight=1)

        accion = str(registro.get("accion", "-")).replace("_", " ").title()
        fecha = registro.get("fecha_evento", "-")
        actor = registro.get("actor_nombre") or "Especialista"

        TitleLabel(
            card,
            accion,
            size=14,
            text_color=self.color("text", "#111827")
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))

        SmallLabel(
            card,
            f"{fecha} · {actor}",
            size=11,
            text_color=self.color("text_soft", "#6B7280")
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 4))

        BodyLabel(
            card,
            registro.get("descripcion", "-"),
            size=12,
            text_color=self.color("text_soft", "#6B7280"),
            wraplength=760
        ).grid(row=2, column=0, sticky="w", padx=14, pady=(0, 10))

    # =====================================================
    # RF-020 Y RF-022
    # =====================================================

    def validar_usuario_seleccionado(self):
        if not self.usuario_seleccionado:
            self.mostrar_mensaje("Selecciona primero un usuario común.", error=True)
            return False

        if self.usuario_seleccionado.get("estado") == "restringida":
            self.mostrar_mensaje("No puedes registrar acciones para una cuenta restringida.", error=True)
            return False

        return True

    def guardar_recomendacion(self):
        if not self.validar_usuario_seleccionado():
            return

        titulo = self.recomendacion_titulo.get().strip()
        descripcion = self.recomendacion_descripcion.get("1.0", "end-1c").strip()

        if not titulo or not descripcion:
            self.mostrar_mensaje("Completa el título y la recomendación.", error=True)
            return

        texto = (
            f"RECOMENDACION\n"
            f"Título: {titulo}\n"
            f"Detalle: {descripcion}\n"
            f"Mongo ID: {self.usuario_seleccionado.get('mongo_id', '-')}"
        )

        resultado = self.registrar_accion(
            accion="asignar_recomendacion",
            descripcion=texto
        )

        if resultado["success"]:
            self.recomendacion_titulo.delete(0, "end")
            self.recomendacion_descripcion.delete("1.0", "end")
            self.seleccionar_usuario(self.usuario_seleccionado.get("id_usuario"))
            self.cargar_usuarios()

        self.mostrar_mensaje(resultado["message"], error=not resultado["success"])

    def guardar_recurso(self):
        if not self.validar_usuario_seleccionado():
            return

        titulo = self.recurso_titulo.get().strip()
        tipo = self.recurso_tipo_var.get().strip()
        contenido = self.recurso_contenido.get("1.0", "end-1c").strip()

        if not titulo or not contenido:
            self.mostrar_mensaje("Completa el título y contenido del recurso.", error=True)
            return

        texto = (
            f"RECURSO\n"
            f"Título: {titulo}\n"
            f"Tipo: {tipo}\n"
            f"Contenido: {contenido}\n"
            f"Mongo ID: {self.usuario_seleccionado.get('mongo_id', '-')}"
        )

        resultado = self.registrar_accion(
            accion="cargar_recurso",
            descripcion=texto
        )

        if resultado["success"]:
            self.recurso_titulo.delete(0, "end")
            self.recurso_contenido.delete("1.0", "end")
            self.seleccionar_usuario(self.usuario_seleccionado.get("id_usuario"))
            self.cargar_usuarios()

        self.mostrar_mensaje(resultado["message"], error=not resultado["success"])

    def sugerir_musica_usuario(self, track):
        if not self.validar_usuario_seleccionado():
            return {
                "success": False,
                "message": "Selecciona primero un usuario común."
            }

        if not isinstance(track, dict):
            return {
                "success": False,
                "message": "Selecciona una pista válida."
            }

        descripcion = (
            f"MUSICA_SUGERIDA\n"
            f"ID: {track.get('id', '-')}\n"
            f"Título: {track.get('title', '-')}\n"
            f"Categoría: {track.get('category', '-')}\n"
            f"Descripción: {track.get('description', '-')}"
        )

        resultado = self.registrar_accion(
            accion="sugerir_musica",
            descripcion=descripcion
        )

        if resultado["success"]:
            self.seleccionar_usuario(self.usuario_seleccionado.get("id_usuario"))
            self.cargar_usuarios()

        return resultado

    def registrar_accion(self, accion, descripcion):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                INSERT INTO bitacora_cuenta (
                    id_admin,
                    id_usuario,
                    accion,
                    descripcion,
                    fecha_evento
                )
                VALUES (%s, %s, %s, %s, NOW());
            """, (
                self.usuario_actual.get("id_usuario"),
                self.usuario_seleccionado.get("id_usuario"),
                accion,
                descripcion
            ))

            conexion.commit()

            return {
                "success": True,
                "message": "Acción registrada correctamente."
            }

        except Exception as error:
            conexion.rollback()

            return {
                "success": False,
                "message": f"No se pudo registrar la acción: {error}"
            }

        finally:
            cursor.close()
            conexion.close()

    # =====================================================
    # MÉTRICAS Y SESIÓN
    # =====================================================

    def actualizar_metricas(self):
        total = len(self.usuarios)
        activos = sum(1 for u in self.usuarios if u.get("estado") == "activa")
        recomendados = sum(1 for u in self.usuarios if u.get("ultima_recomendacion"))
        mongo = sum(1 for u in self.usuarios if u.get("mongo_id"))

        if self.total_label:
            self.total_label.configure(text=str(total))

        if self.activos_label:
            self.activos_label.configure(text=str(activos))

        if self.recomendados_label:
            self.recomendados_label.configure(text=str(recomendados))

        if self.mongo_label:
            self.mongo_label.configure(text=str(mongo))

    def mostrar_mensaje(self, texto, error=False):
        if not self.mensaje_label:
            return

        color = "#DC2626" if error else self.color("text_soft", "#6B7280")
        self.mensaje_label.configure(text=texto, text_color=color)

    def cerrar_sesion(self):
        if self.usuario_actual:
            tema = self.usuario_actual.get("tema_visual", "light")
            self.app.login_theme = tema
            AppState.save_last_theme(tema)

        if self.app:
            self.app.current_user = None

            if hasattr(self.app, "show_login"):
                self.app.show_login()

    def padding_metrica(self, columna, total_columnas):
        if columna == 0:
            return (0, 8)

        if columna == total_columnas - 1:
            return (8, 0)

        return (8, 8)