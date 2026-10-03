import customtkinter as ctk
from tkinter import messagebox
from utils.helpers import get_today_str, parse_float
from models.account import AccountModel
from models.category import CategoryModel, PaymentMethodModel
from models.contact import ContactModel
from models.operation import OperationModel
from models.user import UserModel
from utils.session import Session

class BaseModal(ctk.CTkToplevel):
    """Ventana modal base con estilo en tonos de azul bajo y cristal blanco."""
    def __init__(self, parent, title="Dialogo", width=460, height=520):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Fondo en tono azul bajo esmerilado
        self.configure(fg_color="#f0f6fc")

        # Centrar sobre la ventana padre
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
            self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header del modal
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        self.lbl_title = ctk.CTkLabel(
            self.header_frame, 
            text=title, 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0f2942"
        )
        self.lbl_title.pack(anchor="w")

        # Contenedor de formulario con scroll
        self.body_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=5)
        self.body_frame.grid_columnconfigure(0, weight=1)

        # Barra de botones inferior
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(10, 20))


class OperationModal(BaseModal):
    """Modal para registrar o editar un Ingreso o Gasto."""

    def __init__(self, parent, kind="income", operation_data=None, on_success=None):
        title = "Nuevo Ingreso" if kind == "income" else "Nuevo Gasto"
        if operation_data:
            title = f"Editar {'Ingreso' if kind == 'income' else 'Gasto'}"
        super().__init__(parent, title=title, width=500, height=620)

        self.kind = kind
        self.op_data = operation_data
        self.on_success = on_success

        self._load_options()
        self._build_form()

    def _load_options(self):
        self.accounts = AccountModel.get_all()
        self.categories = CategoryModel.get_all(kind=self.kind)
        self.paymethods = PaymentMethodModel.get_all()
        self.contacts = ContactModel.get_all()

    def _build_form(self):
        ctk.CTkLabel(self.body_frame, text="Concepto *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_concept = ctk.CTkEntry(self.body_frame, placeholder_text="Ej: Pago de factura, Venta de producto...", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_concept.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row1, text="Monto ($) *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ctk.CTkLabel(row1, text="Fecha (AAAA-MM-DD) *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.txt_amount = ctk.CTkEntry(row1, placeholder_text="0.00", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_amount.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(2, 0))

        self.txt_date = ctk.CTkEntry(row1, placeholder_text=get_today_str(), fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_date.insert(0, get_today_str())
        self.txt_date.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(2, 0))

        ctk.CTkLabel(self.body_frame, text="Cuenta Financiera *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        acc_names = [f"{a['id']} - {a['name']}" for a in self.accounts] or ["No hay cuentas"]
        self.cmb_account = ctk.CTkComboBox(self.body_frame, values=acc_names, state="readonly", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942", dropdown_fg_color="#ffffff", dropdown_text_color="#0f2942", dropdown_hover_color="#e8f0fe")
        if acc_names:
            self.cmb_account.set(acc_names[0])
        self.cmb_account.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.body_frame, text="Categoria", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        cat_names = ["(Sin Categoria)"] + [f"{c['id']} - {c['name']}" for c in self.categories]
        self.cmb_category = ctk.CTkComboBox(self.body_frame, values=cat_names, state="readonly", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942", dropdown_fg_color="#ffffff", dropdown_text_color="#0f2942", dropdown_hover_color="#e8f0fe")
        self.cmb_category.set(cat_names[0])
        self.cmb_category.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.body_frame, text="Contacto (Cliente / Proveedor)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        contact_names = ["(General / Ninguno)"] + [f"{co['id']} - {co['name']} {co.get('lastname','')}" for co in self.contacts]
        self.cmb_contact = ctk.CTkComboBox(self.body_frame, values=contact_names, state="readonly", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942", dropdown_fg_color="#ffffff", dropdown_text_color="#0f2942", dropdown_hover_color="#e8f0fe")
        self.cmb_contact.set(contact_names[0])
        self.cmb_contact.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.body_frame, text="Metodo de Pago", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        pay_names = ["(Ninguno)"] + [f"{p['id']} - {p['name']}" for p in self.paymethods]
        self.cmb_paymethod = ctk.CTkComboBox(self.body_frame, values=pay_names, state="readonly", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942", dropdown_fg_color="#ffffff", dropdown_text_color="#0f2942", dropdown_hover_color="#e8f0fe")
        self.cmb_paymethod.set(pay_names[1] if len(pay_names) > 1 else pay_names[0])
        self.cmb_paymethod.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.body_frame, text="Nota / Descripcion", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_desc = ctk.CTkEntry(self.body_frame, placeholder_text="Opcional", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_desc.pack(fill="x", pady=(0, 10))

        if self.op_data:
            self._fill_data()

        btn_cancel = ctk.CTkButton(
            self.footer_frame, 
            text="Cancelar", 
            fg_color="#e2edf9",
            text_color="#334155",
            hover_color="#cbd5e1",
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(10, 0))

        btn_save = ctk.CTkButton(
            self.footer_frame, 
            text="Guardar", 
            fg_color="#10b981" if self.kind == "income" else "#ef4444",
            hover_color="#059669" if self.kind == "income" else "#dc2626",
            text_color="#ffffff",
            command=self._save
        )
        btn_save.pack(side="right")

    def _fill_data(self):
        self.txt_concept.insert(0, self.op_data.get("concept", ""))
        self.txt_amount.insert(0, str(self.op_data.get("amount", "")))
        self.txt_date.delete(0, "end")
        self.txt_date.insert(0, str(self.op_data.get("date_at", "")))
        self.txt_desc.insert(0, self.op_data.get("description", "") or "")

        acc_id = self.op_data.get("account_id")
        for val in self.cmb_account._values:
            if val.startswith(f"{acc_id} -"):
                self.cmb_account.set(val)
                break

        cat_id = self.op_data.get("category_id")
        if cat_id:
            for val in self.cmb_category._values:
                if val.startswith(f"{cat_id} -"):
                    self.cmb_category.set(val)
                    break

        con_id = self.op_data.get("contact_id")
        if con_id:
            for val in self.cmb_contact._values:
                if val.startswith(f"{con_id} -"):
                    self.cmb_contact.set(val)
                    break

        pay_id = self.op_data.get("paymethod_id")
        if pay_id:
            for val in self.cmb_paymethod._values:
                if val.startswith(f"{pay_id} -"):
                    self.cmb_paymethod.set(val)
                    break

    def _save(self):
        concept = self.txt_concept.get().strip()
        amount_val = parse_float(self.txt_amount.get())
        date_at = self.txt_date.get().strip()
        desc = self.txt_desc.get().strip()

        if not concept:
            messagebox.showwarning("Atencion", "El concepto es obligatorio.", parent=self)
            return

        if amount_val <= 0:
            messagebox.showwarning("Atencion", "El monto debe ser un numero mayor a 0.", parent=self)
            return

        if not date_at:
            date_at = get_today_str()

        try:
            account_id = int(self.cmb_account.get().split(" - ")[0])
        except Exception:
            messagebox.showwarning("Atencion", "Seleccione una cuenta valida.", parent=self)
            return

        category_id = None
        if not self.cmb_category.get().startswith("(Sin"):
            category_id = int(self.cmb_category.get().split(" - ")[0])

        contact_id = None
        if not self.cmb_contact.get().startswith("(General"):
            contact_id = int(self.cmb_contact.get().split(" - ")[0])

        paymethod_id = None
        if not self.cmb_paymethod.get().startswith("(Ninguno"):
            paymethod_id = int(self.cmb_paymethod.get().split(" - ")[0])

        user_id = Session.get_user_id()

        if self.op_data:
            OperationModel.update(
                self.op_data["id"],
                concept=concept,
                amount=amount_val,
                date_at=date_at,
                kind=self.kind,
                account_id=account_id,
                category_id=category_id,
                contact_id=contact_id,
                paymethod_id=paymethod_id,
                user_id=user_id,
                description=desc
            )
        else:
            OperationModel.create(
                concept=concept,
                amount=amount_val,
                date_at=date_at,
                kind=self.kind,
                account_id=account_id,
                category_id=category_id,
                contact_id=contact_id,
                paymethod_id=paymethod_id,
                user_id=user_id,
                description=desc
            )

        if self.on_success:
            self.on_success()

        self.destroy()


class AccountModal(BaseModal):
    """Modal para crear y editar cuentas financieras."""

    def __init__(self, parent, account_data=None, on_success=None):
        title = "Editar Cuenta" if account_data else "Nueva Cuenta Financiera"
        super().__init__(parent, title=title, width=440, height=400)
        self.account_data = account_data
        self.on_success = on_success
        self._build_form()

    def _build_form(self):
        ctk.CTkLabel(self.body_frame, text="Nombre de la Cuenta *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_name = ctk.CTkEntry(self.body_frame, placeholder_text="Ej: Banco BBVA, Caja Chica, Tarjeta...", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_name.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.body_frame, text="Descripcion", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_desc = ctk.CTkEntry(self.body_frame, placeholder_text="Ej: Cuenta operativa principal", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_desc.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.body_frame, text="Saldo Inicial ($) *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_balance = ctk.CTkEntry(self.body_frame, placeholder_text="0.00", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_balance.insert(0, "0.00")
        self.txt_balance.pack(fill="x", pady=(0, 10))

        if self.account_data:
            self.txt_name.insert(0, self.account_data.get("name", ""))
            self.txt_desc.insert(0, self.account_data.get("description", "") or "")
            self.txt_balance.delete(0, "end")
            self.txt_balance.insert(0, str(self.account_data.get("initial_balance", "0.00")))

        ctk.CTkButton(
            self.footer_frame, 
            text="Cancelar", 
            fg_color="#e2edf9",
            text_color="#334155",
            hover_color="#cbd5e1",
            command=self.destroy
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            self.footer_frame, 
            text="Guardar", 
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#ffffff",
            command=self._save
        ).pack(side="right")

    def _save(self):
        name = self.txt_name.get().strip()
        desc = self.txt_desc.get().strip()
        init_bal = parse_float(self.txt_balance.get(), 0.0)

        if not name:
            messagebox.showwarning("Atencion", "El nombre de la cuenta es requerido.", parent=self)
            return

        if self.account_data:
            AccountModel.update(self.account_data["id"], name, desc, init_bal)
        else:
            AccountModel.create(name, desc, init_bal)

        if self.on_success:
            self.on_success()
        self.destroy()


class ContactModal(BaseModal):
    """Modal para crear y editar contactos (clientes y proveedores)."""

    def __init__(self, parent, contact_data=None, on_success=None):
        title = "Editar Contacto" if contact_data else "Nuevo Contacto"
        super().__init__(parent, title=title, width=480, height=560)
        self.contact_data = contact_data
        self.on_success = on_success
        self._build_form()

    def _build_form(self):
        row_name = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        row_name.pack(fill="x", pady=(5, 5))
        row_name.grid_columnconfigure(0, weight=1)
        row_name.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row_name, text="Nombre *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ctk.CTkLabel(row_name, text="Apellidos", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.txt_name = ctk.CTkEntry(row_name, placeholder_text="Nombre", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_name.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(2, 0))

        self.txt_lastname = ctk.CTkEntry(row_name, placeholder_text="Apellidos", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_lastname.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(2, 0))

        ctk.CTkLabel(self.body_frame, text="Empresa / Razon Social", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(8, 2))
        self.txt_company = ctk.CTkEntry(self.body_frame, placeholder_text="Empresa o Negocio", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_company.pack(fill="x", pady=(0, 8))

        row_contact = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        row_contact.pack(fill="x", pady=(0, 8))
        row_contact.grid_columnconfigure(0, weight=1)
        row_contact.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row_contact, text="Telefono", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ctk.CTkLabel(row_contact, text="Email", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.txt_phone = ctk.CTkEntry(row_contact, placeholder_text="55 1234 5678", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_phone.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(2, 0))

        self.txt_email = ctk.CTkEntry(row_contact, placeholder_text="correo@empresa.com", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_email.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(2, 0))

        ctk.CTkLabel(self.body_frame, text="Direccion", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(4, 2))
        self.txt_address = ctk.CTkEntry(self.body_frame, placeholder_text="Calle, Numero, Colonia, Ciudad", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_address.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.body_frame, text="Notas adicionales", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(4, 2))
        self.txt_notes = ctk.CTkEntry(self.body_frame, placeholder_text="Cliente habitual, condiciones comerciales, etc.", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_notes.pack(fill="x", pady=(0, 10))

        if self.contact_data:
            self.txt_name.insert(0, self.contact_data.get("name", ""))
            self.txt_lastname.insert(0, self.contact_data.get("lastname", "") or "")
            self.txt_company.insert(0, self.contact_data.get("company", "") or "")
            self.txt_phone.insert(0, self.contact_data.get("phone", "") or "")
            self.txt_email.insert(0, self.contact_data.get("email", "") or "")
            self.txt_address.insert(0, self.contact_data.get("address", "") or "")
            self.txt_notes.insert(0, self.contact_data.get("notes", "") or "")

        ctk.CTkButton(
            self.footer_frame, 
            text="Cancelar", 
            fg_color="#e2edf9",
            text_color="#334155",
            hover_color="#cbd5e1",
            command=self.destroy
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            self.footer_frame, 
            text="Guardar Contacto", 
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#ffffff",
            command=self._save
        ).pack(side="right")

    def _save(self):
        name = self.txt_name.get().strip()
        lastname = self.txt_lastname.get().strip()
        company = self.txt_company.get().strip()
        phone = self.txt_phone.get().strip()
        email = self.txt_email.get().strip()
        address = self.txt_address.get().strip()
        notes = self.txt_notes.get().strip()

        if not name:
            messagebox.showwarning("Atencion", "El nombre es obligatorio.", parent=self)
            return

        if self.contact_data:
            ContactModel.update(self.contact_data["id"], name, lastname, company, phone, email, address, notes)
        else:
            ContactModel.create(name, lastname, company, phone, email, address, notes)

        if self.on_success:
            self.on_success()
        self.destroy()


class CategoryModal(BaseModal):
    """Modal para crear y editar categorias."""

    def __init__(self, parent, category_data=None, on_success=None):
        title = "Editar Categoria" if category_data else "Nueva Categoria"
        super().__init__(parent, title=title, width=440, height=380)
        self.category_data = category_data
        self.on_success = on_success
        self._build_form()

    def _build_form(self):
        ctk.CTkLabel(self.body_frame, text="Nombre de la Categoria *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_name = ctk.CTkEntry(self.body_frame, placeholder_text="Ej: Ventas, Alimentos, Servicios...", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_name.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.body_frame, text="Aplica para", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.cmb_kind = ctk.CTkComboBox(self.body_frame, values=["Ambos (Ingresos y Gastos)", "Solo Ingresos", "Solo Gastos"], state="readonly", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942", dropdown_fg_color="#ffffff", dropdown_text_color="#0f2942", dropdown_hover_color="#e8f0fe")
        self.cmb_kind.set("Ambos (Ingresos y Gastos)")
        self.cmb_kind.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.body_frame, text="Descripcion", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_desc = ctk.CTkEntry(self.body_frame, placeholder_text="Detalle breve", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_desc.pack(fill="x", pady=(0, 10))

        if self.category_data:
            self.txt_name.insert(0, self.category_data.get("name", ""))
            self.txt_desc.insert(0, self.category_data.get("description", "") or "")
            kind = self.category_data.get("kind", "both")
            if kind == "income":
                self.cmb_kind.set("Solo Ingresos")
            elif kind == "expense":
                self.cmb_kind.set("Solo Gastos")
            else:
                self.cmb_kind.set("Ambos (Ingresos y Gastos)")

        ctk.CTkButton(
            self.footer_frame, 
            text="Cancelar", 
            fg_color="#e2edf9",
            text_color="#334155",
            hover_color="#cbd5e1",
            command=self.destroy
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            self.footer_frame, 
            text="Guardar", 
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#ffffff",
            command=self._save
        ).pack(side="right")

    def _save(self):
        name = self.txt_name.get().strip()
        desc = self.txt_desc.get().strip()
        kind_str = self.cmb_kind.get()

        kind = "both"
        if "Ingresos" in kind_str and "Ambos" not in kind_str:
            kind = "income"
        elif "Gastos" in kind_str and "Ambos" not in kind_str:
            kind = "expense"

        if not name:
            messagebox.showwarning("Atencion", "El nombre de la categoria es obligatorio.", parent=self)
            return

        if self.category_data:
            CategoryModel.update(self.category_data["id"], name, desc, kind)
        else:
            CategoryModel.create(name, desc, kind)

        if self.on_success:
            self.on_success()
        self.destroy()


class UserModal(BaseModal):
    """Modal para crear y editar usuarios del sistema."""

    def __init__(self, parent, user_data=None, on_success=None):
        title = "Editar Usuario" if user_data else "Nuevo Usuario"
        super().__init__(parent, title=title, width=440, height=480)
        self.user_data = user_data
        self.on_success = on_success
        self._build_form()

    def _build_form(self):
        ctk.CTkLabel(self.body_frame, text="Nombre completo *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_name = ctk.CTkEntry(self.body_frame, placeholder_text="Nombre", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_name.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.body_frame, text="Nombre de usuario *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_username = ctk.CTkEntry(self.body_frame, placeholder_text="usuario", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_username.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.body_frame, text="Correo electronico *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_email = ctk.CTkEntry(self.body_frame, placeholder_text="usuario@correo.com", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_email.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.body_frame, text="Contraseña", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.txt_password = ctk.CTkEntry(self.body_frame, placeholder_text="Contraseña segura", show="*", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942")
        self.txt_password.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.body_frame, text="Rol de Acceso", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e3a5f").pack(anchor="w", pady=(5, 2))
        self.cmb_role = ctk.CTkComboBox(self.body_frame, values=["admin - Administrador", "operator - Operador"], state="readonly", fg_color="#ffffff", border_color="#bfdbfe", text_color="#0f2942", dropdown_fg_color="#ffffff", dropdown_text_color="#0f2942", dropdown_hover_color="#e8f0fe")
        self.cmb_role.set("admin - Administrador")
        self.cmb_role.pack(fill="x", pady=(0, 10))

        if self.user_data:
            self.txt_name.insert(0, self.user_data.get("name", ""))
            self.txt_username.insert(0, self.user_data.get("username", ""))
            self.txt_email.insert(0, self.user_data.get("email", ""))
            role = self.user_data.get("role", "admin")
            self.cmb_role.set("admin - Administrador" if role == "admin" else "operator - Operador")

        ctk.CTkButton(
            self.footer_frame, 
            text="Cancelar", 
            fg_color="#e2edf9",
            text_color="#334155",
            hover_color="#cbd5e1",
            command=self.destroy
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            self.footer_frame, 
            text="Guardar Usuario", 
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#ffffff",
            command=self._save
        ).pack(side="right")

    def _save(self):
        name = self.txt_name.get().strip()
        username = self.txt_username.get().strip()
        email = self.txt_email.get().strip()
        password = self.txt_password.get().strip()
        role = "admin" if "admin" in self.cmb_role.get() else "operator"

        if not name or not username or not email:
            messagebox.showwarning("Atencion", "Los campos Nombre, Usuario y Correo son obligatorios.", parent=self)
            return

        if not self.user_data and not password:
            messagebox.showwarning("Atencion", "Debe asignar una contraseña para el nuevo usuario.", parent=self)
            return

        try:
            if self.user_data:
                UserModel.update(self.user_data["id"], name, "", username, email, password, role, 1)
            else:
                UserModel.create(name, "", username, email, password, role, 1)

            if self.on_success:
                self.on_success()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el usuario: {e}", parent=self)


class DetailModal(BaseModal):
    """Modal para ver la informacion detallada de cualquier registro (operacion, cuenta, contacto, usuario)."""

    def __init__(self, parent, title="Detalle del Registro", items=None, badge_text=None, badge_color="#2563eb"):
        super().__init__(parent, title=title, width=500, height=540)
        self.items = items or []
        self.badge_text = badge_text
        self.badge_color = badge_color
        self._build_content()

    def _build_content(self):
        if self.badge_text:
            badge = ctk.CTkLabel(
                self.body_frame,
                text=f"  {self.badge_text}  ",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.badge_color,
                text_color="#ffffff",
                corner_radius=8,
                height=28
            )
            badge.pack(anchor="w", pady=(0, 10))

        for key, value in self.items:
            card = ctk.CTkFrame(
                self.body_frame, 
                fg_color="#ffffff", 
                corner_radius=8, 
                border_width=1, 
                border_color="#dbe8f7"
            )
            card.pack(fill="x", pady=3)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                card, 
                text=key, 
                font=ctk.CTkFont(size=11, weight="bold"), 
                text_color="#57708e", 
                width=150, 
                anchor="w"
            ).grid(row=0, column=0, padx=12, pady=9, sticky="w")

            ctk.CTkLabel(
                card, 
                text=str(value if value not in [None, ""] else "—"), 
                font=ctk.CTkFont(size=12, weight="normal"), 
                text_color="#0f2942", 
                anchor="w", 
                wraplength=270,
                justify="left"
            ).grid(row=0, column=1, padx=(0, 12), pady=9, sticky="w")

        ctk.CTkButton(
            self.footer_frame,
            text="Cerrar",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#ffffff",
            width=90,
            corner_radius=8,
            command=self.destroy
        ).pack(side="right")
