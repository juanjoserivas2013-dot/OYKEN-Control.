import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="OYKEN · EBITDA",
    layout="centered"
)

st.title("OYKEN · EBITDA")

# =========================
# ARCHIVOS CANÓNICOS
# =========================
VENTAS_FILE  = Path("ventas_mensuales.csv")
COMPRAS_FILE = Path("compras_mensuales.csv")
RRHH_FILE    = Path("rrhh_mensual.csv")
GASTOS_FILE  = Path("gastos_mensuales.csv")

if not all(p.exists() for p in [VENTAS_FILE, COMPRAS_FILE, RRHH_FILE, GASTOS_FILE]):
    st.warning("Aún no existen cierres mensuales suficientes para calcular EBITDA.")
    st.stop()

# =========================
# CARGA DE DATOS
# =========================
df_v = pd.read_csv(VENTAS_FILE)
df_c = pd.read_csv(COMPRAS_FILE)
df_r = pd.read_csv(RRHH_FILE)
df_g = pd.read_csv(GASTOS_FILE)

# Normalizar tipos
for df in [df_v, df_c, df_r, df_g]:
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
    df["mes"] = pd.to_numeric(df["mes"], errors="coerce")

df_v["ventas_total_eur"] = pd.to_numeric(
    df_v["ventas_total_eur"], errors="coerce"
).fillna(0)

df_c["compras_total_eur"] = pd.to_numeric(
    df_c["compras_total_eur"], errors="coerce"
).fillna(0)

df_r["rrhh_total_eur"] = pd.to_numeric(
    df_r["rrhh_total_eur"], errors="coerce"
).fillna(0)

df_g["gastos_total_eur"] = pd.to_numeric(
    df_g["gastos_total_eur"], errors="coerce"
).fillna(0)

# =========================
# SELECTORES
# =========================
anios_disponibles = sorted(
    set(df_v["anio"].dropna().unique())
    | set(df_c["anio"].dropna().unique())
    | set(df_r["anio"].dropna().unique())
    | set(df_g["anio"].dropna().unique())
)

if not anios_disponibles:
    st.info("No hay datos suficientes para mostrar EBITDA.")
    st.stop()

c1, c2 = st.columns(2)

with c1:
    anio_sel = st.selectbox(
        "Año",
        anios_disponibles,
        index=len(anios_disponibles) - 1
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(range(1, 13)),
        format_func=lambda x: "Todos los meses" if x == 0 else [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ][x - 1]
    )

# =========================
# FILTRADO POR AÑO / MES
# =========================
df_v = df_v[df_v["anio"] == anio_sel]
df_c = df_c[df_c["anio"] == anio_sel]
df_r = df_r[df_r["anio"] == anio_sel]
df_g = df_g[df_g["anio"] == anio_sel]

if mes_sel != 0:
    df_v = df_v[df_v["mes"] == mes_sel]
    df_c = df_c[df_c["mes"] == mes_sel]
    df_r = df_r[df_r["mes"] == mes_sel]
    df_g = df_g[df_g["mes"] == mes_sel]

# =========================
# CRUCE MENSUAL Y CÁLCULO
# =========================
base = pd.DataFrame({"mes": range(1, 13)})

base = base.merge(
    df_v[["mes", "ventas_total_eur"]],
    on="mes",
    how="left"
)

base = base.merge(
    df_c[["mes", "compras_total_eur"]],
    on="mes",
    how="left"
)

base = base.merge(
    df_r[["mes", "rrhh_total_eur"]],
    on="mes",
    how="left"
)

base = base.merge(
    df_g[["mes", "gastos_total_eur"]],
    on="mes",
    how="left"
)

base = base.fillna(0)

base["ebitda_eur"] = (
    base["ventas_total_eur"]
    - base["compras_total_eur"]
    - base["rrhh_total_eur"]
    - base["gastos_total_eur"]
)

# Filtro visual de mes
if mes_sel != 0:
    base = base[base["mes"] == mes_sel]

base = base.sort_values("mes")

# =========================
# PRESENTACIÓN TABLA
# =========================
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

base["Mes"] = base["mes"].map(MESES_ES)

tabla_ebitda = base[[
    "Mes",
    "ventas_total_eur",
    "compras_total_eur",
    "rrhh_total_eur",
    "gastos_total_eur",
    "ebitda_eur"
]].rename(columns={
    "ventas_total_eur": "Ventas (€)",
    "compras_total_eur": "Compras (€)",
    "rrhh_total_eur": "RRHH (€)",
    "gastos_total_eur": "Gastos (€)",
    "ebitda_eur": "EBITDA (€)"
})

# Fila TOTAL solo cuando se muestran todos los meses
if mes_sel == 0:
    total = pd.DataFrame([{
        "Mes": "TOTAL",
        "Ventas (€)": tabla_ebitda["Ventas (€)"].sum(),
        "Compras (€)": tabla_ebitda["Compras (€)"].sum(),
        "RRHH (€)": tabla_ebitda["RRHH (€)"].sum(),
        "Gastos (€)": tabla_ebitda["Gastos (€)"].sum(),
        "EBITDA (€)": tabla_ebitda["EBITDA (€)"].sum()
    }])
    tabla_ebitda = pd.concat([tabla_ebitda, total], ignore_index=True)

st.divider()
st.subheader("EBITDA · Detalle mensual")

st.dataframe(
    tabla_ebitda,
    hide_index=True,
    use_container_width=True
)
