import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OYKEN · Cuenta de Resultados", layout="centered")

st.title("OYKEN · Cuenta de Resultados")
st.caption("Estado financiero real del negocio (foto mensual)")

# =========================
# SELECTOR DE PERIODO
# =========================
col1, col2 = st.columns(2)

with col1:
    mes = st.selectbox(
        "Mes",
        list(range(1, 13)),
        format_func=lambda x: datetime(1900, x, 1).strftime("%B")
    )

with col2:
    anio = st.selectbox(
        "Año",
        list(range(2022, datetime.now().year + 1))
    )

st.divider()

# =========================
# CARGA DE ARCHIVOS
# =========================
def cargar_csv(nombre):
    path = Path(nombre)
    if path.exists():
        return pd.read_csv(path, parse_dates=["fecha"])
    return pd.DataFrame()

ventas = cargar_csv("ventas.csv")
compras = cargar_csv("compras.csv")
gastos = cargar_csv("gastos.csv")
mermas = cargar_csv("mermas.csv")
inventario = cargar_csv("inventario.csv")
rrhh = cargar_csv("rrhh.csv")

# =========================
# FILTRO POR MES
# =========================
def filtrar_mes(df):
    if df.empty:
        return df
    return df[
        (df["fecha"].dt.month == mes) &
        (df["fecha"].dt.year == anio)
    ]

ventas_mes = filtrar_mes(ventas)
compras_mes = filtrar_mes(compras)
gastos_mes = filtrar_mes(gastos)
mermas_mes = filtrar_mes(mermas)

# =========================
# INGRESOS
# =========================
ventas_totales = ventas_mes["ventas_total_eur"].sum() if not ventas_mes.empty else 0

st.subheader("INGRESOS")
st.write(f"Ventas totales: **{ventas_totales:,.2f} €**")

st.divider()

# =========================
# COSTE DE VENTAS
# =========================
compras_total = compras_mes["Coste (€)"].sum() if not compras_mes.empty else 0
mermas_total = mermas_mes["cantidad"].sum() if not mermas_mes.empty else 0

# Inventario (mensual)
inv_ini = 0
inv_fin = 0

if not inventario.empty:
    inv_mes = inventario[
        (inventario["mes"] == mes) &
        (inventario["anio"] == anio)
    ]
    if not inv_mes.empty:
        inv_ini = inv_mes.iloc[0]["inventario_inicial"]
        inv_fin = inv_mes.iloc[0]["inventario_final"]

variacion_inventario = inv_fin - inv_ini

coste_ventas = compras_total + variacion_inventario + mermas_total

st.subheader("COSTE DE VENTAS")
st.write(f"Compras imputadas: {compras_total:,.2f} €")
st.write(f"Variación de inventario: {variacion_inventario:,.2f} €")
st.write(f"Mermas: {mermas_total:,.2f} €")
st.markdown(f"**Coste de ventas total: {coste_ventas:,.2f} €**")

st.divider()

# =========================
# MARGEN BRUTO
# =========================
margen_bruto = ventas_totales - coste_ventas
margen_pct = (margen_bruto / ventas_totales * 100) if ventas_totales > 0 else 0

st.subheader("MARGEN BRUTO")
st.write(f"Margen bruto: {margen_bruto:,.2f} €")
st.write(f"Margen bruto %: {margen_pct:.2f} %")

st.divider()

# =========================
# COSTE DE PERSONAL
# =========================
coste_personal = rrhh["coste_total"].sum() if not rrhh.empty else 0

st.subheader("COSTE DE PERSONAL")
st.write(f"Total personal: {coste_personal:,.2f} €")

st.divider()

# =========================
# GASTOS OPERATIVOS
# =========================
total_gastos = gastos_mes["coste"].sum() if not gastos_mes.empty else 0

st.subheader("GASTOS OPERATIVOS")
st.write(f"Gastos operativos totales: {total_gastos:,.2f} €")

st.divider()

# =========================
# RESULTADO OPERATIVO
# =========================
resultado_operativo = margen_bruto - coste_personal - total_gastos

st.subheader("RESULTADO OPERATIVO")
st.markdown(f"### {resultado_operativo:,.2f} €")

st.caption("Este resultado representa el EBITDA operativo del periodo.")
