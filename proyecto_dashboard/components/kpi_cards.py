"""
Renderizado de las 4 tarjetas superiores de KPIs en columnas nativas y bloque animado de semáforo.
"""
import streamlit as st


def _card_html(color_class: str, valor, subtexto: str, etiqueta: str) -> str:
    """
    Genera el HTML compacto de una tarjeta KPI sin indentación para evitar
    que el parser de Markdown lo interprete como bloque de código (<pre><code>).
    """
    return (
        f'<div class="kpi-card {color_class}">'
        f'<div class="kpi-top">'
        f'<div class="kpi-value">{valor}</div>'
        f'<div class="kpi-subtext">{subtexto}</div>'
        f'</div>'
        f'<div class="kpi-label">{etiqueta}</div>'
        f'</div>'
    )


def render_kpi_cards(kpi_data: dict):
    """
    Renderiza las 4 tarjetas KPI superiores en columnas nativas de Streamlit:
      Card 1 (Verde esmeralda): Tickets Resueltos / En Tiempo
      Card 2 (Celeste / Cyan): Tickets Abiertos / Asignados
      Card 3 (Rojo coral): Tickets Vencidos / Fuera de SLA
      Card 4 (Azul institucional): Total de Tickets Históricos y % de SLA Global
    """
    total = kpi_data.get("total_casos", 0)
    abiertos = kpi_data.get("abiertos", 0)
    cerrados = kpi_data.get("cerrados", 0)
    vencidos = kpi_data.get("vencidos", 0)
    cerrados_en_tiempo = kpi_data.get("cerrados_en_tiempo", 0)
    sla_pct = kpi_data.get("sla_global_pct", "100.0%")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            _card_html(
                "kpi-green",
                cerrados,
                f"{cerrados_en_tiempo} cerrados dentro de SLA",
                "Tickets Resueltos / En Tiempo",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            _card_html(
                "kpi-cyan",
                abiertos,
                "Incidencias en curso activo",
                "Tickets Abiertos / Asignados",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            _card_html(
                "kpi-red",
                vencidos,
                "Requieren atencion inmediata",
                "Tickets Vencidos / Fuera de SLA",
            ),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            _card_html(
                "kpi-blue",
                total,
                f"Cumplimiento Global SLA: {sla_pct}",
                "Total Tickets e Indice SLA",
            ),
            unsafe_allow_html=True,
        )


def render_semaphore_reference():
    """
    Renderiza el contenedor destacado con la referencia de semaforización
    y animación pulse en los indicadores de alerta sin indentación multilínea.
    """
    html = (
        '<div class="sla-ref-container">'
        '<div class="sla-ref-title">Referencia de Semaforizacion Operativa SLA</div>'
        '<div class="sla-ref-items">'
        '<div class="sla-ref-item">'
        '<span class="dot-indicator dot-green"></span>'
        '<span><strong>Verde:</strong> Dentro de SLA (Situacion normal / favorable)</span>'
        '</div>'
        '<div class="sla-ref-item">'
        '<span class="dot-indicator dot-yellow dot-anim-yellow"></span>'
        '<span><strong>Amarillo:</strong> Por vencer — menos del 20% del tiempo de SLA restante (Advertencia)</span>'
        '</div>'
        '<div class="sla-ref-item">'
        '<span class="dot-indicator dot-red dot-anim-red"></span>'
        '<span><strong>Rojo:</strong> Vencido / Fuera de SLA (Situacion critica)</span>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
