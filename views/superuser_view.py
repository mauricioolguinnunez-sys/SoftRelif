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

from controllers.user_controller import UserController
from database.connection import get_connection
from models.user_model import UserModel
from utils.theme_manager import ThemeManager
from utils.app_state import AppState
from utils.i18n import Lang



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

        user_lang = self.usuario_actual.get("idioma") if self.usuario_actual else None
        Lang.set(user_lang or AppState.load_language())

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

    def normalizar_usuario_para_vista(self, usuario):
        if not isinstance(usuario, dict):
            return {}

        datos = dict(usuario)

        def texto(valor, defecto="-"):
            if valor is None:
                return defecto

            valor_str = str(valor).strip()
            return valor_str if valor_str else defecto

        nombre = texto(datos.get("nombre"), "Sin nombre")
        correo = texto(datos.get("correo"), texto(datos.get("usuario"), "Sin correo"))

        rol = str(datos.get("rol") or "").strip().lower()
        if rol in {"superuser", "superusuario"}:
            rol_texto = "superuser"
        elif rol in {"especialista"}:
            rol_texto = "especialista"
        elif rol in {"usuario", "user"}:
            rol_texto = "usuario"
        elif rol in {"sin_rol", "", "none", "null"}:
            rol_texto = "sin_rol"
        else:
            rol_texto = texto(datos.get("rol"), "sin_rol")

        estado = str(datos.get("estado") or "").strip().lower()
        if estado in {"activa", "active", "activo", "activa"}:
            estado_texto = "activa"
        elif estado in {"restringida", "restricted", "bloqueada"}:
            estado_texto = "restringida"
        else:
            estado_texto = texto(datos.get("estado"), "sin_estado")

        tema = str(datos.get("tema_visual") or "").strip().lower()
        if tema in {"light", "claro", "default", ""}:
            tema_texto = "light"
        elif tema in {"dark", "oscuro"}:
            tema_texto = "dark"
        else:
            tema_texto = texto(datos.get("tema_visual"), "light")

        datos["id_usuario"] = texto(datos.get("id_usuario"), "-")
        datos["nombre"] = nombre
        datos["correo"] = correo
        datos["usuario"] = texto(datos.get("usuario"), correo)
        datos["rol"] = rol_texto
        datos["estado"] = estado_texto
        datos["tema_visual"] = tema_texto
        datos["acciones_especialista"] = datos.get("acciones_especialista") or 0
        datos["ultima_recomendacion"] = datos.get("ultima_recomendacion")

        return datos

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
        return ctk.CTkFrame(
            padre,
            fg_color=color,
            **kwargs
        )

    def etiqueta_estado(self, padre, estado):
        estado_normalizado = str(estado).lower()

        if estado_normalizado == "activa":
            texto = Lang.get("super_state_active").capitalize()
            fondo = "#DCFCE7"
            color_texto = "#166534"
        else:
            texto = Lang.get("super_state_restricted").capitalize()
            fondo = "#FEE2E2"
            color_texto = "#991B1B"

        return ctk.CTkLabel(
            padre,
            text=texto,
            width=100,
            height=26,
            corner_radius=13,
            fg_color=fondo,
            text_color=color_texto,
            font=("Segoe UI", 11, "bold")
        )

    def etiqueta_rol(self, padre, rol):
        rol_normalizado = str(rol).lower()

        colores = {
            "superuser": (Lang.get("super_role_superuser"), "#EDE9FE", "#6D28D9"),
            "especialista": (Lang.get("super_role_specialist"), "#DBEAFE", "#1D4ED8"),
            "usuario": (Lang.get("super_role_user"), "#ECFDF5", "#047857"),
        }

        texto, fondo, color_texto = colores.get(
            rol_normalizado,
            (rol, "#F3F4F6", "#374151")
        )

        return ctk.CTkLabel(
            padre,
            text=texto,
            width=105,
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

    def boton_peligro(self, padre, texto, comando, ancho=90):
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


class SuperuserView(BaseVistaComponentes):
    """
    Panel Superuser adaptado al modelo relacional corregido.

    Tablas relacionadas:
    - usuario
    - rol
    - estado_cuenta
    - preferencia_visual
    - tema
    - bitacora_cuenta

    Los datos de bienestar se almacenan en MongoDB y se identifican por id_usuario.

    Funciones:
    - Listar usuarios.
    - Buscar por nombre, correo, rol, estado o tema.
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
        self.especialistas_label = None

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
        header = self.tarjeta(self, alto=120)
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
            Lang.get("super_title"),
            size=32,
            text_color=self.color("text", "#111827")
        ).pack(anchor="w")

        SubtitleLabel(
            caja_texto,
            Lang.get("super_subtitle"),
            size=14,
            text_color=self.color("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(4, 0))

        acciones = self.marco(header)
        acciones.grid(
            row=0,
            column=1,
            padx=28,
            pady=34,
            sticky="e"
        )

        SecondaryButton(
            acciones,
            text=Lang.get("super_refresh"),
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
            text=Lang.get("super_logout"),
            width=130,
            height=36,
            command=self.cerrar_sesion
        ).grid(row=0, column=1)

    def crear_metricas(self):
        contenedor = self.marco(self)
        contenedor.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=35,
            pady=(0, 14)
        )

        for columna in range(4):
            contenedor.grid_columnconfigure(columna, weight=1)

        metricas = [
            (Lang.get("super_total_users"), "0", "total_label"),
            (Lang.get("super_active"), "0", "activos_label"),
            (Lang.get("super_restricted"), "0", "restringidos_label"),
            (Lang.get("super_specialists"), "0", "especialistas_label"),
        ]

        for columna, (titulo, valor, atributo) in enumerate(metricas):
            tarjeta = self.tarjeta(contenedor, alto=92)
            tarjeta.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=self.padding_metrica(columna, total_columnas=4)
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
            Lang.get("super_registered_accounts"),
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
            width=330,
            height=34,
            corner_radius=12,
            placeholder_text=Lang.get("super_search_placeholder"),
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
    # CARGA DE DATOS
    # =====================================================

    def cargar_usuarios(self):
        resultado = self.obtener_usuarios()

        if not resultado["success"]:
            self.usuarios = []
            self.usuarios_filtrados = []
            self.actualizar_metricas()
            self.dibujar_tabla()
            self.mostrar_mensaje(resultado["message"], error=True)
            return

        self.usuarios = [
            self.normalizar_usuario_para_vista(usuario)
            for usuario in resultado["users"]
        ]
        self.usuarios_filtrados = self.usuarios[:]

        self.actualizar_metricas()
        self.dibujar_tabla()
        self.mostrar_mensaje(Lang.get("super_users_loaded"))

    def obtener_usuarios(self):
        """
        Carga los usuarios usando la consulta relacional del modelo.
        """

        if not self.usuario_actual or self.usuario_actual.get("rol") != "superuser":
            return {
                "success": False,
                "message": Lang.get("super_no_permission"),
                "users": []
            }

        try:
            usuarios = self.consultar_usuarios_relacional()

            return {
                "success": True,
                "message": "Usuarios cargados correctamente.",
                "users": usuarios
            }

        except Exception as error:
            return {
                "success": False,
                "message": Lang.get("super_load_error", error=error),
                "users": []
            }

    def consultar_usuarios_relacional(self):
        return UserModel.get_all_users()

    def normalizar_resultado_usuarios(self, resultado):
        if isinstance(resultado, list):
            return {
                "success": True,
                "message": "Usuarios cargados correctamente.",
                "users": [
                    self.normalizar_usuario_para_vista(usuario)
                    for usuario in resultado
                ]
            }

        if isinstance(resultado, dict):
            usuarios = resultado.get("users", resultado.get("usuarios", []))
            return {
                "success": resultado.get("success", True),
                "message": resultado.get("message", "Usuarios cargados correctamente."),
                "users": [
                    self.normalizar_usuario_para_vista(usuario)
                    for usuario in usuarios
                ]
            }

        return {
            "success": False,
            "message": Lang.get("super_invalid_format"),
            "users": []
        }

    # =====================================================
    # FILTROS Y MÉTRICAS
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

        self.dibujar_tabla()

    def coincide_busqueda(self, usuario, texto):
        campos = [
            usuario.get("nombre", ""),
            usuario.get("correo", ""),
            usuario.get("rol", ""),
            usuario.get("estado", ""),
            usuario.get("tema_visual", ""),
        ]

        return any(texto in str(campo).lower() for campo in campos)

    def actualizar_metricas(self):
        total = len(self.usuarios)
        activos = sum(1 for u in self.usuarios if u.get("estado") == "activa")
        restringidos = sum(1 for u in self.usuarios if u.get("estado") == "restringida")
        especialistas = sum(1 for u in self.usuarios if u.get("rol") == "especialista")

        if self.total_label:
            self.total_label.configure(text=str(total))

        if self.activos_label:
            self.activos_label.configure(text=str(activos))

        if self.restringidos_label:
            self.restringidos_label.configure(text=str(restringidos))

        if self.especialistas_label:
            self.especialistas_label.configure(text=str(especialistas))

    def mostrar_mensaje(self, texto, error=False):
        if not self.mensaje:
            return

        color = "#DC2626" if error else self.color("text_soft", "#6B7280")
        self.mensaje.configure(text=texto, text_color=color)

    # =====================================================
    # TABLA
    # =====================================================

    def dibujar_tabla(self):
        if not self.tabla:
            return

        self.limpiar(self.tabla)
        self.configurar_columnas_tabla()
        self.crear_encabezados_tabla()

        if not self.usuarios_filtrados:
            self.crear_tabla_vacia()
            return

        for fila, usuario in enumerate(self.usuarios_filtrados, start=1):
            self.crear_fila_usuario(fila, usuario)

    def configurar_columnas_tabla(self):
        pesos = [0, 2, 2, 1, 1, 1, 2]

        for columna, peso in enumerate(pesos):
            self.tabla.grid_columnconfigure(columna, weight=peso)

    def crear_encabezados_tabla(self):
        encabezados = [
            Lang.get("super_id"),
            Lang.get("super_name"),
            Lang.get("super_email"),
            Lang.get("super_role"),
            Lang.get("super_status"),
            Lang.get("super_theme"),
            Lang.get("super_actions"),
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
            Lang.get("super_no_results"),
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
        valores = [
            usuario.get("id_usuario", "-"),
            usuario.get("nombre", "-"),
            usuario.get("correo", "-"),
        ]

        for columna, valor in enumerate(valores):
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

        self.etiqueta_rol(
            self.tabla,
            usuario.get("rol", "-")
        ).grid(
            row=fila,
            column=3,
            padx=10,
            pady=8,
            sticky="w"
        )

        self.etiqueta_estado(
            self.tabla,
            usuario.get("estado", "-")
        ).grid(
            row=fila,
            column=4,
            padx=10,
            pady=8,
            sticky="w"
        )

        SmallLabel(
            self.tabla,
            str(usuario.get("tema_visual", "-")),
            size=12,
            text_color=self.color("text", "#111827")
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
                text=Lang.get("super_protected"),
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
                Lang.get("super_restrict"),
                lambda uid=id_usuario: self.restringir_usuario(uid),
                ancho=95
            ).grid(row=0, column=0, padx=(0, 6))
        else:
            self.boton_secundario(
                acciones,
                Lang.get("super_activate"),
                lambda uid=id_usuario: self.activar_usuario(uid),
                ancho=95
            ).grid(row=0, column=0, padx=(0, 6))

        self.boton_peligro(
            acciones,
            Lang.get("super_delete"),
            lambda uid=id_usuario: self.confirmar_eliminacion(uid),
            ancho=90
        ).grid(row=0, column=1)

    # =====================================================
    # ACCIONES DE USUARIO
    # =====================================================

    def buscar_usuario_por_id(self, id_usuario):
        for usuario in self.usuarios:
            if str(usuario.get("id_usuario")) == str(id_usuario):
                return usuario

        return None

    def validar_usuario_modificable(self, id_usuario):
        usuario = self.buscar_usuario_por_id(id_usuario)

        if not usuario:
            return {
                "success": False,
                "message": Lang.get("super_not_found")
            }

        if usuario.get("rol") == "superuser":
            return {
                "success": False,
                "message": Lang.get("super_cannot_modify")
            }

        return {
            "success": True,
            "message": "Usuario modificable."
        }

    def restringir_usuario(self, id_usuario):
        validacion = self.validar_usuario_modificable(id_usuario)

        if not validacion["success"]:
            self.mostrar_mensaje(validacion["message"], error=True)
            return

        self.ejecutar_accion_usuario("restrict_user", id_usuario)

    def activar_usuario(self, id_usuario):
        validacion = self.validar_usuario_modificable(id_usuario)

        if not validacion["success"]:
            self.mostrar_mensaje(validacion["message"], error=True)
            return

        self.ejecutar_accion_usuario("activate_user", id_usuario)

    def eliminar_usuario(self, id_usuario, ventana):
        validacion = self.validar_usuario_modificable(id_usuario)

        if not validacion["success"]:
            ventana.destroy()
            self.mostrar_mensaje(validacion["message"], error=True)
            return

        resultado = self.ejecutar_accion_usuario(
            "delete_user",
            id_usuario,
            recargar=False
        )

        ventana.destroy()
        self.mostrar_mensaje(resultado["message"], error=not resultado["success"])
        self.cargar_usuarios()

    def ejecutar_accion_usuario(self, nombre_metodo, id_usuario, recargar=True):
        try:
            if hasattr(UserController, nombre_metodo):
                metodo = getattr(UserController, nombre_metodo)

                try:
                    resultado = metodo(self.usuario_actual, id_usuario)
                except TypeError:
                    resultado = metodo(id_usuario)
            else:
                resultado = self.ejecutar_accion_directa(nombre_metodo, id_usuario)

            resultado = self.normalizar_resultado_accion(resultado)

        except Exception as error:
            resultado = {
                "success": False,
                "message": f"{Lang.get('super_action_failed')}: {error}"
            }

        if recargar:
            self.mostrar_mensaje(resultado["message"], error=not resultado["success"])
            self.cargar_usuarios()

        return resultado

    def ejecutar_accion_directa(self, nombre_metodo, id_usuario):
        if nombre_metodo == "restrict_user":
            return self.actualizar_estado_directo(id_usuario, "restringida")

        if nombre_metodo == "activate_user":
            return self.actualizar_estado_directo(id_usuario, "activa")

        if nombre_metodo == "delete_user":
            return self.eliminar_usuario_directo(id_usuario)

        return {
            "success": False,
            "message": Lang.get("super_action_failed")
        }

    def actualizar_estado_directo(self, id_usuario, estado):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT id_estado
                FROM estado_cuenta
                WHERE nombre = %s
                LIMIT 1;
            """, (estado,))

            estado_db = cursor.fetchone()

            if not estado_db:
                return {
                    "success": False,
                    "message": f"Estado '{estado}' {Lang.get('super_not_found')}"
                }

            cursor.execute("""
                UPDATE usuario
                SET id_estado = %s
                WHERE id_usuario = %s;
            """, (estado_db["id_estado"], id_usuario))

            self.insertar_bitacora_directa(
                cursor,
                id_usuario=id_usuario,
                accion=estado,
                descripcion=f"El superuser cambió el estado de la cuenta a {estado}."
            )

            conexion.commit()

            return {
                "success": True,
                "message": Lang.get("super_state_changed", estado=estado)
            }

        except Exception as error:
            conexion.rollback()

            return {
                "success": False,
                "message": f"No se pudo actualizar el estado: {error}"
            }

        finally:
            cursor.close()
            conexion.close()

    def eliminar_usuario_directo(self, id_usuario):
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT id_preferencia
                FROM usuario
                WHERE id_usuario = %s
                LIMIT 1;
            """, (id_usuario,))

            usuario = cursor.fetchone()

            if not usuario:
                return {
                    "success": False,
                    "message": Lang.get("super_not_found")
                }

            id_preferencia = usuario["id_preferencia"]

            self.insertar_bitacora_directa(
                cursor,
                id_usuario=id_usuario,
                accion="eliminar",
                descripcion="El superuser eliminó una cuenta desde el panel administrativo."
            )

            cursor.execute("""
                DELETE FROM usuario
                WHERE id_usuario = %s;
            """, (id_usuario,))

            cursor.execute("""
                DELETE FROM preferencia_visual
                WHERE id_preferencia = %s;
            """, (id_preferencia,))

            conexion.commit()

            return {
                "success": True,
                "message": Lang.get("super_action_completed")
            }

        except Exception as error:
            conexion.rollback()

            return {
                "success": False,
                "message": f"{Lang.get('super_action_failed')}: {error}"
            }

        finally:
            cursor.close()
            conexion.close()

    def insertar_bitacora_directa(self, cursor, id_usuario, accion, descripcion):
        id_admin = None

        if self.usuario_actual:
            id_admin = self.usuario_actual.get("id_usuario")

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
            id_admin,
            id_usuario,
            accion,
            descripcion
        ))

    def normalizar_resultado_accion(self, resultado):
        if isinstance(resultado, dict):
            return {
                "success": resultado.get("success", False),
                "message": resultado.get("message", Lang.get("super_action_completed"))
            }

        if resultado is True:
            return {
                "success": True,
                "message": Lang.get("super_action_completed")
            }

        return {
            "success": False,
            "message": Lang.get("super_action_failed")
        }

    # =====================================================
    # MODAL DE CONFIRMACIÓN
    # =====================================================

    def confirmar_eliminacion(self, id_usuario):
        validacion = self.validar_usuario_modificable(id_usuario)

        if not validacion["success"]:
            self.mostrar_mensaje(validacion["message"], error=True)
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title(Lang.get("super_confirm_delete_title"))
        ventana.geometry("460x250")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.configure(
            fg_color=self.color("app_bg", "#F8FAFC")
        )

        tarjeta = self.tarjeta(ventana, alto=210)
        tarjeta.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        tarjeta.pack_propagate(False)

        TitleLabel(
            tarjeta,
            Lang.get("super_confirm_delete_msg"),
            size=24,
            text_color=self.color("text", "#111827")
        ).pack(pady=(28, 8))

        BodyLabel(
            tarjeta,
            Lang.get("super_confirm_delete_desc"),
            size=14,
            text_color=self.color("text_soft", "#6B7280"),
            justify="center"
        ).pack(pady=(0, 18))

        botones = self.marco(tarjeta)
        botones.pack()

        self.boton_secundario(
            botones,
            Lang.get("super_cancel"),
            ventana.destroy,
            ancho=130
        ).grid(row=0, column=0, padx=8)

        self.boton_peligro(
            botones,
            Lang.get("super_confirm_delete"),
            lambda: self.eliminar_usuario(id_usuario, ventana),
            ancho=130
        ).grid(row=0, column=1, padx=8)

    # =====================================================
    # UTILIDADES / COMPATIBILIDAD
    # =====================================================

    def padding_metrica(self, columna, total_columnas=4):
        if columna == 0:
            return (0, 8)

        if columna == total_columnas - 1:
            return (8, 0)

        return (8, 8)

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