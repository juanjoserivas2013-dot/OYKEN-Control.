import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OYKEN · Control Operativo", layout="centered")

st.title("OYKEN · Control Operativo")
st.markdown("**Entra en Oyken. En 30 segundos entiendes mejor tu negocio.**")
st.caption("Sistema automático basado en criterio operativo")

DATA_FILE = Path("ventas.csv")

DOW_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

COLUMNAS = [
    "fecha",
    "ventas_manana_eur", "ventas_tarde_eur", "ventas_noche_eur", "ventas_total_eur",
    "comensales_manana", "comensales_tarde", "comensales_noche",
    "tickets_manana", "tickets_tarde", "tickets_noche",
    "observaciones"
]

# =========================
# ESTADO · FECHA ACTIVA
# =========================
if "fecha_activa" not in st.session_state:
    st.session_state.fecha_activa = date.today()

# =========================
# MENÚ PRINCIPAL
# =========================
st.sidebar.title("OYKEN")

seccion = st.sidebar.radio(
    "Navegación",
    [
        "📊 Control Diario",
        "👥 Comportamiento",
        "📈 Tendencia",
        "🧠 Oyken Core"
    ]
)

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=COLUMNAS)

for col in COLUMNAS:
    if col not in df.columns:
        df[col] = 0 if col not in ["fecha", "observaciones"] else ""

df["observaciones"] = df["observaciones"].fillna("")

if df.empty:
    df = pd.DataFrame(columns=COLUMNAS)

# =========================
# PREPARACIÓN ISO
# =========================
if not df.empty:
    df = df.sort_values("fecha")
    iso = df["fecha"].dt.isocalendar()
    df["iso_year"] = iso.year
    df["iso_week"] = iso.week
    df["weekday"] = df["fecha"].dt.weekday
    df["dow"] = df["weekday"].map(DOW_ES)

# ==========================================================
# 📊 CONTROL DIARIO
# ==========================================================
if seccion == "📊 Control Diario":

    st.subheader("Registro diario")

    with st.form("form_ventas", clear_on_submit=True):
        fecha = st.date_input(
            "Fecha",
            value=st.session_state.fecha_activa,
            format="DD/MM/YYYY"
        )
        st.session_state.fecha_activa = fecha

        st.markdown("**Ventas (€)**")
        v1, v2, v3 = st.columns(3)
        vm = v1.number_input("Mañana", min_value=0.0, step=10.0)
        vt = v2.number_input("Tarde", min_value=0.0, step=10.0)
        vn = v3.number_input("Noche", min_value=0.0, step=10.0)

        st.markdown("**Comensales**")
        c1, c2, c3 = st.columns(3)
        cm = c1.number_input("Mañana ", min_value=0, step=1)
        ct = c2.number_input("Tarde ", min_value=0, step=1)
        cn = c3.number_input("Noche ", min_value=0, step=1)

        st.markdown("**Tickets**")
        t1, t2, t3 = st.columns(3)
        tm = t1.number_input("Mañana  ", min_value=0, step=1)
        tt = t2.number_input("Tarde  ", min_value=0, step=1)
        tn = t3.number_input("Noche  ", min_value=0, step=1)

        observaciones = st.text_area(
            "Observaciones del día",
            placeholder="Clima, eventos, incidencias, promociones…",
            height=100
        )

        guardar = st.form_submit_button("Guardar venta")

    if guardar:
        total = vm + vt + vn
        nueva = pd.DataFrame([{
            "fecha": pd.to_datetime(fecha),
            "ventas_manana_eur": vm,
            "ventas_tarde_eur": vt,
            "ventas_noche_eur": vn,
            "ventas_total_eur": total,
            "comensales_manana": cm,
            "comensales_tarde": ct,
            "comensales_noche": cn,
            "tickets_manana": tm,
            "tickets_tarde": tt,
            "tickets_noche": tn,
            "observaciones": observaciones.strip()
        }])

        df = pd.concat([df, nueva], ignore_index=True)
        df = df.drop_duplicates(subset=["fecha"], keep="last")
        df.to_csv(DATA_FILE, index=False)
        st.success("Venta guardada correctamente")
        st.rerun()

    if df.empty:
        st.info("Aún no hay ventas registradas.")
        st.stop()

    # =========================
    # BLOQUE HOY (DINÁMICO)
    # =========================
    st.divider()
    st.subheader("HOY")

    fecha_hoy = pd.to_datetime(st.session_state.fecha_activa)
    iso_hoy = fecha_hoy.isocalendar()

    fila = df[df["fecha"] == fecha_hoy]

    if fila.empty:
        st.info("No hay datos para la fecha seleccionada.")
        st.stop()

    f = fila.iloc[0]

    total_h = f["ventas_total_eur"]
    com_h = f["comensales_manana"] + f["comensales_tarde"] + f["comensales_noche"]
    tic_h = f["tickets_manana"] + f["tickets_tarde"] + f["tickets_noche"]

    st.markdown(f"**{DOW_ES[fecha_hoy.weekday()]} · {fecha_hoy.strftime('%d/%m/%Y')}**")
    st.metric("Ventas totales", f"{total_h:,.2f} €")
    st.metric("Comensales", com_h)
    st.metric("Tickets", tic_h)

# ==========================================================
# 👥 COMPORTAMIENTO
# ==========================================================
elif seccion == "👥 Comportamiento":

    st.subheader("Comportamiento del cliente")
    st.caption("Valores agregados · Comparativa vs mismo DOW del año anterior")

    fecha_ref = pd.to_datetime(st.session_state.fecha_activa)
    iso_ref = fecha_ref.isocalendar()

    df_hoy = df[df["fecha"] == fecha_ref]
    if df_hoy.empty:
        st.info("No hay datos para la fecha seleccionada.")
        st.stop()

    h = df_hoy.iloc[0]

    ventas_h = h["ventas_total_eur"]
    com_h = h["comensales_manana"] + h["comensales_tarde"] + h["comensales_noche"]
    tic_h = h["tickets_manana"] + h["tickets_tarde"] + h["tickets_noche"]

    tpc_h = tic_h / com_h if com_h > 0 else 0
    epc_h = ventas_h / com_h if com_h > 0 else 0

    df_dow = df[
        (df["iso_year"] == iso_ref.year - 1) &
        (df["iso_week"] == iso_ref.week) &
        (df["weekday"] == fecha_ref.weekday())
    ]

    if df_dow.empty:
        st.info("No hay histórico comparable.")
        st.stop()

    a = df_dow.iloc[0]

    ventas_a = a["ventas_total_eur"]
    com_a = a["comensales_manana"] + a["comensales_tarde"] + a["comensales_noche"]
    tic_a = a["tickets_manana"] + a["tickets_tarde"] + a["tickets_noche"]

    tpc_a = tic_a / com_a if com_a > 0 else 0
    epc_a = ventas_a / com_a if com_a > 0 else 0

    def diff_pct(act, base):
        d = act - base
        p = (d / base * 100) if base > 0 else 0
        return d, p

    d_tpc, p_tpc = diff_pct(tpc_h, tpc_a)
    d_epc, p_epc = diff_pct(epc_h, epc_a)

    st.markdown("### Tickets por comensal")
    st.write(f"HOY: **{tpc_h:.2f}**")
    st.write(f"DOW: **{tpc_a:.2f}**")
    st.write(f"VARIACIÓN: **{d_tpc:+.2f} ({p_tpc:+.1f}%)**")

    st.divider()

    st.markdown("### € por comensal")
    st.write(f"HOY: **{epc_h:,.2f} €**")
    st.write(f"DOW: **{epc_a:,.2f} €**")
    st.write(f"VARIACIÓN: **{d_epc:+.2f} € ({p_epc:+.1f}%)**")

# ==========================================================
# 📈 TENDENCIA
# ==========================================================
elif seccion == "📈 Tendencia":
    st.subheader("Tendencia")
    st.info("Módulo en construcción")

# ==========================================================
# 🧠 OYKEN CORE
# ==========================================================
elif seccion == "🧠 Oyken Core":
    st.subheader("Oyken Core")
    st.info("Análisis inteligente en desarrollo")

