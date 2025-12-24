import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="OYKEN · Compras",
    layout="centered"
)

st.title("OYKEN · Compras")
st.divider()

# =========================
# PERSISTENCIA
# =========================
DATA_FILE = Path("compras.csv")

if "compras" not in st.session_state:
    if DATA_FILE.exists():
        st.session_state.compras = pd.read_csv(DATA_FILE)
    else:
        st.session_state.compras = pd.DataFrame(
            columns=["Fecha", "Proveedor", "Familia", "Coste (€)"]
        )

if "proveedores" not in st.session_state:
    st.session_state.proveedores = sorted(
        st.session_state.compras["Proveedor"].dropna().unique().tolist()
        if not st.session_state.compras.empty else []
    )

FAMILIAS = ["Materia prima", "Bebidas", "Limpieza", "Otros"]

# =========================
# REGISTRAR COMPRA
# =========================
st.subheader("Registrar compra")

with st.container(border=True):
    with st.form("registro_compras", clear_on_submit=True):

        c1, c2, c3 = st.columns(3)

        with c1:
            fecha = st.date_input(
                "Fecha",
                value=date.today(),
                format="DD/MM/YYYY"
            )

        with c2:
            proveedor = st.selectbox(
                "Proveedor",
                st.session_state.proveedores + ["+ Añadir proveedor"]
            )
            if proveedor == "+ Añadir proveedor":
                nuevo_proveedor = st.text_input("Nuevo proveedor")
            else:
                nuevo_proveedor = None

        with c3:
            familia = st.selectbox("Familia", FAMILIAS)

        coste = st.number_input(
            "Coste total (€)",
            min_value=0.00,
            step=0.01,
            format="%.2f"
        )

        guardar = st.form_submit_button("Registrar compra", use_container_width=True)

        if guardar:

            if proveedor == "+ Añadir proveedor":
                if not nuevo_proveedor:
                    st.stop()
                proveedor = nuevo_proveedor
                if proveedor not in st.session_state.proveedores:
                    st.session_state.proveedores.append(proveedor)

            if coste <= 0:
                st.stop()

            nueva = {
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Proveedor": proveedor,
                "Familia": familia,
                "Coste (€)": round(coste, 2)
            }

            st.session_state.compras = pd.concat(
                [st.session_state.compras, pd.DataFrame([nueva])],
                ignore_index=True
            )
            st.session_state.compras.to_csv(DATA_FILE, index=False)
            st.success("Compra registrada")

# =========================
# RESUMEN
# =========================
st.divider()
st.subheader("Resumen")

total = st.session_state.compras["Coste (€)"].sum() if not st.session_state.compras.empty else 0
num = len(st.session_state.compras)

c1, c2 = st.columns(2)
c1.metric("Total registrado (€)", f"{total:.2f}")
c2.metric("Nº de compras", num)

# =========================
# HISTÓRICO
# =========================
st.divider()
st.subheader("Histórico de compras")

if not st.session_state.compras.empty:
    st.dataframe(
        st.session_state.compras,
        hide_index=True,
        use_container_width=True
    )

# =========================
# CORRECCIÓN DE ERRORES
# =========================
st.divider()
st.subheader("Corrección de errores")

with st.container(border=True):
    if not st.session_state.compras.empty:
        idx = st.selectbox(
            "Selecciona una compra",
            st.session_state.compras.index,
            format_func=lambda i: (
                f'{st.session_state.compras.loc[i,"Fecha"]} · '
                f'{st.session_state.compras.loc[i,"Proveedor"]} · '
                f'{st.session_state.compras.loc[i,"Coste (€)"]:.2f} €'
            )
        )

        if st.button("Eliminar compra", use_container_width=True):
            st.session_state.compras = (
                st.session_state.compras
                .drop(idx)
                .reset_index(drop=True)
            )
            st.session_state.compras.to_csv(DATA_FILE, index=False)
            st.success("Compra eliminada")
