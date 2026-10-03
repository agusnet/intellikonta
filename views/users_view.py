import customtkinter as ctk
from tkinter import messagebox
from components.modals import UserModal
from models.user import UserModel
from utils.session import Session

class UsersView(ctk.CTkFrame):
    """Vista de administracion de usuarios del sistema con tonos de azul bajo."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Cabecera
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 15))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        lbl_title = ctk.CTkLabel(
            title_box, 
            text="Usuarios y Permisos", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f2942"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box, 
            text="Control de acceso de operadores y administradores a IntelliKonta", 
            font=ctk.CTkFont(size=12),
            text_color="#57708e"
        )
        lbl_sub.pack(anchor="w")

        btn_new = ctk.CTkButton(
            header_frame,
            text="+ Nuevo Usuario",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#ffffff",
            corner_radius=8,
            height=36,
            command=self._open_new_modal
        )
        btn_new.grid(row=0, column=1, sticky="e")

        # 2. Tabla con scroll esmerilada
        self.table_card = ctk.CTkFrame(
            self, 
            corner_radius=14, 
            border_width=1, 
            border_color="#cde0f5", 
            fg_color="#ffffff"
        )
        self.table_card.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        self.table_card.grid_columnconfigure(0, weight=1)
        self.table_card.grid_rowconfigure(1, weight=1)

        # Encabezado
        table_hdr = ctk.CTkFrame(self.table_card, fg_color="#dbe9f9", height=38, corner_radius=8)
        table_hdr.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        table_hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(table_hdr, text="Usuario", width=120, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=0, padx=8)
        ctk.CTkLabel(table_hdr, text="Nombre Completo", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f", anchor="w").grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(table_hdr, text="Correo Electronico", width=220, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=2, padx=8)
        ctk.CTkLabel(table_hdr, text="Rol", width=110, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=3, padx=8)
        ctk.CTkLabel(table_hdr, text="Estado", width=90, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=4, padx=8)
        ctk.CTkLabel(table_hdr, text="Acciones", width=110, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=5, padx=8)

        self.table_body = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.table_body.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.table_body.grid_columnconfigure(1, weight=1)

    def refresh_data(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        users = UserModel.get_all()

        for idx, u in enumerate(users):
            bg = "#ffffff" if idx % 2 == 0 else "#f5f9fe"
            row = ctk.CTkFrame(self.table_body, corner_radius=8, fg_color=bg, border_width=1, border_color="#dbe8f7", height=46)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(1, weight=1)

            # Nombre de usuario
            u_box = ctk.CTkFrame(row, fg_color="transparent", width=120)
            u_box.grid(row=0, column=0, padx=8, pady=6)
            ctk.CTkLabel(u_box, text=f"@{u['username']}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2563eb").pack()

            # Nombre
            full_name = f"{u['name']} {u.get('lastname', '')}".strip()
            ctk.CTkLabel(row, text=full_name, font=ctk.CTkFont(size=12, weight="bold"), text_color="#0f2942", anchor="w").grid(row=0, column=1, sticky="w", padx=10)

            # Correo
            ctk.CTkLabel(row, text=u["email"], width=220, font=ctk.CTkFont(size=11), text_color="#57708e").grid(row=0, column=2, padx=8)

            # Rol
            is_admin = u.get("role") == "admin"
            role_badge = ctk.CTkLabel(
                row, 
                text="Administrador" if is_admin else "Operador", 
                width=100, 
                height=24, 
                corner_radius=6, 
                fg_color="#2563eb" if is_admin else "#94a3b8",
                text_color="#ffffff",
                font=ctk.CTkFont(size=10, weight="bold")
            )
            role_badge.grid(row=0, column=3, padx=8)

            # Estado
            status_lbl = ctk.CTkLabel(
                row, 
                text="Activo" if u["status"] == 1 else "Inactivo", 
                width=80, 
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#059669" if u["status"] == 1 else "#dc2626"
            )
            status_lbl.grid(row=0, column=4, padx=8)

            # Acciones con 3 botones: Detalle (Azul Info), Editar (Amarillo Warning), Eliminar (Rojo Danger)
            act_box = ctk.CTkFrame(row, fg_color="transparent", width=110)
            act_box.grid(row=0, column=5, padx=8)

            btn_detail = ctk.CTkButton(
                act_box, 
                text="👁️", 
                width=28, 
                height=26, 
                corner_radius=6,
                fg_color="#2563eb",
                hover_color="#1d4ed8",
                text_color="#ffffff",
                command=lambda user=u: self._show_detail(user)
            )
            btn_detail.pack(side="left", padx=2)

            btn_edit = ctk.CTkButton(
                act_box, 
                text="✏️", 
                width=28, 
                height=26, 
                corner_radius=6,
                fg_color="#f59e0b",
                hover_color="#d97706",
                text_color="#ffffff",
                command=lambda user=u: self._open_edit_modal(user)
            )
            btn_edit.pack(side="left", padx=2)

            btn_del = ctk.CTkButton(
                act_box, 
                text="🗑️", 
                width=28, 
                height=26, 
                corner_radius=6,
                fg_color="#ef4444",
                hover_color="#dc2626",
                text_color="#ffffff",
                command=lambda user=u: self._delete_user(user)
            )
            btn_del.pack(side="left", padx=2)

    def _open_new_modal(self):
        UserModal(self.winfo_toplevel(), on_success=self.refresh_data)

    def _open_edit_modal(self, user_data):
        UserModal(self.winfo_toplevel(), user_data=user_data, on_success=self.refresh_data)

    def _delete_user(self, user_data):
        if user_data["id"] == Session.get_user_id():
            messagebox.showwarning("Atencion", "No puedes eliminar tu propio usuario de sesion activa.", parent=self)
            return

        users = UserModel.get_all()
        if len(users) <= 1:
            messagebox.showwarning("Atencion", "Debe existir al menos un usuario en el sistema.", parent=self)
            return

        msg = f"¿Seguro que deseas eliminar al usuario '@{user_data['username']}'?"
        if messagebox.askyesno("Confirmar", msg, parent=self):
            UserModel.delete(user_data["id"])
            self.refresh_data()

    def _show_detail(self, user_data):
        from components.modals import DetailModal
        full_name = f"{user_data.get('name', '')} {user_data.get('lastname', '')}".strip()
        role_label = "Administrador" if user_data.get("role") == "admin" else "Operador"
        status_label = "Activo" if user_data.get("status") == 1 else "Inactivo"

        items = [
            ("ID de Usuario", f"#{user_data.get('id', '')}"),
            ("Nombre de Usuario", f"@{user_data.get('username', '')}"),
            ("Nombre Completo", full_name or "Sin nombre"),
            ("Correo Electrónico", user_data.get("email", "Sin correo")),
            ("Rol en el Sistema", role_label),
            ("Estado", status_label),
            ("Fecha de Registro", user_data.get("created_at") or "N/A"),
        ]

        DetailModal(
            self.winfo_toplevel(),
            title=f"Detalle de Usuario: @{user_data.get('username', '')}",
            items=items,
            badge_text=role_label,
            badge_color="#2563eb" if user_data.get("role") == "admin" else "#64748b"
        )
