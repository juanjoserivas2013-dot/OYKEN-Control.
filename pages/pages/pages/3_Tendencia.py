import streamlit as st

st.set_page_config(page_title="OYKEN · Tendencia", layout="centered")

st.title("OYKEN · Tendencia")
st.caption("Hacia dónde va el negocio")

st.divider()

st.subheader("ESTADÍSTICAS DE TENDENCIA")
st.markdown("_Segundo bloque_")

st.markdown("""
Estas explican **hacia dónde va el negocio**:

- **Media móvil 7 días**
- **Comparativa semana vs semana**
- **Comparativa mes vs mes**
- **Días fuertes vs días débiles**
""")

st.info("Aquí Oyken empieza a **anticipar**, no solo a mirar atrás.")
