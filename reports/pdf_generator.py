import os
from fpdf import FPDF
from datetime import datetime

class IntelliReportPDF(FPDF):
    """Clase personalizada para reportes PDF de IntelliKonta."""

    def __init__(self, title="Reporte Financiero", subtitle=""):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.report_title = title
        self.report_subtitle = subtitle
        self.set_auto_page_break(auto=True, margin=15)
        self.alias_nb_pages()

    def header(self):
        # Fondo decorativo en la barra superior
        self.set_fill_color(30, 41, 59) # Slate 800
        self.rect(0, 0, 210, 8, "F")

        # Titulo de la marca
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(30, 41, 59)
        self.cell(100, 10, "INTELLIKONTA", border=0, align="L")

        # Fecha y hora de generacion
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 116, 139)
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(90, 10, f"Generado: {now_str}", border=0, align="R")
        self.ln(10)

        # Titulo del Reporte
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(15, 23, 42)
        self.cell(0, 7, self.report_title, border=0, align="L")
        self.ln(6)

        # Subtitulo o rango de filtros
        if self.report_subtitle:
            self.set_font("Helvetica", "", 10)
            self.set_text_color(71, 85, 105)
            self.cell(0, 6, self.report_subtitle, border=0, align="L")
            self.ln(7)

        # Linea divisoria elegante
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_y(-10)

        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(100, 5, "IntelliKonta - Sistema Contable y Financiero", border=0, align="L")
        page_str = f"Pagina {self.page_no()} de {{nb}}"
        self.cell(90, 5, page_str, border=0, align="R")


class PDFReportGenerator:
    """Generador de reportes contables en formato PDF."""

    @staticmethod
    def generate_operations_report(operations, summary_data, title="Reporte de Operaciones", subtitle="", output_path="reporte_operaciones.pdf"):
        pdf = IntelliReportPDF(title=title, subtitle=subtitle)
        pdf.add_page()

        # Tarjetas de resumen financiero
        total_in = summary_data.get("income", 0.0)
        total_out = summary_data.get("expense", 0.0)
        total_net = summary_data.get("net", 0.0)

        card_w = 60
        card_h = 16
        start_y = pdf.get_y()

        # Tarjeta Ingresos
        pdf.set_fill_color(240, 253, 244) # Verde suave
        pdf.set_draw_color(187, 247, 208)
        pdf.rect(10, start_y, card_w, card_h, "FD")
        pdf.set_xy(10, start_y + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(22, 101, 52)
        pdf.cell(card_w, 4, "TOTAL INGRESOS", border=0, align="C")
        pdf.set_xy(10, start_y + 7)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(card_w, 6, f"$ {total_in:,.2f}", border=0, align="C")

        # Tarjeta Gastos
        pdf.set_fill_color(254, 242, 242) # Rojo suave
        pdf.set_draw_color(254, 202, 202)
        pdf.rect(75, start_y, card_w, card_h, "FD")
        pdf.set_xy(75, start_y + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(153, 27, 27)
        pdf.cell(card_w, 4, "TOTAL GASTOS", border=0, align="C")
        pdf.set_xy(75, start_y + 7)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(card_w, 6, f"$ {total_out:,.2f}", border=0, align="C")

        # Tarjeta Balance Neto
        net_bg = (239, 246, 255) if total_net >= 0 else (255, 241, 242)
        net_border = (191, 219, 254) if total_net >= 0 else (254, 205, 211)
        net_text = (30, 64, 175) if total_net >= 0 else (159, 18, 57)

        pdf.set_fill_color(*net_bg)
        pdf.set_draw_color(*net_border)
        pdf.rect(140, start_y, card_w, card_h, "FD")
        pdf.set_xy(140, start_y + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*net_text)
        pdf.cell(card_w, 4, "BALANCE NETO", border=0, align="C")
        pdf.set_xy(140, start_y + 7)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(card_w, 6, f"$ {total_net:,.2f}", border=0, align="C")

        pdf.set_y(start_y + card_h + 8)

        # Encabezado de la Tabla
        col_widths = [22, 58, 32, 32, 24, 22] # Suma 190 mm (A4 210 - 20 margenes)
        headers = ["Fecha", "Concepto", "Categoria", "Cuenta", "Tipo", "Monto"]

        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)

        for i, h in enumerate(headers):
            align = "R" if i == 5 else ("C" if i in [0, 4] else "L")
            pdf.cell(col_widths[i], 8, f"  {h}  ", border=0, align=align, fill=True)
        pdf.ln(8)

        # Filas de datos
        pdf.set_font("Helvetica", "", 8)
        fill = False

        for op in operations:
            if pdf.get_y() > 265:
                pdf.add_page()
                # Re-imprimir encabezados
                pdf.set_fill_color(30, 41, 59)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Helvetica", "B", 8)
                for i, h in enumerate(headers):
                    align = "R" if i == 5 else ("C" if i in [0, 4] else "L")
                    pdf.cell(col_widths[i], 8, f"  {h}  ", border=0, align=align, fill=True)
                pdf.ln(8)
                pdf.set_font("Helvetica", "", 8)

            # Fondo alternado
            if fill:
                pdf.set_fill_color(248, 250, 252)
            else:
                pdf.set_fill_color(255, 255, 255)

            pdf.set_text_color(30, 41, 59)

            date_str = str(op.get("date_at", ""))
            concept = str(op.get("concept", ""))[:32]
            category = str(op.get("category_name", "Sin Categoria"))[:18]
            account = str(op.get("account_name", "N/A"))[:18]
            kind = "Ingreso" if op.get("kind") == "income" else "Gasto"
            amount = float(op.get("amount", 0.0))
            amount_str = f"$ {amount:,.2f}"

            # Colores segun tipo
            pdf.cell(col_widths[0], 7, date_str, border="B", align="C", fill=True)
            pdf.cell(col_widths[1], 7, f" {concept}", border="B", align="L", fill=True)
            pdf.cell(col_widths[2], 7, f" {category}", border="B", align="L", fill=True)
            pdf.cell(col_widths[3], 7, f" {account}", border="B", align="L", fill=True)

            if kind == "Ingreso":
                pdf.set_text_color(22, 101, 52)
            else:
                pdf.set_text_color(185, 28, 28)
            pdf.cell(col_widths[4], 7, kind, border="B", align="C", fill=True)
            pdf.cell(col_widths[5], 7, f"{amount_str} ", border="B", align="R", fill=True)

            pdf.ln(7)
            fill = not fill

        # Fila de Totales
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(15, 23, 42)
        pdf.set_fill_color(241, 245, 249)
        total_w = sum(col_widths[:5])
        pdf.cell(total_w, 8, f"TOTAL REGISTROS ({len(operations)}):", border="T", align="R", fill=True)
        total_display = total_net if "General" in title else (total_in if "Ingreso" in title else total_out)
        pdf.cell(col_widths[5], 8, f"$ {total_display:,.2f} ", border="T", align="R", fill=True)
        pdf.ln(8)

        pdf.output(output_path)
        return output_path

    @staticmethod
    def generate_accounts_report(accounts, output_path="reporte_cuentas.pdf"):
        pdf = IntelliReportPDF(title="Estado General de Cuentas y Fondos", subtitle="Balances consolidados por cuenta financiera")
        pdf.add_page()

        total_balance = sum(float(a.get("current_balance", 0.0)) for a in accounts)

        # Tarjeta saldo total
        start_y = pdf.get_y()
        pdf.set_fill_color(238, 242, 255)
        pdf.set_draw_color(199, 210, 254)
        pdf.rect(10, start_y, 190, 16, "FD")
        pdf.set_xy(10, start_y + 2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(67, 56, 202)
        pdf.cell(190, 4, "FONDO TOTAL CONSOLIDADO EN CUENTAS", border=0, align="C")
        pdf.set_xy(10, start_y + 7)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(190, 7, f"$ {total_balance:,.2f}", border=0, align="C")

        pdf.set_y(start_y + 24)

        # Tabla de Cuentas
        col_widths = [15, 65, 55, 25, 30]
        headers = ["#", "Nombre de Cuenta", "Descripcion", "Apertura", "Saldo Actual"]

        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)

        for i, h in enumerate(headers):
            align = "R" if i in [3, 4] else ("C" if i == 0 else "L")
            pdf.cell(col_widths[i], 8, f"  {h}  ", border=0, align=align, fill=True)
        pdf.ln(8)

        pdf.set_font("Helvetica", "", 8)
        fill = False

        for acc in accounts:
            if fill:
                pdf.set_fill_color(248, 250, 252)
            else:
                pdf.set_fill_color(255, 255, 255)

            pdf.set_text_color(30, 41, 59)
            pdf.cell(col_widths[0], 7, str(acc["id"]), border="B", align="C", fill=True)
            pdf.cell(col_widths[1], 7, f" {acc['name'][:35]}", border="B", align="L", fill=True)
            pdf.cell(col_widths[2], 7, f" {acc.get('description', '')[:30]}", border="B", align="L", fill=True)
            pdf.cell(col_widths[3], 7, f"$ {float(acc.get('initial_balance', 0)):,.2f}", border="B", align="R", fill=True)

            cur_bal = float(acc.get("current_balance", 0.0))
            if cur_bal < 0:
                pdf.set_text_color(185, 28, 28)
            else:
                pdf.set_text_color(22, 101, 52)
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(col_widths[4], 7, f"$ {cur_bal:,.2f} ", border="B", align="R", fill=True)
            pdf.set_font("Helvetica", "", 8)

            pdf.ln(7)
            fill = not fill

        # Totales
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(15, 23, 42)
        pdf.set_fill_color(241, 245, 249)
        pdf.cell(sum(col_widths[:4]), 8, "TOTAL CONSOLIDADO: ", border="T", align="R", fill=True)
        pdf.cell(col_widths[4], 8, f"$ {total_balance:,.2f} ", border="T", align="R", fill=True)
        pdf.ln(8)

        pdf.output(output_path)
        return output_path
