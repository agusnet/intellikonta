from database.db import get_connection
from datetime import datetime

class ContactModel:
    """Modelo para directorio de contactos (clientes y proveedores)."""

    @staticmethod
    def get_all(search_term=None):
        conn = get_connection()
        cursor = conn.cursor()
        if search_term and search_term.strip():
            term = f"%{search_term.strip()}%"
            cursor.execute("""
                SELECT * FROM contacts 
                WHERE name LIKE ? OR lastname LIKE ? OR company LIKE ? OR phone LIKE ? OR email LIKE ?
                ORDER BY name ASC
            """, (term, term, term, term, term))
        else:
            cursor.execute("SELECT * FROM contacts ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(contact_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(name, lastname="", company="", phone="", email="", address="", notes=""):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO contacts (name, lastname, company, phone, email, address, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, lastname, company, phone, email, address, notes, now))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def update(contact_id, name, lastname="", company="", phone="", email="", address="", notes=""):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts 
            SET name = ?, lastname = ?, company = ?, phone = ?, email = ?, address = ?, notes = ?
            WHERE id = ?
        """, (name, lastname, company, phone, email, address, notes, contact_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(contact_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_summary(contact_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as ops_count,
                COALESCE(SUM(CASE WHEN kind = 'income' THEN amount ELSE 0 END), 0.0) as total_in,
                COALESCE(SUM(CASE WHEN kind = 'expense' THEN amount ELSE 0 END), 0.0) as total_out
            FROM operations
            WHERE contact_id = ?
        """, (contact_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {"ops_count": 0, "total_in": 0.0, "total_out": 0.0}
