import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from reports.pdf_generator import PDFReportGenerator
from models.operation import OperationModel
from models.account import AccountModel
from utils.helpers import format_currency

class ReportsView(ctk.CTkFrame):
    """Vista para generacion, filtrado y exportacion de reportes PDF con tonos de azul bajo."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()
        self.apply_preset_month()
        self.preview_report()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Cabecera
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        lbl_title = ctk.CTkLabel(
            title_box, 
            text="Centro de Reportes Financieros", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f2942"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box, 
            text="Emision de estados de cuenta y reportes impresos en formato PDF profesional", 
            font=ctk.CTkFont(size=12),
            text_color="#57708e"
        )
        lbl_sub.pack(anchor="w")

        btn_pdf = ctk.CTkButton(
            header_frame,
            text="📄 Generar e Imprimir PDF",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            text_color="#ffffff",
            corner_radius=8,
            height=38,
            command=self.export_pdf
        )
        btn_pdf.grid(row=0, column=1, sticky="e")

        # 2. Panel de Parametros y Filtros esmerilado
        filters_card = ctk.CTkFrame(
            self, 
            corner_radius=12, 
            fg_color="#ffffff", 
            border_width=1, 
            border_color="#cde0f5"
        )
        filters_card.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 15))
        filters_card.grid_columnconfigure(0, weight=1)

        f_inner = ctk.CTkFrame(filters_card, fg_color="transparent")
        f_inner.pack(fill="x", padx=16, pady=12)

        # Fila 1: Tipo de reporte y Cuentas
        f_row1 = ctk.CTkFrame(f_inner, fg_color="transparent")
        f_row1.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(f_row1, text="Tipo de Reporte:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(side="left", padx=(0, 8))
        self.cmb_report_type = ctk.CTkComboBox(
            f_row1, 
            values=[
                "Estado de Cuenta / Flujo General", 
                "Reporte de Solo Ingresos", 
                "Reporte de Solo Gastos",
                "Estado Consolidado de Cuentas"
            ],
            width=260,
            state="readonly",
            fg_color="#f8fbfe",
            border_color="#bfdbfe",
            text_color="#0f2942",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#0f2942",
            dropdown_hover_color="#e8f0fe",
            command=lambda v: self.preview_report()
        )
        self.cmb_report_type.set("Estado de Cuenta / Flujo General")
        self.cmb_report_type.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(f_row1, text="Cuenta:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(side="left", padx=(0, 8))
        accounts = AccountModel.get_all()
        acc_opts = ["Todas las Cuentas"] + [f"{a['id']} - {a['name']}" for a in accounts]
        self.cmb_account = ctk.CTkComboBox(
            f_row1, 
            values=acc_opts, 
            width=200, 
            state="readonly", 
            fg_color="#f8fbfe",
            border_color="#bfdbfe",
            text_color="#0f2942",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#0f2942",
            dropdown_hover_color="#e8f0fe",
            command=lambda v: self.preview_report()
        )
        self.cmb_account.set("Todas las Cuentas")
        self.cmb_account.pack(side="left", padx=(0, 10))

        # Fila 2: Fechas y Botones rapidos
        f_row2 = ctk.CTkFrame(f_inner, fg_color="transparent")
        f_row2.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(f_row2, text="Desde:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(side="left", padx=(0, 6))
        self.txt_date_start = ctk.CTkEntry(
            f_row2, 
            width=105, 
            placeholder_text="YYYY-MM-DD",
            fg_color="#f8fbfe",
            border_color="#bfdbfe",
            text_color="#0f2942"
        )
        self.txt_date_start.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(f_row2, text="Hasta:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(side="left", padx=(0, 6))
        self.txt_date_end = ctk.CTkEntry(
            f_row2, 
            width=105, 
            placeholder_text="YYYY-MM-DD",
            fg_color="#f8fbfe",
            border_color="#bfdbfe",
            text_color="#0f2942"
        )
        self.txt_date_end.pack(side="left", padx=(0, 15))

        btn_month = ctk.CTkButton(
            f_row2, 
            text="Este Mes", 
            width=80, 
            height=28, 
            fg_color="#dbeafe", 
            text_color="#1d4ed8", 
            hover_color="#bfdbfe",
            command=self.apply_preset_month
        )
        btn_month.pack(side="left", padx=4)

        btn_year = ctk.CTkButton(
            f_row2, 
            text="Este Año", 
            width=80, 
            height=28, 
            fg_color="#dbeafe", 
            text_color="#1d4ed8", 
            hover_color="#bfdbfe",
            command=self.apply_preset_year
        )
        btn_year.pack(side="left", padx=4)

        btn_all = ctk.CTkButton(
            f_row2, 
            text="Historico", 
            width=80, 
            height=28, 
            fg_color="#dbeafe", 
            text_color="#1d4ed8", 
            hover_color="#bfdbfe",
            command=self.apply_preset_all
        )
        btn_all.pack(side="left", padx=4)

        btn_refresh = ctk.CTkButton(
            f_row2, 
            text="Actualizar Vista", 
            width=110, 
            height=28, 
            fg_color="#2563eb", 
            hover_color="#1d4ed8",
            text_color="#ffffff",
            corner_radius=6,
            command=self.preview_report
        )
        btn_refresh.pack(side="left", padx=(15, 0))

        # 3. Vista previa de resultados Glassmorphic
        self.preview_card = ctk.CTkFrame(
            self, 
            corner_radius=14, 
            border_width=1, 
            border_color="#cde0f5", 
            fg_color="#ffffff"
        )
        self.preview_card.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 20))
        self.preview_card.grid_columnconfigure(0, weight=1)
        self.preview_card.grid_rowconfigure(2, weight=1)

        # Barra de KPIs en la vista previa
        self.kpi_bar = ctk.CTkFrame(
            self.preview_card, 
            fg_color="#eef5fc", 
            corner_radius=8, 
            border_width=1, 
            border_color="#d5e5f7",
            height=46
        )
        self.kpi_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=10)
        self.kpi_bar.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_kpi_ops = ctk.CTkLabel(self.kpi_bar, text="Movimientos: 0", font=ctk.CTkFont(size=12, weight="bold"), text_color="#0f2942")
        self.lbl_kpi_ops.grid(row=0, column=0, pady=10)

        self.lbl_kpi_in = ctk.CTkLabel(self.kpi_bar, text="Ingresos: $ 0.00", font=ctk.CTkFont(size=12, weight="bold"), text_color="#059669")
        self.lbl_kpi_in.grid(row=0, column=1, pady=10)

        self.lbl_kpi_out = ctk.CTkLabel(self.kpi_bar, text="Gastos: $ 0.00", font=ctk.CTkFont(size=12, weight="bold"), text_color="#dc2626")
        self.lbl_kpi_out.grid(row=0, column=2, pady=10)

        self.lbl_kpi_net = ctk.CTkLabel(self.kpi_bar, text="Balance Neto: $ 0.00", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2563eb")
        self.lbl_kpi_net.grid(row=0, column=3, pady=10)

        # Encabezado tabla previa
        table_hdr = ctk.CTkFrame(self.preview_card, fg_color="#dbe9f9", height=34, corner_radius=6)
        table_hdr.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))
        table_hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(table_hdr, text="Fecha", width=90, font=ctk.CTkFont(size=11, weight="bold"), text_color="#1e3a5f").grid(row=0, column=0, padx=6)
        ctk.CTkLabel(table_hdr, text="Concepto", font=ctk.CTkFont(size=11, weight="bold"), text_color="#1e3a5f", anchor="w").grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(table_hdr, text="Categoria", width=120, font=ctk.CTkFont(size=11, weight="bold"), text_color="#1e3a5f").grid(row=0, column=2, padx=6)
        ctk.CTkLabel(table_hdr, text="Cuenta", width=120, font=ctk.CTkFont(size=11, weight="bold"), text_color="#1e3a5f").grid(row=0, column=3, padx=6)
        ctk.CTkLabel(table_hdr, text="Tipo", width=90, font=ctk.CTkFont(size=11, weight="bold"), text_color="#1e3a5f").grid(row=0, column=4, padx=6)
        ctk.CTkLabel(table_hdr, text="Monto", width=120, font=ctk.CTkFont(size=11, weight="bold"), text_color="#1e3a5f", anchor="e").grid(row=0, column=5, sticky="e", padx=12)

        self.preview_body = ctk.CTkScrollableFrame(self.preview_card, fg_color="transparent")
        self.preview_body.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.preview_body.grid_columnconfigure(1, weight=1)

    def apply_preset_month(self):
        today = datetime.now()
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        self.txt_date_start.delete(0, "end")
        self.txt_date_start.insert(0, start)
        self.txt_date_end.delete(0, "end")
        self.txt_date_end.insert(0, end)
        self.preview_report()

    def apply_preset_year(self):
        today = datetime.now()
        start = f"{today.year}-01-01"
        end = today.strftime("%Y-%m-%d")
        self.txt_date_start.delete(0, "end")
        self.txt_date_start.insert(0, start)
        self.txt_date_end.delete(0, "end")
        self.txt_date_end.insert(0, end)
        self.preview_report()

    def apply_preset_all(self):
        self.txt_date_start.delete(0, "end")
        self.txt_date_start.insert(0, "2000-01-01")
        self.txt_date_end.delete(0, "end")
        self.txt_date_end.insert(0, "2099-12-31")
        self.preview_report()

    def _get_current_filters(self):
        rep_type = self.cmb_report_type.get()
        start_date = self.txt_date_start.get().strip() or None
        end_date = self.txt_date_end.get().strip() or None

        account_id = None
        acc_val = self.cmb_account.get()
        if acc_val and not acc_val.startswith("Todas"):
            account_id = int(acc_val.split(" - ")[0])

        kind = None
        if "Solo Ingresos" in rep_type:
            kind = "income"
        elif "Solo Gastos" in rep_type:
            kind = "expense"

        return rep_type, start_date, end_date, account_id, kind

    def preview_report(self):
        """Muestra en pantalla los datos que iran al reporte PDF."""
        for w in self.preview_body.winfo_children():
            w.destroy()

        rep_type, start_date, end_date, account_id, kind = self._get_current_filters()

        if "Consolidado de Cuentas" in rep_type:
            accounts = AccountModel.get_all()
            total_bal = sum(float(a["current_balance"]) for a in accounts)

            self.lbl_kpi_ops.configure(text=f"Cuentas: {len(accounts)}")
            self.lbl_kpi_in.configure(text=f"Fondo Total: {format_currency(total_bal)}")
            self.lbl_kpi_out.configure(text="—")
            self.lbl_kpi_net.configure(text=f"Activas: {len(accounts)}")

            for idx, a in enumerate(accounts):
                bg = "#ffffff" if idx % 2 == 0 else "#f5f9fe"
                row = ctk.CTkFrame(self.preview_body, corner_radius=6, fg_color=bg, border_width=1, border_color="#dbe8f7", height=36)
                row.pack(fill="x", pady=2)
                row.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(row, text=str(a["id"]), width=90, text_color="#1e3a5f").grid(row=0, column=0, padx=6)
                ctk.CTkLabel(row, text=a["name"], font=ctk.CTkFont(size=12, weight="bold"), text_color="#0f2942", anchor="w").grid(row=0, column=1, sticky="w", padx=10)
                ctk.CTkLabel(row, text=a.get("description", "") or "—", width=120, text_color="#57708e").grid(row=0, column=2, padx=6)
                ctk.CTkLabel(row, text=format_currency(a.get("initial_balance", 0)), width=120, text_color="#1e3a5f").grid(row=0, column=3, padx=6)
                ctk.CTkLabel(row, text="Cuenta", width=90, text_color="#57708e").grid(row=0, column=4, padx=6)

                cur_bal = float(a.get("current_balance", 0))
                ctk.CTkLabel(
                    row, 
                    text=format_currency(cur_bal), 
                    width=120, 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#059669" if cur_bal >= 0 else "#dc2626",
                    anchor="e"
                ).grid(row=0, column=5, sticky="e", padx=12)
            return

        ops = OperationModel.get_all(
            kind=kind,
            start_date=start_date,
            end_date=end_date,
            account_id=account_id
        )

        summary = OperationModel.get_summary(start_date=start_date, end_date=end_date, account_id=account_id)

        self.lbl_kpi_ops.configure(text=f"Movimientos: {len(ops)}")
        self.lbl_kpi_in.configure(text=f"Ingresos: {format_currency(summary['income'])}")
        self.lbl_kpi_out.configure(text=f"Gastos: {format_currency(summary['expense'])}")
        self.lbl_kpi_net.configure(text=f"Balance: {format_currency(summary['net'])}")

        if not ops:
            ctk.CTkLabel(self.preview_body, text="No hay registros para los filtros seleccionados.", text_color="#738a9c", pady=25).pack()
            return

        for idx, op in enumerate(ops):
            bg = "#ffffff" if idx % 2 == 0 else "#f5f9fe"
            row = ctk.CTkFrame(self.preview_body, corner_radius=6, fg_color=bg, border_width=1, border_color="#dbe8f7", height=36)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(1, weight=1)

            is_in = op["kind"] == "income"
            ctk.CTkLabel(row, text=op["date_at"], width=90, font=ctk.CTkFont(size=11), text_color="#57708e").grid(row=0, column=0, padx=6)
            ctk.CTkLabel(row, text=op["concept"], font=ctk.CTkFont(size=12, weight="bold"), text_color="#0f2942", anchor="w").grid(row=0, column=1, sticky="w", padx=10)
            ctk.CTkLabel(row, text=op["category_name"], width=120, font=ctk.CTkFont(size=11), text_color="#57708e").grid(row=0, column=2, padx=6)
            ctk.CTkLabel(row, text=op["account_name"], width=120, font=ctk.CTkFont(size=11), text_color="#1e3a5f").grid(row=0, column=3, padx=6)

            kind_str = "Ingreso" if is_in else "Gasto"
            ctk.CTkLabel(
                row, 
                text=kind_str, 
                width=90, 
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#10b981" if is_in else "#ef4444"
            ).grid(row=0, column=4, padx=6)

            amt_str = f"{'+' if is_in else '-'}{format_currency(op['amount'])}"
            ctk.CTkLabel(
                row, 
                text=amt_str, 
                width=120, 
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#059669" if is_in else "#dc2626",
                anchor="e"
            ).grid(row=0, column=5, sticky="e", padx=12)

    def export_pdf(self):
        """Genera el reporte PDF y lo abre para impresion."""
        rep_type, start_date, end_date, account_id, kind = self._get_current_filters()

        default_filename = f"Reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialfile=default_filename,
            title="Guardar Reporte PDF de IntelliKonta"
        )

        if not file_path:
            return

        try:
            if "Consolidado de Cuentas" in rep_type:
                accounts = AccountModel.get_all()
                PDFReportGenerator.generate_accounts_report(accounts, output_path=file_path)
            else:
                ops = OperationModel.get_all(
                    kind=kind,
                    start_date=start_date,
                    end_date=end_date,
                    account_id=account_id
                )
                summary = OperationModel.get_summary(start_date=start_date, end_date=end_date, account_id=account_id)

                subtitle_parts = []
                if start_date and end_date:
                    subtitle_parts.append(f"Periodo: {start_date} al {end_date}")
                if account_id:
                    acc_val = self.cmb_account.get()
                    subtitle_parts.append(f"Cuenta: {acc_val}")
                subtitle = " | ".join(subtitle_parts) if subtitle_parts else "Todos los registros historicos"

                PDFReportGenerator.generate_operations_report(
                    operations=ops,
                    summary_data=summary,
                    title=rep_type,
                    subtitle=subtitle,
                    output_path=file_path
                )

            if messagebox.askyesno("Reporte Generado", "El reporte PDF se creo con exito.\n\n¿Deseas abrirlo ahora para visualizarlo o imprimirlo?", parent=self):
                try:
                    os.startfile(file_path)
                except Exception as err:
                    messagebox.showinfo("Reporte Guardado", f"El archivo fue guardado en:\n{file_path}\n({err})", parent=self)
        except Exception as e:
            messagebox.showerror("Error al generar PDF", f"Ocurrio un problema al generar el archivo:\n{e}", parent=self)
