"""
Vista Nivel 1: Departamentos.
Muestra KPIs consolidados, referencia animada de semáforo, lista con Drill Down a Nivel 2
y Gráfico comparativo de barras agrupadas (Totales, Abiertos, Cerrados).
"""
import streamlit as st
import plotly.graph_objects as go

from config import (
    COLOR_PRIMARY,
    COLOR_AMBER,
    COLOR_GREEN,
    COLOR_GRID,
)
from database.queries import (
    obtener_kpis_globales,
    obtener_metricas_departamentos,
)
from components.kpi_cards import (
    render_kpi_cards,
    render_semaphore_reference,
)
from components.styles import get_semaphore_badge


def render_nivel1_view():
    """
    Renderiza la vista principal del Nivel 1 (Departamentos).
    """
    st.subheader("Nivel 1: Departamentos")

    # 1. Tarjetas Superiores de KPIs Globales
    kpis = obtener_kpis_globales()
    render_kpi_cards(kpis)

    # 2. Referencia Animada de Semaforización
    render_semaphore_reference()

    st.markdown("### Resumen de Departamentos")

    # 3. Datos de Departamentos agrupados por SQL
    df_deptos = obtener_metricas_departamentos()
    if df_deptos.empty:
        st.info("No se registran departamentos en la base de datos.")
        return

    # Listado estructurado con columnas y botón de Drill Down
    for _, depto in df_deptos.iterrows():
        with st.container(border=True):
            col_nombre, col_conteo, col_semaforo, col_boton = st.columns([3, 3, 2.5, 1.8])
            with col_nombre:
                st.markdown(f"**{depto['nombre']}**")
            with col_conteo:
                st.markdown(
                    f"{int(depto['total_tickets'])} total | "
                    f"{int(depto['tickets_abiertos'])} abiertos | "
                    f"{int(depto['tickets_cerrados'])} cerrados"
                )
            with col_semaforo:
                st.markdown(get_semaphore_badge(depto["semaforo"]), unsafe_allow_html=True)
            with col_boton:
                if st.button("Ver tecnicos", key=f"btn_depto_{depto['id']}", use_container_width=True):
                    st.session_state["nivel"] = 2
                    st.session_state["departamento_id"] = int(depto["id"])
                    st.session_state["departamento_nombre"] = depto["nombre"]
                    st.rerun()

    st.markdown("---")

    # 4. Gráfico Comparativo Principal (Nivel 1): Barras Agrupadas
    st.markdown("### Comparativa de Incidencias por Departamento")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_deptos["nombre"],
        y=df_deptos["total_tickets"],
        name="Tickets Totales",
        marker_color=COLOR_PRIMARY,
        text=df_deptos["total_tickets"],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=df_deptos["nombre"],
        y=df_deptos["tickets_abiertos"],
        name="Tickets Abiertos",
        marker_color=COLOR_AMBER,
        text=df_deptos["tickets_abiertos"],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=df_deptos["nombre"],
        y=df_deptos["tickets_cerrados"],
        name="Tickets Cerrados",
        marker_color=COLOR_GREEN,
        text=df_deptos["tickets_cerrados"],
        textposition="outside",
    ))

    fig.update_layout(
        barmode="group",
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Departamento",
            showgrid=True,
            gridcolor=COLOR_GRID,
            griddash="dot",
            linecolor="#CBD5E1",
            tickfont=dict(size=12, color="#334155")
        ),
        yaxis=dict(
            title="Cantidad de Incidencias",
            showgrid=True,
            gridcolor=COLOR_GRID,
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
            font=dict(size=11, color="#334155")
        ),
        margin=dict(t=50, b=40, l=40, r=40),
    )

    st.plotly_chart(fig, use_container_width=True)
