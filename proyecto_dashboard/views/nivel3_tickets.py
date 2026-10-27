"""
Vista Nivel 3: Detalle de Tickets del Técnico.
Incluye retorno Drill Up a Nivel 2, referencia de semáforo, listado en tarjetas/tabla
y gráficos de distribución de tickets según su Prioridad y según su Estado.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import (
    COLOR_RED,
    COLOR_AMBER,
    COLOR_PRIMARY,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_GRID,
    COLOR_CRITICAL,
)
from database.queries import (
    obtener_tickets_por_tecnico,
    obtener_distribucion_prioridad_tecnico,
    obtener_distribucion_estado_tecnico,
)
from components.kpi_cards import render_semaphore_reference
from components.styles import get_semaphore_badge


def render_nivel3_view():
    """
    Renderiza la vista de Nivel 3 (Detalle de tickets asignados al técnico).
    """
    tecnico_id = st.session_state.get("tecnico_id")
    tecnico_nombre = st.session_state.get("tecnico_nombre", "General")
    depto_nombre = st.session_state.get("departamento_nombre", "General")

    # 1. Botón superior de retorno: <- Volver a tecnicos (Drill Up)
    col_retorno, col_bread = st.columns([1.8, 5])
    with col_retorno:
        if st.button("<- Volver a tecnicos", key="btn_volver_tecnicos"):
            st.session_state["nivel"] = 2
            st.session_state["tecnico_id"] = None
            st.session_state["tecnico_nombre"] = None
            st.rerun()

    with col_bread:
        bread_html = f'<div class="breadcrumb-box">Departamentos &nbsp;/&nbsp; {depto_nombre} &nbsp;/&nbsp; <strong>{tecnico_nombre}</strong></div>'
        st.markdown(bread_html, unsafe_allow_html=True)

    # 2. Título formal sin emojis
    st.subheader(f"Nivel 3: Detalle de Tickets — Tecnico: {tecnico_nombre}")

    # 3. Referencia del semáforo visible
    render_semaphore_reference()

    # 4. Obtención de datos mediante consulta SQL con JOIN
    df_tickets = obtener_tickets_por_tecnico(tecnico_id)
    if df_tickets.empty:
        st.info("Sin tickets registrados para este tecnico.")
        return

    # Sanitización explícita del campo fecha_cierre para evitar NaN o None en pantalla
    df_tickets["fecha_cierre"] = (
        df_tickets["fecha_cierre"]
        .fillna("En curso")
        .apply(lambda val: "En curso" if pd.isna(val) or str(val).strip() in ("", "None", "nan", "NaN") else str(val))
    )

    # Selector de modalidad visual (Tarjetas formales o Tabla estilizada)
    modalidad = st.radio(
        "Modalidad de presentacion:",
        ["Tarjetas Operativas", "Tabla Estilizada de Registros"],
        horizontal=True,
    )

    if modalidad == "Tarjetas Operativas":
        for _, t in df_tickets.iterrows():
            with st.container(border=True):
                col_id_tit, col_prio, col_est = st.columns([4, 2, 2])
                with col_id_tit:
                    st.markdown(f"**ID Ticket #{t['id']} — {t['titulo']}**")
                with col_prio:
                    st.markdown(f"<span class='prio-{t['prioridad']}'>Prioridad {t['prioridad'].upper()}</span>", unsafe_allow_html=True)
                with col_est:
                    est_class = "estado-abierto" if t["estado"] == "abierto" else "estado-cerrado"
                    st.markdown(f"<span class='{est_class}'>Estado: {t['estado'].capitalize()}</span>", unsafe_allow_html=True)

                col_sol, col_sla, col_ap, col_ci = st.columns(4)
                with col_sol:
                    st.markdown(f"**Reportado por (Solicitante):**<br>{t['solicitante']}", unsafe_allow_html=True)
                with col_sla:
                    st.markdown(f"**SLA (horas):**<br>{t['sla_horas']} hs", unsafe_allow_html=True)
                with col_ap:
                    st.markdown(f"**Fecha de Apertura:**<br>{t['fecha_apertura']}", unsafe_allow_html=True)
                with col_ci:
                    cierre_raw = t["fecha_cierre"]
                    cierre_str = (
                        "En curso"
                        if pd.isna(cierre_raw) or str(cierre_raw).strip() in ("", "None", "nan", "NaN")
                        else str(cierre_raw)
                    )
                    st.markdown(f"**Fecha de Cierre:**<br>{cierre_str}", unsafe_allow_html=True)

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                col_computo, col_sem = st.columns([5, 3])
                with col_computo:
                    st.markdown(f"Tiempo transcurrido: **{t['horas_transcurridas']} hs** (Limite SLA: {t['sla_horas']} hs)")
                with col_sem:
                    st.markdown(get_semaphore_badge(t["semaforo"]), unsafe_allow_html=True)
    else:
        df_grid = df_tickets[[
            "id", "titulo", "solicitante", "prioridad", "estado",
            "sla_horas", "horas_transcurridas", "fecha_apertura", "fecha_cierre", "semaforo"
        ]].copy()
        df_grid.columns = [
            "ID Ticket", "Titulo", "Reportado por (Solicitante)", "Prioridad", "Estado",
            "SLA (horas)", "Horas Usadas", "Fecha de Apertura", "Fecha de Cierre", "Semáforo"
        ]
        df_grid["Fecha de Cierre"] = (
            df_grid["Fecha de Cierre"]
            .fillna("En curso")
            .replace({None: "En curso", "nan": "En curso", "NaN": "En curso", "None": "En curso", "": "En curso"})
        )
        st.dataframe(df_grid, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 5. Gráficos de Nivel 3: Distribución por Prioridad y por Estado
    st.markdown(f"### Distribucion de Incidencias — Tecnico: {tecnico_nombre}")
    col_g1, col_g2 = st.columns(2)

    df_prio = obtener_distribucion_prioridad_tecnico(tecnico_id)
    df_estado = obtener_distribucion_estado_tecnico(tecnico_id)

    with col_g1:
        if not df_prio.empty:
            fig_prio = px.pie(
                df_prio,
                names="prioridad",
                values="cantidad",
                hole=0.55,
                color="prioridad",
                color_discrete_map={
                    "critica": COLOR_CRITICAL,
                    "alta": COLOR_RED,
                    "media": COLOR_AMBER,
                    "baja": COLOR_PRIMARY,
                },
            )
            fig_prio.update_traces(
                textposition="inside",
                textinfo="percent+label+value",
                marker=dict(line=dict(color="#FFFFFF", width=2)),
            )
            fig_prio.update_layout(
                title=dict(
                    text="Distribucion segun Prioridad",
                    font=dict(size=14, color="#1e293b", family="Segoe UI, Arial, sans-serif")
                ),
                template="plotly_white",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11, color="#334155")
                ),
                margin=dict(t=35, b=40, l=20, r=20),
            )
            st.plotly_chart(fig_prio, use_container_width=True)
        else:
            st.info("Sin datos de prioridad para graficar.")

    with col_g2:
        if not df_estado.empty:
            fig_estado = go.Figure(go.Bar(
                x=df_estado["estado"].str.capitalize(),
                y=df_estado["cantidad"],
                marker_color=[COLOR_CYAN if e == "abierto" else COLOR_GREEN for e in df_estado["estado"]],
                text=df_estado["cantidad"],
                textposition="outside",
            ))
            fig_estado.update_layout(
                title=dict(
                    text="Distribucion segun Estado (Abiertos vs. Cerrados)",
                    font=dict(size=14, color="#1e293b", family="Segoe UI, Arial, sans-serif")
                ),
                template="plotly_white",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    title="Estado del Ticket",
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
                margin=dict(t=35, b=40, l=20, r=20),
            )
            st.plotly_chart(fig_estado, use_container_width=True)
        else:
            st.info("Sin datos de estado para graficar.")
