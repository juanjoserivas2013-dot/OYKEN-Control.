import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="OYKEN · RRHH",
    layout="centered"
)

st.title("OYKEN · RRHH")
st.caption("Estructura salarial y coste de personal")

# =====================================================
# CONSTANTES
# =====================================================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

COLUMNAS_RRHH = ["Puesto", "Bruto anual (€)"] + MESES
RRHH_FILE = Path("rrhh_coste_mensual.csv")

# =====================================================
# ESTADO INICIAL
# =====================================================

if "rrhh_personal" not in st.session_state:
    st.session_state.rrhh_personal = pd.DataFrame(columns=COLUMNAS_RRHH)

# =====================================================
# FASE 1 · ALTA DE PUESTOS
# =====================================================

st.subheader("Fase 1 · Personal")

with st.form("form_rrhh", clear_on_submit=True):

    puesto = st.text_input("Puesto")
    bruto_anual = st.number_input(
        "Bruto anual (€)",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    st.markdown("**Personas por mes**")

    cols = st.columns(6)
    personas_mes = {}

    for i, mes in enumerate(MESES):
        with cols[i % 6]:
            personas_mes[mes] = st.number_input(
                mes,
                min_value=0,
                step=1,
                key=f"personas_{mes}"
            )

    submit = st.form_submit_button("Añadir puesto")

    if submit and puesto.strip() != "":
        fila = {
            "Puesto": puesto.strip(),
            "Bruto anual (€)": float(bruto_anual)
        }

        for mes in MESES:
            fila[mes] = int(personas_mes.get(mes, 0))

        st.session_state.rrhh_personal = pd.concat(
            [
                st.session_state.rrhh_personal,
                pd.DataFrame([fila], columns=COLUMNAS_RRHH)
            ],
            ignore_index=True
        )

# =====================================================
# VISUALIZACIÓN PERSONAL
# =====================================================

if not st.session_state.rrhh_personal.empty:
    st.dataframe(
        st.session_state.rrhh_personal,
        hide_index=True,
        use_container_width=True
    )

st.divider()

# =====================================================
# FASE 2 · COSTE DE PERSONAL (NÓMINA)
# =====================================================

st.subheader("Fase 2 · Coste de personal (nómina)")

tabla_nominas = []

for _, row in st.session_state.rrhh_personal.iterrows():

    bruto_mensual = row["Bruto anual (€)"] / 12
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        fila[mes] = round(bruto_mensual * row[mes], 2)

    tabla_nominas.append(fila)

df_nominas = pd.DataFrame(tabla_nominas)

st.dataframe(
    df_nominas,
    hide_index=True,
    use_container_width=True
)

st.divider()

# =====================================================
# FASE 3 · SEGURIDAD SOCIAL Y COSTE EMPRESA
# =====================================================

st.subheader("Fase 3 · Seguridad Social y coste salarial")

aplicar_ss = st.checkbox(
    "Aplicar Seguridad Social Empresa (33%)",
    value=True
)

SS_EMPRESA = 0.33
tabla_coste = []

for _, row in df_nominas.iterrows():

    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        nomina = row[mes]
        ss = nomina * SS_EMPRESA if aplicar_ss else 0.0

        fila[f"{mes} · Nómina"] = round(nomina, 2)
        fila[f"{mes} · SS Empresa"] = round(ss, 2)
        fila[f"{mes} · Coste Empresa"] = round(nomina + ss, 2)

    tabla_coste.append(fila)

df_coste = pd.DataFrame(tabla_coste)

st.dataframe(
    df_coste,
    hide_index=True,
    use_container_width=True
)

st.divider()

# =====================================================
# TOTALES MENSUALES
# =====================================================

st.subheader("Totales mensuales")

totales = []

for mes in MESES:
    nomina = df_coste[f"{mes} · Nómina"].sum()
    ss = df_coste[f"{mes} · SS Empresa"].sum()
    coste = df_coste[f"{mes} · Coste Empresa"].sum()

    totales.append({
        "Mes": mes,
        "Nómina (€)": round(nomina, 2),
        "Seguridad Social (€)": round(ss, 2),
        "Coste Empresa (€)": round(coste, 2)
    })

df_totales = pd.DataFrame(totales)

st.dataframe(
    df_totales,
    hide_index=True,
    use_container_width=True
)

# =====================================================
# EXPORTACIÓN CSV (CONTRATO OYKEN)
# =====================================================

anio = st.selectbox(
    "Año de referencia",
    list(range(2022, 2031)),
    index=3
)

export = []

for _, row in df_totales.iterrows():
    export.append({
        "Año": anio,
        "Mes": row["Mes"],
        "Nomina (€)": row["Nómina (€)"],
        "Seguridad Social (€)": row["Seguridad Social (€)"],
        "Coste Empresa (€)": row["Coste Empresa (€)"]
    })

df_export = pd.DataFrame(export)
df_export.to_csv(RRHH_FILE, index=False)

st.success("Coste de RRHH mensual guardado correctamente")
st.caption("Este módulo construye y persiste el coste salarial completo.")
