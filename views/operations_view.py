import customtkinter as ctk
from tkinter import messagebox
from components.modals import OperationModal
from models.operation import OperationModel
from models.account import AccountModel
from models.category import CategoryModel
from utils.helpers import format_currency

class OperationsView(ctk.CTkFrame):
    """Vista modular para la administracion de Ingresos o Gastos en tonos de azul bajo."""

    def __init__(self, master, kind="income", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.kind = kind
        self.is_income = (kind == "income")
        self.title_text = "Gestion de Ingresos" if self.is_income else "Gestion de Gastos"
        self.accent_color = "#10b981" if self.is_income else "#ef4444"
        self.btn_hover = "#059669" if self.is_income else "#dc2626"

        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Cabecera y boton de nuevo registro
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        lbl_title = ctk.CTkLabel(
            title_box, 
            text=self.title_text, 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f2942"
        )
        lbl_title.pack(anchor="w")

        sub_text = "Entradas de dinero y cobranzas a clientes" if self.is_income else "Salidas operativas y pagos a proveedores"
        lbl_sub = ctk.CTkLabel(
            title_box, 
            text=sub_text, 
            font=ctk.CTkFont(size=12),
            text_color="#57708e"
        )
        lbl_sub.pack(anchor="w")

        btn_new = ctk.CTkButton(
            header_frame,
            text=f"+ Registrar {'Ingreso' if self.is_income else 'Gasto'}",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.accent_color,
            hover_color=self.btn_hover,
            text_color="#ffffff",
            corner_radius=8,
            height=36,
            command=self._open_new_modal
        )
        btn_new.grid(row=0, column=1, sticky="e")

        # 2. Barra de Filtros y Busqueda en cristal esmerilado blanco/azul bajo
        filter_card = ctk.CTkFrame(
            self, 
            corner_radius=12, 
            fg_color="#ffffff", 
            border_width=1, 
            border_color="#cde0f5"
        )
        filter_card.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 10))
        filter_card.grid_columnconfigure(0, weight=1)

        filter_row = ctk.CTkFrame(filter_card, fg_color="transparent")
        filter_row.pack(fill="x", padx=14, pady=10)

        # Buscador por texto
        self.txt_search = ctk.CTkEntry(
            filter_row, 
            placeholder_text="Buscar por concepto...", 
            width=210,
            fg_color="#f8fbfe",
            border_color="#bfdbfe",
            text_color="#0f2942"
        )
        self.txt_search.pack(side="left", padx=(0, 10))
        self.txt_search.bind("<Return>", lambda e: self.refresh_data())

        # Filtro de Cuenta
        accounts = AccountModel.get_all()
        self.acc_options = ["Todas las Cuentas"] + [f"{a['id']} - {a['name']}" for a in accounts]
        self.cmb_filter_acc = ctk.CTkComboBox(
            filter_row, 
            values=self.acc_options, 
            width=180, 
            state="readonly", 
            fg_color="#f8fbfe",
            border_color="#bfdbfe",
            text_color="#0f2942",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#0f2942",
            dropdown_hover_color="#e8f0fe",
            command=lambda v: self.refresh_data()
        )
        self.cmb_filter_acc.set("Todas las Cuentas")
        self.cmb_filter_acc.pack(side="left", padx=5)

        # Filtro de Categoria
        categories = CategoryModel.get_all(kind=self.kind)
        self.cat_options = ["Todas las Categorias"] + [f"{c['id']} - {c['name']}" for c in categories]
        self.cmb_filter_cat = ctk.CTkComboBox(
            filter_row, 
            values=self.cat_options, 
            width=180, 
            state="readonly", 
            fg_color="#f8fbfe",
            border_color="#bfdbfe",
            text_color="#0f2942",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#0f2942",
            dropdown_hover_color="#e8f0fe",
            command=lambda v: self.refresh_data()
        )
        self.cmb_filter_cat.set("Todas las Categorias")
        self.cmb_filter_cat.pack(side="left", padx=5)

        # Boton buscar
        btn_filter = ctk.CTkButton(
            filter_row, 
            text="Buscar", 
            width=75, 
            fg_color="#dbeafe",
            text_color="#1d4ed8",
            hover_color="#bfdbfe",
            command=self.refresh_data
        )
        btn_filter.pack(side="left", padx=5)

        # Boton limpiar
        btn_clear = ctk.CTkButton(
            filter_row, 
            text="Limpiar", 
            width=70, 
            fg_color="transparent",
            text_color="#57708e",
            hover_color="#f1f5f9",
            command=self._clear_filters
        )
        btn_clear.pack(side="left", padx=5)

        # Resumen de totales filtrados
        self.lbl_filtered_total = ctk.CTkLabel(
            filter_row, 
            text="Total: $ 0.00 (0 registros)", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.accent_color
        )
        self.lbl_filtered_total.pack(side="right", padx=10)

        # 3. Contenedor de la Tabla Glassmorphic
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

        # Encabezado fijo de columnas
        table_hdr = ctk.CTkFrame(self.table_card, fg_color="#dbe9f9", height=38, corner_radius=8)
        table_hdr.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        table_hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(table_hdr, text="Fecha", width=90, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=0, padx=6)
        ctk.CTkLabel(table_hdr, text="Concepto / Detalle", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f", anchor="w").grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(table_hdr, text="Categoria", width=120, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=2, padx=6)
        ctk.CTkLabel(table_hdr, text="Cuenta", width=120, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=3, padx=6)
        ctk.CTkLabel(table_hdr, text="Contacto", width=120, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=4, padx=6)
        ctk.CTkLabel(table_hdr, text="Monto", width=110, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f", anchor="e").grid(row=0, column=5, sticky="e", padx=10)
        ctk.CTkLabel(table_hdr, text="Acciones", width=110, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=6, padx=6)

        # Area con scroll para las filas
        self.table_body = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.table_body.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.table_body.grid_columnconfigure(1, weight=1)

    def refresh_data(self):
        """Consulta la base de datos con los filtros aplicados y redibuja la lista."""
        for w in self.table_body.winfo_children():
            w.destroy()

        search = self.txt_search.get().strip()
        
        account_id = None
        acc_val = self.cmb_filter_acc.get()
        if acc_val and not acc_val.startswith("Todas"):
            account_id = int(acc_val.split(" - ")[0])

        category_id = None
        cat_val = self.cmb_filter_cat.get()
        if cat_val and not cat_val.startswith("Todas"):
            category_id = int(cat_val.split(" - ")[0])

        ops = OperationModel.get_all(
            kind=self.kind,
            search=search,
            account_id=account_id,
            category_id=category_id
        )

        total_amount = sum(float(op["amount"]) for op in ops)
        self.lbl_filtered_total.configure(text=f"Total: {format_currency(total_amount)} ({len(ops)} registros)")

        if not ops:
            ctk.CTkLabel(
                self.table_body, 
                text="No hay registros que coincidan con la busqueda.", 
                text_color="#738a9c",
                pady=30
            ).pack()
            return

        for idx, op in enumerate(ops):
            bg = "#ffffff" if idx % 2 == 0 else "#f5f9fe"
            row = ctk.CTkFrame(self.table_body, corner_radius=8, fg_color=bg, border_width=1, border_color="#dbe8f7", height=46)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(1, weight=1)

            # Fecha
            ctk.CTkLabel(row, text=op["date_at"], width=90, font=ctk.CTkFont(size=11), text_color="#57708e").grid(row=0, column=0, padx=6)

            # Concepto y descripcion
            c_box = ctk.CTkFrame(row, fg_color="transparent")
            c_box.grid(row=0, column=1, sticky="w", padx=10, pady=4)
            ctk.CTkLabel(c_box, text=op["concept"], font=ctk.CTkFont(size=12, weight="bold"), text_color="#0f2942", anchor="w").pack(anchor="w")
            if op.get("description"):
                ctk.CTkLabel(c_box, text=op["description"], font=ctk.CTkFont(size=10), text_color="#738a9c", anchor="w").pack(anchor="w")

            # Categoria
            ctk.CTkLabel(row, text=op["category_name"], width=120, font=ctk.CTkFont(size=11), text_color="#57708e").grid(row=0, column=2, padx=6)

            # Cuenta
            ctk.CTkLabel(row, text=op["account_name"], width=120, font=ctk.CTkFont(size=11), text_color="#1e3a5f").grid(row=0, column=3, padx=6)

            # Contacto
            ctk.CTkLabel(row, text=op["contact_name"], width=120, font=ctk.CTkFont(size=11), text_color="#57708e").grid(row=0, column=4, padx=6)

            # Monto
            prefix = "+" if self.is_income else "-"
            amt_lbl = ctk.CTkLabel(
                row, 
                text=f"{prefix}{format_currency(op['amount'])}", 
                width=110, 
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.accent_color,
                anchor="e"
            )
            amt_lbl.grid(row=0, column=5, sticky="e", padx=10)

            # Acciones con 3 botones: Detalle (Azul Info), Editar (Amarillo Warning), Eliminar (Rojo Danger)
            act_box = ctk.CTkFrame(row, fg_color="transparent", width=110)
            act_box.grid(row=0, column=6, padx=6)

            btn_detail = ctk.CTkButton(
                act_box, 
                text="👁️", 
                width=28, 
                height=26, 
                corner_radius=6,
                fg_color="#2563eb",
                hover_color="#1d4ed8",
                text_color="#ffffff",
                command=lambda o=op: self._show_detail(o)
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
                command=lambda o=op: self._open_edit_modal(o)
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
                command=lambda o=op: self._delete_op(o)
            )
            btn_del.pack(side="left", padx=2)

    def _clear_filters(self):
        self.txt_search.delete(0, "end")
        self.cmb_filter_acc.set("Todas las Cuentas")
        self.cmb_filter_cat.set("Todas las Categorias")
        self.refresh_data()

    def _show_detail(self, op_data):
        full_op = OperationModel.get_by_id(op_data["id"]) or op_data
        is_in = full_op["kind"] == "income"
        prefix = "+" if is_in else "-"

        items = [
            ("Concepto", full_op["concept"]),
            ("Tipo de Operacion", "Ingreso (Cobro)" if is_in else "Gasto (Egreso)"),
            ("Monto", f"{prefix}{format_currency(full_op['amount'])}"),
            ("Fecha de Operacion", full_op["date_at"]),
            ("Cuenta Financiera", full_op.get("account_name", "N/A")),
            ("Categoria", full_op.get("category_name", "Sin Categoria")),
            ("Contacto", full_op.get("contact_name", "General / Ninguno")),
            ("Metodo de Pago", full_op.get("paymethod_name", "N/A")),
            ("Registrado por", full_op.get("user_name", "Sistema")),
            ("Notas / Detalle", full_op.get("description", "")),
            ("Fecha de Creacion", full_op.get("created_at", ""))
        ]

        from components.modals import DetailModal
        DetailModal(
            self.winfo_toplevel(),
            title=f"Detalle de {'Ingreso' if is_in else 'Gasto'} #{full_op['id']}",
            items=items,
            badge_text=f"{prefix}{format_currency(full_op['amount'])}",
            badge_color="#10b981" if is_in else "#ef4444"
        )

    def _open_new_modal(self):
        OperationModal(self.winfo_toplevel(), kind=self.kind, on_success=self.refresh_data)

    def _open_edit_modal(self, op_data):
        OperationModal(self.winfo_toplevel(), kind=self.kind, operation_data=op_data, on_success=self.refresh_data)

    def _delete_op(self, op_data):
        msg = f"¿Seguro que deseas eliminar la operacion '{op_data['concept']}' por {format_currency(op_data['amount'])}?"
        if messagebox.askyesno("Confirmar Eliminacion", msg, parent=self):
            OperationModel.delete(op_data["id"])
            self.refresh_data()
