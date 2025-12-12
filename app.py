import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="OYKEN · Ventas", layout="centered")

st.title("OYKEN · Ventas")
st.caption("Registro y control de ventas (prototipo operativo)")

# --- Configuración archivo ---
DATA_FILE = Path("ventas.csv")

# --- Cargar o crear datos ---
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=["fecha", "ventas_eur"])

# --- Formulario de entrada ---
with st.form("form_ventas"):
    fecha = st.date_input("Fecha")
    ventas = st.number_input("Ventas (€)", min_value=0.0, step=10.0, format="%.2f")
    guardar = st.form_submit_button("Guardar")

if guardar:
    nueva_fila = pd.DataFrame(
        [{"fecha": pd.to_datetime(fecha), "ventas_eur": ventas}]
    )
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("Venta guardada correctamente")

st.divider()

# --- Filtros ---
st.subheader("Listado de ventas")

if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input(
            "Desde", df["fecha"].min().date()
        )
    with col2:
        fecha_fin = st.date_input(
            "Hasta", df["fecha"].max().date()
        )

    mask = (
        (df["fecha"].dt.date >= fecha_inicio)
        & (df["fecha"].dt.date <= fecha_fin)
    )
    df_filtrado = df.loc[mask].sort_values("fecha")

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True,
    )

    total = df_filtrado["ventas_eur"].sum()
    st.metric("Total periodo (€)", f"{total:,.2f} €")

else:
    st.info("Aún no hay ventas registradas.")
