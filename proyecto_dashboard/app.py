"""
Punto de entrada principal, configuración de página y router de sesión/vistas.
Mesa de Ayuda TI — Panel de Control y Monitoreo de SLA.
"""
import os
import sys
import streamlit as st

# Garantizar que el directorio actual esté en sys.path para resolución de módulos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database.schema_seed import init_db
from components.styles import inject_corporate_styles
from components.header_sidebar import render_header, render_sidebar
from views.login_view import render_login_view
from views.nivel1_deptos import render_nivel1_view
from views.nivel2_tecnicos import render_nivel2_view
from views.nivel3_tickets import render_nivel3_view

# Configuración formal de la página de Streamlit
st.set_page_config(
    page_title="Mesa de Ayuda TI - Panel de Control",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar y verificar esquema y datos semilla de SQLite
init_db()


def inicializar_session_state():
    """Inicializa todas las claves requeridas para control de sesión y niveles."""
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


def main():
    """Función de enrutamiento principal."""
    inicializar_session_state()

    if not st.session_state["logueado"]:
        render_login_view()
    else:
        inject_corporate_styles()
        render_header()
        render_sidebar()

        nivel = st.session_state.get("nivel", 1)
        if nivel == 1:
            render_nivel1_view()
        elif nivel == 2:
            render_nivel2_view()
        elif nivel == 3:
            render_nivel3_view()


if __name__ == "__main__":
    main()
