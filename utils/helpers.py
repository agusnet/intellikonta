from datetime import datetime

def format_currency(amount, symbol="$"):
    """Formatea un valor flotante o entero como moneda, ej: $ 1,500.00"""
    try:
        val = float(amount or 0.0)
        return f"{symbol} {val:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol} 0.00"

def get_today_str():
    """Retorna la fecha actual en formato YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")

def format_date(date_val):
    """Devuelve la fecha limpia YYYY-MM-DD."""
    if not date_val:
        return ""
    if isinstance(date_val, datetime):
        return date_val.strftime("%Y-%m-%d")
    return str(date_val)[:10]

def parse_float(val, default=0.0):
    """Convierte texto a float de forma segura."""
    try:
        clean = str(val).replace("$", "").replace(",", "").strip()
        return float(clean)
    except (ValueError, TypeError):
        return default
