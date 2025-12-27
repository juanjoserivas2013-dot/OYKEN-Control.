import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# =========================
# CABECERA
# =========================
st.title("OYKEN · Cuenta de Resultados")
st.caption("Lectura económica real del negocio. Sin interpretación.")

# =========================
# ARCHIVOS
# =========================
VENTAS_FILE = Path("ventas.csv")
COMPRAS_FILE = Path("compras.csv")
INVENTARIO_FILE = Path("inventario.csv")
MERMAS_FILE = Path("mermas.csv")
RRHH_FILE = Path("rrhh.csv")
GASTOS_FILE = Path("gastos.csv")

# =========================
# SELECCIÓN DE PERIODO
# =========================
col1, col2 = st.columns(2)

with col1:
    mes = st.selectbox(
        "Mes",
        list(range(1, 13)),
        index=datetime.today().month - 1
    )

with col2:
    anio = st.selectbox(
        "Año",
        [2023, 2024, 2025],
        index=2
    )

# =========================
# FUNCIONES AUXILIARES
# =========================
def cargar_df(path, parse_dates=None):
    if path.exists():
        return pd.read_csv(path, parse_dates=parse_dates)
    return pd.DataFrame()

def filtrar_periodo(df, col_fecha):
    if df.empty:
        return df
    return df[
        (df[col_fecha].dt.month == mes) &
        (df[col_fecha].dt.year == anio)
    ]

# =========================
# INGRESOS
# =========================
df_ventas = cargar_df(VENTAS_FILE, parse_dates=["fecha"])
df_ventas_periodo = filtrar_periodo(df_ventas, "fecha")

ventas_totales = df_ventas_periodo["ventas_total_eur"].sum()

# =========================
# COMPRAS
# =========================
df_compras = cargar_df(COMPRAS_FILE, parse_dates=["Fecha"])
df_compras["Fecha"] = pd.to_datetime(df_compras["Fecha"], dayfirst=True)
df_compras_periodo = filtrar_periodo(df_compras, "Fecha")

compras_totales = df_compras_periodo["Coste (€)"].sum()

# =========================
# INVENTARIO
# =========================
df_inventario = cargar_df(INVENTARIO_FILE)

inventario_inicio = (
    df_inventario
    .query("Mes == @mes and Año == @anio")
    .get("Inventario Inicial", pd.Series([0]))
    .sum()
)

inventario_final = (
    df_inventario
    .query("Mes == @mes and Año == @anio")
    .get("Inventario Final", pd.Series([0]))
    .sum()
)

variacion_inventario = inventario_final - inventario_inicio

# =========================
# MERMAS
# =========================
df_mermas = cargar_df(MERMAS_FILE, parse_dates=["Fecha"])
df_mermas_periodo = filtrar_periodo(df_mermas, "Fecha")

mermas_total = df_mermas_periodo["Cantidad"].sum() if not df_mermas_periodo.empty else 0

# =========================
# COSTE DE VENTAS
# =========================
coste_ventas = compras_totales + variacion_inventario + mermas_total

# =========================
# MARGEN BRUTO
# =========================
margen_bruto = ventas_totales - coste_ventas
margen_bruto_pct = (
    (margen_bruto / ventas_totales) * 100
    if ventas_totales > 0 else 0
)

# =========================
# COSTES DE PERSONAL
# =========================
df_rrhh = cargar_df(RRHH_FILE)
df_rrhh_periodo = df_rrhh.query("Mes == @mes and Año == @anio")

coste_personal = df_rrhh_periodo["Coste Total"].sum() if not df_rrhh_periodo.empty else 0

# =========================
# GASTOS OPERATIVOS
# =========================
df_gastos = cargar_df(GASTOS_FILE, parse_dates=["Fecha"])
df_gastos_periodo = filtrar_periodo(df_gastos, "Fecha")

gastos_operativos = df_gastos_periodo["Importe (€)"].sum() if not df_gastos_periodo.empty else 0

# =========================
# RESULTADO OPERATIVO
# =========================
resultado_operativo = margen_bruto - coste_personal - gastos_operativos

# =========================
# VISUALIZACIÓN
# =========================
st.divider()

st.markdown("### INGRESOS")
st.metric("Ventas totales", f"{ventas_totales:,.2f} €")

st.divider()

st.markdown("### COSTE DE VENTAS")
st.write(f"Compras imputadas: {compras_totales:,.2f} €")
st.write(f"Variación de inventario: {variacion_inventario:,.2f} €")
st.write(f"Mermas: {mermas_total:,.2f}")
st.markdown(f"**Coste de ventas total: {coste_ventas:,.2f} €**")

st.divider()

st.markdown("### MARGEN BRUTO")
st.write(f"Margen bruto: {margen_bruto:,.2f} €")
st.write(f"Margen bruto %: {margen_bruto_pct:.1f} %")

st.divider()

st.markdown("### COSTES DE PERSONAL")
st.write(f"Total personal: {coste_personal:,.2f} €")

st.divider()

st.markdown("### GASTOS OPERATIVOS")
st.write(f"Gastos varios: {gastos_operativos:,.2f} €")

st.divider()

st.markdown("### RESULTADO OPERATIVO")
st.metric("Resultado operativo", f"{resultado_operativo:,.2f} €")

st.caption(
    "La Cuenta de Resultados consolida ventas, compras, inventario, mermas, personal y gastos. "
    "Las señales de control se mostrarán en el módulo de Calidad Operativa."
)
