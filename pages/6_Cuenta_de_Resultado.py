import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Cuenta de Resultados")

DATA_PATH = Path("data")

# ===============================
# CONFIGURACIÓN
# ===============================
YEAR = st.session_state.get("year_rrhh", 2025)

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# ===============================
# FUNCIONES AUXILIARES
# ===============================
def load_csv_safe(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

# ===============================
# INGRESOS (VENTAS)
# ===============================
st.subheader("Ingresos")

df_ventas = load_csv_safe(DATA_PATH / "ventas.csv")

ventas_total = 0.0

if not df_ventas.empty and "fecha" in df_ventas.columns:
    df_ventas["fecha"] = pd.to_datetime(df_ventas["fecha"], errors="coerce")
    df_ventas = df_ventas[df_ventas["fecha"].dt.year == YEAR]
    ventas_total = df_ventas["importe"].sum()

st.metric("Ventas netas", f"{ventas_total:,.2f} €")

# ===============================
# COSTE DE VENTAS (COGS)
# ===============================
st.divider()
st.subheader("Coste de ventas (COGS)")

df_compras = load_csv_safe(DATA_PATH / "compras.csv")

compras_total = 0.0

if not df_compras.empty and "fecha" in df_compras.columns:
    df_compras["fecha"] = pd.to_datetime(df_compras["fecha"], errors="coerce")
    df_compras = df_compras[df_compras["fecha"].dt.year == YEAR]
    compras_total = df_compras["importe"].sum()

st.write("Compras de producto", f"-{compras_total:,.2f} €")

margen_bruto = ventas_total - compras_total

st.markdown(
    f"### **MARGEN BRUTO**  \n**{margen_bruto:,.2f} €**"
)

# ===============================
# GASTOS DE PERSONAL (RRHH)
# ===============================
st.divider()
st.subheader("Gastos de personal")

df_rrhh = load_csv_safe(DATA_PATH / f"rrhh_{YEAR}.csv")

coste_personal = 0.0

if not df_rrhh.empty and "coste_empresa" in df_rrhh.columns:
    coste_personal = df_rrhh["coste_empresa"].sum()

st.write("Coste de personal", f"-{coste_personal:,.2f} €")

# ===============================
# GASTOS OPERATIVOS
# ===============================
st.divider()
st.subheader("Gastos operativos")

df_gastos = load_csv_safe(DATA_PATH / "gastos.csv")

gastos_operativos = 0.0

if not df_gastos.empty and "fecha" in df_gastos.columns:
    df_gastos["fecha"] = pd.to_datetime(df_gastos["fecha"], errors="coerce")
    df_gastos = df_gastos[df_gastos["fecha"].dt.year == YEAR]
    gastos_operativos = df_gastos["importe"].sum()

st.write("Otros gastos operativos", f"-{gastos_operativos:,.2f} €")

# ===============================
# EBITDA
# ===============================
st.divider()
st.subheader("Resultado del periodo")

ebitda = margen_bruto - coste_personal - gastos_operativos

st.markdown(
    f"""
    ### **EBITDA**
    **{ebitda:,.2f} €**
    """
)
