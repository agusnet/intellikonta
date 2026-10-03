import customtkinter as ctk

class StatCard(ctk.CTkFrame):
    """Tarjeta con efecto glassmorfismo en tonos de azul bajo y blanco esmerilado."""

    def __init__(self, master, title, value, subtitle="", accent_color="#2563eb", **kwargs):
        super().__init__(
            master, 
            corner_radius=14, 
            border_width=1, 
            border_color="#cde0f5", 
            fg_color="#ffffff",
            **kwargs
        )

        self.grid_columnconfigure(1, weight=1)
        
        # Barra lateral con color de acento
        self.bar = ctk.CTkFrame(self, width=5, corner_radius=3, fg_color=accent_color)
        self.bar.grid(row=0, column=0, rowspan=3, sticky="nsw", padx=(8, 10), pady=10)

        # Titulo con tono azul grisaceo suave
        self.lbl_title = ctk.CTkLabel(
            self, 
            text=title.upper(), 
            font=ctk.CTkFont(size=11, weight="bold"), 
            text_color="#57708e"
        )
        self.lbl_title.grid(row=0, column=1, sticky="w", padx=(0, 15), pady=(12, 0))

        # Valor numerico destacado en azul oscuro legible
        self.lbl_value = ctk.CTkLabel(
            self, 
            text=value, 
            font=ctk.CTkFont(size=21, weight="bold"), 
            text_color="#0f2942"
        )
        self.lbl_value.grid(row=1, column=1, sticky="w", padx=(0, 15), pady=(2, 2))

        # Subtitulo
        self.lbl_sub = ctk.CTkLabel(
            self, 
            text=subtitle, 
            font=ctk.CTkFont(size=11), 
            text_color="#738a9c"
        )
        self.lbl_sub.grid(row=2, column=1, sticky="w", padx=(0, 15), pady=(0, 12))

    def update_value(self, new_value, new_sub=None):
        self.lbl_value.configure(text=new_value)
        if new_sub is not None:
            self.lbl_sub.configure(text=new_sub)
