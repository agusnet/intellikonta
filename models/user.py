from database.db import get_connection
from datetime import datetime

class UserModel:
    """Modelo para la gestion de usuarios del sistema."""

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, lastname, username, email, role, status, created_at FROM users ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def authenticate(username, password):
        """Valida credenciales de acceso de un usuario."""
        u_clean = username.strip() if username else ""
        p_clean = password.strip() if password else ""
        if not u_clean or not p_clean:
            return None, "Por favor ingrese usuario y contraseña."

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (u_clean, p_clean))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None, "Usuario o contraseña incorrectos."

        user = dict(row)
        if user.get("status") != 1:
            return None, "Este usuario se encuentra inactivo. Contacte al administrador."

        return user, None

    @staticmethod
    def create(name, lastname, username, email, password, role="admin", status=1):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO users (name, lastname, username, email, password, role, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, lastname, username, email, password, role, status, now))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def update(user_id, name, lastname, username, email, password=None, role="admin", status=1):
        conn = get_connection()
        cursor = conn.cursor()
        if password and password.strip():
            cursor.execute("""
                UPDATE users SET name = ?, lastname = ?, username = ?, email = ?, password = ?, role = ?, status = ?
                WHERE id = ?
            """, (name, lastname, username, email, password, role, status, user_id))
        else:
            cursor.execute("""
                UPDATE users SET name = ?, lastname = ?, username = ?, email = ?, role = ?, status = ?
                WHERE id = ?
            """, (name, lastname, username, email, role, status, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
