import customtkinter as ctk
from models.user import UserModel
from utils.session import Session

class LoginView(ctk.CTkFrame):
    """Vista de inicio de sesion con estetica glassmorphism en tonos de azul suave."""

    def __init__(self, master, on_login_success=None, **kwargs):
        super().__init__(master, fg_color="#ebf2fc", **kwargs)
        self.on_login_success = on_login_success
        self._build_ui()

    def _build_ui(self):
        # Tarjeta central flotante con efecto cristal esmerilado blanco
        card = ctk.CTkFrame(
            self,
            width=420,
            corner_radius=18,
            border_width=1,
            border_color="#cde0f5",
            fg_color="#ffffff"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=35, pady=32, fill="both", expand=True)

        # 1. Cabecera con isotipo
        hdr_frame = ctk.CTkFrame(content, fg_color="transparent")
        hdr_frame.pack(fill="x", pady=(0, 15))

        logo_badge = ctk.CTkLabel(
            hdr_frame,
            text="IK",
            width=46,
            height=46,
            corner_radius=10,
            fg_color="#2563eb",
            text_color="#ffffff",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        logo_badge.pack(pady=(0, 8))

        lbl_app = ctk.CTkLabel(
            hdr_frame,
            text="IntelliKonta",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#0f2942"
        )
        lbl_app.pack()

        lbl_sub = ctk.CTkLabel(
            hdr_frame,
            text="Sistema de Gestión Financiera",
            font=ctk.CTkFont(size=12),
            text_color="#57708e"
        )
        lbl_sub.pack(pady=(2, 4))

        lbl_action = ctk.CTkLabel(
            hdr_frame,
            text="Iniciar Sesión",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#1e3a5f"
        )
        lbl_action.pack(pady=(8, 0))

        # 2. Formulario de acceso
        form_frame = ctk.CTkFrame(content, fg_color="transparent")
        form_frame.pack(fill="x", pady=(5, 10))

        # Campo: Usuario
        lbl_u = ctk.CTkLabel(
            form_frame,
            text="Usuario",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#1e3a5f"
        )
        lbl_u.pack(anchor="w", pady=(4, 2))

        self.txt_username = ctk.CTkEntry(
            form_frame,
            placeholder_text="admin",
            height=40,
            corner_radius=8,
            border_width=1,
            border_color="#bfdbfe",
            fg_color="#f8fbfe",
            text_color="#0f2942",
            font=ctk.CTkFont(size=13)
        )
        self.txt_username.pack(fill="x", pady=(0, 10))
        self.txt_username.bind("<Return>", lambda e: self.txt_password.focus_set())

        # Campo: Contraseña
        lbl_p = ctk.CTkLabel(
            form_frame,
            text="Contraseña",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#1e3a5f"
        )
        lbl_p.pack(anchor="w", pady=(4, 2))

        self.txt_password = ctk.CTkEntry(
            form_frame,
            placeholder_text="••••••••",
            show="*",
            height=40,
            corner_radius=8,
            border_width=1,
            border_color="#bfdbfe",
            fg_color="#f8fbfe",
            text_color="#0f2942",
            font=ctk.CTkFont(size=13)
        )
        self.txt_password.pack(fill="x", pady=(0, 4))
        self.txt_password.bind("<Return>", lambda e: self._submit())

        # Mensaje de error
        self.lbl_error = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ef4444",
            wraplength=340
        )
        self.lbl_error.pack(pady=(2, 6))

        # Boton de inicio
        self.btn_login = ctk.CTkButton(
            content,
            text="Ingresar al Sistema ➔",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#ffffff",
            command=self._submit
        )
        self.btn_login.pack(fill="x", pady=(4, 15))

        # 3. Caja informativa con credenciales por defecto
        tip_box = ctk.CTkFrame(
            content,
            corner_radius=8,
            border_width=1,
            border_color="#bfdbfe",
            fg_color="#eff6ff"
        )
        tip_box.pack(fill="x")

        lbl_tip_title = ctk.CTkLabel(
            tip_box,
            text="🔑 Credenciales de acceso por defecto:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#1e40af"
        )
        lbl_tip_title.pack(anchor="w", padx=12, pady=(8, 2))

        lbl_tip_body = ctk.CTkLabel(
            tip_box,
            text="Usuario: admin  |  Contraseña: admin",
            font=ctk.CTkFont(size=11),
            text_color="#2563eb"
        )
        lbl_tip_body.pack(anchor="w", padx=12, pady=(0, 8))

        # Enfocar campo de usuario
        self.txt_username.focus_set()

    def _submit(self):
        username = self.txt_username.get().strip()
        password = self.txt_password.get().strip()

        self.lbl_error.configure(text="")

        user, err_msg = UserModel.authenticate(username, password)
        if err_msg:
            self.lbl_error.configure(text=err_msg)
            return

        # Establecer sesion activa
        Session.login(user)

        if self.on_login_success:
            self.on_login_success(user)
