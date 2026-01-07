import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =====================================================
# CONFIGURACIÓN
# =====================================================
st.title("OYKEN · Inventario")

INVENTARIO_FILE = Path("inventario_mensual.csv")

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# =====================================================
# CARGA / INICIALIZACIÓN CSV
# =====================================================
if INVENTARIO_FILE.exists():
    df_inv = pd.read_csv(INVENTARIO_FILE)
else:
    df_inv = pd.DataFrame(
        columns=[
            "anio",
            "mes",
            "inventario_cierre_eur",
            "variacion_inventario_eur",
            "fecha_actualizacion"
        ]
    )

# Asegurar tipos
df_inv["anio"] = pd.to_numeric(df_inv["anio"], errors="coerce")
df_inv["mes"] = pd.to_numeric(df_inv["mes"], errors="coerce")
df_inv["inventario_cierre_eur"] = pd.to_numeric(
    df_inv["inventario_cierre_eur"], errors="coerce"
).fillna(0)

# =====================================================
# BLOQUE 1 — REGISTRO DE INVENTARIO MENSUAL
# =====================================================
st.divider()
st.subheader("Registro de inventario mensual")

with st.form("form_inventario_mensual", clear_on_submit=True):

    c1, c2 = st.columns(2)

    with c1:
        anios_disponibles = sorted(
            set(df_inv["anio"].dropna().astype(int).tolist())
            | {date.today().year}
        )
        anio_sel = st.selectbox("Año", anios_disponibles)

    with c2:
        mes_sel = st.selectbox(
            "Mes",
            options=list(MESES_ES.keys()),
            format_func=lambda x: MESES_ES[x]
        )

    inventario_valor = st.number_input(
        "Inventario a cierre de mes (€)",
        min_value=0.0,
        step=100.0,
        format="%.2f"
    )

    guardar = st.form_submit_button("Guardar inventario")

    if guardar:
        # Eliminar posible registro previo del mismo año/mes
        df_inv = df_inv[
            ~((df_inv["anio"] == anio_sel) & (df_inv["mes"] == mes_sel))
        ]

        nuevo = pd.DataFrame([{
            "anio": anio_sel,
            "mes": mes_sel,
            "inventario_cierre_eur": round(inventario_valor, 2),
            "variacion_inventario_eur": 0,  # se recalcula luego
            "fecha_actualizacion": date.today().isoformat()
        }])

        df_inv = pd.concat([df_inv, nuevo], ignore_index=True)
        df_inv.to_csv(INVENTARIO_FILE, index=False)

        st.success("Inventario mensual guardado correctamente")
        st.rerun()

# =====================================================
# BLOQUE 2 — HISTÓRICO DE INVENTARIOS MENSUALES
# =====================================================
st.divider()
st.subheader("Histórico de inventarios mensuales")

if df_inv.empty:
    st.info("Aún no hay inventarios registrados.")
else:
    df_hist = df_inv.sort_values(["anio", "mes"]).copy()
    df_hist["Mes"] = df_hist["mes"].map(MESES_ES)

    st.dataframe(
        df_hist[[
            "anio",
            "Mes",
            "inventario_cierre_eur"
        ]].rename(columns={
            "anio": "Año",
            "inventario_cierre_eur": "Inventario cierre (€)"
        }),
        hide_index=True,
        use_container_width=True
    )

# =====================================================
# BLOQUE 3 — VARIACIÓN DE INVENTARIO MENSUAL
# =====================================================
st.divider()
st.subheader("Variación de inventario mensual")

if not df_inv.empty:

    df_var = df_inv.sort_values(["anio", "mes"]).copy()

    df_var["variacion_inventario_eur"] = (
        df_var["inventario_cierre_eur"]
        - df_var["inventario_cierre_eur"].shift(1)
    )

    # Primer registro sin variación
    df_var.loc[df_var.index[0], "variacion_inventario_eur"] = 0

    # Persistir variación recalculada
    df_inv.update(df_var)
    df_inv.to_csv(INVENTARIO_FILE, index=False)

    df_var["Mes"] = df_var["mes"].map(MESES_ES)

    st.dataframe(
        df_var[[
            "anio",
            "Mes",
            "inventario_cierre_eur",
            "variacion_inventario_eur"
        ]].rename(columns={
            "anio": "Año",
            "inventario_cierre_eur": "Inventario cierre (€)",
            "variacion_inventario_eur": "Variación (€)"
        }),
        hide_index=True,
        use_container_width=True
    )

# =====================================================
# BLOQUE 4 — INVENTARIO MENSUAL (CSV CANÓNICO)
# =====================================================
st.divider()
st.subheader("Inventario mensual (estructura de cálculo)")

st.caption(
    "Este bloque representa exactamente los datos utilizados por EBITDA. "
    "No se edita manualmente."
)

if not df_inv.empty:

    df_csv = df_inv.sort_values(["anio", "mes"]).copy()
    df_csv["Mes"] = df_csv["mes"].map(MESES_ES)

    st.dataframe(
        df_csv[[
            "anio",
            "Mes",
            "inventario_cierre_eur",
            "variacion_inventario_eur",
            "fecha_actualizacion"
        ]].rename(columns={
            "anio": "Año",
            "inventario_cierre_eur": "Inventario cierre (€)",
            "variacion_inventario_eur": "Variación inventario (€)",
            "fecha_actualizacion": "Última actualización"
        }),
        hide_index=True,
        use_container_width=True
    )
