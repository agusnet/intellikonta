import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "intellikonta.db")

def get_connection():
    """Retorna una conexion activa a la base de datos SQLite."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Crea las tablas de la base de datos si no existen y carga datos iniciales."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        lastname TEXT DEFAULT '',
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'admin', -- 'admin', 'operator', 'viewer'
        status INTEGER NOT NULL DEFAULT 1,  -- 1 activo, 0 inactivo
        created_at TEXT NOT NULL
    );
    """)

    # Tabla de cuentas financieras (bancos, efectivo, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        initial_balance REAL NOT NULL DEFAULT 0.0,
        current_balance REAL NOT NULL DEFAULT 0.0,
        created_at TEXT NOT NULL
    );
    """)

    # Tabla de categorias (ingreso, gasto o ambos)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        kind TEXT NOT NULL DEFAULT 'both', -- 'income', 'expense', 'both'
        created_at TEXT NOT NULL
    );
    """)

    # Tabla de metodos de pago
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # Tabla de contactos (clientes, proveedores)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        lastname TEXT DEFAULT '',
        company TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        address TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    """)

    # Tabla de operaciones (ingresos y gastos)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concept TEXT NOT NULL,
        description TEXT DEFAULT '',
        amount REAL NOT NULL,
        date_at TEXT NOT NULL,            -- YYYY-MM-DD
        kind TEXT NOT NULL,               -- 'income' o 'expense'
        category_id INTEGER,
        contact_id INTEGER,
        account_id INTEGER NOT NULL,
        paymethod_id INTEGER,
        user_id INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE RESTRICT,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
        FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
        FOREIGN KEY (paymethod_id) REFERENCES payment_methods(id) ON DELETE SET NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # Tabla de configuracion
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    # Migracion/Ajuste de contrasena default para usuario admin
    cursor.execute("UPDATE users SET password = 'admin' WHERE username = 'admin' AND password = 'admin123'")
    conn.commit()

    # Insertar datos por defecto si la base de datos esta vacia
    _seed_initial_data(cursor, conn)

    conn.close()

def _seed_initial_data(cursor, conn):
    """Inserta datos por defecto para el primer arranque."""
    # Usuario por defecto (admin / admin)
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()["count"] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO users (name, lastname, username, email, password, role, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Administrador", "Principal", "admin", "admin@intellikonta.com", "admin", "admin", 1, now))

    # Cuentas por defecto
    cursor.execute("SELECT COUNT(*) as count FROM accounts")
    if cursor.fetchone()["count"] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        accounts_data = [
            ("Mi Cartera / Efectivo", "Efectivo disponible en caja", 2500.0, 2500.0, now),
            ("Banco BBVA", "Cuenta de cheques y transferencias", 18500.0, 18500.0, now),
            ("Banco Santander", "Cuenta de ahorros e inversiones", 32000.0, 32000.0, now)
        ]
        cursor.executemany("""
        INSERT INTO accounts (name, description, initial_balance, current_balance, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, accounts_data)

    # Categorias por defecto
    cursor.execute("SELECT COUNT(*) as count FROM categories")
    if cursor.fetchone()["count"] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cat_data = [
            ("Ventas / Servicios", "Ingresos por ventas o servicios profesionales", "income", now),
            ("Cobros / Honorarios", "Cobros varios y honorarios", "income", now),
            ("Otros Ingresos", "Rendimientos o ingresos extraordinarios", "income", now),
            ("Alimentacion", "Gastos en comida y despensa", "expense", now),
            ("Transporte y Combustible", "Transporte publico, gasolina y peajes", "expense", now),
            ("Servicios y Renta", "Luz, agua, internet, renta de local u oficina", "expense", now),
            ("Nomina y Personal", "Pago a colaboradores y salarios", "expense", now),
            ("Publicidad y Marketing", "Campanas y promocion", "expense", now),
            ("Otros Gastos", "Gastos varios no categorizados", "expense", now)
        ]
        cursor.executemany("""
        INSERT INTO categories (name, description, kind, created_at)
        VALUES (?, ?, ?, ?)
        """, cat_data)

    # Metodos de pago por defecto
    cursor.execute("SELECT COUNT(*) as count FROM payment_methods")
    if cursor.fetchone()["count"] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        methods = [
            ("Efectivo", now),
            ("Transferencia Bancaria (SPEI)", now),
            ("Tarjeta de Debito/Credito", now),
            ("Cheque", now),
            ("PayPal", now)
        ]
        cursor.executemany("""
        INSERT INTO payment_methods (name, created_at)
        VALUES (?, ?)
        """, methods)

    # Contactos de ejemplo
    cursor.execute("SELECT COUNT(*) as count FROM contacts")
    if cursor.fetchone()["count"] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        contacts_data = [
            ("Juan", "Perez", "Soluciones Digitales SA", "5512345678", "juan@digitales.com", "Av. Insurgentes 123", "Cliente recurrente", now),
            ("Maria", "Gonzalez", "Distribuidora del Norte", "5598765432", "maria@distribuidora.com", "Calle Reforma 45", "Proveedor de insumos", now),
            ("Carlos", "Hernandez", "Consultoria MX", "5555551234", "carlos@consultoriamx.com", "Av. Juarez 80", "Cliente de consultoria", now)
        ]
        cursor.executemany("""
        INSERT INTO contacts (name, lastname, company, phone, email, address, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, contacts_data)

    # Operaciones de ejemplo si esta vacio
    cursor.execute("SELECT COUNT(*) as count FROM operations")
    if cursor.fetchone()["count"] == 0:
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ops = [
            ("Desarrollo de Software Web", "Primer anticipo del proyecto", 12500.0, today, "income", 1, 1, 2, 2, 1, now),
            ("Consultoria Financiera", "Pago por asesoria contable", 4500.0, today, "income", 2, 3, 2, 2, 1, now),
            ("Pago de Renta Oficina", "Mensualidad de oficina corporativa", 6000.0, today, "expense", 6, 2, 2, 2, 1, now),
            ("Servicio de Internet y Telefonia", "Factura de fibra optica", 899.0, today, "expense", 6, 2, 1, 1, 1, now),
            ("Combustible semana", "Gasolina para vehiculo de reparto", 650.0, today, "expense", 5, 2, 1, 1, 1, now)
        ]
        cursor.executemany("""
        INSERT INTO operations (concept, description, amount, date_at, kind, category_id, contact_id, account_id, paymethod_id, user_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ops)

    # Configuraciones basicas
    cursor.execute("SELECT COUNT(*) as count FROM settings")
    if cursor.fetchone()["count"] == 0:
        settings = [
            ("company_name", "IntelliKonta S.A. de C.V."),
            ("currency_symbol", "$"),
            ("tax_id", "XAXX010101000"),
            ("phone", "+52 55 1234 5678"),
            ("email", "contacto@intellikonta.com"),
            ("address", "Ciudad de Mexico, Mexico")
        ]
        cursor.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", settings)

    conn.commit()
    # Recalcular saldos de cuentas con base en balance inicial + ingresos - gastos
    recalculate_account_balances(conn)

def recalculate_account_balances(conn=None):
    """Recalcula el saldo actual de cada cuenta a partir del saldo inicial y sus operaciones."""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    cursor = conn.cursor()
    cursor.execute("SELECT id, initial_balance FROM accounts")
    accounts = cursor.fetchall()

    for acc in accounts:
        acc_id = acc["id"]
        init_bal = acc["initial_balance"]

        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN kind = 'income' THEN amount ELSE 0 END), 0) as total_in,
                COALESCE(SUM(CASE WHEN kind = 'expense' THEN amount ELSE 0 END), 0) as total_out
            FROM operations
            WHERE account_id = ?
        """, (acc_id,))
        totals = cursor.fetchone()
        current_balance = init_bal + totals["total_in"] - totals["total_out"]

        cursor.execute("UPDATE accounts SET current_balance = ? WHERE id = ?", (current_balance, acc_id))

    conn.commit()
    if should_close:
        conn.close()
