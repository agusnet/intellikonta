from database.db import get_connection, recalculate_account_balances
from datetime import datetime

class AccountModel:
    """Modelo para la administracion de cuentas bancarias y efectivo."""

    @staticmethod
    def get_all():
        recalculate_account_balances()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(account_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(name, description="", initial_balance=0.0):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO accounts (name, description, initial_balance, current_balance, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, initial_balance, initial_balance, now))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        recalculate_account_balances()
        return new_id

    @staticmethod
    def update(account_id, name, description, initial_balance):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE accounts SET name = ?, description = ?, initial_balance = ?
            WHERE id = ?
        """, (name, description, initial_balance, account_id))
        conn.commit()
        conn.close()
        recalculate_account_balances()

    @staticmethod
    def delete(account_id):
        conn = get_connection()
        cursor = conn.cursor()
        # Verificar si tiene operaciones asociadas
        cursor.execute("SELECT COUNT(*) as count FROM operations WHERE account_id = ?", (account_id,))
        if cursor.fetchone()["count"] > 0:
            conn.close()
            raise ValueError("No se puede eliminar la cuenta porque contiene movimientos registrados.")
        
        cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_summary(account_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as ops_count,
                COALESCE(SUM(CASE WHEN kind = 'income' THEN amount ELSE 0 END), 0.0) as total_in,
                COALESCE(SUM(CASE WHEN kind = 'expense' THEN amount ELSE 0 END), 0.0) as total_out
            FROM operations
            WHERE account_id = ?
        """, (account_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {"ops_count": 0, "total_in": 0.0, "total_out": 0.0}

    @staticmethod
    def get_total_balance():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(current_balance), 0.0) as total FROM accounts")
        res = cursor.fetchone()["total"]
        conn.close()
        return res
