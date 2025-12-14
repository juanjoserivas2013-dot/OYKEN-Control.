st.divider()
st.subheader("Resumen mensual · Acumulado vs mes anterior")

if df.empty:
    st.info("Aún no hay datos suficientes para el resumen mensual.")
else:
    # --- Mes actual automático (último día con ventas)
    fecha_ref = df["fecha"].max()
    mes_actual = fecha_ref.month
    año_actual = fecha_ref.year

    # --- Mes anterior (manejo cambio de año)
    if mes_actual == 1:
        mes_anterior = 12
        año_anterior = año_actual - 1
    else:
        mes_anterior = mes_actual - 1
        año_anterior = año_actual

    # --- Datos mes actual (acumulado)
    df_mes_actual = df[
        (df["fecha"].dt.year == año_actual) &
        (df["fecha"].dt.month == mes_actual)
    ]

    total_actual = df_mes_actual["ventas_total_eur"].sum()
    dias_actual = df_mes_actual["fecha"].nunique()
    prom_actual = total_actual / dias_actual if dias_actual > 0 else 0

    # --- Datos mes anterior (completo)
    df_mes_anterior = df[
        (df["fecha"].dt.year == año_anterior) &
        (df["fecha"].dt.month == mes_anterior)
    ]

    total_anterior = df_mes_anterior["ventas_total_eur"].sum()
    dias_anterior = df_mes_anterior["fecha"].nunique()
    prom_anterior = total_anterior / dias_anterior if dias_anterior > 0 else 0

    # --- Diferencias
    dif_eur = total_actual - total_anterior
    dif_pct = (dif_eur / total_anterior * 100) if total_anterior > 0 else 0

    # --- Nombres de meses
    meses = [
        "Enero","Febrero","Marzo","Abril","Mayo","Junio",
        "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
    ]
    nombre_mes_actual = f"{meses[mes_actual-1]} {año_actual}"
    nombre_mes_anterior = f"{meses[mes_anterior-1]} {año_anterior}"

    # =========================
    # VISUALIZACIÓN
    # =========================
    c1, c2, c3 = st.columns(3)

    # --- Mes actual
    with c1:
        st.markdown(f"**Mes actual · {nombre_mes_actual}**")
        st.write(f"Total acumulado: **{total_actual:,.2f} €**")
        st.write(f"Días con venta: {dias_actual}")
        st.write(f"Promedio diario: {prom_actual:,.2f} €")

    # --- Mes anterior
    with c2:
        st.markdown(f"**Mes anterior · {nombre_mes_anterior}**")
        st.write(f"Total mes: **{total_anterior:,.2f} €**")
        st.write(f"Días con venta: {dias_anterior}")
        st.write(f"Promedio diario: {prom_anterior:,.2f} €")

    # --- Diferencia
    with c3:
        st.markdown("**Diferencia**")
        st.metric(
            "€ vs mes anterior",
            f"{dif_eur:+,.2f} €",
            f"{dif_pct:+.1f} %"
        )
