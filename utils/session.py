class Session:
    """Gestiona la sesion del usuario activo en la aplicacion."""
    _current_user = None

    @classmethod
    def login(cls, user_dict):
        """Inicia sesion con el diccionario de usuario provisto."""
        cls._current_user = user_dict

    @classmethod
    def logout(cls):
        """Cierra la sesion activa."""
        cls._current_user = None

    @classmethod
    def is_logged_in(cls):
        """Verifica si existe un usuario autenticado."""
        return cls._current_user is not None

    @classmethod
    def get_current_user(cls):
        return cls._current_user

    @classmethod
    def set_current_user(cls, user_dict):
        cls._current_user = user_dict

    @classmethod
    def get_user_id(cls):
        return cls._current_user.get("id", 1) if cls._current_user else 1

    @classmethod
    def get_username(cls):
        return cls._current_user.get("username", "admin") if cls._current_user else "admin"

    @classmethod
    def get_full_name(cls):
        if not cls._current_user:
            return "Invitado"
        full = f"{cls._current_user.get('name', '')} {cls._current_user.get('lastname', '')}".strip()
        return full or cls._current_user.get("username", "Usuario")
