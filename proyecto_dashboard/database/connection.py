"""
Gestión de conexión centralizada a la base de datos SQLite.
"""
import sqlite3
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """
    Retorna una conexión activa a SQLite con row_factory habilitado
    para acceso a columnas por nombre.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
