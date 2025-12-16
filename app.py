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
    "ventas_manana_eur",
    "ventas_tarde_eur",
    "ventas_noche_eur",
    "ventas_total_eur",
    "observaciones"
]

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=COLUMNAS)

for col in COLUMNAS:
    if col not in df.columns:
        df[col] = ""

df["observaciones"] = df["observaciones"].fillna("")

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas", clear_on_submit=True):
    fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")

    c1, c2, c3 = st.columns(3)
    with c1:
        vm = st.number_input("Mañana (€)", min_value=0.0, step=10.0)
    with c2:
        vt = st.number_input("Tarde (€)", min_value=0.0, step=10.0)
    with c3:
        vn = st.number_input("Noche (€)", min_value=0.0, step=10.0)

    observaciones = st.text_area(
        "Observaciones del día",
        placeholder="Clima, eventos, incidencias, promociones, obras, festivos…",
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
# PREPARACIÓN (ISO)
# =========================
df = df.sort_values("fecha")

iso = df["fecha"].dt.isocalendar()
df["iso_year"] = iso.year
df["iso_week"] = iso.week
df["weekday"] = df["fecha"].dt.weekday
df["dow"] = df["weekday"].map(DOW_ES)

# =========================
# BLOQUE HOY
# =========================
st.divider()
st.subheader("HOY")

fecha_hoy = pd.to_datetime(date.today())
iso_hoy = fecha_hoy.isocalendar()

iso_year_hoy = iso_hoy.year
iso_week_hoy = iso_hoy.week
weekday_hoy = fecha_hoy.weekday()
dow_hoy = DOW_ES[weekday_hoy]

# --- Venta HOY ---
venta_hoy = df[df["fecha"] == fecha_hoy]

if venta_hoy.empty:
    vm_h = vt_h = vn_h = total_h = 0.0
else:
    fila = venta_hoy.iloc[0]
    vm_h = fila["ventas_manana_eur"]
    vt_h = fila["ventas_tarde_eur"]
    vn_h = fila["ventas_noche_eur"]
    total_h = fila["ventas_total_eur"]

# =========================
# DOW AÑO ANTERIOR — ISO CORRECTO
# =========================
cand = df[
    (df["iso_year"] == iso_year_hoy - 1) &
    (df["iso_week"] == iso_week_hoy) &
    (df["weekday"] == weekday_hoy)
]

nivel = "Exacto"

# Fallback ISO -1 / +1
if cand.empty:
    cand = df[
        (df["iso_year"] == iso_year_hoy - 1) &
        (df["iso_week"].isin([iso_week_hoy - 1, iso_week_hoy + 1])) &
        (df["weekday"] == weekday_hoy)
    ]
    nivel = "Aproximado"

if cand.empty:
    fecha_a_txt = "Sin histórico comparable fiable"
    vm_a = vt_a = vn_a = total_a = 0.0
else:
    comp = cand.sort_values("fecha").iloc[0]
    fecha_a_txt = (
        f"{DOW_ES[comp['weekday']]} · "
        f"{comp['fecha'].strftime('%d/%m/%Y')} ({nivel})"
    )
    vm_a = comp["ventas_manana_eur"]
    vt_a = comp["ventas_tarde_eur"]
    vn_a = comp["ventas_noche_eur"]
    total_a = comp["ventas_total_eur"]

# =========================
# CÁLCULOS DE VARIACIÓN
# =========================
def diff_and_pct(actual, base):
    diff = actual - base
    pct = (diff / base * 100) if base > 0 else 0
    return diff, pct

def color(v):
    if v > 0:
        return "green"
    if v < 0:
        return "red"
    return "gray"

def icono_variacion(pct):
    if pct >= 30:
        return "👁️"
    elif pct >= 1:
        return "↑"
    elif pct <= -30:
        return "⚠️"
    elif pct <= -1:
        return "↓"
    else:
        return ""

d_vm, p_vm = diff_and_pct(vm_h, vm_a)
d_vt, p_vt = diff_and_pct(vt_h, vt_a)
d_vn, p_vn = diff_and_pct(vn_h, vn_a)
d_tot, p_tot = diff_and_pct(total_h, total_a)

# =========================
# DISPOSICIÓN VISUAL
# =========================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**HOY**")
    st.caption(f"{dow_hoy} · {fecha_hoy.strftime('%d/%m/%Y')}")
    st.write("Mañana"); st.write(f"{vm_h:,.2f} €")
    st.write("Tarde"); st.write(f"{vt_h:,.2f} €")
    st.write("Noche"); st.write(f"{vn_h:,.2f} €")
    st.markdown("---")
    st.markdown(f"### TOTAL HOY\n{total_h:,.2f} €")

with c2:
    st.markdown("**DOW (Año anterior)**")
    st.caption(fecha_a_txt)
    st.write("Mañana"); st.write(f"{vm_a:,.2f} €")
    st.write("Tarde"); st.write(f"{vt_a:,.2f} €")
    st.write("Noche"); st.write(f"{vn_a:,.2f} €")
    st.markdown("---")
    st.markdown(f"### TOTAL DOW\n{total_a:,.2f} €")

with c3:
    st.markdown("**VARIACIÓN**")
    st.caption("Vs. DOW año anterior")

    st.markdown(
        f"**Mañana** <span style='color:{color(d_vm)}'>"
        f"{d_vm:+,.2f} € ({p_vm:+.1f}%) {icono_variacion(p_vm)}</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"**Tarde** <span style='color:{color(d_vt)}'>"
        f"{d_vt:+,.2f} € ({p_vt:+.1f}%) {icono_variacion(p_vt)}</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"**Noche** <span style='color:{color(d_vn)}'>"
        f"{d_vn:+,.2f} € ({p_vn:+.1f}%) {icono_variacion(p_vn)}</span>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        f"### TOTAL <span style='color:{color(d_tot)}'>"
        f"{d_tot:+,.2f} € ({p_tot:+.1f}%)</span>",
        unsafe_allow_html=True
    )

# =========================
# BITÁCORA DEL MES
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

df_mes = df[
    (df["fecha"].dt.month == fecha_hoy.month) &
    (df["fecha"].dt.year == fecha_hoy.year)
].copy()

df_mes["fecha_display"] = df_mes["fecha"].dt.strftime("%d-%m-%Y")
df_mes["fecha_display"] = df_mes.apply(
    lambda r: f"{r['fecha_display']} 👁️" if r["observaciones"].strip() else r["fecha_display"],
    axis=1
)

st.dataframe(
    df_mes[[
        "fecha_display",
        "dow",
        "ventas_manana_eur",
        "ventas_tarde_eur",
        "ventas_noche_eur",
        "ventas_total_eur",
        "observaciones"
    ]].rename(columns={"fecha_display": "fecha"}),
    hide_index=True,
    use_container_width=True
)
