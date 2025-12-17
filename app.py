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
# HELPERS FORMATO
# =========================
def fmt_var(value, decimals=2):
    if value > 0:
        return f"+{value:,.{decimals}f}"
    if value < 0:
        return f"{value:,.{decimals}f}"
    return f"{value:,.{decimals}f}"

def fmt_pct(p):
    if p > 0:
        return f"+{p:.1f}%"
    if p < 0:
        return f"{p:.1f}%"
    return "0.0%"

def diff_pct(actual, base):
    d = actual - base
    p = (d / base * 100) if base > 0 else (100.0 if actual > 0 else 0.0)
    return d, p

def color(v):
    return "green" if v > 0 else "red" if v < 0 else "gray"

def icono(p):
    if p > 0:
        return "↑"
    if p < 0:
        return "↓"
    return ""

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

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas", clear_on_submit=True):
    fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")

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
# PREPARACIÓN ISO
# =========================
df = df.sort_values("fecha")
iso = df["fecha"].dt.isocalendar()
df["iso_year"] = iso.year
df["iso_week"] = iso.week
df["weekday"] = df["fecha"].dt.weekday
df["dow"] = df["weekday"].map(DOW_ES)

# =========================
# HOY
# =========================
st.divider()
st.subheader("HOY")

fecha_hoy = pd.to_datetime(date.today())
iso_hoy = fecha_hoy.isocalendar()

venta_hoy = df[df["fecha"] == fecha_hoy]
fila = venta_hoy.iloc[0] if not venta_hoy.empty else None

def v(col):
    return fila[col] if fila is not None else 0

vm_h, vt_h, vn_h, total_h = v("ventas_manana_eur"), v("ventas_tarde_eur"), v("ventas_noche_eur"), v("ventas_total_eur")
cm_h, ct_h, cn_h = v("comensales_manana"), v("comensales_tarde"), v("comensales_noche")
tm_h, tt_h, tn_h = v("tickets_manana"), v("tickets_tarde"), v("tickets_noche")

tmed_m_h = vm_h / tm_h if tm_h > 0 else 0
tmed_t_h = vt_h / tt_h if tt_h > 0 else 0
tmed_n_h = vn_h / tn_h if tn_h > 0 else 0
tmed_tot_h = total_h / (tm_h + tt_h + tn_h) if (tm_h + tt_h + tn_h) > 0 else 0

# =========================
# DOW AÑO ANTERIOR
# =========================
dow_ant = df[
    (df["iso_year"] == iso_hoy.year - 1) &
    (df["iso_week"] == iso_hoy.week) &
    (df["weekday"] == fecha_hoy.weekday())
]

if dow_ant.empty:
    vm_a = vt_a = vn_a = total_a = 0
    cm_a = ct_a = cn_a = 0
    tm_a = tt_a = tn_a = 0
    fecha_dow_txt = "Sin histórico comparable"
else:
    comp = dow_ant.iloc[0]
    fecha_dow_txt = f"{DOW_ES[comp['weekday']]} · {comp['fecha'].strftime('%d/%m/%Y')}"
    vm_a, vt_a, vn_a, total_a = comp["ventas_manana_eur"], comp["ventas_tarde_eur"], comp["ventas_noche_eur"], comp["ventas_total_eur"]
    cm_a, ct_a, cn_a = comp["comensales_manana"], comp["comensales_tarde"], comp["comensales_noche"]
    tm_a, tt_a, tn_a = comp["tickets_manana"], comp["tickets_tarde"], comp["tickets_noche"]

tmed_m_a = vm_a / tm_a if tm_a > 0 else 0
tmed_t_a = vt_a / tt_a if tt_a > 0 else 0
tmed_n_a = vn_a / tn_a if tn_a > 0 else 0
tmed_tot_a = total_a / (tm_a + tt_a + tn_a) if (tm_a + tt_a + tn_a) > 0 else 0

# =========================
# VARIACIONES
# =========================
d_vm, p_vm = diff_pct(vm_h, vm_a)
d_vt, p_vt = diff_pct(vt_h, vt_a)
d_vn, p_vn = diff_pct(vn_h, vn_a)
d_tot, p_tot = diff_pct(total_h, total_a)

d_cm, d_ct, d_cn = cm_h - cm_a, ct_h - ct_a, cn_h - cn_a
d_tm, d_tt, d_tn = tm_h - tm_a, tt_h - tt_a, tn_h - tn_a

d_tmed_m, p_tmed_m = diff_pct(tmed_m_h, tmed_m_a)
d_tmed_t, p_tmed_t = diff_pct(tmed_t_h, tmed_t_a)
d_tmed_n, p_tmed_n = diff_pct(tmed_n_h, tmed_n_a)
d_tmed_tot, p_tmed_tot = diff_pct(tmed_tot_h, tmed_tot_a)

# =========================
# DISPOSICIÓN VISUAL
# =========================
c1, c2, c3 = st.columns(3)

with c3:
    st.markdown("**VARIACIÓN**")
    st.caption("Vs. DOW año anterior")

    st.write("**Mañana**")
    st.markdown(
        f"<span style='color:{color(d_vm)}'>{fmt_var(d_vm)} € ({fmt_pct(p_vm)}) {icono(p_vm)}</span>",
        unsafe_allow_html=True
    )
    st.caption(f"{fmt_var(d_cm,0)} comensales · {fmt_var(d_tm,0)} tickets")
    st.caption(f"Ticket medio: {fmt_var(d_tmed_m)} € ({fmt_pct(p_tmed_m)}) {icono(p_tmed_m)}")

    st.write("**Tarde**")
    st.markdown(
        f"<span style='color:{color(d_vt)}'>{fmt_var(d_vt)} € ({fmt_pct(p_vt)}) {icono(p_vt)}</span>",
        unsafe_allow_html=True
    )
    st.caption(f"{fmt_var(d_ct,0)} comensales · {fmt_var(d_tt,0)} tickets")
    st.caption(f"Ticket medio: {fmt_var(d_tmed_t)} € ({fmt_pct(p_tmed_t)}) {icono(p_tmed_t)}")

    st.write("**Noche**")
    st.markdown(
        f"<span style='color:{color(d_vn)}'>{fmt_var(d_vn)} € ({fmt_pct(p_vn)}) {icono(p_vn)}</span>",
        unsafe_allow_html=True
    )
    st.caption(f"{fmt_var(d_cn,0)} comensales · {fmt_var(d_tn,0)} tickets")
    st.caption(f"Ticket medio: {fmt_var(d_tmed_n)} € ({fmt_pct(p_tmed_n)}) {icono(p_tmed_n)}")

    st.markdown("---")
    st.markdown(
        f"<span style='color:{color(d_tot)}'>TOTAL {fmt_var(d_tot)} € ({fmt_pct(p_tot)})</span>",
        unsafe_allow_html=True
    )
    st.caption(f"Ticket medio: {fmt_var(d_tmed_tot)} € ({fmt_pct(p_tmed_tot)}) {icono(p_tmed_tot)}")

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
        "fecha_display", "dow",
        "ventas_manana_eur", "ventas_tarde_eur", "ventas_noche_eur",
        "ventas_total_eur",
        "comensales_manana", "comensales_tarde", "comensales_noche",
        "tickets_manana", "tickets_tarde", "tickets_noche",
        "observaciones"
    ]].rename(columns={"fecha_display": "fecha"}),
    hide_index=True,
    use_container_width=True
)
