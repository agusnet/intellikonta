import webbrowser
import customtkinter as ctk
from database.db import init_db
from utils.session import Session
from components.navbar import Navbar
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.operations_view import OperationsView
from views.accounts_view import AccountsView
from views.contacts_view import ContactsView
from views.categories_view import CategoriesView
from views.reports_view import ReportsView
from views.users_view import UsersView

class IntelliKontaApp(ctk.CTk):
    """Ventana principal de la aplicacion IntelliKonta."""

    def __init__(self):
        super().__init__()

        # Configuracion general de la ventana
        self.title("IntelliKonta - Sistema de Gestion Financiera")
        self.geometry("1200x760")
        self.minsize(1050, 680)

        # Inicializar base de datos SQLite
        init_db()

        # Contenedor superior (Menu / Navbar)
        self.navbar = Navbar(self, on_navigate_callback=self.navigate_to, on_logout_callback=self.logout)

        # Pie de aplicacion (Footer con Copyleft por AgusBot con fondo azul suave)
        self.footer = ctk.CTkFrame(
            self, 
            height=30, 
            fg_color="#dbe9f9", 
            border_width=1, 
            border_color="#c2daf5", 
            corner_radius=0
        )
        self.footer.pack(side="bottom", fill="x")

        footer_box = ctk.CTkFrame(self.footer, fg_color="transparent")
        footer_box.pack(pady=4)

        lbl_copyleft = ctk.CTkLabel(
            footer_box,
            text="🄯 Copyleft por AgusBot",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#1e3a5f"
        )
        lbl_copyleft.pack(side="left")

        lbl_separator = ctk.CTkLabel(
            footer_box,
            text=" • ",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        lbl_separator.pack(side="left")

        lbl_link = ctk.CTkLabel(
            footer_box,
            text="agusbot.com",
            font=ctk.CTkFont(size=11, weight="bold", underline=True),
            text_color="#2563eb",
            cursor="hand2"
        )
        lbl_link.pack(side="left")
        lbl_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://agusbot.com"))
        lbl_link.bind("<Enter>", lambda e: lbl_link.configure(text_color="#1d4ed8"))
        lbl_link.bind("<Leave>", lambda e: lbl_link.configure(text_color="#2563eb"))

        # Contenedor de vistas con fondo en tonos de azul bajo (#ebf2fc)
        self.container = ctk.CTkFrame(self, fg_color="#ebf2fc", corner_radius=0)
        self.container.pack(side="top", fill="both", expand=True)

        self.current_view = None

        # Mostrar pantalla de inicio de sesion por defecto
        if Session.is_logged_in():
            self._show_main_app()
        else:
            self.show_login()

    def show_login(self):
        """Muestra la pantalla de inicio de sesion y oculta el navbar."""
        if self.navbar.winfo_ismapped():
            self.navbar.pack_forget()

        if self.current_view is not None:
            self.current_view.destroy()

        self.current_view = LoginView(self.container, on_login_success=self._on_login_success)
        self.current_view.pack(fill="both", expand=True)

    def _on_login_success(self, user_dict):
        """Maneja el acceso exitoso desde el Login."""
        self._show_main_app()

    def _show_main_app(self):
        """Configura la interfaz con navbar y carga el Dashboard inicial."""
        self.container.pack_forget()
        self.navbar.pack(side="top", fill="x")
        self.navbar.refresh_user()
        self.container.pack(side="top", fill="both", expand=True)

        self.navigate_to("dashboard")

    def logout(self):
        """Cierra la sesion del usuario y regresa a la pantalla de Login."""
        Session.logout()
        self.show_login()

    def navigate_to(self, view_name):
        """Cambia la vista activa segun el modulo seleccionado en el menu."""
        # Limpiar vista anterior
        if self.current_view is not None:
            self.current_view.destroy()

        # Actualizar boton activo en la barra superior
        self.navbar.set_active(view_name)

        # Instanciar el modulo correspondiente
        if view_name == "dashboard":
            self.current_view = DashboardView(self.container, on_navigate_callback=self.navigate_to)
        elif view_name == "ingresos":
            self.current_view = OperationsView(self.container, kind="income")
        elif view_name == "gastos":
            self.current_view = OperationsView(self.container, kind="expense")
        elif view_name == "cuentas":
            self.current_view = AccountsView(self.container)
        elif view_name == "contactos":
            self.current_view = ContactsView(self.container)
        elif view_name == "categorias":
            self.current_view = CategoriesView(self.container)
        elif view_name == "reportes":
            self.current_view = ReportsView(self.container)
        elif view_name == "usuarios":
            self.current_view = UsersView(self.container)
        else:
            self.current_view = DashboardView(self.container, on_navigate_callback=self.navigate_to)

        self.current_view.pack(fill="both", expand=True)


if __name__ == "__main__":
    # Eliminamos el tema oscuro: se fija la apariencia en modo claro con tonos de azul bajo
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    app = IntelliKontaApp()
    app.mainloop()
