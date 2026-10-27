"""
Vista Nivel 2: Técnicos del Departamento seleccionado.
Incluye retorno Drill Up a Nivel 1, referencia de semáforo, lista con Drill Down a Nivel 3
y gráfico comparativo de carga de tickets (Abiertos vs. Cerrados) por técnico.
"""
import streamlit as st
import plotly.graph_objects as go

from config import (
    COLOR_AMBER,
    COLOR_GREEN,
    COLOR_GRID,
)
from database.queries import obtener_tecnicos_por_departamento
from components.kpi_cards import render_semaphore_reference
from components.styles import get_semaphore_badge


def render_nivel2_view():
    """
    Renderiza la vista de Nivel 2 (Técnicos por Departamento).
    """
    depto_id = st.session_state.get("departamento_id")
    depto_nombre = st.session_state.get("departamento_nombre", "General")

    # 1. Botón superior de retorno: <- Volver a departamentos (Drill Up)
    col_retorno, col_bread = st.columns([1.8, 5])
    with col_retorno:
        if st.button("<- Volver a departamentos", key="btn_volver_deptos"):
            st.session_state["nivel"] = 1
            st.session_state["departamento_id"] = None
            st.session_state["departamento_nombre"] = None
            st.rerun()

    with col_bread:
        bread_html = f'<div class="breadcrumb-box">Departamentos &nbsp;/&nbsp; <strong>{depto_nombre}</strong></div>'
        st.markdown(bread_html, unsafe_allow_html=True)

    # 2. Título formal sin emojis
    st.subheader(f"Nivel 2: Tecnicos del Departamento de {depto_nombre}")

    # 3. Referencia del semáforo visible
    render_semaphore_reference()

    # 4. Listado de técnicos del departamento seleccionado
    df_tecnicos = obtener_tecnicos_por_departamento(depto_id)
    if df_tecnicos.empty:
        st.info("No se registran tecnicos asignados a este departamento.")
        return

    st.markdown("### Tecnicos Asignados")
    for _, tec in df_tecnicos.iterrows():
        with st.container(border=True):
            col_nom, col_stats, col_sem, col_btn = st.columns([3, 3.2, 2.3, 1.8])
            with col_nom:
                st.markdown(f"**{tec['nombre']}**")
            with col_stats:
                st.markdown(
                    f"{int(tec['total_tickets'])} asignados | "
                    f"{int(tec['tickets_abiertos'])} abiertos | "
                    f"{int(tec['tickets_cerrados'])} cerrados"
                )
            with col_sem:
                st.markdown(get_semaphore_badge(tec["semaforo"]), unsafe_allow_html=True)
            with col_btn:
                if st.button("Ver tickets", key=f"btn_tec_{tec['id']}", use_container_width=True):
                    st.session_state["nivel"] = 3
                    st.session_state["tecnico_id"] = int(tec["id"])
                    st.session_state["tecnico_nombre"] = tec["nombre"]
                    st.rerun()

    st.markdown("---")

    # 5. Gráfico de Nivel 2: Comparativa de Carga (Abiertos vs. Cerrados) por Técnico
    st.markdown(f"### Comparativa de Carga de Tickets por Tecnico — {depto_nombre}")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_tecnicos["nombre"],
        y=df_tecnicos["tickets_abiertos"],
        name="Tickets Abiertos",
        marker_color=COLOR_AMBER,
        text=df_tecnicos["tickets_abiertos"],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=df_tecnicos["nombre"],
        y=df_tecnicos["tickets_cerrados"],
        name="Tickets Cerrados",
        marker_color=COLOR_GREEN,
        text=df_tecnicos["tickets_cerrados"],
        textposition="outside",
    ))

    fig.update_layout(
        barmode="group",
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Tecnico Asignado",
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
