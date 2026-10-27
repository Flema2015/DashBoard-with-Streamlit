"""
Capa de consultas SQL puras para autenticación, KPIs analíticos y navegación en 3 niveles.
"""
import hashlib
import bcrypt
import pandas as pd
from .connection import get_connection


def validar_credenciales(username: str, password: str) -> tuple[bool, str | None]:
    """
    Valida credenciales contra usuarios_sistema.
    Soporta contraseñas con SHA-256 (estándar de seed) y bcrypt (legado / administración).
    Retorna (True, rol) si las credenciales son válidas, (False, None) si no coinciden.
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

    password_hash = fila["password_hash"]
    rol = fila["rol"]

    # 1. Comprobación directa con SHA-256 (seed y creación rápida)
    sha_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if password_hash == sha_hash:
        return True, rol

    # 2. Comprobación de respaldo con bcrypt
    try:
        coincide = bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        coincide = False

    return (True, rol) if coincide else (False, None)


def obtener_kpis_globales() -> dict:
    """
    Calcula métricas consolidadas para las 4 tarjetas superiores de estilo GLPI:
      Card 1 (Verde): Tickets Resueltos / En Tiempo
      Card 2 (Celeste): Tickets Abiertos / Asignados
      Card 3 (Rojo): Tickets Vencidos / Fuera de SLA
      Card 4 (Azul): Total de Tickets Históricos y % de SLA Global
    """
    sql = """
    SELECT 
        COUNT(t.id) AS total_casos,
        SUM(CASE WHEN t.estado = 'abierto' THEN 1 ELSE 0 END) AS abiertos,
        SUM(CASE WHEN t.estado = 'cerrado' THEN 1 ELSE 0 END) AS cerrados,
        SUM(CASE 
            WHEN (t.estado = 'cerrado' AND (julianday(t.fecha_cierre) - julianday(t.fecha_apertura))*24.0 > t.sla_horas)
                 OR (t.estado = 'abierto' AND (julianday('now', 'localtime') - julianday(t.fecha_apertura))*24.0 > t.sla_horas)
            THEN 1 ELSE 0 END
        ) AS vencidos,
        SUM(CASE 
            WHEN t.estado = 'cerrado' AND (julianday(t.fecha_cierre) - julianday(t.fecha_apertura))*24.0 <= t.sla_horas
            THEN 1 ELSE 0 END
        ) AS cerrados_en_tiempo,
        SUM(CASE 
            WHEN (t.estado = 'cerrado' AND (julianday(t.fecha_cierre) - julianday(t.fecha_apertura))*24.0 <= t.sla_horas)
                 OR (t.estado = 'abierto' AND (julianday('now', 'localtime') - julianday(t.fecha_apertura))*24.0 <= t.sla_horas)
            THEN 1 ELSE 0 END
        ) AS dentro_sla
    FROM tickets t
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    conn.close()

    if row:
        total = row["total_casos"] or 0
        abiertos = row["abiertos"] or 0
        cerrados = row["cerrados"] or 0
        vencidos = row["vencidos"] or 0
        cerrados_en_tiempo = row["cerrados_en_tiempo"] or 0
        dentro_sla = row["dentro_sla"] or 0

        sla_pct = round((dentro_sla / total * 100.0), 1) if total > 0 else 100.0

        return {
            "total_casos": total,
            "abiertos": abiertos,
            "cerrados": cerrados,
            "vencidos": vencidos,
            "cerrados_en_tiempo": cerrados_en_tiempo,
            "sla_global_pct": f"{sla_pct}%",
        }

    return {
        "total_casos": 0,
        "abiertos": 0,
        "cerrados": 0,
        "vencidos": 0,
        "cerrados_en_tiempo": 0,
        "sla_global_pct": "100.0%",
    }


def obtener_metricas_departamentos() -> pd.DataFrame:
    """
    Nivel 1: Departamentos
    Consulta SQL que agrupa por departamento y computa mediante COUNT y CASE WHEN:
      - Total de tickets
      - Tickets abiertos
      - Tickets cerrados
      - Estado del semáforo general según SLA
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
    Consulta SQL con JOIN entre tickets y usuarios (solicitantes), técnicos y departamentos.
    Calcula horas transcurridas y el estado individual del semáforo.
    """
    sql = """
    SELECT 
        t.id,
        t.titulo,
        t.prioridad,
        t.estado,
        t.sla_horas,
        t.fecha_apertura,
        COALESCE(t.fecha_cierre, 'En curso') AS fecha_cierre,
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
        CASE t.prioridad WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 WHEN 'media' THEN 3 WHEN 'baja' THEN 4 ELSE 5 END,
        t.fecha_apertura DESC
    """
    conn = get_connection()
    df = pd.read_sql_query(sql, conn, params=(tecnico_id,))
    conn.close()
    return df.where(pd.notnull(df), None)


def obtener_distribucion_prioridad_tecnico(tecnico_id: int) -> pd.DataFrame:
    """
    Nivel 3: Conteo de tickets agrupados por Prioridad para el técnico.
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
            WHEN 'critica' THEN 1
            WHEN 'alta' THEN 2 
            WHEN 'media' THEN 3 
            WHEN 'baja' THEN 4 
            ELSE 5 
        END
    """
    conn = get_connection()
    df = pd.read_sql_query(sql, conn, params=(tecnico_id,))
    conn.close()
    return df


def obtener_distribucion_estado_tecnico(tecnico_id: int) -> pd.DataFrame:
    """
    Nivel 3: Conteo de tickets agrupados por Estado para el técnico.
    """
    sql = """
    SELECT 
        estado,
        COUNT(id) AS cantidad
    FROM tickets
    WHERE tecnico_id = ?
    GROUP BY estado
    ORDER BY estado ASC
    """
    conn = get_connection()
    df = pd.read_sql_query(sql, conn, params=(tecnico_id,))
    conn.close()
    return df


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
    except Exception:
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

