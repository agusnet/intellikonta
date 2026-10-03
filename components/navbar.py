import customtkinter as ctk
from utils.session import Session

class Navbar(ctk.CTkFrame):
    """Barra de navegacion superior compacta para visualizacion completa de opciones."""

    def __init__(self, master, on_navigate_callback, on_logout_callback=None, **kwargs):
        super().__init__(
            master, 
            height=58, 
            corner_radius=0, 
            fg_color="#070a13", 
            border_width=1, 
            border_color="#182338",
            **kwargs
        )
        self.on_navigate = on_navigate_callback
        self.on_logout = on_logout_callback
        self.buttons = {}
        self.active_module = None

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)

        # 1. Logo y Nombre de Marca
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=(14, 10), pady=10, sticky="w")

        logo_badge = ctk.CTkLabel(
            brand_frame, 
            text="IK", 
            width=30, 
            height=30, 
            corner_radius=8, 
            fg_color="#2563eb", 
            text_color="#ffffff", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        logo_badge.pack(side="left", padx=(0, 8))

        title_label = ctk.CTkLabel(
            brand_frame, 
            text="IntelliKonta", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f8fafc"
        )
        title_label.pack(side="left")

        # 2. Botones de navegacion compactos (width=0 para ajustar al texto exacto)
        nav_items_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_items_frame.grid(row=0, column=1, sticky="w", padx=2)

        modules = [
            ("dashboard", "Dashboard"),
            ("ingresos", "Ingresos"),
            ("gastos", "Gastos"),
            ("cuentas", "Cuentas"),
            ("contactos", "Contactos"),
            ("categorias", "Categorias"),
            ("reportes", "Reportes"),
            ("usuarios", "Usuarios"),
        ]

        for mod_id, label in modules:
            btn = ctk.CTkButton(
                nav_items_frame,
                text=label,
                font=ctk.CTkFont(size=12, weight="normal"),
                width=0, # Auto-ajuste de ancho compacto segun el texto
                height=32,
                corner_radius=7,
                fg_color="transparent",
                text_color="#94a3b8",
                hover_color="#172238",
                command=lambda m=mod_id: self._handle_click(m)
            )
            btn.pack(side="left", padx=2)
            self.buttons[mod_id] = btn

        # 3. Informacion de usuario y boton cerrar sesion
        right_frame = ctk.CTkFrame(
            self, 
            corner_radius=8, 
            fg_color="#10192b", 
            border_width=1, 
            border_color="#1e2e4a"
        )
        right_frame.grid(row=0, column=2, padx=(5, 14), pady=10, sticky="e")

        self.user_lbl = ctk.CTkLabel(
            right_frame,
            text=f"👤 {Session.get_full_name()}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#93c5fd"
        )
        self.user_lbl.pack(side="left", padx=(10, 8), pady=5)

        btn_logout = ctk.CTkButton(
            right_frame,
            text="Salir 🚪",
            width=58,
            height=26,
            corner_radius=6,
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff",
            command=self._handle_logout
        )
        btn_logout.pack(side="left", padx=(0, 6), pady=5)

    def refresh_user(self):
        """Actualiza el nombre de usuario mostrado en la barra."""
        self.user_lbl.configure(text=f"👤 {Session.get_full_name()}")

    def set_active(self, module_id):
        """Marca el boton del modulo activo con azul vibrante."""
        self.active_module = module_id
        for m_id, btn in self.buttons.items():
            if m_id == module_id:
                btn.configure(
                    fg_color="#2563eb",
                    text_color="#ffffff",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#94a3b8",
                    font=ctk.CTkFont(size=12, weight="normal")
                )

    def _handle_click(self, module_id):
        self.set_active(module_id)
        if self.on_navigate:
            self.on_navigate(module_id)

    def _handle_logout(self):
        from tkinter import messagebox
        if messagebox.askyesno("Cerrar Sesión", "¿Deseas cerrar la sesión activa?", parent=self.winfo_toplevel()):
            if self.on_logout:
                self.on_logout()
