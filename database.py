import os
import sqlite3
import bcrypt
import pandas as pd

# Ruta absoluta a la base de datos para garantizar portabilidad
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mesa_ayuda.db")


def get_connection() -> sqlite3.Connection:
    """Retorna una conexión a la base de datos SQLite con row_factory habilitado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    """
    Inicializa y migra la base de datos al esquema corporativo.
    Esquema de usuarios_sistema:
        (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, rol TEXT)
    Garantiza la presencia de usuarios seed como 'hamui' (Administrador).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Comprobar tabla usuarios_sistema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios_sistema'")
    existe_tabla = cursor.fetchone() is not None

    if existe_tabla:
        columnas = [col["name"] for col in cursor.execute("PRAGMA table_info(usuarios_sistema)").fetchall()]
        if "nombre_completo" in columnas or "rol" not in columnas:
            cursor.execute("""
                CREATE TABLE usuarios_sistema_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    rol TEXT NOT NULL
                )
            """)
            cursor.execute("""
                INSERT INTO usuarios_sistema_new (id, username, password_hash, rol)
                SELECT id, username, password_hash,
                       CASE 
                           WHEN LOWER(username) IN ('admin', 'hamui') THEN 'Administrador'
                           ELSE 'Técnico'
                       END
                FROM usuarios_sistema
            """)
            cursor.execute("DROP TABLE usuarios_sistema")
            cursor.execute("ALTER TABLE usuarios_sistema_new RENAME TO usuarios_sistema")
            conn.commit()
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL
            )
        """)
        conn.commit()

    # 2. Garantizar usuarios seed requeridos
    usuarios_seed = [
        ("hamui", "hamui123", "Administrador"),
        ("admin", "admin123", "Administrador"),
        ("soporte", "soporte123", "Técnico"),
        ("Mirko", "Mirko123", "Técnico"),
    ]

    for uname, pwd, rol in usuarios_seed:
        cursor.execute("SELECT id, rol FROM usuarios_sistema WHERE LOWER(username) = LOWER(?)", (uname,))
        usuario_existente = cursor.fetchone()
        if not usuario_existente:
            p_hash = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute(
                "INSERT INTO usuarios_sistema (username, password_hash, rol) VALUES (?, ?, ?)",
                (uname, p_hash, rol),
            )
        else:
            # Normalizar formato de rol
            if usuario_existente["rol"] != rol:
                cursor.execute(
                    "UPDATE usuarios_sistema SET rol = ? WHERE id = ?",
                    (rol, usuario_existente["id"]),
                )

    conn.commit()
    conn.close()


def validar_credenciales(username: str, password: str) -> tuple[bool, str | None]:
    """
    Valida credenciales contra la tabla usuarios_sistema.
    Retorna (True, rol) si es válido, (False, None) si es inválido.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash, rol FROM usuarios_sistema WHERE LOWER(username) = LOWER(?)",
        (username.strip(),),
    )
    fila = cursor.fetchone()
    conn.close()

    if fila is None:
        return False, None

    password_hash_guardado = fila["password_hash"]
    rol = fila["rol"]

    try:
        coincide = bcrypt.checkpw(password.encode("utf-8"), password_hash_guardado.encode("utf-8"))
    except Exception:
        coincide = False

    return (True, rol) if coincide else (False, None)


def crear_usuario(username: str, password: str, rol: str = "Técnico") -> bool:
    """Registra un nuevo usuario en la base de datos con contraseña hasheada y rol."""
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios_sistema (username, password_hash, rol) VALUES (?, ?, ?)",
            (username.strip(), password_hash, rol.strip()),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def cambiar_password(username: str, password_nueva: str) -> bool:
    """Actualiza la contraseña de un usuario existente."""
    password_hash = bcrypt.hashpw(password_nueva.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios_sistema SET password_hash = ? WHERE LOWER(username) = LOWER(?)",
        (password_hash, username.strip()),
    )
    conn.commit()
    filas = cursor.rowcount
    conn.close()
    return filas > 0


def listar_usuarios() -> list[dict]:
    """Retorna la lista de usuarios del sistema con sus roles formales."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, rol FROM usuarios_sistema ORDER BY id ASC")
    filas = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return filas


# ---------------------------------------------------------------------------
# Consultas SQL Analíticas para Dashboard ITSM / GLPI (Niveles 1, 2 y 3)
# ---------------------------------------------------------------------------

def obtener_kpis_superiores() -> dict:
    """
    Retorna métricas consolidadas para las tarjetas superiores estilo GLPI:
      - Total de Casos (azul institucional)
      - En Proceso / Abiertos (celeste / cyan)
      - Vencidos / Críticos (rojo / coral)
      - Eficiencia SLA / Resueltos en SLA (verde esmeralda)
    """
    sql = """
    SELECT 
        COUNT(t.id) AS total_casos,
        SUM(CASE WHEN t.estado = 'abierto' THEN 1 ELSE 0 END) AS en_proceso,
        SUM(CASE WHEN t.estado = 'cerrado' THEN 1 ELSE 0 END) AS cerrados,
        SUM(CASE 
            WHEN (t.estado = 'cerrado' AND (julianday(t.fecha_cierre) - julianday(t.fecha_apertura))*24.0 > t.sla_horas)
                 OR (t.estado = 'abierto' AND (julianday('now', 'localtime') - julianday(t.fecha_apertura))*24.0 > t.sla_horas)
            THEN 1 ELSE 0 END
        ) AS vencidos,
        SUM(CASE 
            WHEN t.estado = 'cerrado' AND (julianday(t.fecha_cierre) - julianday(t.fecha_apertura))*24.0 <= t.sla_horas
            THEN 1 ELSE 0 END
        ) AS cerrados_a_tiempo
    FROM tickets t
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    conn.close()

    if row:
        total = row["total_casos"] or 0
        en_proceso = row["en_proceso"] or 0
        cerrados = row["cerrados"] or 0
        vencidos = row["vencidos"] or 0
        cerrados_a_tiempo = row["cerrados_a_tiempo"] or 0
        
        # Cumplimiento global dentro de SLA
        dentro_sla = total - vencidos
        eficiencia_pct = round((dentro_sla / total * 100.0), 1) if total > 0 else 100.0

        return {
            "total_casos": total,
            "en_proceso": en_proceso,
            "cerrados": cerrados,
            "vencidos": vencidos,
            "cerrados_a_tiempo": cerrados_a_tiempo,
            "eficiencia_sla": f"{eficiencia_pct}%",
        }

    return {
        "total_casos": 0,
        "en_proceso": 0,
        "cerrados": 0,
        "vencidos": 0,
        "cerrados_a_tiempo": 0,
        "eficiencia_sla": "100.0%",
    }


def obtener_metricas_departamentos() -> pd.DataFrame:
    """
    Nivel 1: Departamentos
    Consulta SQL que agrupa por departamento y computa mediante CASE WHEN:
      - Total de tickets
      - Tickets abiertos (en curso)
      - Tickets cerrados (resueltos)
      - Estado de semáforo ('VERDE', 'AMARILLO', 'ROJO')
    """
    sql = """
    SELECT 
        d.id,
        d.nombre,
        COUNT(t.id) AS total_tickets,
        SUM(CASE WHEN t.estado = 'abierto' THEN 1 ELSE 0 END) AS tickets_abiertos,
        SUM(CASE WHEN t.estado = 'cerrado' THEN 1 ELSE 0 END) AS tickets_cerrados,
        CASE 
            WHEN SUM(CASE 
                WHEN t.id IS NOT NULL AND (
                    (t.estado = 'cerrado' AND (julianday(t.fecha_cierre) - julianday(t.fecha_apertura))*24.0 > t.sla_horas)
                    OR
                    (t.estado = 'abierto' AND (julianday('now', 'localtime') - julianday(t.fecha_apertura))*24.0 > t.sla_horas)
                ) THEN 1 ELSE 0 END) > 0 THEN 'ROJO'
            WHEN SUM(CASE 
                WHEN t.id IS NOT NULL AND t.estado = 'abierto' 
                    AND (julianday('now', 'localtime') - julianday(t.fecha_apertura))*24.0 <= t.sla_horas
                    AND (t.sla_horas - (julianday('now', 'localtime') - julianday(t.fecha_apertura))*24.0) < 0.20 * t.sla_horas
                THEN 1 ELSE 0 END) > 0 THEN 'AMARILLO'
            ELSE 'VERDE'
        END AS semaforo
    FROM departamentos d
    LEFT JOIN tecnicos tec ON tec.departamento_id = d.id
    LEFT JOIN tickets t ON t.tecnico_id = tec.id
    GROUP BY d.id, d.nombre
    ORDER BY d.nombre ASC
    """
    conn = get_connection()
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


def obtener_departamento_por_id(departamento_id: int) -> dict | None:
    """Retorna los datos de un departamento específico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM departamentos WHERE id = ?", (departamento_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def obtener_tecnicos_por_departamento(departamento_id: int) -> pd.DataFrame:
    """
    Nivel 2: Técnicos por Departamento
    Consulta SQL que agrupa por técnico del departamento seleccionado y computa:
      - Total de tickets asignados
      - Tickets abiertos
      - Tickets cerrados
      - Estado de semáforo ('VERDE', 'AMARILLO', 'ROJO')
    """
    sql = """
    SELECT 
        tec.id,
        tec.nombre,
        tec.departamento_id,
        d.nombre AS departamento_nombre,
        COUNT(t.id) AS total_tickets,
        SUM(CASE WHEN t.estado = 'abierto' THEN 1 ELSE 0 END) AS tickets_abiertos,
        SUM(CASE WHEN t.estado = 'cerrado' THEN 1 ELSE 0 END) AS tickets_cerrados,
        CASE 
            WHEN SUM(CASE 
                WHEN t.id IS NOT NULL AND (
                    (t.estado = 'cerrado' AND (julianday(t.fecha_cierre) - julianday(t.fecha_apertura))*24.0 > t.sla_horas)
                    OR
                    (t.estado = 'abierto' AND (julianday('now', 'localtime') - julianday(t.fecha_apertura))*24.0 > t.sla_horas)
                ) THEN 1 ELSE 0 END) > 0 THEN 'ROJO'
            WHEN SUM(CASE 
                WHEN t.id IS NOT NULL AND t.estado = 'abierto' 
                    AND (julianday('now', 'localtime') - julianday(t.fecha_apertura))*24.0 <= t.sla_horas
                    AND (t.sla_horas - (julianday('now', 'localtime') - julianday(t.fecha_apertura))*24.0) < 0.20 * t.sla_horas
                THEN 1 ELSE 0 END) > 0 THEN 'AMARILLO'
            ELSE 'VERDE'
        END AS semaforo
    FROM tecnicos tec
    JOIN departamentos d ON d.id = tec.departamento_id
    LEFT JOIN tickets t ON t.tecnico_id = tec.id
    WHERE tec.departamento_id = ?
    GROUP BY tec.id, tec.nombre, tec.departamento_id, d.nombre
    ORDER BY total_tickets DESC, tec.nombre ASC
    """
    conn = get_connection()
    df = pd.read_sql_query(sql, conn, params=(departamento_id,))
    conn.close()
    return df


def obtener_tecnico_por_id(tecnico_id: int) -> dict | None:
    """Retorna los datos de un técnico específico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tec.id, tec.nombre, tec.departamento_id, d.nombre AS departamento_nombre
        FROM tecnicos tec
        JOIN departamentos d ON d.id = tec.departamento_id
        WHERE tec.id = ?
    """, (tecnico_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def obtener_tickets_por_tecnico(tecnico_id: int) -> pd.DataFrame:
    """
    Nivel 3: Detalle de Tickets por Técnico
    Consulta SQL con JOIN a usuarios (solicitantes), técnicos y departamentos.
    Calcula horas transcurridas y estado de semáforo ('VERDE', 'AMARILLO', 'ROJO').
    """
    sql = """
    SELECT 
        t.id,
        t.titulo,
        t.prioridad,
        t.estado,
        t.sla_horas,
        t.fecha_apertura,
        t.fecha_cierre,
        u.id AS usuario_id,
        u.nombre AS solicitante,
        tec.id AS tecnico_id,
        tec.nombre AS tecnico_nombre,
        d.nombre AS departamento_nombre,
        ROUND((julianday(COALESCE(t.fecha_cierre, 'now', 'localtime')) - julianday(t.fecha_apertura)) * 24.0, 1) AS horas_transcurridas,
        ROUND(t.sla_horas - (julianday(COALESCE(t.fecha_cierre, 'now', 'localtime')) - julianday(t.fecha_apertura)) * 24.0, 1) AS horas_restantes,
        CASE 
            WHEN t.estado = 'cerrado' THEN
                CASE 
                    WHEN (julianday(t.fecha_cierre) - julianday(t.fecha_apertura)) * 24.0 <= t.sla_horas THEN 'VERDE'
                    ELSE 'ROJO'
                END
            ELSE
                CASE 
                    WHEN (julianday('now', 'localtime') - julianday(t.fecha_apertura)) * 24.0 > t.sla_horas THEN 'ROJO'
                    WHEN (t.sla_horas - (julianday('now', 'localtime') - julianday(t.fecha_apertura)) * 24.0) < 0.20 * t.sla_horas THEN 'AMARILLO'
                    ELSE 'VERDE'
                END
        END AS semaforo
    FROM tickets t
    JOIN usuarios u ON u.id = t.usuario_id
    JOIN tecnicos tec ON tec.id = t.tecnico_id
    JOIN departamentos d ON d.id = tec.departamento_id
    WHERE t.tecnico_id = ?
    ORDER BY 
        CASE t.estado WHEN 'abierto' THEN 1 ELSE 2 END,
        t.fecha_apertura DESC
    """
    conn = get_connection()
    df = pd.read_sql_query(sql, conn, params=(tecnico_id,))
    conn.close()
    return df.where(pd.notnull(df), None)


def obtener_distribucion_prioridad_tecnico(tecnico_id: int) -> pd.DataFrame:
    """
    Nivel 3: Distribución por prioridad de los tickets del técnico.
    Consulta SQL con COUNT y GROUP BY prioridad.
    """
    sql = """
    SELECT 
        prioridad,
        COUNT(id) AS cantidad
    FROM tickets
    WHERE tecnico_id = ?
    GROUP BY prioridad
    ORDER BY 
        CASE prioridad 
            WHEN 'alta' THEN 1 
            WHEN 'media' THEN 2 
            WHEN 'baja' THEN 3 
            ELSE 4 
        END
    """
    conn = get_connection()
    df = pd.read_sql_query(sql, conn, params=(tecnico_id,))
    conn.close()
    return df
