import streamlit as st
import pandas as pd
from datetime import date

def registro_compras_page():

    st.subheader("OYKEN · Compras")
    st.caption("Registro operativo diario de compras")

    # -------- Estado --------
    if "compras" not in st.session_state:
        st.session_state.compras = pd.DataFrame(
            columns=["Fecha", "Proveedor", "Familia", "Coste (€)"]
        )

    if "proveedores" not in st.session_state:
        st.session_state.proveedores = []

    familias = ["Materia prima", "Bebidas", "Limpieza", "Otros"]

    # -------- Formulario --------
    with st.form("form_compras", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            fecha = st.date_input(
                "Fecha",
                value=date.today(),
                format="DD/MM/YYYY"
            )

        with col2:
            proveedor = st.selectbox(
                "Proveedor",
                st.session_state.proveedores + ["+ Añadir proveedor"]
            )

        if proveedor == "+ Añadir proveedor":
            nuevo_proveedor = st.text_input("Nuevo proveedor")
        else:
            nuevo_proveedor = None

        familia = st.selectbox("Familia / Apartado", familias)

        coste = st.number_input(
            "Coste total (€)",
            min_value=0.00,
            step=0.01,
            format="%.2f"
        )

        submitted = st.form_submit_button("Registrar compra")

        if submitted:

            if proveedor == "+ Añadir proveedor":
                if not nuevo_proveedor:
                    st.warning("Introduce el nombre del proveedor")
                    st.stop()
                proveedor = nuevo_proveedor
                if proveedor not in st.session_state.proveedores:
                    st.session_state.proveedores.append(proveedor)

            if coste <= 0:
                st.warning("El coste debe ser mayor que 0")
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

            st.success("Compra registrada")

    # -------- Tabla --------
    st.divider()

    if st.session_state.compras.empty:
        st.info("No hay compras registradas")
    else:
        st.dataframe(
            st.session_state.compras,
            hide_index=True,
            use_container_width=True
        )

        total = st.session_state.compras["Coste (€)"].sum()
        st.markdown(f"### Total registrado: **{total:.2f} €**")

        idx = st.selectbox(
            "Eliminar compra",
            st.session_state.compras.index,
            format_func=lambda i: (
                f'{st.session_state.compras.loc[i,"Fecha"]} | '
                f'{st.session_state.compras.loc[i,"Proveedor"]} | '
                f'{st.session_state.compras.loc[i,"Coste (€)"]:.2f} €'
            )
        )

        if st.button("Eliminar"):
            st.session_state.compras = (
                st.session_state.compras
                .drop(idx)
                .reset_index(drop=True)
            )
            st.success("Compra eliminada")
