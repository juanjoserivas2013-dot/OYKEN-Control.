import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="OYKEN · Control Operativo",
    layout="wide"
)

st.title("OYKEN · Control Operativo")
st.caption("Gestión diaria, comparables y criterio operativo")

# =========================
# CARGA DE DATOS
# =========================
DATA_FILE = Path("ventas.csv")

if not DATA_FILE.exists():
    st.warning("⚠️ No se ha encontrado el archivo ventas.csv")
    st.info("Crea un archivo ventas.csv para activar los comparables.")
    st.stop()

df = pd.read_csv(DATA_FILE)

# Aseguramos tipos
df["fecha"] = pd.to_datetime(df["fecha"])
df["ventas"] = pd.to_numeric(df["ventas"], errors="coerce")
df["tickets"] = pd.to_numeric(df["tickets"], errors="coerce")
df["comensales"] = pd.to_numeric(df["comensales"], errors="coerce")

# =========================
# FECHAS CLAVE
# =========================
hoy = date.today()
ayer = hoy - timedelta(days=1)
dow_hoy = hoy.weekday()  # lunes = 0

df_hoy = df[df["fecha"].dt.date == hoy]
df_ayer = df[df["fecha"].dt.date == ayer]
df_dow = df[df["fecha"].dt.weekday == dow_hoy]

# =========================
# FUNCIONES
# =========================
def variacion(actual, referencia):
    if referencia == 0 or pd.isna(referencia):
        return 0
    return (actual - referencia) / referencia * 100


def badge_variacion(valor):
    if valor >= 30:
        return "👁️"
    elif valor <= -25:
        return "⚠️"
    elif -25 < valor < 25:
        return "⬆️" if valor > 0 else "⬇️" if valor < 0 else ""
    return ""


# =========================
# BLOQUE HOY
# =========================
st.subheader("📅 HOY")

col1, col2, col3 = st.columns(3)

ventas_hoy = df_hoy["ventas"].sum()
tickets_hoy = df_hoy["tickets"].sum()
comensales_hoy = df_hoy["comensales"].sum()

ventas_ayer = df_ayer["ventas"].sum()
tickets_ayer = df_ayer["tickets"].sum()
comensales_ayer = df_ayer["comensales"].sum()

var_ventas = variacion(ventas_hoy, ventas_ayer)
var_tickets = variacion(tickets_hoy, tickets_ayer)
var_comensales = variacion(comensales_hoy, comensales_ayer)

with col1:
    st.metric(
        "Ventas (€)",
        f"{ventas_hoy:,.0f}",
        f"{var_ventas:+.1f}% {badge_variacion(var_ventas)}"
    )
    st.caption(f"Comensales: {comensales_hoy}")

with col2:
    st.metric(
        "Tickets",
        f"{tickets_hoy:,.0f}",
        f"{var_tickets:+.1f}% {badge_variacion(var_tickets)}"
    )
    st.caption(f"Comensales: {comensales_hoy}")

with col3:
    st.metric(
        "Comensales",
        f"{comensales_hoy:,.0f}",
        f"{var_comensales:+.1f}% {badge_variacion(var_comensales)}"
    )

# =========================
# BLOQUE DOW
# =========================
st.subheader("📊 Comparativa DOW (mismo día de la semana)")

ventas_dow = df_dow["ventas"].mean()
tickets_dow = df_dow["tickets"].mean()
comensales_dow = df_dow["comensales"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Ventas vs DOW",
        f"{ventas_hoy:,.0f}",
        f"{variacion(ventas_hoy, ventas_dow):+.1f}% {badge_variacion(variacion(ventas_hoy, ventas_dow))}"
    )

with col2:
    st.metric(
        "Tickets vs DOW",
        f"{tickets_hoy:,.0f}",
        f"{variacion(tickets_hoy, tickets_dow):+.1f}% {badge_variacion(variacion(tickets_hoy, tickets_dow))}"
    )

with col3:
    st.metric(
        "Comensales vs DOW",
        f"{comensales_hoy:,.0f}",
        f"{variacion(comensales_hoy, comensales_dow):+.1f}% {badge_variacion(variacion(comensales_hoy, comensales_dow))}"
    )

# =========================
# VARIACIONES DETALLADAS
# =========================
st.subheader("📉 Variaciones detalladas")

tabla_variaciones = pd.DataFrame({
    "Métrica": ["Ventas", "Tickets", "Comensales"],
    "Hoy": [ventas_hoy, tickets_hoy, comensales_hoy],
    "Ayer": [ventas_ayer, tickets_ayer, comensales_ayer],
    "Variación %": [
        f"{var_ventas:+.1f}%",
        f"{var_tickets:+.1f}%",
        f"{var_comensales:+.1f}%"
    ]
})

st.dataframe(tabla_variaciones, use_container_width=True)

# =========================
# BITÁCORA OPERATIVA
# =========================
st.subheader("📝 Bitácora operativa")

with st.form("bitacora"):
    nota = st.text_area("Observaciones del día")
    enviar = st.form_submit_button("Guardar")

    if enviar and nota.strip():
        st.success("Nota registrada (pendiente de persistencia)")
