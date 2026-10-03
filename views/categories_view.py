import customtkinter as ctk
from tkinter import messagebox, simpledialog
from components.modals import CategoryModal
from models.category import CategoryModel, PaymentMethodModel

class CategoriesView(ctk.CTkFrame):
    """Vista de administracion de categorias contables y metodos de pago con tonos de azul bajo."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()
        self.refresh_categories()
        self.refresh_paymethods()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Cabecera
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        lbl_title = ctk.CTkLabel(
            header_frame, 
            text="Categorias y Formas de Pago", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f2942"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header_frame, 
            text="Configuracion de clasificaciones financieras y vias de liquidacion", 
            font=ctk.CTkFont(size=12),
            text_color="#57708e"
        )
        lbl_sub.pack(anchor="w")

        # 2. Pestañas en cristal esmerilado blanco y azul bajo
        self.tabview = ctk.CTkTabview(
            self, 
            corner_radius=14, 
            fg_color="#ffffff", 
            segmented_button_fg_color="#e2edf9", 
            segmented_button_selected_color="#2563eb", 
            segmented_button_selected_hover_color="#1d4ed8", 
            border_width=1, 
            border_color="#cde0f5"
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))

        self.tab_cat = self.tabview.add("Categorias de Ingreso y Gasto")
        self.tab_pay = self.tabview.add("Metodos de Pago")

        self._build_categories_tab()
        self._build_paymethods_tab()

    def _build_categories_tab(self):
        self.tab_cat.grid_columnconfigure(0, weight=1)
        self.tab_cat.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self.tab_cat, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 10))
        top_bar.grid_columnconfigure(0, weight=1)

        # Filtro de tipo
        self.cmb_cat_kind = ctk.CTkComboBox(
            top_bar, 
            values=["Todas las Categorias", "Solo Ingresos", "Solo Gastos"], 
            state="readonly",
            fg_color="#f8fbfe",
            border_color="#bfdbfe",
            text_color="#0f2942",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#0f2942",
            dropdown_hover_color="#e8f0fe",
            command=lambda v: self.refresh_categories()
        )
        self.cmb_cat_kind.set("Todas las Categorias")
        self.cmb_cat_kind.grid(row=0, column=0, sticky="w")

        btn_new_cat = ctk.CTkButton(
            top_bar, 
            text="+ Nueva Categoria", 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2563eb", 
            hover_color="#1d4ed8",
            text_color="#ffffff",
            corner_radius=8,
            command=self._open_new_cat_modal
        )
        btn_new_cat.grid(row=0, column=1, sticky="e")

        self.cat_scroll = ctk.CTkScrollableFrame(self.tab_cat, fg_color="transparent")
        self.cat_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.cat_scroll.grid_columnconfigure(0, weight=1)

    def _build_paymethods_tab(self):
        self.tab_pay.grid_columnconfigure(0, weight=1)
        self.tab_pay.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self.tab_pay, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 10))
        top_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top_bar, text="Vias de cobro y pago disponibles", font=ctk.CTkFont(size=12), text_color="#57708e").grid(row=0, column=0, sticky="w")

        btn_new_pay = ctk.CTkButton(
            top_bar, 
            text="+ Nuevo Metodo", 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2563eb", 
            hover_color="#1d4ed8",
            text_color="#ffffff",
            corner_radius=8,
            command=self._new_paymethod_prompt
        )
        btn_new_pay.grid(row=0, column=1, sticky="e")

        self.pay_scroll = ctk.CTkScrollableFrame(self.tab_pay, fg_color="transparent")
        self.pay_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.pay_scroll.grid_columnconfigure(0, weight=1)

    def refresh_categories(self):
        for w in self.cat_scroll.winfo_children():
            w.destroy()

        kind_filter = "all"
        sel = self.cmb_cat_kind.get()
        if "Ingresos" in sel:
            kind_filter = "income"
        elif "Gastos" in sel:
            kind_filter = "expense"

        categories = CategoryModel.get_all(kind=kind_filter)

        for idx, cat in enumerate(categories):
            bg = "#ffffff" if idx % 2 == 0 else "#f5f9fe"
            row = ctk.CTkFrame(self.cat_scroll, corner_radius=8, fg_color=bg, border_width=1, border_color="#dbe8f7", height=46)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(1, weight=1)

            # Badge de aplicacion
            kind_label = "Ambos"
            kind_color = "#3b82f6"
            if cat.get("kind") == "income":
                kind_label = "Ingreso"
                kind_color = "#10b981"
            elif cat.get("kind") == "expense":
                kind_label = "Gasto"
                kind_color = "#ef4444"

            badge = ctk.CTkLabel(
                row, 
                text=kind_label, 
                width=68, 
                height=24, 
                corner_radius=6, 
                fg_color=kind_color,
                text_color="#ffffff",
                font=ctk.CTkFont(size=10, weight="bold")
            )
            badge.grid(row=0, column=0, padx=(12, 10), pady=6)

            # Nombre y descripcion
            c_box = ctk.CTkFrame(row, fg_color="transparent")
            c_box.grid(row=0, column=1, sticky="w", pady=4)
            ctk.CTkLabel(c_box, text=cat["name"], font=ctk.CTkFont(size=12, weight="bold"), text_color="#0f2942", anchor="w").pack(anchor="w")
            if cat.get("description"):
                ctk.CTkLabel(c_box, text=cat["description"], font=ctk.CTkFont(size=10), text_color="#738a9c", anchor="w").pack(anchor="w")

            # Botones
            act_box = ctk.CTkFrame(row, fg_color="transparent")
            act_box.grid(row=0, column=2, padx=12)

            ctk.CTkButton(
                act_box, 
                text="✏️", 
                width=28, 
                height=26, 
                corner_radius=6,
                fg_color="#f59e0b",
                hover_color="#d97706",
                text_color="#ffffff",
                command=lambda c=cat: self._open_edit_cat_modal(c)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                act_box, 
                text="🗑️", 
                width=28, 
                height=26, 
                corner_radius=6,
                fg_color="#ef4444",
                hover_color="#dc2626",
                text_color="#ffffff",
                command=lambda c=cat: self._delete_cat(c)
            ).pack(side="left", padx=2)

    def refresh_paymethods(self):
        for w in self.pay_scroll.winfo_children():
            w.destroy()

        methods = PaymentMethodModel.get_all()

        for idx, m in enumerate(methods):
            bg = "#ffffff" if idx % 2 == 0 else "#f5f9fe"
            row = ctk.CTkFrame(self.pay_scroll, corner_radius=8, fg_color=bg, border_width=1, border_color="#dbe8f7", height=42)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text="💳", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(14, 8), pady=6)
            ctk.CTkLabel(row, text=m["name"], font=ctk.CTkFont(size=12, weight="bold"), text_color="#0f2942", anchor="w").grid(row=0, column=1, sticky="w", pady=6)

            act_box = ctk.CTkFrame(row, fg_color="transparent")
            act_box.grid(row=0, column=2, padx=12)

            ctk.CTkButton(
                act_box, 
                text="✏️", 
                width=28, 
                height=26, 
                corner_radius=6,
                fg_color="#f59e0b",
                hover_color="#d97706",
                text_color="#ffffff",
                command=lambda item=m: self._edit_paymethod_prompt(item)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                act_box, 
                text="🗑️", 
                width=28, 
                height=26, 
                corner_radius=6,
                fg_color="#ef4444",
                hover_color="#dc2626",
                text_color="#ffffff",
                command=lambda item=m: self._delete_paymethod(item)
            ).pack(side="left", padx=2)

    def _open_new_cat_modal(self):
        CategoryModal(self.winfo_toplevel(), on_success=self.refresh_categories)

    def _open_edit_cat_modal(self, category_data):
        CategoryModal(self.winfo_toplevel(), category_data=category_data, on_success=self.refresh_categories)

    def _delete_cat(self, cat):
        if messagebox.askyesno("Eliminar Categoria", f"¿Deseas eliminar la categoria '{cat['name']}'?", parent=self):
            CategoryModel.delete(cat["id"])
            self.refresh_categories()

    def _new_paymethod_prompt(self):
        name = simpledialog.askstring("Nuevo Metodo", "Nombre de la forma de pago (ej. Cripto, Vale):", parent=self)
        if name and name.strip():
            PaymentMethodModel.create(name.strip())
            self.refresh_paymethods()

    def _edit_paymethod_prompt(self, item):
        name = simpledialog.askstring("Editar Metodo", "Nombre de la forma de pago:", initialvalue=item["name"], parent=self)
        if name and name.strip():
            PaymentMethodModel.update(item["id"], name.strip())
            self.refresh_paymethods()

    def _delete_paymethod(self, item):
        if messagebox.askyesno("Eliminar", f"¿Eliminar la forma de pago '{item['name']}'?", parent=self):
            PaymentMethodModel.delete(item["id"])
            self.refresh_paymethods()
