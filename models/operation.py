from database.db import get_connection, recalculate_account_balances
from datetime import datetime

class OperationModel:
    """Modelo para ingresos y gastos financieros."""

    @staticmethod
    def create(concept, amount, date_at, kind, account_id, category_id=None, contact_id=None, paymethod_id=None, user_id=None, description=""):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO operations (
                concept, description, amount, date_at, kind,
                category_id, contact_id, account_id, paymethod_id, user_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (concept, description, float(amount), date_at, kind, category_id, contact_id, account_id, paymethod_id, user_id, now))

        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        recalculate_account_balances()
        return new_id

    @staticmethod
    def update(op_id, concept, amount, date_at, kind, account_id, category_id=None, contact_id=None, paymethod_id=None, user_id=None, description=""):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE operations SET
                concept = ?, description = ?, amount = ?, date_at = ?, kind = ?,
                account_id = ?, category_id = ?, contact_id = ?, paymethod_id = ?, user_id = ?
            WHERE id = ?
        """, (concept, description, float(amount), date_at, kind, account_id, category_id, contact_id, paymethod_id, user_id, op_id))

        conn.commit()
        conn.close()
        recalculate_account_balances()

    @staticmethod
    def delete(op_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM operations WHERE id = ?", (op_id,))
        conn.commit()
        conn.close()
        recalculate_account_balances()

    @staticmethod
    def get_by_id(op_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, 
                   c.name as category_name,
                   co.name || ' ' || co.lastname as contact_name,
                   a.name as account_name,
                   p.name as paymethod_name,
                   u.name as user_name
            FROM operations o
            LEFT JOIN categories c ON o.category_id = c.id
            LEFT JOIN contacts co ON o.contact_id = co.id
            LEFT JOIN accounts a ON o.account_id = a.id
            LEFT JOIN payment_methods p ON o.paymethod_id = p.id
            LEFT JOIN users u ON o.user_id = u.id
            WHERE o.id = ?
        """, (op_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all(kind=None, start_date=None, end_date=None, account_id=None, category_id=None, contact_id=None, search=None, limit=None):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT o.*, 
                   COALESCE(c.name, 'Sin Categoria') as category_name,
                   COALESCE(co.name || ' ' || co.lastname, 'General') as contact_name,
                   a.name as account_name,
                   COALESCE(p.name, 'N/A') as paymethod_name,
                   COALESCE(u.name, 'Sistema') as user_name
            FROM operations o
            LEFT JOIN categories c ON o.category_id = c.id
            LEFT JOIN contacts co ON o.contact_id = co.id
            LEFT JOIN accounts a ON o.account_id = a.id
            LEFT JOIN payment_methods p ON o.paymethod_id = p.id
            LEFT JOIN users u ON o.user_id = u.id
            WHERE 1=1
        """
        params = []

        if kind and kind != "all":
            query += " AND o.kind = ?"
            params.append(kind)

        if start_date:
            query += " AND o.date_at >= ?"
            params.append(start_date)

        if end_date:
            query += " AND o.date_at <= ?"
            params.append(end_date)

        if account_id and str(account_id) != "all":
            query += " AND o.account_id = ?"
            params.append(account_id)

        if category_id and str(category_id) != "all":
            query += " AND o.category_id = ?"
            params.append(category_id)

        if contact_id and str(contact_id) != "all":
            query += " AND o.contact_id = ?"
            params.append(contact_id)

        if search and search.strip():
            query += " AND (o.concept LIKE ? OR o.description LIKE ?)"
            s = f"%{search.strip()}%"
            params.extend([s, s])

        query += " ORDER BY o.date_at DESC, o.id DESC"

        if limit:
            query += f" LIMIT {int(limit)}"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_summary(start_date=None, end_date=None, account_id=None):
        """Retorna totales de ingresos, gastos y balance neto."""
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                COALESCE(SUM(CASE WHEN kind = 'income' THEN amount ELSE 0 END), 0.0) as total_income,
                COALESCE(SUM(CASE WHEN kind = 'expense' THEN amount ELSE 0 END), 0.0) as total_expense
            FROM operations
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND date_at >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date_at <= ?"
            params.append(end_date)
        if account_id and str(account_id) != "all":
            query += " AND account_id = ?"
            params.append(account_id)

        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()

        income = row["total_income"] if row else 0.0
        expense = row["total_expense"] if row else 0.0
        net = income - expense

        return {
            "income": income,
            "expense": expense,
            "net": net
        }

    @staticmethod
    def get_category_summary(kind="expense", start_date=None, end_date=None):
        """Retorna el agrupado por categorias con su suma de montos."""
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                COALESCE(c.name, 'Sin Categoria') as category_name,
                SUM(o.amount) as total_amount,
                COUNT(o.id) as operation_count
            FROM operations o
            LEFT JOIN categories c ON o.category_id = c.id
            WHERE o.kind = ?
        """
        params = [kind]

        if start_date:
            query += " AND o.date_at >= ?"
            params.append(start_date)
        if end_date:
            query += " AND o.date_at <= ?"
            params.append(end_date)

        query += " GROUP BY category_name ORDER BY total_amount DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
