import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OYKEN · Ventas", layout="centered")
st.title("OYKEN · Ventas")

DATA_FILE = Path("ventas.csv")

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=[
        "fecha",
        "ventas_manana_eur",
        "ventas_tarde_eur",
        "ventas_noche_eur",
        "ventas_total_eur",
    ])

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas"):
    fecha = st.date_input(
        "Fecha",
        value=date.today(),
        min_value=date(2015, 1, 1),
        max_value=date.today()
    )

    st.caption("Desglose por franja")
    c1, c2, c3 = st.columns(3)
    with c1:
        vm = st.number_input("Mañana (€)", min_value=0.0, step=10.0, format="%.2f")
    with c2:
        vt = st.number_input("Tarde (€)", min_value=0.0, step=10.0, format="%.2f")
    with c3:
        vn = st.number_input("Noche (€)", min_value=0.0, step=10.0, format="%.2f")

    total = vm + vt + vn
    st.metric("Total del día (€)", f"{total:,.2f}")

    guardar = st.form_submit_button("Guardar")

if guardar:
    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": total
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df = df.sort_values("fecha")
    df.to_csv(DATA_FILE, index=False)

    st.success(f"Venta guardada para {fecha.strftime('%d/%m/%Y')}")

st.divider()

# =========================
# VISTA MENSUAL
# =========================
st.subheader("Vista mensual")

if not df.empty:
    df["año"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["dia"] = df["fecha"].dt.day
    df["dow"] = df["fecha"].dt.day_name()

    c1, c2 = st.columns(2)
    with c1:
        año_sel = st.selectbox("Año", sorted(df["año"].unique()))
    with c2:
        mes_sel = st.selectbox(
            "Mes",
            list(range(1, 13)),
            format_func=lambda m: [
                "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
            ][m - 1]
        )

    mensual = df[(df["año"] == año_sel) & (df["mes"] == mes_sel)]

    st.dataframe(
        mensual[[
            "fecha","dia","dow",
            "ventas_manana_eur",
            "ventas_tarde_eur",
            "ventas_noche_eur",
            "ventas_total_eur"
        ]],
        hide_index=True,
        use_container_width=True
    )

    st.divider()

# =========================
# COMPARABLE INTERANUAL
# =========================
st.subheader("Comparable diario · Mismo día año anterior")

if df.empty:
    st.info("No hay datos suficientes para comparar.")
else:
    dia_sel = st.date_input(
        "Selecciona el día a analizar",
        value=df["fecha"].max(),
        min_value=df["fecha"].min(),
        max_value=df["fecha"].max(),
        key="comp_day"
    )

    actual = df[df["fecha"] == pd.to_datetime(dia_sel)]
    anterior = df[df["fecha"] == pd.to_datetime(
        date(dia_sel.year - 1, dia_sel.month, dia_sel.day)
    )]

    c1, c2, c3 = st.columns(3)

    if actual.empty:
        c1.warning("No hay datos para este día.")
    else:
        venta_actual = actual.iloc[0]["ventas_total_eur"]
        c1.success(f"Día actual\n€ {venta_actual:,.2f}")

    if anterior.empty:
        c2.warning("No existe histórico comparable.")
    else:
        venta_ant = anterior.iloc[0]["ventas_total_eur"]
        c2.info(f"Año anterior\n€ {venta_ant:,.2f}")

    if not actual.empty and not anterior.empty:
        dif = venta_actual - venta_ant
        pct = (dif / venta_ant) * 100 if venta_ant != 0 else 0

        if dif >= 0:
            c3.success(f"+€ {dif:,.2f}  ({pct:.1f} %)")
        else:
            c3.error(f"€ {dif:,.2f}  ({pct:.1f} %)")
    else:
        c3.warning("No se puede calcular variación.")
        st.divider()
st.subheader("Comparable diario · Mismo día de la semana (año anterior)")

if df.empty:
    st.info("No hay datos suficientes para comparaciones.")
else:
    fecha_base = df["fecha"].max().date()

    fecha_sel = st.date_input(
        "Selecciona el día a analizar (DOW)",
        value=fecha_base,
        key="fecha_dow"
    )

    fecha_actual = pd.to_datetime(fecha_sel)
    dow_actual = fecha_actual.weekday()  # lunes=0

    # Día actual
    actual = df[df["fecha"] == fecha_actual]

    # Buscar mismo DOW en año anterior
    año_anterior = fecha_actual.year - 1
    candidatos = df[
        (df["fecha"].dt.year == año_anterior) &
        (df["fecha"].dt.weekday == dow_actual)
    ].copy()

    if not candidatos.empty:
        # Elegir el más cercano en fecha
        candidatos["dist"] = (candidatos["fecha"] - fecha_actual).abs()
        comparable = candidatos.sort_values("dist").iloc[0]
    else:
        comparable = None

    c1, c2, c3 = st.columns(3)

    # -------------------------
    # DÍA ACTUAL
    # -------------------------
    with c1:
        st.markdown("**Día actual**")
        if actual.empty:
            st.warning("No hay datos para este día.")
        else:
            r = actual.iloc[0]
            st.write(f"Fecha: {fecha_actual.date()}")
            st.write(f"Mañana: {r['ventas_manana_eur']:.2f} €")
            st.write(f"Tarde: {r['ventas_tarde_eur']:.2f} €")
            st.write(f"Noche: {r['ventas_noche_eur']:.2f} €")
            st.write(f"**Total: {r['ventas_total_eur']:.2f} €**")

    # -------------------------
    # AÑO ANTERIOR (MISMO DOW)
    # -------------------------
    with c2:
        st.markdown("**Mismo DOW · Año anterior**")
        if comparable is None:
            st.warning("No existe día comparable.")
        else:
            st.write(f"Fecha: {comparable['fecha'].date()}")
            st.write(f"Mañana: {comparable['ventas_manana_eur']:.2f} €")
            st.write(f"Tarde: {comparable['ventas_tarde_eur']:.2f} €")
            st.write(f"Noche: {comparable['ventas_noche_eur']:.2f} €")
            st.write(f"**Total: {comparable['ventas_total_eur']:.2f} €**")

    # -------------------------
    # VARIACIÓN
    # -------------------------
    with c3:
        st.markdown("**Variación**")
        if actual.empty or comparable is None:
            st.info("No se puede calcular variación.")
        else:
            dif = r["ventas_total_eur"] - comparable["ventas_total_eur"]
            pct = (dif / comparable["ventas_total_eur"] * 100) if comparable["ventas_total_eur"] > 0 else 0

            st.metric("Total", f"{dif:+.2f} €", f"{pct:+.1f} %")

            for franja in ["manana", "tarde", "noche"]:
                act = r[f"ventas_{franja}_eur"]
                prev = comparable[f"ventas_{franja}_eur"]
                d = act - prev
                p = (d / prev * 100) if prev > 0 else 0
                st.write(f"{franja.capitalize()}: {d:+.2f} € ({p:+.1f} %)")

