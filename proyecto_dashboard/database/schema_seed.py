"""
Esquema y generación de datos semilla (Seed) realistas con fechas dinámicas.
Puebla la base de datos con 5 departamentos, 12 técnicos, 15 usuarios solicitantes
y más de 45 tickets calculados en relación con datetime.now() para lucir los 3 estados
del semáforo (Verde, Amarillo y Rojo) en todos los niveles.
"""
import hashlib
from datetime import datetime, timedelta
from .connection import get_connection


def hash_password(password: str) -> str:
    """Genera hash SHA-256 de la contraseña para autenticación formal."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def fmt_dt(dt: datetime) -> str:
    """Formatea objetos datetime al estándar SQL 'YYYY-MM-DD HH:MM:SS'."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def init_and_seed_db(force_reset: bool = False):
    """
    Inicializa el esquema de tablas y puebla el dataset completo.
    Si force_reset es True o si la base de datos no cuenta con el dataset completo,
    recrea las tablas e inserta los datos semilla.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if force_reset:
        cursor.executescript("""
            DROP TABLE IF EXISTS tickets;
            DROP TABLE IF EXISTS usuarios;
            DROP TABLE IF EXISTS tecnicos;
            DROP TABLE IF EXISTS departamentos;
            DROP TABLE IF EXISTS usuarios_sistema;
        """)

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS departamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tecnicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departamento_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departamento_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            estado TEXT NOT NULL,
            prioridad TEXT NOT NULL,
            fecha_apertura TEXT NOT NULL,
            fecha_cierre TEXT,
            sla_horas INTEGER NOT NULL,
            tecnico_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM tickets")
    total_tickets = cursor.fetchone()[0]
    if total_tickets >= 45 and not force_reset:
        conn.close()
        return

    # Si no tiene el dataset completo y no se forzó el reset, limpiamos para recargar limpio
    if total_tickets < 45 and not force_reset:
        cursor.executescript("""
            DELETE FROM tickets;
            DELETE FROM usuarios;
            DELETE FROM tecnicos;
            DELETE FROM departamentos;
            DELETE FROM usuarios_sistema;
        """)

    # 1. Usuarios del Sistema
    usuarios_sis = [
        ("hamui", hash_password("hamui123"), "Administrador"),
        ("admin", hash_password("admin123"), "Administrador"),
        ("supervisor", hash_password("super123"), "Supervisor"),
    ]
    cursor.executemany(
        "INSERT INTO usuarios_sistema (username, password_hash, rol) VALUES (?, ?, ?)",
        usuarios_sis,
    )

    # 2. Departamentos (5 departamentos con estados diseñados)
    departamentos = [
        (1, "Infraestructura y Servidores"),      # Semáforo ROJO
        (2, "Ciberseguridad y Redes"),            # Semáforo AMARILLO
        (3, "Desarrollo y Base de Datos"),        # Semáforo VERDE
        (4, "Soporte Tecnico y Mesa de Ayuda"),   # Semáforo ROJO / AMARILLO
        (5, "Administracion y Finanzas"),         # Semáforo VERDE
    ]
    cursor.executemany("INSERT INTO departamentos (id, nombre) VALUES (?, ?)", departamentos)

    # 3. Técnicos (12 técnicos distribuidos entre los 5 departamentos)
    tecnicos = [
        # Depto 1: Infraestructura y Servidores
        (1, 1, "Marcos Ibanez"),
        (2, 1, "Julieta Fernandez"),
        (3, 1, "Ramiro Sosa"),
        # Depto 2: Ciberseguridad y Redes
        (4, 2, "Lucas Dominguez"),
        (5, 2, "Camila Peralta"),
        # Depto 3: Desarrollo y Base de Datos
        (6, 3, "Sofia Rossi"),
        (7, 3, "Nicolas Gimenez"),
        (8, 3, "Federico Lopez"),
        # Depto 4: Soporte Técnico y Mesa de Ayuda
        (9, 4, "Valentina Castro"),
        (10, 4, "Tomas Morales"),
        # Depto 5: Administración y Finanzas
        (11, 5, "Agustina Paz"),
        (12, 5, "Martin Silva"),
    ]
    cursor.executemany("INSERT INTO tecnicos (id, departamento_id, nombre) VALUES (?, ?, ?)", tecnicos)

    # 4. Usuarios Solicitantes (15 usuarios distribuidos)
    usuarios_solicitantes = [
        (1, 1, "Carla Gomez"),
        (2, 1, "Diego Torres"),
        (3, 2, "Hernan Acosta"),
        (4, 2, "Paula Medina"),
        (5, 3, "Esteban Rios"),
        (6, 3, "Lucia Benitez"),
        (7, 4, "Gonzalo Vera"),
        (8, 4, "Mariana Ortiz"),
        (9, 5, "Roberto Ledesma"),
        (10, 5, "Florencia Cabrera"),
        (11, 1, "Alejandro Navarro"),
        (12, 3, "Victoria Molina"),
        (13, 2, "Manuel Herrera"),
        (14, 4, "Sonia Iriarte"),
        (15, 5, "Joaquin Mendez"),
    ]
    cursor.executemany("INSERT INTO usuarios (id, departamento_id, nombre) VALUES (?, ?, ?)", usuarios_solicitantes)

    # 5. Dataset de más de 45 Tickets con tiempos relativos a datetime.now()
    now = datetime.now()

    # Formato: (titulo, estado, prioridad, fecha_apertura, fecha_cierre, sla_horas, tecnico_id, usuario_id)
    tickets_data = [
        # =======================================================================
        # DEPTO 1: Infraestructura y Servidores (Diseñado para Semáforo ROJO)
        # =======================================================================
        # Marcos Ibanez (id 1) -> Estado ROJO (Tiene vencidos y alertas)
        ("Caida de cluster principal de virtualizacion", "abierto", "critica", fmt_dt(now - timedelta(hours=8)), None, 4, 1, 1),
        ("Fallo en raid de almacenamiento SAN", "abierto", "critica", fmt_dt(now - timedelta(hours=10)), None, 6, 1, 2),
        ("Alerta de temperatura en rack central B2", "abierto", "alta", fmt_dt(now - timedelta(hours=7, minutes=15)), None, 8, 1, 11),
        ("Reinicio inesperado de servidor de impresion", "cerrado", "media", fmt_dt(now - timedelta(hours=30)), fmt_dt(now - timedelta(hours=20)), 12, 1, 1),
        ("Migracion de maquina virtual de produccion", "cerrado", "alta", fmt_dt(now - timedelta(hours=50)), fmt_dt(now - timedelta(hours=35)), 8, 1, 2),
        ("Depuracion de snapshots huerfanos en vCenter", "cerrado", "media", fmt_dt(now - timedelta(hours=22)), fmt_dt(now - timedelta(hours=14)), 12, 1, 1),

        # Julieta Fernandez (id 2) -> Estado AMARILLO (Ticket por vencer < 20% SLA)
        ("Renovacion de certificado SSL en balanceador", "abierto", "alta", fmt_dt(now - timedelta(hours=7)), None, 8, 2, 1),
        ("Aprovisionamiento de entorno Docker Linux", "abierto", "media", fmt_dt(now - timedelta(hours=4)), None, 12, 2, 11),
        ("Actualizacion de firmware en UPS central", "cerrado", "media", fmt_dt(now - timedelta(hours=40)), fmt_dt(now - timedelta(hours=32)), 12, 2, 2),
        ("Limpieza de logs en particion /var/log", "cerrado", "baja", fmt_dt(now - timedelta(hours=24)), fmt_dt(now - timedelta(hours=18)), 24, 2, 1),
        ("Auditoria de espacio en LUN de backup", "cerrado", "baja", fmt_dt(now - timedelta(hours=18)), fmt_dt(now - timedelta(hours=10)), 24, 2, 2),

        # Ramiro Sosa (id 3) -> Estado VERDE (Dentro de SLA)
        ("Configuracion de backup incremental nocturno", "abierto", "media", fmt_dt(now - timedelta(hours=3)), None, 12, 3, 2),
        ("Alta de volumen iSCSI para contabilidad", "cerrado", "baja", fmt_dt(now - timedelta(hours=20)), fmt_dt(now - timedelta(hours=12)), 24, 3, 11),
        ("Monitoreo de consumo de RAM en nodo 4", "cerrado", "baja", fmt_dt(now - timedelta(hours=15)), fmt_dt(now - timedelta(hours=10)), 12, 3, 1),
        ("Reemplazo de modulo SFP en switch top-of-rack", "abierto", "media", fmt_dt(now - timedelta(hours=2)), None, 12, 3, 11),

        # =======================================================================
        # DEPTO 2: Ciberseguridad y Redes (Diseñado para Semáforo AMARILLO)
        # =======================================================================
        # Lucas Dominguez (id 4) -> Estado AMARILLO (Tiene 1 ticket por vencer)
        ("Latencia elevada en enlace fibra sucursal norte", "abierto", "alta", fmt_dt(now - timedelta(hours=6, minutes=45)), None, 8, 4, 3),
        ("Configuracion de tunel VPN Site-to-Site", "abierto", "media", fmt_dt(now - timedelta(hours=5)), None, 12, 4, 4),
        ("Bloqueo de puerto sospechoso en Firewall", "cerrado", "critica", fmt_dt(now - timedelta(hours=18)), fmt_dt(now - timedelta(hours=16)), 4, 4, 3),
        ("Cambio de reglas NAT para servidor web", "cerrado", "media", fmt_dt(now - timedelta(hours=36)), fmt_dt(now - timedelta(hours=28)), 12, 4, 4),
        ("Renovacion de llaves precompartidas IPsec", "cerrado", "alta", fmt_dt(now - timedelta(hours=14)), fmt_dt(now - timedelta(hours=10)), 8, 4, 13),

        # Camila Peralta (id 5) -> Estado VERDE
        ("Auditoria de accesos fallidos por SSH", "abierto", "alta", fmt_dt(now - timedelta(hours=2)), None, 8, 5, 4),
        ("Revocacion de credenciales de ex-empleado", "cerrado", "critica", fmt_dt(now - timedelta(hours=12)), fmt_dt(now - timedelta(hours=10)), 4, 5, 3),
        ("Actualizacion de firmas en IPS perimetral", "cerrado", "baja", fmt_dt(now - timedelta(hours=30)), fmt_dt(now - timedelta(hours=22)), 24, 5, 4),
        ("Analisis de trafico anomalas en VLAN DMZ", "abierto", "media", fmt_dt(now - timedelta(hours=3)), None, 12, 5, 13),

        # =======================================================================
        # DEPTO 3: Desarrollo y Base de Datos (Diseñado para Semáforo VERDE)
        # =======================================================================
        # Sofia Rossi (id 6) -> Estado VERDE
        ("Optimizacion de query con cuello de botella", "abierto", "alta", fmt_dt(now - timedelta(hours=2)), None, 8, 6, 5),
        ("Creacion de indices en tabla de facturacion", "cerrado", "media", fmt_dt(now - timedelta(hours=28)), fmt_dt(now - timedelta(hours=22)), 12, 6, 6),
        ("Correccion de deadlock en proceso nocturno", "cerrado", "critica", fmt_dt(now - timedelta(hours=14)), fmt_dt(now - timedelta(hours=11)), 4, 6, 12),
        ("Refactor de procedimiento almacenado de cobranzas", "cerrado", "media", fmt_dt(now - timedelta(hours=26)), fmt_dt(now - timedelta(hours=18)), 12, 6, 12),

        # Nicolas Gimenez (id 7) -> Estado VERDE
        ("Despliegue de hotfix en API de pagos", "abierto", "media", fmt_dt(now - timedelta(hours=3)), None, 12, 7, 6),
        ("Restauracion de dump en entorno de testing", "cerrado", "baja", fmt_dt(now - timedelta(hours=40)), fmt_dt(now - timedelta(hours=26)), 24, 7, 5),
        ("Ajuste de timeout en conector SQLite", "cerrado", "media", fmt_dt(now - timedelta(hours=20)), fmt_dt(now - timedelta(hours=15)), 12, 7, 12),
        ("Implementacion de cache Redis en servicio de catalogo", "abierto", "media", fmt_dt(now - timedelta(hours=4)), None, 12, 7, 5),

        # Federico Lopez (id 8) -> Estado VERDE
        ("Integracion de webhook con sistema ERP", "cerrado", "media", fmt_dt(now - timedelta(hours=32)), fmt_dt(now - timedelta(hours=24)), 12, 8, 5),
        ("Validacion de integridad referencial en BD", "cerrado", "baja", fmt_dt(now - timedelta(hours=25)), fmt_dt(now - timedelta(hours=15)), 24, 8, 6),
        ("Actualizacion de ORM en microservicio de usuarios", "abierto", "baja", fmt_dt(now - timedelta(hours=6)), None, 24, 8, 6),

        # =======================================================================
        # DEPTO 4: Soporte Tecnico y Mesa de Ayuda (Diseñado para ROJO / AMARILLO)
        # =======================================================================
        # Valentina Castro (id 9) -> Estado ROJO (Tickets vencidos)
        ("Equipo de recepcion no da video al encender", "abierto", "alta", fmt_dt(now - timedelta(hours=11)), None, 6, 9, 7),
        ("Atasco de etiquetas en impresora termica Zebra", "abierto", "critica", fmt_dt(now - timedelta(hours=5)), None, 3, 9, 8),
        ("Instalacion de suite de diseno grafico", "abierto", "baja", fmt_dt(now - timedelta(hours=4)), None, 24, 9, 7),
        ("Reemplazo de fuente ATX en puesto 14", "cerrado", "alta", fmt_dt(now - timedelta(hours=28)), fmt_dt(now - timedelta(hours=22)), 8, 9, 8),
        ("Falla intermitente en lector biometrico sede sur", "cerrado", "alta", fmt_dt(now - timedelta(hours=35)), fmt_dt(now - timedelta(hours=20)), 8, 9, 14),

        # Tomas Morales (id 10) -> Estado AMARILLO (Por vencer)
        ("Desbloqueo de cuenta en Active Directory", "abierto", "media", fmt_dt(now - timedelta(hours=5, minutes=10)), None, 6, 10, 8),
        ("Configuracion de doble monitor en puesto gerencial", "cerrado", "baja", fmt_dt(now - timedelta(hours=30)), fmt_dt(now - timedelta(hours=18)), 24, 10, 7),
        ("Fallo de autenticacion en cliente de correo", "cerrado", "media", fmt_dt(now - timedelta(hours=16)), fmt_dt(now - timedelta(hours=11)), 8, 10, 8),
        ("Configuracion de telefono IP en nuevo puesto", "abierto", "baja", fmt_dt(now - timedelta(hours=5)), None, 24, 10, 14),
        ("Reemplazo de teclado ergonomico en administracion", "cerrado", "baja", fmt_dt(now - timedelta(hours=16)), fmt_dt(now - timedelta(hours=12)), 24, 10, 8),

        # =======================================================================
        # DEPTO 5: Administracion y Finanzas (Diseñado para Semáforo VERDE)
        # =======================================================================
        # Agustina Paz (id 11) -> Estado VERDE
        ("Habilitacion de permisos en modulo de sueldos", "abierto", "media", fmt_dt(now - timedelta(hours=2)), None, 12, 11, 9),
        ("Exportacion de padron de legajos a CSV", "cerrado", "baja", fmt_dt(now - timedelta(hours=22)), fmt_dt(now - timedelta(hours=14)), 24, 11, 10),
        ("Alta de perfil para ingresante de administracion", "cerrado", "media", fmt_dt(now - timedelta(hours=18)), fmt_dt(now - timedelta(hours=12)), 12, 11, 9),
        ("Generacion de reporte de liquidacion de haberes", "cerrado", "media", fmt_dt(now - timedelta(hours=14)), fmt_dt(now - timedelta(hours=10)), 12, 11, 15),

        # Martin Silva (id 12) -> Estado VERDE
        ("Actualizacion de planilla de retenciones", "abierto", "baja", fmt_dt(now - timedelta(hours=5)), None, 24, 12, 10),
        ("Error de redondeo en reporte mensual de caja", "cerrado", "alta", fmt_dt(now - timedelta(hours=20)), fmt_dt(now - timedelta(hours=15)), 8, 12, 9),
        ("Sincronizacion de reloj biometrico de fichada", "cerrado", "media", fmt_dt(now - timedelta(hours=26)), fmt_dt(now - timedelta(hours=20)), 12, 12, 10),
        ("Ajuste de formula de calculo de aguinaldo", "cerrado", "alta", fmt_dt(now - timedelta(hours=16)), fmt_dt(now - timedelta(hours=12)), 8, 12, 15),
    ]

    cursor.executemany("""
        INSERT INTO tickets (
            titulo, estado, prioridad, fecha_apertura, fecha_cierre, sla_horas, tecnico_id, usuario_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, tickets_data)

    conn.commit()
    conn.close()


def init_db(force_reset: bool = False):
    """Alias principal para inicializar y sembrar la base de datos."""
    return init_and_seed_db(force_reset=force_reset)
