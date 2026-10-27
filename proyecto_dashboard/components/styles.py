"""
Módulo de inyección de estilos CSS corporativos inspirados en tableros ITSM y GLPI.
Garantiza cero emojis, tarjetas de color sólido de altura fija y animaciones pulse de semáforo.
"""
import streamlit as st

CSS_CORP = """
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
    margin-bottom: 22px;
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

/* Tarjetas KPI Superiores en Bloques de Color Sólido (Estilo GLPI) */
.kpi-card {
    height: 155px;
    min-height: 150px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 18px 20px;
    border-radius: 8px;
    box-sizing: border-box;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    color: #ffffff;
}
.kpi-top {
    display: flex;
    flex-direction: column;
}
.kpi-green {
    background-color: #059669;
}
.kpi-cyan {
    background-color: #0284c7;
}
.kpi-red {
    background-color: #dc2626;
}
.kpi-blue {
    background-color: #1e40af;
}
.kpi-value {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.1;
    color: #ffffff;
    letter-spacing: -0.02em;
}
.kpi-subtext {
    font-size: 0.82rem;
    color: rgba(255, 255, 255, 0.9);
    margin-top: 4px;
    font-weight: 500;
}
.kpi-label {
    font-size: 0.80rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: rgba(255, 255, 255, 0.92);
}

/* Animación Pulse Requerida para Semáforos */
@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7); }
    70% { transform: scale(1.08); box-shadow: 0 0 0 8px rgba(220, 53, 69, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }
}

@keyframes pulse-amber {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(217, 119, 6, 0.7); }
    70% { transform: scale(1.08); box-shadow: 0 0 0 8px rgba(217, 119, 6, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(217, 119, 6, 0); }
}

.dot-anim-red { 
    animation: pulse 1.6s infinite ease-in-out; 
}
.dot-anim-yellow { 
    animation: pulse-amber 2s infinite ease-in-out; 
}

/* Contenedor Destacado de Referencia de Semáforo */
.sla-ref-container {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 16px 22px;
    margin-bottom: 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
}
.sla-ref-title {
    font-size: 0.86rem;
    font-weight: 700;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.sla-ref-items {
    display: flex;
    gap: 26px;
    align-items: center;
    flex-wrap: wrap;
}
.sla-ref-item {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 0.90rem;
    color: #1e293b;
}

.dot-indicator {
    width: 13px;
    height: 13px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.dot-green { background-color: #059669; }
.dot-yellow { background-color: #d97706; }
.dot-red { background-color: #dc2626; }

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
.prio-critica { background: #fee2e2; color: #7f1d1d; font-weight: 800; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; border: 1px solid #f87171; text-transform: uppercase; }
.prio-alta { background: #fee2e2; color: #b91c1c; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; border: 1px solid #fca5a5; }
.prio-media { background: #fef3c7; color: #b45309; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; border: 1px solid #fcd34d; }
.prio-baja { background: #e0f2fe; color: #0369a1; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; border: 1px solid #bae6fd; }

/* Badges de Estado del Ticket */
.estado-abierto { background: #eff6ff; color: #1d4ed8; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; border: 1px solid #bfdbfe; }
.estado-cerrado { background: #f1f5f9; color: #475569; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; border: 1px solid #cbd5e1; }

/* Ruta de Navegación Formal (Breadcrumbs) */
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


def inject_corporate_styles():
    """Inyecta el bloque de estilo CSS corporativo en la sesión de Streamlit."""
    st.markdown(CSS_CORP, unsafe_allow_html=True)


def get_semaphore_badge(status: str) -> str:
    """Genera HTML para badge semafórico con animación pulse sin emojis ni saltos multilínea."""
    if status == "ROJO":
        return '<span class="status-badge badge-red"><span class="dot-indicator dot-red dot-anim-red"></span> Fuera de SLA</span>'
    elif status == "AMARILLO":
        return '<span class="status-badge badge-yellow"><span class="dot-indicator dot-yellow dot-anim-yellow"></span> Por vencer</span>'
    else:
        return '<span class="status-badge badge-green"><span class="dot-indicator dot-green"></span> Dentro de SLA</span>'
