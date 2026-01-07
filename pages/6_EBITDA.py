import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =====================================================
# CONFIGURACIÓN
# =====================================================
st.title("OYKEN · EBITDA")

VENTAS_FILE = Path("ventas_mensuales.csv")
COMPRAS_FILE = Path("compras_mensuales.csv")
RRHH_FILE = Path("rrhh_mensual.csv")
GASTOS_FILE = Path("gastos_mensuales.csv")
INVENTARIO_FILE = Path("inventario_mensual.csv")

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# =====================================================
# CARGA CSV
# =====================================================
def cargar_csv(path, col_valor):
    if not path.exists():
        return pd.DataFrame(columns=["anio", "mes", col_valor])
    df = pd.read_csv(path)
    df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce").fillna(0)
    return df[["anio", "mes", col_valor]]

df_ventas = cargar_csv(VENTAS_FILE, "ventas_eur")
df_compras = cargar_csv(COMPRAS_FILE, "compras_eur")
df_rrhh = cargar_csv(RRHH_FILE, "rrhh_eur")
df_gastos = cargar_csv(GASTOS_FILE, "gastos_eur")

if INVENTARIO_FILE.exists():
    df_inv = pd.read_csv(INVENTARIO_FILE)
    df_inv["variacion_inventario_eur"] = pd.to_numeric(
        df_inv["variacion_inventario_eur"], errors="coerce"
    ).fillna(0)
    df_inv = df_inv[["anio", "mes", "variacion_inventario_eur"]]
else:
    df_inv = pd.DataFrame(columns=["anio", "mes", "variacion_inventario_eur"])

# =====================================================
# CONSOLIDACIÓN MENSUAL
# =====================================================
df = (
    df_ventas
    .merge(df_compras, on=["anio", "mes"], how="left")
    .merge(df_rrhh, on=["anio", "mes"], how="left")
    .merge(df_gastos, on=["anio", "mes"], how="left")
    .merge(df_inv, on=["anio", "mes"], how="left")
    .fillna(0)
)

df = df.sort_values(["anio", "mes"])
df["Mes"] = df["mes"].map(MESES_ES)

# =====================================================
# SELECTORES
# =====================================================
st.divider()
c1, c2 = st.columns(2)

with c1:
    anio_sel = st.selectbox(
        "Año",
        sorted(df["anio"].unique()),
        index=len(sorted(df["anio"].unique())) - 1
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(MESES_ES.keys()),
        format_func=lambda x: "Todos los meses" if x == 0 else MESES_ES[x]
    )

df_f = df[df["anio"] == anio_sel]
if mes_sel != 0:
    df_f = df_f[df_f["mes"] == mes_sel]

# =====================================================
# CÁLCULOS
# =====================================================
df_f["ebitda_base"] = (
    df_f["ventas_eur"]
    - df_f["compras_eur"]
    - df_f["rrhh_eur"]
    - df_f["gastos_eur"]
)

df_f["ebitda_ajustado"] = (
    df_f["ebitda_base"]
    - df_f["variacion_inventario_eur"]
)

# =====================================================
# BLOQUE 1 — EBITDA OPERATIVO (BASE)
# =====================================================
st.divider()
st.subheader("EBITDA operativo (base)")

st.dataframe(
    df_f[[
        "Mes",
        "ventas_eur",
        "compras_eur",
        "rrhh_eur",
        "gastos_eur",
        "ebitda_base"
    ]].rename(columns={
        "ventas_eur": "Ventas (€)",
        "compras_eur": "Compras (€)",
        "rrhh_eur": "RRHH (€)",
        "gastos_eur": "Gastos (€)",
        "ebitda_base": "EBITDA base (€)"
    }),
    hide_index=True,
    use_container_width=True
)

# =====================================================
# BLOQUE 2 — AJUSTE POR VARIACIÓN DE INVENTARIO
# =====================================================
st.divider()
st.subheader("Ajuste por variación de inventario")

st.dataframe(
    df_f[[
        "Mes",
        "variacion_inventario_eur"
    ]].rename(columns={
        "variacion_inventario_eur": "Variación inventario (€)"
    }),
    hide_index=True,
    use_container_width=True
)

# =====================================================
# BLOQUE 3 — EBITDA AJUSTADO
# =====================================================
st.divider()
st.subheader("EBITDA ajustado (consumo real)")

st.dataframe(
    df_f[[
        "Mes",
        "ebitda_base",
        "variacion_inventario_eur",
        "ebitda_ajustado"
    ]].rename(columns={
        "ebitda_base": "EBITDA base (€)",
        "variacion_inventario_eur": "Variación inventario (€)",
        "ebitda_ajustado": "EBITDA ajustado (€)"
    }),
    hide_index=True,
    use_container_width=True
)
