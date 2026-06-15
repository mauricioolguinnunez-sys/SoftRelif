import customtkinter as ctk
from controllers.user_controller import UserController


class SuperuserView(ctk.CTkFrame):

    def __init__(self, master, app):
        super().__init__(
            master,
            width=980,
            height=700,
            corner_radius=0,
            fg_color="transparent"
        )

        self.app = app
        self.current_user = app.current_user

        self.pack(fill="both", expand=True)

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self,
            text="Panel Superuser",
            font=("Segoe UI", 34)
        )
        self.title.place(x=40, y=35)

        self.subtitle = ctk.CTkLabel(
            self,
            text="Administra cuentas registradas en SoftRelief.",
            font=("Segoe UI", 15)
        )
        self.subtitle.place(x=42, y=85)

        self.table_frame = ctk.CTkScrollableFrame(
            self,
            width=880,
            height=500,
            corner_radius=18
        )
        self.table_frame.place(x=40, y=130)

        self.message_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 14)
        )
        self.message_label.place(x=40, y=650)

    def load_users(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        result = UserController.get_all_users(self.current_user)

        if not result["success"]:
            self.message_label.configure(text=result["message"])
            return

        headers = ["ID", "Nombre", "Usuario", "Correo", "Rol", "Estado", "Acciones"]

        for col, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=("Segoe UI", 13, "bold")
            )
            label.grid(row=0, column=col, padx=8, pady=8, sticky="w")

        for row_index, user in enumerate(result["users"], start=1):
            values = [
                user["id_usuario"],
                user["nombre"],
                user["usuario"],
                user["correo"],
                user["rol"],
                user["estado"]
            ]

            for col, value in enumerate(values):
                label = ctk.CTkLabel(
                    self.table_frame,
                    text=str(value),
                    font=("Segoe UI", 12)
                )
                label.grid(row=row_index, column=col, padx=8, pady=8, sticky="w")

            action_frame = ctk.CTkFrame(
                self.table_frame,
                fg_color="transparent"
            )
            action_frame.grid(row=row_index, column=6, padx=8, pady=8)

            if user["rol"] == "superuser":
                protected_label = ctk.CTkLabel(
                    action_frame,
                    text="Protegido",
                    font=("Segoe UI", 12)
                )
                protected_label.pack()
            else:
                if user["estado"] == "activa":
                    restrict_button = ctk.CTkButton(
                        action_frame,
                        text="Restringir",
                        width=85,
                        height=28,
                        command=lambda uid=user["id_usuario"]: self.restrict_user(uid)
                    )
                    restrict_button.grid(row=0, column=0, padx=3)
                else:
                    activate_button = ctk.CTkButton(
                        action_frame,
                        text="Activar",
                        width=85,
                        height=28,
                        command=lambda uid=user["id_usuario"]: self.activate_user(uid)
                    )
                    activate_button.grid(row=0, column=0, padx=3)

                delete_button = ctk.CTkButton(
                    action_frame,
                    text="Eliminar",
                    width=85,
                    height=28,
                    fg_color="#D9534F",
                    hover_color="#C9433F",
                    command=lambda uid=user["id_usuario"]: self.confirm_delete_user(uid)
                )
                delete_button.grid(row=0, column=1, padx=3)

    def restrict_user(self, id_usuario):
        result = UserController.restrict_user(self.current_user, id_usuario)
        self.message_label.configure(text=result["message"])
        self.load_users()

    def activate_user(self, id_usuario):
        result = UserController.activate_user(self.current_user, id_usuario)
        self.message_label.configure(text=result["message"])
        self.load_users()

    def confirm_delete_user(self, id_usuario):
        confirm_window = ctk.CTkToplevel(self)
        confirm_window.title("Confirmar eliminación")
        confirm_window.geometry("430x220")
        confirm_window.resizable(False, False)
        confirm_window.grab_set()

        title = ctk.CTkLabel(
            confirm_window,
            text="¿Eliminar usuario?",
            font=("Segoe UI", 24)
        )
        title.pack(pady=(25, 10))

        message = ctk.CTkLabel(
            confirm_window,
            text="Esta acción eliminará la cuenta seleccionada.\n¿Deseas continuar?",
            font=("Segoe UI", 14),
            justify="center"
        )
        message.pack(pady=10)

        button_frame = ctk.CTkFrame(
            confirm_window,
            fg_color="transparent"
        )
        button_frame.pack(pady=20)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            width=130,
            command=confirm_window.destroy
        )
        cancel_button.grid(row=0, column=0, padx=10)

        delete_button = ctk.CTkButton(
            button_frame,
            text="Sí, eliminar",
            width=130,
            fg_color="#D9534F",
            hover_color="#C9433F",
            command=lambda: self.delete_user(id_usuario, confirm_window)
        )
        delete_button.grid(row=0, column=1, padx=10)

    def delete_user(self, id_usuario, window):
        result = UserController.delete_user(self.current_user, id_usuario)
        window.destroy()
        self.message_label.configure(text=result["message"])
        self.load_users()