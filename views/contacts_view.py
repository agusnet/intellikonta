import customtkinter as ctk
from tkinter import messagebox
from components.modals import ContactModal
from models.contact import ContactModel

class ContactsView(ctk.CTkFrame):
    """Vista del directorio de contactos comerciales con estilo en tonos de azul bajo."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Cabecera y boton nuevo
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        lbl_title = ctk.CTkLabel(
            title_box, 
            text="Directorio de Contactos", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f2942"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box, 
            text="Administracion de clientes, proveedores y socios comerciales", 
            font=ctk.CTkFont(size=12),
            text_color="#57708e"
        )
        lbl_sub.pack(anchor="w")

        btn_new = ctk.CTkButton(
            header_frame,
            text="+ Nuevo Contacto",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#ffffff",
            corner_radius=8,
            height=36,
            command=self._open_new_modal
        )
        btn_new.grid(row=0, column=1, sticky="e")

        # 2. Barra de busqueda esmerilada
        search_card = ctk.CTkFrame(
            self, 
            corner_radius=12, 
            fg_color="#ffffff", 
            border_width=1, 
            border_color="#cde0f5"
        )
        search_card.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 10))

        search_row = ctk.CTkFrame(search_card, fg_color="transparent")
        search_row.pack(fill="x", padx=14, pady=10)

        self.txt_search = ctk.CTkEntry(
            search_row, 
            placeholder_text="Buscar contacto por nombre, empresa, telefono o correo...", 
            width=400,
            fg_color="#f8fbfe",
            border_color="#bfdbfe",
            text_color="#0f2942"
        )
        self.txt_search.pack(side="left", padx=(0, 10))
        self.txt_search.bind("<Return>", lambda e: self.refresh_data())

        btn_search = ctk.CTkButton(
            search_row, 
            text="Buscar", 
            width=80, 
            fg_color="#dbeafe",
            text_color="#1d4ed8",
            hover_color="#bfdbfe",
            command=self.refresh_data
        )
        btn_search.pack(side="left", padx=5)

        btn_clear = ctk.CTkButton(
            search_row, 
            text="Limpiar", 
            width=70, 
            fg_color="transparent",
            text_color="#57708e",
            hover_color="#f1f5f9",
            command=self._clear_search
        )
        btn_clear.pack(side="left", padx=5)

        self.lbl_count = ctk.CTkLabel(search_row, text="0 contactos", font=ctk.CTkFont(size=12), text_color="#738a9c")
        self.lbl_count.pack(side="right", padx=10)

        # 3. Lista con scroll
        self.table_card = ctk.CTkFrame(
            self, 
            corner_radius=14, 
            border_width=1, 
            border_color="#cde0f5", 
            fg_color="#ffffff"
        )
        self.table_card.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 20))
        self.table_card.grid_columnconfigure(0, weight=1)
        self.table_card.grid_rowconfigure(1, weight=1)

        # Encabezado
        table_hdr = ctk.CTkFrame(self.table_card, fg_color="#dbe9f9", height=38, corner_radius=8)
        table_hdr.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        table_hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(table_hdr, text="Nombre Completo / Empresa", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f", anchor="w").grid(row=0, column=0, sticky="w", padx=14)
        ctk.CTkLabel(table_hdr, text="Telefono", width=130, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=1, padx=6)
        ctk.CTkLabel(table_hdr, text="Correo Electronico", width=200, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=2, padx=6)
        ctk.CTkLabel(table_hdr, text="Direccion / Ciudad", width=180, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=3, padx=6)
        ctk.CTkLabel(table_hdr, text="Acciones", width=110, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=4, padx=6)

        self.table_body = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.table_body.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.table_body.grid_columnconfigure(0, weight=1)

    def refresh_data(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        search = self.txt_search.get().strip()
        contacts = ContactModel.get_all(search_term=search)
        self.lbl_count.configure(text=f"{len(contacts)} contacto{'s' if len(contacts) != 1 else ''}")

        if not contacts:
            ctk.CTkLabel(
                self.table_body, 
                text="No hay contactos que coincidan con la busqueda.", 
                text_color="#738a9c",
                pady=30
            ).pack()
            return

        for idx, con in enumerate(contacts):
            bg = "#ffffff" if idx % 2 == 0 else "#f5f9fe"
            row = ctk.CTkFrame(self.table_body, corner_radius=8, fg_color=bg, border_width=1, border_color="#dbe8f7", height=46)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=1)

            # Nombre y Empresa
            c_box = ctk.CTkFrame(row, fg_color="transparent")
            c_box.grid(row=0, column=0, sticky="w", padx=14, pady=4)
            full_name = f"{con['name']} {con.get('lastname', '')}".strip()
            ctk.CTkLabel(c_box, text=full_name, font=ctk.CTkFont(size=12, weight="bold"), text_color="#0f2942", anchor="w").pack(anchor="w")
            if con.get("company"):
                ctk.CTkLabel(c_box, text=con["company"], font=ctk.CTkFont(size=10), text_color="#2563eb", anchor="w").pack(anchor="w")

            # Telefono
            phone = con.get("phone") or "—"
            ctk.CTkLabel(row, text=phone, width=130, font=ctk.CTkFont(size=11), text_color="#57708e").grid(row=0, column=1, padx=6)

            # Email
            email = con.get("email") or "—"
            ctk.CTkLabel(row, text=email, width=200, font=ctk.CTkFont(size=11), text_color="#57708e").grid(row=0, column=2, padx=6)

            # Direccion
            address = con.get("address") or "—"
            ctk.CTkLabel(row, text=address, width=180, font=ctk.CTkFont(size=11), text_color="#57708e").grid(row=0, column=3, padx=6)

            # Acciones con 3 botones: Detalle (Azul Info), Editar (Amarillo Warning), Eliminar (Rojo Danger)
            act_box = ctk.CTkFrame(row, fg_color="transparent", width=110)
            act_box.grid(row=0, column=4, padx=6)

            btn_detail = ctk.CTkButton(
                act_box, 
                text="👁️", 
                width=28, 
                height=26, 
                corner_radius=6,
                fg_color="#2563eb",
                hover_color="#1d4ed8",
                text_color="#ffffff",
                command=lambda c=con: self._show_detail(c)
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
                command=lambda c=con: self._open_edit_modal(c)
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
                command=lambda c=con: self._delete_contact(c)
            )
            btn_del.pack(side="left", padx=2)

    def _clear_search(self):
        self.txt_search.delete(0, "end")
        self.refresh_data()

    def _show_detail(self, contact_data):
        summary = ContactModel.get_summary(contact_data["id"])
        from utils.helpers import format_currency
        full_name = f"{contact_data['name']} {contact_data.get('lastname', '')}".strip()

        items = [
            ("Nombre Completo", full_name),
            ("Empresa / Negocio", contact_data.get("company", "Particular")),
            ("Telefono", contact_data.get("phone", "—")),
            ("Correo Electronico", contact_data.get("email", "—")),
            ("Direccion", contact_data.get("address", "—")),
            ("Notas", contact_data.get("notes", "Sin notas")),
            ("Operaciones Totales", f"{summary['ops_count']} movimientos registrados"),
            ("Ingresos Cobrados", f"+{format_currency(summary['total_in'])}"),
            ("Gastos Pagados", f"-{format_currency(summary['total_out'])}"),
            ("Fecha de Alta", contact_data.get("created_at", "N/A"))
        ]

        from components.modals import DetailModal
        DetailModal(
            self.winfo_toplevel(),
            title=f"Ficha de Contacto: {full_name}",
            items=items,
            badge_text=contact_data.get("company") or "Contacto",
            badge_color="#2563eb"
        )

    def _open_new_modal(self):
        ContactModal(self.winfo_toplevel(), on_success=self.refresh_data)

    def _open_edit_modal(self, contact_data):
        ContactModal(self.winfo_toplevel(), contact_data=contact_data, on_success=self.refresh_data)

    def _delete_contact(self, contact_data):
        msg = f"¿Seguro que deseas eliminar el contacto '{contact_data['name']}'?"
        if messagebox.askyesno("Confirmar Eliminacion", msg, parent=self):
            ContactModel.delete(contact_data["id"])
            self.refresh_data()
