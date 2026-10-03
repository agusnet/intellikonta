import customtkinter as ctk
from components.stat_card import StatCard
from components.modals import OperationModal
from models.operation import OperationModel
from models.account import AccountModel
from utils.helpers import format_currency

class DashboardView(ctk.CTkFrame):
    """Vista principal con estilo glassmorfismo en tonos de azul bajo y esmerilado suave."""

    def __init__(self, master, on_navigate_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_navigate = on_navigate_callback
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Encabezado con titulo y botones de accion rapida
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 15))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        lbl_title = ctk.CTkLabel(
            title_box, 
            text="Panel de Control Financiero", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f2942"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box, 
            text="Resumen en tiempo real de ingresos, gastos y liquidez", 
            font=ctk.CTkFont(size=12),
            text_color="#57708e"
        )
        lbl_sub.pack(anchor="w")

        # Botones de accion rapida
        actions_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_box.grid(row=0, column=1, sticky="e")

        btn_income = ctk.CTkButton(
            actions_box,
            text="+ Nuevo Ingreso",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#ffffff",
            height=36,
            corner_radius=8,
            command=lambda: self._open_modal("income")
        )
        btn_income.pack(side="left", padx=5)

        btn_expense = ctk.CTkButton(
            actions_box,
            text="- Nuevo Gasto",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="#ffffff",
            height=36,
            corner_radius=8,
            command=lambda: self._open_modal("expense")
        )
        btn_expense.pack(side="left", padx=5)

        # 2. Fila de tarjetas de estadisticas (Glassmorphism en tonos de azul bajo)
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 15))
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_balance = StatCard(self.cards_frame, "Fondos en Cuentas", "$ 0.00", "Liquidez activa consolidada", accent_color="#2563eb")
        self.card_balance.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.card_income = StatCard(self.cards_frame, "Total Ingresos", "$ 0.00", "Historico acumulado", accent_color="#10b981")
        self.card_income.grid(row=0, column=1, sticky="ew", padx=8)

        self.card_expense = StatCard(self.cards_frame, "Total Gastos", "$ 0.00", "Historico acumulado", accent_color="#ef4444")
        self.card_expense.grid(row=0, column=2, sticky="ew", padx=8)

        self.card_net = StatCard(self.cards_frame, "Balance Neto", "$ 0.00", "Ingresos vs Gastos", accent_color="#3b82f6")
        self.card_net.grid(row=0, column=3, sticky="ew", padx=(8, 0))

        # 3. Seccion inferior: Cuentas a la izquierda y Movimientos recientes a la derecha
        bottom_grid = ctk.CTkFrame(self, fg_color="transparent")
        bottom_grid.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 20))
        bottom_grid.grid_columnconfigure(0, weight=4)
        bottom_grid.grid_columnconfigure(1, weight=6)
        bottom_grid.grid_rowconfigure(0, weight=1)

        # Panel izquierdo esmerilado: Cuentas
        self.accounts_card = ctk.CTkFrame(
            bottom_grid, 
            corner_radius=14, 
            border_width=1, 
            border_color="#cde0f5", 
            fg_color="#ffffff"
        )
        self.accounts_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.accounts_card.grid_columnconfigure(0, weight=1)
        self.accounts_card.grid_rowconfigure(1, weight=1)

        acc_header = ctk.CTkFrame(self.accounts_card, fg_color="transparent")
        acc_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        acc_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            acc_header, 
            text="Cuentas Financieras", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0f2942"
        ).grid(row=0, column=0, sticky="w")

        btn_view_accs = ctk.CTkButton(
            acc_header, 
            text="Administrar →", 
            width=85, 
            height=26, 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="transparent",
            text_color="#2563eb",
            hover_color="#e8f0fe",
            command=lambda: self.on_navigate("cuentas") if self.on_navigate else None
        )
        btn_view_accs.grid(row=0, column=1, sticky="e")

        self.accounts_scroll = ctk.CTkScrollableFrame(self.accounts_card, fg_color="transparent")
        self.accounts_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        # Panel derecho esmerilado: Movimientos recientes
        self.ops_card = ctk.CTkFrame(
            bottom_grid, 
            corner_radius=14, 
            border_width=1, 
            border_color="#cde0f5", 
            fg_color="#ffffff"
        )
        self.ops_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.ops_card.grid_columnconfigure(0, weight=1)
        self.ops_card.grid_rowconfigure(1, weight=1)

        ops_header = ctk.CTkFrame(self.ops_card, fg_color="transparent")
        ops_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        ops_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            ops_header, 
            text="Ultimos Movimientos", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0f2942"
        ).grid(row=0, column=0, sticky="w")

        btn_view_ops = ctk.CTkButton(
            ops_header, 
            text="Ver Todos →", 
            width=85, 
            height=26, 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="transparent",
            text_color="#2563eb",
            hover_color="#e8f0fe",
            command=lambda: self.on_navigate("ingresos") if self.on_navigate else None
        )
        btn_view_ops.grid(row=0, column=1, sticky="e")

        self.ops_scroll = ctk.CTkScrollableFrame(self.ops_card, fg_color="transparent")
        self.ops_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

    def refresh_data(self):
        """Actualiza todas las metricas y listas del dashboard."""
        summary = OperationModel.get_summary()
        total_balance = AccountModel.get_total_balance()

        self.card_balance.update_value(format_currency(total_balance))
        self.card_income.update_value(format_currency(summary["income"]))
        self.card_expense.update_value(format_currency(summary["expense"]))
        self.card_net.update_value(format_currency(summary["net"]))

        # Refrescar lista de cuentas
        for w in self.accounts_scroll.winfo_children():
            w.destroy()

        accounts = AccountModel.get_all()
        for acc in accounts:
            item = ctk.CTkFrame(
                self.accounts_scroll, 
                corner_radius=10, 
                fg_color="#f5f9fe", 
                border_width=1, 
                border_color="#dbe8f7", 
                height=48
            )
            item.pack(fill="x", pady=4)
            item.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                item, 
                text="🏦", 
                font=ctk.CTkFont(size=15)
            ).grid(row=0, column=0, padx=(12, 8), pady=8)

            txt_box = ctk.CTkFrame(item, fg_color="transparent")
            txt_box.grid(row=0, column=1, sticky="w", pady=6)

            ctk.CTkLabel(
                txt_box, 
                text=acc["name"], 
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#0f2942",
                anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                txt_box, 
                text=acc.get("description", "") or "Cuenta disponible", 
                font=ctk.CTkFont(size=10),
                text_color="#57708e",
                anchor="w"
            ).pack(anchor="w")

            bal_lbl = ctk.CTkLabel(
                item, 
                text=format_currency(acc["current_balance"]), 
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#059669" if acc["current_balance"] >= 0 else "#dc2626"
            )
            bal_lbl.grid(row=0, column=2, padx=(10, 14), pady=8)

        # Refrescar movimientos recientes
        for w in self.ops_scroll.winfo_children():
            w.destroy()

        recent_ops = OperationModel.get_all(limit=8)
        if not recent_ops:
            ctk.CTkLabel(self.ops_scroll, text="No hay movimientos registrados todavia.", text_color="#738a9c").pack(pady=20)
        else:
            for op in recent_ops:
                is_in = op["kind"] == "income"
                item = ctk.CTkFrame(
                    self.ops_scroll, 
                    corner_radius=10, 
                    fg_color="#f5f9fe", 
                    border_width=1, 
                    border_color="#dbe8f7", 
                    height=48
                )
                item.pack(fill="x", pady=4)
                item.grid_columnconfigure(1, weight=1)

                badge = ctk.CTkLabel(
                    item, 
                    text="↓" if is_in else "↑", 
                    width=28, 
                    height=28, 
                    corner_radius=7, 
                    fg_color="#10b981" if is_in else "#ef4444",
                    text_color="#ffffff",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                badge.grid(row=0, column=0, padx=(10, 8), pady=8)

                txt_box = ctk.CTkFrame(item, fg_color="transparent")
                txt_box.grid(row=0, column=1, sticky="w", pady=6)

                ctk.CTkLabel(
                    txt_box, 
                    text=op["concept"], 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#0f2942",
                    anchor="w"
                ).pack(anchor="w")

                sub_text = f"{op['date_at']} • {op['category_name']} • {op['account_name']}"
                ctk.CTkLabel(
                    txt_box, 
                    text=sub_text, 
                    font=ctk.CTkFont(size=10),
                    text_color="#57708e",
                    anchor="w"
                ).pack(anchor="w")

                prefix = "+" if is_in else "-"
                amt_lbl = ctk.CTkLabel(
                    item, 
                    text=f"{prefix}{format_currency(op['amount'])}", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#059669" if is_in else "#dc2626"
                )
                amt_lbl.grid(row=0, column=2, padx=(10, 14), pady=8)

    def _open_modal(self, kind):
        OperationModal(self.winfo_toplevel(), kind=kind, on_success=self.refresh_data)
