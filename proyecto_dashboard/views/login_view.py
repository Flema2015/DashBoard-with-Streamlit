"""
Vista formal de inicio de sesión (Login View) corporativo sin emojis.
"""
import streamlit as st
from database.queries import validar_credenciales
from components.styles import inject_corporate_styles


def render_login_view():
    """
    Renderiza la pantalla de autenticación con placeholders formales y estética sobria.
    """
    inject_corporate_styles()

    st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)
    col_izq, col_centro, col_der = st.columns([1, 1.25, 1])

    with col_centro:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center; color: #1e3a8a; margin-bottom: 4px; font-weight: 700;'>Mesa de Ayuda TI</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.90rem; margin-bottom: 24px;'>Tablero de Control y Monitoreo de SLA</p>", unsafe_allow_html=True)

            with st.form("login_form_corporativo"):
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
                    st.warning("Debe ingresar su usuario y contraseña.")
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
