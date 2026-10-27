"""
Componente de cabecera superior y barra lateral con perfil de usuario, rol y navegación.
"""
import streamlit as st


def render_header(title: str = None):
    """
    Renderiza la cabecera superior corporativa post-login.
    Formato: Mesa de Ayuda — Panel de Control | Rol: {rol}
    """
    rol = st.session_state.get("usuario_rol", "Administrador")
    username = st.session_state.get("username", "")

    header_text = title if title else f"Mesa de Ayuda — Panel de Control | Rol: {rol}"

    html = (
        f'<div class="header-container">'
        f'<div class="header-title">{header_text}</div>'
        f'<div class="header-badge">Usuario: {username} | Rol: {rol}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_sidebar():
    """
    Renderiza la barra lateral con información del perfil, filtros de nivel y logout.
    """
    username = st.session_state.get("username", "")
    rol = st.session_state.get("usuario_rol", "Administrador")
    nivel = st.session_state.get("nivel", 1)

    with st.sidebar:
        st.markdown("### Perfil de Acceso")
        st.markdown(f"**Usuario:** `{username}`")
        st.markdown(f"**Rol:** `{rol}`")
        st.markdown("---")

        st.markdown("### Navegacion Analitica")
        st.markdown(f"**Nivel Activo:** Nivel {nivel}")
        if st.session_state.get("departamento_nombre"):
            st.markdown(f"**Departamento:** {st.session_state['departamento_nombre']}")
        if st.session_state.get("tecnico_nombre"):
            st.markdown(f"**Tecnico:** {st.session_state['tecnico_nombre']}")

        st.markdown("---")
        if st.button("Cerrar Sesion", key="sidebar_btn_logout", use_container_width=True):
            st.session_state["logueado"] = False
            st.session_state["username"] = None
            st.session_state["usuario_rol"] = None
            st.session_state["nivel"] = 1
            st.session_state["departamento_id"] = None
            st.session_state["departamento_nombre"] = None
            st.session_state["tecnico_id"] = None
            st.session_state["tecnico_nombre"] = None
            st.rerun()
