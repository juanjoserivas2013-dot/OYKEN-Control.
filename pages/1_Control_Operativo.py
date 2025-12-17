import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# ==============================
# TÍTULO DE LA PÁGINA
# ==============================
st.title("OYKEN · Control Operativo")
st.markdown("**Entra en Oyken. En 30 segundos entiendes mejor tu negocio.**")
st.caption("Sistema automático basado en criterio operativo")

st.divider()

# ==============================
# CARGA DE DATOS
# ==============================
DATA_FILE = Path("ventas.csv")

if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    st.warning("No se ha encontrado el archivo ventas.csv")
    st.stop()

# ==============================
# FILTRO DE FECHA
# ==============================
fecha_seleccionada = st.date_input(
    "Selecciona una fecha",
    value=date.today()
)

df_dia = df[df["fecha"].dt.date == fecha_seleccionada]

if df_dia.empty:
    st.info("No hay datos para la fecha seleccionada")
    st.stop()

st.divider()

# ==============================
# KPIs PRINCIPALES
# ==============================
ventas_total = df_dia["ventas"].sum()
comensales = df_dia["comensales"].sum()
tickets = df_dia["tickets"].sum()

ticket_medio = ventas_total / tickets if tickets > 0 else 0
venta_por_comensal = ventas_total / comensales if comensales > 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Ventas (€)", f"{ventas_total:,.2f}")
col2.metric("Comensales", int(comensales))
col3.metric("Tickets", int(tickets))
col4.metric("Ticket medio (€)", f"{ticket_medio:,.2f}")

st.divider()

# ==============================
# RATIOS OPERATIVOS
# ==============================
st.subheader("Ratios operativos")

col1, col2 = st.columns(2)

col1.metric("€ / Comensal", f"{venta_por_comensal:,.2f}")
col2.metric("Tickets / Comensal", f"{tickets / comensales:.2f}" if comensales > 0 else "0")

# ==============================
# TABLA DETALLE
# ==============================
st.subheader("Detalle del día")
st.dataframe(
    df_dia.sort_values("fecha"),
    use_container_width=True
)
