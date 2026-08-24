import streamlit as st
st.title("Mesa de ayuda")
departamento = st.selectbox("Elegí un depto", ["IT", "RRHH", "Ventas"])  
st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")
st.write(f"Mostrando tickets de {departamento}") 
if departamento == "IT":
    st.write("Técnico 1: Juan Pérez")
    st.write("Técnico 2: María Gómez")
if "nivel" not in st.session_state:
    st.session_state.nivel = 1
    st.session_state.depto_elegido = None

if st.session_state.nivel == 1:
    # mostrás la tabla de deptos
    if st.button("Ver técnicos de IT"):
        st.session_state.depto_elegido = "IT"
        st.session_state.nivel = 2  # bajás de nivel

elif st.session_state.nivel == 2:
    # consultás SQL filtrando por st.session_state.depto_elegido
    if st.button("← Volver"):
        st.session_state.nivel = 1  # subís de nivel