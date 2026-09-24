import streamlit as st
import sqlite3
import bcrypt
import plotly.express as px

DB_PATH = "mesa_ayuda.db"

# Mapeo de emoji de semáforo a color real para los gráficos
COLOR_SEMAFORO = {"🟢": "#1D9E75", "🟡": "#BA7517", "🔴": "#E24B4A"}


def leyenda_semaforo():
    """Referencia de qué significa cada color. Se muestra en TODAS las pantallas del tablero."""
    st.caption("🟢 Dentro de SLA · 🟡 Por vencer (menos del 20% del tiempo restante) · 🔴 Vencido / fuera de SLA")


# ------------------------------------------------------
# Lógica de validación (separada de la interfaz)
# ------------------------------------------------------
def validar_credenciales(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash, nombre_completo FROM usuarios_sistema WHERE username = ?",
        (username,),
    )
    resultado = cursor.fetchone()
    conn.close()

    if resultado is None:
        return False, None

    password_hash_guardado, nombre_completo = resultado
    coincide = bcrypt.checkpw(password.encode(), password_hash_guardado.encode())

    return (True, nombre_completo) if coincide else (False, None)


# ------------------------------------------------------
# Pantalla de login
# ------------------------------------------------------
def pantalla_login():
    st.title("Mesa de Ayuda IT")
    st.subheader("Iniciar sesión")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")

    if submit:
        valido, nombre = validar_credenciales(username, password)
        if valido:
            st.session_state.logueado = True
            st.session_state.nombre_usuario = nombre
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")


# ------------------------------------------------------
# DATOS DE EJEMPLO (fijos, solo para maquetar el diseño)
# En el próximo paso esto se reemplaza por consultas SQL reales.
# ------------------------------------------------------
DATOS_DEPARTAMENTOS = [
    {"nombre": "Sistemas", "tickets_abiertos": 4, "semaforo": "🔴"},
    {"nombre": "Recursos Humanos", "tickets_abiertos": 1, "semaforo": "🟢"},
    {"nombre": "Ventas", "tickets_abiertos": 2, "semaforo": "🟡"},
]

DATOS_TECNICOS = {
    "Sistemas": [
        {"nombre": "Marcos Ibáñez", "tickets": 3, "semaforo": "🟡"},
        {"nombre": "Julieta Fernández", "tickets": 2, "semaforo": "🟢"},
    ],
    "Recursos Humanos": [
        {"nombre": "Nicolás Paz", "tickets": 1, "semaforo": "🟢"},
    ],
    "Ventas": [
        {"nombre": "Sofía Ramírez", "tickets": 2, "semaforo": "🔴"},
    ],
}

# Cada ticket ahora incluye: quién lo reportó (usuario), cuándo se abrió
# y cuándo se cerró (o "-" si sigue abierto).
DATOS_TICKETS = {
    "Marcos Ibáñez": [
        {
            "titulo": "Error al iniciar sesión",
            "prioridad": "alta",
            "estado": "abierto",
            "semaforo": "🔴",
            "usuario": "Carla Gómez",
            "fecha_apertura": "2026-08-29 07:00",
            "fecha_cierre": "-",
        },
        {
            "titulo": "No enciende la PC",
            "prioridad": "alta",
            "estado": "cerrado",
            "semaforo": "🟢",
            "usuario": "Diego Torres",
            "fecha_apertura": "2026-08-20 09:00",
            "fecha_cierre": "2026-08-20 14:00",
        },
    ],
    "Julieta Fernández": [
        {
            "titulo": "Impresora de red no responde",
            "prioridad": "media",
            "estado": "abierto",
            "semaforo": "🟡",
            "usuario": "Carla Gómez",
            "fecha_apertura": "2026-08-28 08:00",
            "fecha_cierre": "-",
        },
    ],
}


# ------------------------------------------------------
# Nivel 1: Departamentos
# ------------------------------------------------------
def nivel1_departamentos():
    st.title(f"Mesa de Ayuda — Bienvenido, {st.session_state.nombre_usuario} 👋")
    st.subheader("Nivel 1: Departamentos")
    leyenda_semaforo()

    for depto in DATOS_DEPARTAMENTOS:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 2])
        col1.write(depto["nombre"])
        col2.write(f"{depto['tickets_abiertos']} tickets abiertos")
        col3.write(depto["semaforo"])
        if col4.button("Ver técnicos", key=f"depto_{depto['nombre']}"):
            st.session_state.nivel = 2
            st.session_state.depto_elegido = depto["nombre"]
            st.rerun()

    fig = px.bar(
        DATOS_DEPARTAMENTOS,
        x="tickets_abiertos",
        y="nombre",
        orientation="h",
        color="semaforo",
        color_discrete_map=COLOR_SEMAFORO,
        labels={"tickets_abiertos": "Tickets abiertos", "nombre": "Departamento"},
    )
    fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    if st.button("Cerrar sesión"):
        st.session_state.logueado = False
        st.rerun()


# ------------------------------------------------------
# Nivel 2: Técnicos del departamento elegido
# ------------------------------------------------------
def nivel2_tecnicos():
    depto = st.session_state.depto_elegido
    st.title(f"Nivel 2: Técnicos — {depto}")
    leyenda_semaforo()

    if st.button("← Volver a departamentos"):
        st.session_state.nivel = 1
        st.rerun()

    tecnicos_depto = DATOS_TECNICOS.get(depto, [])
    for tec in tecnicos_depto:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 2])
        col1.write(tec["nombre"])
        col2.write(f"{tec['tickets']} tickets")
        col3.write(tec["semaforo"])
        if col4.button("Ver tickets", key=f"tec_{tec['nombre']}"):
            st.session_state.nivel = 3
            st.session_state.tecnico_elegido = tec["nombre"]
            st.rerun()

    if tecnicos_depto:
        fig = px.bar(
            tecnicos_depto,
            x="tickets",
            y="nombre",
            orientation="h",
            color="semaforo",
            color_discrete_map=COLOR_SEMAFORO,
            labels={"tickets": "Tickets asignados", "nombre": "Técnico"},
        )
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------
# Nivel 3: Detalle de tickets del técnico elegido
# ------------------------------------------------------
def nivel3_detalle():
    tecnico = st.session_state.tecnico_elegido
    st.title(f"Nivel 3: Tickets de {tecnico}")
    leyenda_semaforo()

    if st.button("← Volver a técnicos"):
        st.session_state.nivel = 2
        st.rerun()

    tickets = DATOS_TICKETS.get(tecnico, [])
    if not tickets:
        st.info("Sin datos de ejemplo cargados para este técnico todavía.")

    for t in tickets:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown(f"**{t['titulo']}**")
            col2.write(f"Prioridad: {t['prioridad']}")
            col3.write(f"{t['semaforo']} {t['estado']}")

            col4, col5, col6 = st.columns(3)
            col4.write(f"👤 Reportado por: {t['usuario']}")
            col5.write(f"🗓️ Apertura: {t['fecha_apertura']}")
            col6.write(f"✅ Cierre: {t['fecha_cierre']}")

    if tickets:
        fig = px.pie(tickets, names="prioridad", title="Distribución por prioridad")
        st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------
# Router de niveles (decide qué pantalla del tablero mostrar)
# ------------------------------------------------------
def pantalla_principal():
    if "nivel" not in st.session_state:
        st.session_state.nivel = 1

    if st.session_state.nivel == 1:
        nivel1_departamentos()
    elif st.session_state.nivel == 2:
        nivel2_tecnicos()
    elif st.session_state.nivel == 3:
        nivel3_detalle()


# ------------------------------------------------------
# Punto de entrada: decide qué pantalla mostrar
# ------------------------------------------------------
if "logueado" not in st.session_state:
    st.session_state.logueado = False

if st.session_state.logueado:
    pantalla_principal()
else:
    pantalla_login()