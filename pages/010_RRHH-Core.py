import streamlit as st
from datetime import date

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================
st.set_page_config(
    page_title="OIKEN · RRHH Core",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ======================================================
# SESSION STATE · MODELO RRHH CORE
# ======================================================
if "rrhh_core" not in st.session_state:
    st.session_state.rrhh_core = {
        "configuracion": {
            "apertura": "13:00",
            "cierre": "23:30",
            "dias": ["L", "M", "X", "J", "V", "S", "D"],
            "partido": False,
            "tramos": []
        },
        "posicionamiento": {},
        "horas_estructurales": {},
        "salida": {}
    }

# ======================================================
# HEADER
# ======================================================
st.title("RRHH Core · Estructura Operativa")
st.caption(
    "Definición de la estructura humana mínima del negocio "
    "(independiente de ventas, plantilla y resultados)"
)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("**Estado del modelo:** 🟢 Activo")
with col_h2:
    st.markdown(f"**Última revisión:** {date.today().strftime('%d/%m/%Y')}")

st.info(
    "Esta página define la estructura humana mínima necesaria para operar. "
    "No se utiliza en el día a día, solo cuando cambia el modelo operativo."
)

st.divider()

# ======================================================
# BLOQUE 1 · CONFIGURACIÓN OPERATIVA
# ======================================================
st.subheader("Configuración operativa del negocio")
st.caption("Define cómo funciona tu negocio en el tiempo. No hablamos de personas ni de costes.")

c1, c2, c3, c4 = st.columns(4)
with c1:
    apertura = st.text_input("Hora de apertura", st.session_state.rrhh_core["configuracion"]["apertura"])
with c2:
    cierre = st.text_input("Hora de cierre", st.session_state.rrhh_core["configuracion"]["cierre"])
with c3:
    dias = st.multiselect(
        "Días operativos",
        ["L", "M", "X", "J", "V", "S", "D"],
        st.session_state.rrhh_core["configuracion"]["dias"]
    )
with c4:
    partido = st.checkbox("Horario partido", st.session_state.rrhh_core["configuracion"]["partido"])

st.session_state.rrhh_core["configuracion"].update({
    "apertura": apertura,
    "cierre": cierre,
    "dias": dias,
    "partido": partido
})

st.divider()

# ======================================================
# BLOQUE 1B · TRAMOS OPERATIVOS
# ======================================================
st.subheader("Tramos operativos")
st.caption("Un tramo es un periodo donde la lógica del servicio no cambia.")

if st.button("➕ Añadir tramo"):
    st.session_state.rrhh_core["configuracion"]["tramos"].append({
        "nombre": f"Tramo {len(st.session_state.rrhh_core['configuracion']['tramos']) + 1}",
        "inicio": "",
        "fin": "",
        "servicio": "Producción intensiva"
    })

for i, tramo in enumerate(st.session_state.rrhh_core["configuracion"]["tramos"]):
    with st.expander(tramo["nombre"]):
        t1, t2, t3, t4 = st.columns(4)
        with t1:
            tramo["nombre"] = st.text_input("Nombre del tramo", tramo["nombre"], key=f"tramo_nombre_{i}")
        with t2:
            tramo["inicio"] = st.text_input("Hora inicio", tramo["inicio"], key=f"tramo_inicio_{i}")
        with t3:
            tramo["fin"] = st.text_input("Hora fin", tramo["fin"], key=f"tramo_fin_{i}")
        with t4:
            tramo["servicio"] = st.selectbox(
                "Servicio dominante",
                ["Producción intensiva", "Servicio en mesa", "Rapidez / rotación", "Híbrido"],
                key=f"tramo_servicio_{i}"
            )

st.divider()

# ======================================================
# BLOQUE 2 · GUÍA DE POSICIONAMIENTO
# ======================================================
st.subheader("Guía de posicionamiento por tramo")
st.caption("Indica qué funciones existen realmente en cada tramo. No personas. No puestos.")

ZONAS = {
    "Cocina": [
        "Producción plancha",
        "Freidora",
        "Pase caliente",
        "Office / limpieza operativa"
    ],
    "Sala": [
        "Responsable / coordinación",
        "Servicio en mesa",
        "Runner comida"
    ],
    "Barra": [
        "Pedido / cobro",
        "Entrega take away"
    ],
    "Back": [
        "Reposición"
    ]
}

for tramo in st.session_state.rrhh_core["configuracion"]["tramos"]:
    st.markdown(f"### {tramo['nombre']} ({tramo['inicio']}–{tramo['fin']})")

    if tramo["nombre"] not in st.session_state.rrhh_core["posicionamiento"]:
        st.session_state.rrhh_core["posicionamiento"][tramo["nombre"]] = {}

    cols = st.columns(len(ZONAS))
    for col, (zona, funciones) in zip(cols, ZONAS.items()):
        with col:
            st.markdown(f"**{zona}**")
            for funcion in funciones:
                key = f"{tramo['nombre']}_{zona}_{funcion}"
                valor = st.checkbox(
                    funcion,
                    st.session_state.rrhh_core["posicionamiento"][tramo["nombre"]].get(funcion, False),
                    key=key
                )
                st.session_state.rrhh_core["posicionamiento"][tramo["nombre"]][funcion] = valor

st.divider()

# ======================================================
# BLOQUE 3 · MOTOR DE ESTRUCTURALIDAD
# ======================================================
st.subheader("Estructura operativa mínima detectada")
st.caption("OIKEN determina qué funciones son estructurales para sostener la operación.")

FUNCIONES_NO_ESTRUCTURALES = ["Runner comida", "Runner bebida", "Refuerzo"]

estructura_detectada = []

for tramo, funciones in st.session_state.rrhh_core["posicionamiento"].items():
    for funcion, existe in funciones.items():
        if not existe:
            continue
        if funcion in FUNCIONES_NO_ESTRUCTURALES:
            estructura_detectada.append((tramo, funcion, False))
        else:
            estructura_detectada.append((tramo, funcion, True))

if estructura_detectada:
    for tramo in sorted(set(t[0] for t in estructura_detectada)):
        st.markdown(f"**{tramo}**")
        tabla = []
        for t, f, es in estructura_detectada:
            if t == tramo:
                tabla.append({
                    "Función": f,
                    "Resultado": "🟢 ESTRUCTURAL" if es else "⚪ NO estructural"
                })
        st.table(tabla)
else:
    st.info("Define funciones para detectar la estructura.")

st.divider()

# ======================================================
# BLOQUE 4 · HORAS ESTRUCTURALES
# ======================================================
st.subheader("Cobertura estructural por función")
st.caption("Define durante cuántas horas cada función estructural debe estar cubierta.")

for tramo, funcion, es in estructura_detectada:
    if not es:
        continue

    clave = f"{tramo}_{funcion}"
    if clave not in st.session_state.rrhh_core["horas_estructurales"]:
        st.session_state.rrhh_core["horas_estructurales"][clave] = {"inicio": "", "fin": "", "horas": 0}

    with st.container():
        st.markdown(f"**{funcion}** · *{tramo}*")
        h1, h2, h3 = st.columns([2, 2, 1])

        with h1:
            inicio = st.text_input("Inicio", st.session_state.rrhh_core["horas_estructurales"][clave]["inicio"], key=f"hi_{clave}")
        with h2:
            fin = st.text_input("Fin", st.session_state.rrhh_core["horas_estructurales"][clave]["fin"], key=f"hf_{clave}")

        horas = 0
        try:
            if inicio and fin:
                hi, mi = map(int, inicio.split(":"))
                hf, mf = map(int, fin.split(":"))
                horas = max((hf + mf/60) - (hi + mi/60), 0)
        except:
            st.warning("Formato HH:MM")

        st.session_state.rrhh_core["horas_estructurales"][clave] = {
            "inicio": inicio,
            "fin": fin,
            "horas": horas
        }

        with h3:
            st.metric("Horas", f"{horas:.1f}")

        st.divider()

# ======================================================
# BLOQUE 5 · HUELLA HUMANA ESTRUCTURAL
# ======================================================
st.subheader("Huella Humana Estructural")
st.caption("Define el suelo humano real del negocio.")

intervalos = []
for datos in st.session_state.rrhh_core["horas_estructurales"].values():
    try:
        hi, mi = map(int, datos["inicio"].split(":"))
        hf, mf = map(int, datos["fin"].split(":"))
        intervalos.append((hi*60 + mi, hf*60 + mf))
    except:
        continue

if intervalos:
    conteos = []
    for minuto in range(0, 24*60, 15):
        activos = sum(1 for i, f in intervalos if i <= minuto < f)
        conteos.append(activos)

    pico = max(conteos)
    total_horas = sum((f - i) for i, f in intervalos) / 60

    st.metric("Pico estructural simultáneo", f"{pico} funciones")
    st.metric("Horas estructurales totales", f"{total_horas:.1f} h / día")

    st.info(
        "Este resultado no depende del volumen ni de la plantilla real. "
        "Define el suelo humano del negocio."
    )

    st.session_state.rrhh_core["salida"] = {
        "pico_simultaneo": pico,
        "horas_diarias": total_horas,
        "fecha_modelo": date.today().isoformat()
    }
else:
    st.info("Completa las horas estructurales para ver la huella humana.")

# ======================================================
# BLOQUE FINAL · SALIDA ESTRUCTURAL
# ======================================================
st.divider()
st.subheader("Salida estructural RRHH Core")

if st.session_state.rrhh_core["salida"]:
    st.write(st.session_state.rrhh_core["salida"])
    st.caption(
        "Este objeto será consumido por el módulo Breakeven Operativo "
        "cuando esté disponible."
    )
else:
    st.info("Todavía no hay salida estructural disponible.")
