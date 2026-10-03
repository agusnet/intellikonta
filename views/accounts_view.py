import customtkinter as ctk
from tkinter import messagebox
from components.modals import AccountModal
from models.account import AccountModel
from utils.helpers import format_currency

class AccountsView(ctk.CTkFrame):
    """Vista de administracion de cuentas bancarias y cajas con estilo en tonos de azul bajo."""

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
            text="Cuentas Financieras", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f2942"
        )
        lbl_title.pack(anchor="w")

        self.lbl_total_banner = ctk.CTkLabel(
            title_box, 
            text="Fondo total consolidado: $ 0.00", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#2563eb"
        )
        self.lbl_total_banner.pack(anchor="w")

        btn_new = ctk.CTkButton(
            header_frame,
            text="+ Nueva Cuenta",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#ffffff",
            corner_radius=8,
            height=36,
            command=self._open_new_modal
        )
        btn_new.grid(row=0, column=1, sticky="e")

        # 2. Area con scroll para las tarjetas de cuentas
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_area.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        self.scroll_area.grid_columnconfigure(0, weight=1)

    def refresh_data(self):
        for w in self.scroll_area.winfo_children():
            w.destroy()

        accounts = AccountModel.get_all()
        total_balance = sum(float(a.get("current_balance", 0.0)) for a in accounts)
        self.lbl_total_banner.configure(text=f"Fondo total consolidado en {len(accounts)} cuentas: {format_currency(total_balance)}")

        if not accounts:
            ctk.CTkLabel(
                self.scroll_area, 
                text="No hay cuentas registradas.", 
                text_color="#738a9c",
                pady=30
            ).pack()
            return

        for acc in accounts:
            card = ctk.CTkFrame(
                self.scroll_area, 
                corner_radius=14, 
                border_width=1, 
                border_color="#cde0f5", 
                fg_color="#ffffff", 
                height=82
            )
            card.pack(fill="x", pady=6)
            card.grid_columnconfigure(1, weight=1)

            # Icono
            icon = ctk.CTkLabel(
                card, 
                text="🏦", 
                width=46, 
                height=46, 
                corner_radius=10, 
                fg_color="#e0edfb",
                font=ctk.CTkFont(size=20)
            )
            icon.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=12)

            # Informacion de la cuenta
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=1, rowspan=2, sticky="w", pady=10)

            ctk.CTkLabel(
                info_frame, 
                text=acc["name"], 
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#0f2942"
            ).pack(anchor="w")

            desc = acc.get("description") or "Sin notas descriptivas"
            init_str = format_currency(acc.get("initial_balance", 0.0))
            ctk.CTkLabel(
                info_frame, 
                text=f"{desc} • Saldo inicial: {init_str}", 
                font=ctk.CTkFont(size=11),
                text_color="#57708e"
            ).pack(anchor="w")

            # Saldo actual
            bal_frame = ctk.CTkFrame(card, fg_color="transparent")
            bal_frame.grid(row=0, column=2, rowspan=2, padx=15, pady=10)

            ctk.CTkLabel(
                bal_frame, 
                text="SALDO DISPONIBLE", 
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#738a9c"
            ).pack(anchor="e")

            cur_bal = float(acc.get("current_balance", 0.0))
            ctk.CTkLabel(
                bal_frame, 
                text=format_currency(cur_bal), 
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#059669" if cur_bal >= 0 else "#dc2626"
            ).pack(anchor="e")

            # Botones de accion: Detalle (Azul Info), Editar (Amarillo Warning), Eliminar (Rojo Danger)
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=3, rowspan=2, padx=(8, 16), pady=10)

            btn_detail = ctk.CTkButton(
                btn_frame, 
                text="👁️", 
                width=32, 
                height=30,
                corner_radius=6,
                fg_color="#2563eb",
                hover_color="#1d4ed8",
                text_color="#ffffff",
                command=lambda a=acc: self._show_detail(a)
            )
            btn_detail.pack(side="left", padx=3)

            btn_edit = ctk.CTkButton(
                btn_frame, 
                text="✏️", 
                width=32, 
                height=30,
                corner_radius=6,
                fg_color="#f59e0b",
                hover_color="#d97706",
                text_color="#ffffff",
                command=lambda a=acc: self._open_edit_modal(a)
            )
            btn_edit.pack(side="left", padx=3)

            btn_del = ctk.CTkButton(
                btn_frame, 
                text="🗑️", 
                width=32, 
                height=30,
                corner_radius=6,
                fg_color="#ef4444",
                hover_color="#dc2626",
                text_color="#ffffff",
                command=lambda a=acc: self._delete_acc(a)
            )
            btn_del.pack(side="left", padx=3)

    def _show_detail(self, account_data):
        summary = AccountModel.get_summary(account_data["id"])
        init_bal = float(account_data.get("initial_balance", 0.0))
        cur_bal = float(account_data.get("current_balance", 0.0))

        items = [
            ("Nombre de la Cuenta", account_data["name"]),
            ("Descripcion", account_data.get("description", "Sin descripcion")),
            ("Saldo de Apertura", format_currency(init_bal)),
            ("Total Ingresos Recibidos", f"+{format_currency(summary['total_in'])}"),
            ("Total Gastos Pagados", f"-{format_currency(summary['total_out'])}"),
            ("Saldo Actual Disponible", format_currency(cur_bal)),
            ("Movimientos Vinculados", f"{summary['ops_count']} operaciones registradas"),
            ("Fecha de Alta", account_data.get("created_at", "N/A"))
        ]

        from components.modals import DetailModal
        DetailModal(
            self.winfo_toplevel(),
            title=f"Resumen de Cuenta: {account_data['name']}",
            items=items,
            badge_text=f"Saldo: {format_currency(cur_bal)}",
            badge_color="#059669" if cur_bal >= 0 else "#dc2626"
        )

    def _open_new_modal(self):
        AccountModal(self.winfo_toplevel(), on_success=self.refresh_data)

    def _open_edit_modal(self, account_data):
        AccountModal(self.winfo_toplevel(), account_data=account_data, on_success=self.refresh_data)

    def _delete_acc(self, account_data):
        try:
            msg = f"¿Seguro que deseas eliminar la cuenta '{account_data['name']}'?"
            if messagebox.askyesno("Confirmar Eliminacion", msg, parent=self):
                AccountModel.delete(account_data["id"])
                self.refresh_data()
        except ValueError as err:
            messagebox.showwarning("No se puede eliminar", str(err), parent=self)
