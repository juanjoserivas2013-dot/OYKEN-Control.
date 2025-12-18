import streamlit as st

st.set_page_config(
    page_title="OYKEN",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Menú")
st.sidebar.write("selecciona un módulo")

st.title("OYKEN")
st.caption("Sistema operativo de gestión")
st.markdown("Selecciona un módulo en el menú lateral")
