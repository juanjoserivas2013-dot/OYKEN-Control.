import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================

st.title("OYKEN · Totales Operativos")
st.caption("Consolidado mensual de magnitudes económicas operativas")

# =========================
# FUENTE DE DATOS
# =========================
DATA_FILE = Path("totales_operativos.csv")

if not DATA_FILE.exists():
    st.warning("No existen datos en Totales Operativos.")
    st.stop()

df = pd.read_csv(DATA_FILE)

if df.empty:
    st.info("Totales Operativos no contiene registros.")
    st.stop()

# Normalizar tipos
df["anio"] = df["anio"].astype(int)
df["mes"] = df["mes"].astype(int)
df["importe_eur"] = df["importe_eur"].astype(float)

# =========================
# SELECTOR DE AÑO
# =========================
anios = sorted(df["anio"].unique())
anio_sel = st.selectbox("Año", anios, index=len(anios) - 1)

df_anio = df[df["anio"] == anio_sel].copy()

# =========================
# ESTADO DE COBERTURA
# =========================
st.divider()

st.markdown("**Estado de cobertura**")

MODULOS = [
    "Control Operativo",
    "Compras",
    "Gastos",
    "RRHH",
    "Inventario",
]

cobertura = []
for m in MODULOS:
    if (df_anio["origen"] == m).any():
        cobertura.append(f"{m}: OK")
    else:
        cobertura.append(f"{m}: Sin datos")

st.write(" · ".join(cobertura))

# =========================
# FILTROS DISCRETOS
# =========================
st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    origen_sel = st.multiselect(
        "Origen",
        sorted(df_anio["origen"].unique()),
        default=sorted(df_anio["origen"].unique())
    )

with c2:
    concepto_sel = st.multiselect(
        "Concepto",
        sorted(df_anio["concepto"].unique()),
        default=sorted(df_anio["concepto"].unique())
    )

with c3:
    meses_disp = sorted(df_anio["mes"].unique())
    mes_sel = st.multiselect(
        "Mes",
        meses_disp,
        default=meses_disp
    )

df_filtro = df_anio[
    (df_anio["origen"].isin(origen_sel)) &
    (df_anio["concepto"].isin(concepto_sel)) &
    (df_anio["mes"].isin(mes_sel))
].copy()

# =========================
# PRESENTACIÓN TABULAR
# =========================
st.divider()

# Mes en texto
MESES_TXT = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

df_filtro["Mes"] = df_filtro["mes"].map(MESES_TXT)

tabla = (
    df_filtro
    .sort_values(["anio", "mes", "origen"])
    .rename(columns={
        "anio": "Año",
        "origen": "Origen",
        "concepto": "Concepto",
        "importe_eur": "Importe (€)"
    })
    [["Año", "Mes", "Origen", "Concepto", "Importe (€)"]]
)

st.dataframe(
    tabla,
    hide_index=True,
    use_container_width=True
)

# =========================
# NOTA DE SISTEMA
# =========================
st.caption(
    "Esta página consolida totales mensuales. "
    "No calcula resultados ni aplica criterios financieros."
)

