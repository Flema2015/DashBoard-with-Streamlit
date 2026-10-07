import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database import (
    inicializar_db,
    validar_credenciales,
    obtener_kpis_superiores,
    obtener_metricas_departamentos,
    obtener_tecnicos_por_departamento,
    obtener_tickets_por_tecnico,
    obtener_distribucion_prioridad_tecnico,
)

# Inicializar y verificar esquema y datos seed de la base de datos
inicializar_db()

# Configuración formal de la página (cero emojis)
st.set_page_config(
    page_title="Mesa de Ayuda TI - Panel de Control",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Estilos CSS Corporativos (Inspirado en Paneles Operativos ITSM / GLPI)
# ---------------------------------------------------------------------------
CSS_CORPORATIVO = """
<style>
/* Tipografía y Base Corporativa */
body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Encabezado Corporativo */
.header-container {
    background: #1e293b;
    padding: 18px 24px;
    border-radius: 8px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 6px solid #2563eb;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.header-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.01em;
}
.header-badge {
    background: #334155;
    color: #93c5fd;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 0.88rem;
    font-weight: 600;
    border: 1px solid #475569;
}

/* Tarjetas KPI Superiores Estilo GLPI */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}
.kpi-card {
    background: #ffffff;
    border-radius: 8px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    border: 1px solid #e2e8f0;
}
.kpi-blue {
    border-top: 5px solid #1e40af;
    background: linear-gradient(180deg, #eff6ff 0%, #ffffff 45%);
}
.kpi-cyan {
    border-top: 5px solid #0284c7;
    background: linear-gradient(180deg, #f0f9ff 0%, #ffffff 45%);
}
.kpi-red {
    border-top: 5px solid #dc2626;
    background: linear-gradient(180deg, #fef2f2 0%, #ffffff 45%);
}
.kpi-green {
    border-top: 5px solid #059669;
    background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 45%);
}
.kpi-value {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    color: #0f172a;
    letter-spacing: -0.02em;
}
.kpi-label {
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #475569;
    margin-top: 8px;
}

/* Animaciones de Semáforo */
@keyframes pulse {
    0% { transform: scale(0.92); opacity: 0.75; }
    50% { transform: scale(1.1); opacity: 1; filter: drop-shadow(0 0 5px rgba(220, 38, 38, 0.7)); }
    100% { transform: scale(0.92); opacity: 0.75; }
}
@keyframes pulse-yellow {
    0% { transform: scale(0.94); opacity: 0.8; }
    50% { transform: scale(1.08); opacity: 1; filter: drop-shadow(0 0 5px rgba(217, 119, 6, 0.6)); }
    100% { transform: scale(0.94); opacity: 0.8; }
}

.dot-anim-red { 
    animation: pulse 1.5s infinite ease-in-out; 
}
.dot-anim-yellow { 
    animation: pulse-yellow 2s infinite ease-in-out; 
}

/* Contenedor del Semáforo Destacado */
.sla-banner {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 16px 22px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.sla-banner-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.sla-items {
    display: flex;
    gap: 28px;
    align-items: center;
    flex-wrap: wrap;
}
.sla-item {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 0.90rem;
    color: #1e293b;
}

.dot-indicator {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.dot-green { background-color: #10b981; }
.dot-yellow { background-color: #f59e0b; }
.dot-red { background-color: #ef4444; }

/* Badges de Estado */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.82rem;
    font-weight: 600;
}
.badge-green { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.badge-yellow { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
.badge-red { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

/* Badges de Prioridad */
.prio-alta { background: #fee2e2; color: #b91c1c; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; border: 1px solid #fca5a5; }
.prio-media { background: #fef3c7; color: #b45309; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; border: 1px solid #fcd34d; }
.prio-baja { background: #e0f2fe; color: #0369a1; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; border: 1px solid #bae6fd; }

/* Estado Ticket Badge */
.estado-abierto { background: #eff6ff; color: #1d4ed8; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; border: 1px solid #bfdbfe; }
.estado-cerrado { background: #f1f5f9; color: #475569; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; border: 1px solid #cbd5e1; }

/* Ruta de Navegación (Breadcrumbs) */
.breadcrumb-box {
    background: #f8fafc;
    padding: 10px 18px;
    border-radius: 6px;
    font-size: 0.88rem;
    color: #475569;
    font-weight: 500;
    margin-bottom: 18px;
    border: 1px solid #e2e8f0;
}
.breadcrumb-box strong {
    color: #0f172a;
}
</style>
"""


def renderizar_css():
    """Inyecta los estilos corporativos globales."""
    st.markdown(CSS_CORPORATIVO, unsafe_allow_html=True)


def badge_semaforo_html(estado_semaforo: str) -> str:
    """Retorna un indicador animado formal sin emojis según el estado del semáforo."""
    if estado_semaforo == "ROJO":
        return '<span class="status-badge badge-red"><span class="dot-indicator dot-red dot-anim-red"></span> Fuera de SLA</span>'
    elif estado_semaforo == "AMARILLO":
        return '<span class="status-badge badge-yellow"><span class="dot-indicator dot-yellow dot-anim-yellow"></span> Por vencer</span>'
    else:
        return '<span class="status-badge badge-green"><span class="dot-indicator dot-green"></span> Dentro de SLA</span>'


def banner_referencia_semaforo():
    """Bloque visual superior destacado con la referencia animada del semáforo."""
    html = """
    <div class="sla-banner">
        <div class="sla-banner-title">Referencia de Monitoreo SLA</div>
        <div class="sla-items">
            <div class="sla-item">
                <span class="dot-indicator dot-green"></span>
                <span><strong>Verde:</strong> Dentro de SLA</span>
            </div>
            <div class="sla-item">
                <span class="dot-indicator dot-yellow dot-anim-yellow"></span>
                <span><strong>Amarillo:</strong> Por vencer (&lt; 20% del tiempo restante)</span>
            </div>
            <div class="sla-item">
                <span class="dot-indicator dot-red dot-anim-red"></span>
                <span><strong>Rojo:</strong> Fuera de SLA / Vencido</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def inicializar_session_state():
    """Inicializa el estado de sesión sin dependencias externas."""
    if "logueado" not in st.session_state:
        st.session_state["logueado"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "usuario_rol" not in st.session_state:
        st.session_state["usuario_rol"] = None
    if "nivel" not in st.session_state:
        st.session_state["nivel"] = 1
    if "departamento_id" not in st.session_state:
        st.session_state["departamento_id"] = None
    if "departamento_nombre" not in st.session_state:
        st.session_state["departamento_nombre"] = None
    if "tecnico_id" not in st.session_state:
        st.session_state["tecnico_id"] = None
    if "tecnico_nombre" not in st.session_state:
        st.session_state["tecnico_nombre"] = None


def cerrar_sesion():
    """Cierra la sesión y limpia el estado."""
    st.session_state["logueado"] = False
    st.session_state["username"] = None
    st.session_state["usuario_rol"] = None
    st.session_state["nivel"] = 1
    st.session_state["departamento_id"] = None
    st.session_state["departamento_nombre"] = None
    st.session_state["tecnico_id"] = None
    st.session_state["tecnico_nombre"] = None
    st.rerun()


# ---------------------------------------------------------------------------
# Pantalla de Login (Formal, Corporativa, Cero Emojis)
# ---------------------------------------------------------------------------
def pantalla_login():
    renderizar_css()

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    col_izq, col_centro, col_der = st.columns([1, 1.3, 1])

    with col_centro:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center; color: #1e3a8a; margin-bottom: 4px;'>Mesa de Ayuda TI</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.92rem; margin-bottom: 24px;'>Sistema de Autenticacion y Monitoreo ITSM</p>", unsafe_allow_html=True)

            with st.form("form_login_formal"):
                username = st.text_input(
                    "Usuario",
                    placeholder="Ingrese su nombre de usuario",
                )
                password = st.text_input(
                    "Contrasena",
                    type="password",
                    placeholder="Ingrese su contraseña",
                )
                submit = st.form_submit_button("Iniciar Sesion", use_container_width=True)

            if submit:
                if not username.strip() or not password.strip():
                    st.warning("Por favor complete todos los campos para continuar.")
                else:
                    valido, rol = validar_credenciales(username, password)
                    if valido:
                        st.session_state["logueado"] = True
                        st.session_state["username"] = username.strip()
                        st.session_state["usuario_rol"] = rol
                        st.session_state["nivel"] = 1
                        st.rerun()
                    else:
                        st.error("Credenciales invalidas. Verifique su usuario y contraseña.")


# ---------------------------------------------------------------------------
# Encabezado Sobrio y Barra Lateral
# ---------------------------------------------------------------------------
def renderizar_encabezado():
    """Muestra la cabecera sobria y formal requerida."""
    rol = st.session_state.get("usuario_rol", "Usuario")
    username = st.session_state.get("username", "")

    header_html = f"""
    <div class="header-container">
        <div class="header-title">Mesa de Ayuda | Panel de Control — Rol: {rol}</div>
        <div class="header-badge">Usuario: {username} | {rol}</div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Sesion de Usuario")
        st.markdown(f"**Identificador:** `{username}`")
        st.markdown(f"**Rol Asignado:** `{rol}`")
        st.markdown("---")
        st.markdown(f"**Nivel de Exploracion:** Nivel {st.session_state.nivel}")
        if st.session_state.departamento_nombre:
            st.markdown(f"**Departamento:** {st.session_state.departamento_nombre}")
        if st.session_state.tecnico_nombre:
            st.markdown(f"**Tecnico:** {st.session_state.tecnico_nombre}")
        st.markdown("---")
        if st.button("Cerrar Sesion", key="btn_logout_sidebar", use_container_width=True):
            cerrar_sesion()


# ---------------------------------------------------------------------------
# Nivel 1: Departamentos
# ---------------------------------------------------------------------------
def nivel1_departamentos():
    st.subheader("Nivel 1: Departamentos")

    # 1. Tarjetas Superiores Estilo GLPI
    kpis = obtener_kpis_superiores()
    kpi_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card kpi-blue">
            <div class="kpi-value">{kpis['total_casos']}</div>
            <div class="kpi-label">Total de Casos</div>
        </div>
        <div class="kpi-card kpi-cyan">
            <div class="kpi-value">{kpis['en_proceso']}</div>
            <div class="kpi-label">En Proceso</div>
        </div>
        <div class="kpi-card kpi-red">
            <div class="kpi-value">{kpis['vencidos']}</div>
            <div class="kpi-label">Vencidos</div>
        </div>
        <div class="kpi-card kpi-green">
            <div class="kpi-value">{kpis['eficiencia_sla']}</div>
            <div class="kpi-label">Eficiencia SLA</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

    # 2. Bloque Animado de Referencia del Semáforo
    banner_referencia_semaforo()

    st.markdown("### Resumen Operativo por Departamento")

    df_deptos = obtener_metricas_departamentos()
    if df_deptos.empty:
        st.info("No se registran departamentos en el sistema.")
        return

    # 3. Listado formal de Departamentos con Semáforo y Botón 'Ver tecnicos'
    for _, depto in df_deptos.iterrows():
        with st.container(border=True):
            col_nombre, col_info, col_semaforo, col_accion = st.columns([3, 3, 2.5, 2])
            with col_nombre:
                st.markdown(f"**{depto['nombre']}**")
            with col_info:
                st.markdown(f"{int(depto['tickets_abiertos'])} abiertos de {int(depto['total_tickets'])} totales")
            with col_semaforo:
                st.markdown(badge_semaforo_html(depto["semaforo"]), unsafe_allow_html=True)
            with col_accion:
                if st.button("Ver tecnicos", key=f"depto_{depto['id']}", use_container_width=True):
                    st.session_state.nivel = 2
                    st.session_state.departamento_id = int(depto["id"])
                    st.session_state.departamento_nombre = depto["nombre"]
                    st.rerun()

    st.markdown("---")

    # 4. Gráfico Comparativo Principal (Nivel 1): Barras Agrupadas
    st.markdown("### Comparativa de Incidencias por Departamento")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_deptos["nombre"],
        y=df_deptos["total_tickets"],
        name="Total de tickets",
        marker_color="#1E40AF",  # Azul institucional
        text=df_deptos["total_tickets"],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=df_deptos["nombre"],
        y=df_deptos["tickets_abiertos"],
        name="Tickets abiertos / en curso",
        marker_color="#0284C7",  # Celeste / Cyan corporativo
        text=df_deptos["tickets_abiertos"],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=df_deptos["nombre"],
        y=df_deptos["tickets_cerrados"],
        name="Tickets cerrados / resueltos",
        marker_color="#059669",  # Verde esmeralda corporativo
        text=df_deptos["tickets_cerrados"],
        textposition="outside",
    ))

    fig.update_layout(
        barmode="group",
        template="plotly_white",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Departamento",
            showgrid=True,
            gridcolor="#E2E8F0",
            griddash="dot",
            linecolor="#CBD5E1",
            tickfont=dict(size=12, color="#334155")
        ),
        yaxis=dict(
            title="Cantidad de Incidencias",
            showgrid=True,
            gridcolor="#E2E8F0",
            griddash="dot",
            linecolor="#CBD5E1",
            tickfont=dict(size=12, color="#334155")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#334155")
        ),
        margin=dict(t=50, b=40, l=40, r=40),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Botón formal de cierre al pie
    st.markdown("---")
    if st.button("Cerrar Sesion", key="btn_logout_bottom"):
        cerrar_sesion()


# ---------------------------------------------------------------------------
# Nivel 2: Técnicos por Departamento
# ---------------------------------------------------------------------------
def nivel2_tecnicos():
    depto_id = st.session_state.departamento_id
    depto_nombre = st.session_state.departamento_nombre or f"Departamento {depto_id}"

    # Botón de retorno sobrio y miga de pan
    col_retorno, col_bread = st.columns([1.8, 5])
    with col_retorno:
        if st.button("<- Volver a departamentos", key="btn_volver_deptos"):
            st.session_state.nivel = 1
            st.session_state.departamento_id = None
            st.session_state.departamento_nombre = None
            st.rerun()
    with col_bread:
        bread_html = f"""
        <div class="breadcrumb-box">
            Departamentos &nbsp;/&nbsp; <strong>{depto_nombre}</strong>
        </div>
        """
        st.markdown(bread_html, unsafe_allow_html=True)

    # Título formal requerido
    st.subheader(f"Nivel 2: Desglose de Tecnicos - Departamento {depto_nombre}")

    # Referencia animada de SLA
    banner_referencia_semaforo()

    df_tecnicos = obtener_tecnicos_por_departamento(depto_id)
    if df_tecnicos.empty:
        st.info("No se registran tecnicos asignados a este departamento.")
        return

    # Listado de técnicos con tickets asignados, semáforo individual y botón 'Ver tickets'
    for _, tec in df_tecnicos.iterrows():
        with st.container(border=True):
            col_nom, col_det, col_sem, col_btn = st.columns([3, 3, 2.5, 2])
            with col_nom:
                st.markdown(f"**{tec['nombre']}**")
            with col_det:
                st.markdown(f"{int(tec['total_tickets'])} asignados ({int(tec['tickets_abiertos'])} abiertos)")
            with col_sem:
                st.markdown(badge_semaforo_html(tec["semaforo"]), unsafe_allow_html=True)
            with col_btn:
                if st.button("Ver tickets", key=f"tec_{tec['id']}", use_container_width=True):
                    st.session_state.nivel = 3
                    st.session_state.tecnico_id = int(tec["id"])
                    st.session_state.tecnico_nombre = tec["nombre"]
                    st.rerun()

    st.markdown("---")

    # Gráfico de barras horizontales con el volumen de tickets asignados por técnico
    st.markdown(f"### Carga de Trabajo por Tecnico - Departamento {depto_nombre}")

    fig = go.Figure(go.Bar(
        x=df_tecnicos["total_tickets"],
        y=df_tecnicos["nombre"],
        orientation="h",
        marker_color="#1E40AF",  # Azul institucional
        text=df_tecnicos["total_tickets"],
        textposition="outside",
    ))

    fig.update_layout(
        template="plotly_white",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Volumen de Tickets Asignados",
            showgrid=True,
            gridcolor="#E2E8F0",
            griddash="dot",
            linecolor="#CBD5E1",
            tickfont=dict(size=12, color="#334155")
        ),
        yaxis=dict(
            title="Tecnico Asignado",
            showgrid=True,
            gridcolor="#E2E8F0",
            griddash="dot",
            linecolor="#CBD5E1",
            categoryorder="total ascending",
            tickfont=dict(size=12, color="#334155")
        ),
        margin=dict(t=40, b=40, l=40, r=40),
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Nivel 3: Detalle de Tickets por Técnico
# ---------------------------------------------------------------------------
def nivel3_detalle():
    tecnico_id = st.session_state.tecnico_id
    tecnico_nombre = st.session_state.tecnico_nombre or f"Tecnico {tecnico_id}"
    depto_nombre = st.session_state.departamento_nombre or "Departamento"

    # Botón de retorno sobrio y miga de pan
    col_retorno, col_bread = st.columns([1.8, 5])
    with col_retorno:
        if st.button("<- Volver a tecnicos", key="btn_volver_tecnicos"):
            st.session_state.nivel = 2
            st.session_state.tecnico_id = None
            st.session_state.tecnico_nombre = None
            st.rerun()
    with col_bread:
        bread_html = f"""
        <div class="breadcrumb-box">
            Departamentos &nbsp;/&nbsp; {depto_nombre} &nbsp;/&nbsp; <strong>{tecnico_nombre}</strong>
        </div>
        """
        st.markdown(bread_html, unsafe_allow_html=True)

    # Título formal requerido
    st.subheader(f"Nivel 3: Detalle de Tickets - Tecnico {tecnico_nombre}")

    # Referencia animada de SLA
    banner_referencia_semaforo()

    df_tickets = obtener_tickets_por_tecnico(tecnico_id)
    if df_tickets.empty:
        st.info("Sin incidencias asignadas a este tecnico.")
        return

    # Visualización formal de los registros
    modo_vista = st.radio(
        "Modalidad de visualizacion:",
        ["Formato de Tarjetas Operativas", "Tabla Interactiva de Registros"],
        horizontal=True,
    )

    if modo_vista == "Formato de Tarjetas Operativas":
        for _, t in df_tickets.iterrows():
            with st.container(border=True):
                col_encabezado, col_prio, col_estado = st.columns([4, 2, 2.5])
                with col_encabezado:
                    st.markdown(f"**Ticket #{t['id']} — {t['titulo']}**")
                with col_prio:
                    st.markdown(f"<span class='prio-{t['prioridad']}'>Prioridad {t['prioridad'].upper()}</span>", unsafe_allow_html=True)
                with col_estado:
                    est_class = "estado-abierto" if t["estado"] == "abierto" else "estado-cerrado"
                    st.markdown(f"<span class='{est_class}'>Estado: {t['estado'].capitalize()}</span>", unsafe_allow_html=True)

                col_u, col_sla, col_ap, col_ci = st.columns(4)
                with col_u:
                    st.markdown(f"**Solicitante:**<br>{t['solicitante']}", unsafe_allow_html=True)
                with col_sla:
                    st.markdown(f"**SLA Base:**<br>{t['sla_horas']} horas", unsafe_allow_html=True)
                with col_ap:
                    st.markdown(f"**Apertura:**<br>{t['fecha_apertura']}", unsafe_allow_html=True)
                with col_ci:
                    cierre_str = t['fecha_cierre'] if t['fecha_cierre'] else "En curso"
                    st.markdown(f"**Cierre:**<br>{cierre_str}", unsafe_allow_html=True)

                # Diagnóstico operativo formal
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                col_eval, col_status = st.columns([5, 3])
                with col_eval:
                    st.markdown(f"Tiempo transcurrido computado: **{t['horas_transcurridas']} hs** (Limite SLA: {t['sla_horas']} hs)")
                with col_status:
                    st.markdown(badge_semaforo_html(t["semaforo"]), unsafe_allow_html=True)
    else:
        df_grid = df_tickets[[
            "id", "titulo", "solicitante", "prioridad", "estado", 
            "sla_horas", "horas_transcurridas", "fecha_apertura", "fecha_cierre", "semaforo"
        ]].copy()
        df_grid.columns = [
            "ID", "Titulo", "Solicitante", "Prioridad", "Estado", 
            "SLA (Horas)", "Horas Usadas", "Apertura", "Cierre", "Estado SLA"
        ]
        df_grid["Cierre"] = df_grid["Cierre"].fillna("En curso")
        st.dataframe(df_grid, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Gráfico de dona de distribución de incidencias por prioridad
    st.markdown(f"### Distribucion de Incidencias por Prioridad - Tecnico {tecnico_nombre}")
    df_prioridades = obtener_distribucion_prioridad_tecnico(tecnico_id)

    if not df_prioridades.empty:
        col_grafico, col_datos = st.columns([2.5, 1.5])
        with col_grafico:
            fig = px.pie(
                df_prioridades,
                names="prioridad",
                values="cantidad",
                hole=0.55,
                color="prioridad",
                color_discrete_map={
                    "alta": "#DC2626",    # Rojo corporativo
                    "media": "#D97706",   # Ámbar corporativo
                    "baja": "#2563EB",    # Azul corporativo
                },
            )
            fig.update_traces(
                textposition="inside",
                textinfo="percent+label+value",
                marker=dict(line=dict(color="#FFFFFF", width=2)),
            )
            fig.update_layout(
                template="plotly_white",
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12, color="#334155")
                ),
                margin=dict(t=20, b=40, l=20, r=20),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_datos:
            with st.container(border=True):
                st.markdown("**Resumen de Prioridades**")
                for _, fila in df_prioridades.iterrows():
                    st.write(f"- Prioridad {fila['prioridad'].capitalize()}: {fila['cantidad']} ticket(s)")
                st.markdown(f"**Total asignado al tecnico:** {df_prioridades['cantidad'].sum()} ticket(s)")


# ---------------------------------------------------------------------------
# Router y Ejecución Principal
# ---------------------------------------------------------------------------
def main():
    inicializar_session_state()

    if not st.session_state["logueado"]:
        pantalla_login()
    else:
        renderizar_css()
        renderizar_encabezado()

        if st.session_state.nivel == 1:
            nivel1_departamentos()
        elif st.session_state.nivel == 2:
            nivel2_tecnicos()
        elif st.session_state.nivel == 3:
            nivel3_detalle()


if __name__ == "__main__":
    main()
