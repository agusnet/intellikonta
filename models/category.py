from database.db import get_connection
from datetime import datetime

class CategoryModel:
    """Modelo para clasificacion de ingresos y gastos."""

    @staticmethod
    def get_all(kind=None):
        conn = get_connection()
        cursor = conn.cursor()
        if kind and kind != "all":
            cursor.execute("SELECT * FROM categories WHERE kind = ? OR kind = 'both' ORDER BY name ASC", (kind,))
        else:
            cursor.execute("SELECT * FROM categories ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create(name, description="", kind="both"):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO categories (name, description, kind, created_at)
            VALUES (?, ?, ?, ?)
        """, (name, description, kind, now))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def update(cat_id, name, description="", kind="both"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE categories SET name = ?, description = ?, kind = ?
            WHERE id = ?
        """, (name, description, kind, cat_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(cat_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()
        conn.close()


class PaymentMethodModel:
    """Modelo para formas de pago."""

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payment_methods ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create(name):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO payment_methods (name, created_at) VALUES (?, ?)", (name, now))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def update(method_id, name):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE payment_methods SET name = ? WHERE id = ?", (name, method_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(method_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM payment_methods WHERE id = ?", (method_id,))
        conn.commit()
        conn.close()
