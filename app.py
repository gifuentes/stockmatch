# ==========================================================
# STOCKMATCH
# Auditoría de inventarios no estructurados
# Matemáticas Discretas - Álgebra Relacional
# ==========================================================

import re
import unicodedata
from html import escape
from difflib import SequenceMatcher
from itertools import combinations
from textwrap import dedent

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# ==========================================================
# 1. CONFIGURACIÓN GENERAL
# ==========================================================

st.set_page_config(
    page_title="StockMatch | Auditoría de Inventarios",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# 2. ESTADO INICIAL
# ==========================================================

if "page" not in st.session_state:
    st.session_state["page"] = "Inicio"

if "result_view" not in st.session_state:
    st.session_state["result_view"] = "Resumen"

if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

if "_scroll_top" not in st.session_state:
    st.session_state["_scroll_top"] = False


# ==========================================================
# 3. FUNCIONES DE INTERFAZ
# ==========================================================

def ui(markup: str):
    """Renderiza HTML de presentación sin que Streamlit lo muestre como código."""
    clean = dedent(markup).strip()
    clean = re.sub(r"\s*\n\s*", " ", clean)
    clean = re.sub(r">\s+<", "><", clean)
    st.markdown(clean, unsafe_allow_html=True)


def scroll_to_top():
    """Sube al inicio después de cambiar de pantalla."""
    if st.session_state.get("_scroll_top", False):
        components.html(
            """
            <script>
            setTimeout(function() {
                try { window.parent.scrollTo({top: 0, behavior: "smooth"}); }
                catch(e) {}
            }, 80);
            </script>
            """,
            height=0
        )
        st.session_state["_scroll_top"] = False


def change_page(page_name: str):
    """Cambia de pantalla sin perder la configuración guardada."""
    st.session_state["page"] = page_name
    st.session_state["_scroll_top"] = True

    if page_name == "Análisis":
        st.session_state.setdefault("result_view", "Resumen")


def change_view(view_name: str):
    """Cambia la sección interna del análisis."""
    st.session_state["result_view"] = view_name
    st.session_state["_scroll_top"] = True


def altura_tabla(df, minimo=150, maximo=430):
    """
    Calcula una altura adecuada para evitar filas vacías grandes.
    """
    if df is None or df.empty:
        return minimo

    filas = len(df)
    altura = 44 + filas * 36
    return max(minimo, min(altura, maximo))


# ==========================================================
# 4. ESTILOS VISUALES
# ==========================================================

st.markdown(
    """
    <style>
    :root {
        --navy: #020B1F;
        --navy2: #061A33;
        --blue: #123E73;
        --sky: #EAF2FF;
        --bg: #F4F7FB;
        --white: #FFFFFF;
        --text: #0F172A;
        --muted: #64748B;
        --border: #D6E0EF;
        --teal: #0F766E;
        --gold: #B7791F;
        --red: #B42318;
    }

    .stApp {
        background: linear-gradient(180deg, #F7FAFE 0%, #EEF4FA 100%);
        color: var(--text);
    }

    .block-container {
        max-width: 1220px;
        padding-top: 1.1rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        display: none !important;
    }

    html, body, [class*="css"] {
        font-family: "Segoe UI", "Inter", Arial, sans-serif;
        color: var(--text);
    }

    h1 {
        color: var(--navy2) !important;
        font-size: 2.45rem !important;
        font-weight: 850 !important;
        letter-spacing: -0.04em !important;
        margin-bottom: 0.6rem !important;
    }

    h2 {
        color: var(--navy2) !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
    }

    h3 {
        color: var(--navy2) !important;
        font-weight: 780 !important;
    }

    .top-separator {
        height: 5px;
        background: linear-gradient(90deg, #061A33, #123E73, transparent);
        border-radius: 999px;
        margin: 18px 0 28px;
    }

    .brand-box {
        display: flex;
        align-items: center;
        gap: 12px;
        min-height: 54px;
        background: #FFFFFF;
        border: 1px solid #D6E0EF;
        border-radius: 18px;
        padding: 12px 16px;
        box-shadow: 0 8px 20px rgba(6, 26, 51, 0.06);
    }

    .brand-mark {
        width: 44px;
        height: 44px;
        border-radius: 13px;
        background: linear-gradient(135deg, var(--navy), var(--blue));
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-weight: 900;
        font-size: 14px;
    }

    .brand-name {
        font-size: 1.18rem;
        font-weight: 900;
        color: var(--navy2);
        line-height: 1.1;
    }

    .brand-sub {
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 3px;
    }

    [class*="st-key-nav_"] button {
        background: #F1F5FB !important;
        color: var(--navy2) !important;
        border: 1px solid #D6E0EF !important;
        border-radius: 14px !important;
        height: 54px !important;
        font-weight: 850 !important;
        box-shadow: 0 6px 14px rgba(6, 26, 51, 0.04) !important;
    }

    [class*="st-key-nav_"] button:hover {
        background: #EAF2FF !important;
        border-color: #BBD0EA !important;
    }

    [class*="st-key-nav_"][class*="_active"] button {
        background: var(--navy2) !important;
        color: #FFFFFF !important;
        border-color: var(--navy2) !important;
        box-shadow: 0 8px 18px rgba(6, 26, 51, 0.20) !important;
    }

    .hero {
        background:
            radial-gradient(circle at 82% 18%, rgba(31,93,153,0.95) 0%, rgba(6,26,51,0.92) 35%, rgba(2,11,31,1) 100%);
        border-radius: 28px;
        color: white;
        padding: 48px 52px;
        margin-bottom: 24px;
        box-shadow: 0 22px 50px rgba(2, 11, 31, 0.24);
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.35fr 0.85fr;
        gap: 36px;
        align-items: center;
    }

    .hero-pill {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.22);
        color: #D8E9FF;
        font-size: 0.78rem;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 3.65rem;
        font-weight: 950;
        letter-spacing: -0.065em;
        line-height: 1.0;
        margin-bottom: 14px;
    }

    .hero-text {
        font-size: 1.04rem;
        line-height: 1.75;
        color: #E5F0FF;
        max-width: 790px;
    }

    .hero-panel {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 22px;
        padding: 24px;
    }

    .hero-panel-title {
        color: #FFFFFF;
        font-weight: 850;
        font-size: 1.05rem;
        margin-bottom: 16px;
    }

    .flow-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 15px;
        padding: 12px 14px;
        margin-bottom: 10px;
        color: #EAF2FF;
        font-weight: 760;
        font-size: 0.93rem;
    }

    .flow-tag {
        color: #A7D3FF;
        font-weight: 950;
    }

    .card {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 26px 28px;
        margin-bottom: 22px;
        box-shadow: 0 10px 26px rgba(6, 26, 51, 0.07);
    }

    .card-tight {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 8px 20px rgba(6, 26, 51, 0.055);
    }

    .label {
        color: var(--muted);
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .card-title {
        color: var(--navy2);
        font-size: 1.35rem;
        font-weight: 900;
        letter-spacing: -0.04em;
        margin-bottom: 8px;
    }

    .card-text {
        color: #334155;
        font-size: 0.98rem;
        line-height: 1.68;
    }

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 9px 22px rgba(6, 26, 51, 0.07);
        min-height: 118px;
        border-top: 6px solid var(--navy2);
        margin-bottom: 16px;
    }

    .kpi-card.blue { border-top-color: var(--blue); }
    .kpi-card.teal { border-top-color: var(--teal); }
    .kpi-card.gold { border-top-color: var(--gold); }
    .kpi-card.red { border-top-color: var(--red); }

    .kpi-label {
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 10px;
    }

    .kpi-value {
        color: var(--navy2);
        font-size: 1.72rem;
        font-weight: 950;
        letter-spacing: -0.055em;
        line-height: 1.05;
        word-break: break-word;
    }

    .kpi-note {
        color: #64748B;
        font-size: 0.84rem;
        margin-top: 9px;
        line-height: 1.4;
    }

    .step-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }

    .step-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 22px;
        min-height: 162px;
        box-shadow: 0 8px 20px rgba(6, 26, 51, 0.055);
    }

    .step-num {
        width: 36px;
        height: 36px;
        border-radius: 12px;
        background: var(--navy2);
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 950;
        margin-bottom: 14px;
    }

    .step-title {
        font-size: 1.05rem;
        color: var(--navy2);
        font-weight: 900;
        margin-bottom: 8px;
    }

    .step-text {
        color: var(--muted);
        line-height: 1.6;
        font-size: 0.92rem;
    }

    .info-box {
        background: #EAF2FF;
        border: 1px solid #C7D9F0;
        border-left: 6px solid var(--blue);
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 20px;
        color: #1E293B;
        line-height: 1.65;
    }

    .empty-box {
        background: #FFFFFF;
        border: 1px dashed #9DB8D8;
        border-radius: 22px;
        padding: 36px 30px;
        text-align: center;
        margin: 0;
    }

    .empty-title {
        color: var(--navy2);
        font-weight: 900;
        font-size: 1.55rem;
        margin-bottom: 8px;
    }

    .empty-text {
        color: var(--muted);
        line-height: 1.65;
        max-width: 680px;
        margin: 0 auto;
    }

    [class*="st-key-view_"] button {
        background: #F1F5FB !important;
        color: var(--navy2) !important;
        border: 1px solid #D6E0EF !important;
        border-radius: 14px !important;
        height: 50px !important;
        font-weight: 850 !important;
        box-shadow: none !important;
    }

    [class*="st-key-view_"] button:hover {
        background: #EAF2FF !important;
        border-color: #BBD0EA !important;
    }

    [class*="st-key-view_"][class*="_active"] button {
        background: var(--navy2) !important;
        color: #FFFFFF !important;
        border-color: var(--navy2) !important;
        box-shadow: 0 8px 18px rgba(6, 26, 51, 0.20) !important;
    }

    .st-key-main_start button,
    .st-key-save_config button,
    .st-key-run_analysis button,
    .st-key-go_config_empty button {
        background: var(--navy2) !important;
        color: white !important;
        border-radius: 13px !important;
        border: none !important;
        font-weight: 850 !important;
        height: 50px !important;
    }

    .st-key-main_start button:hover,
    .st-key-save_config button:hover,
    .st-key-run_analysis button:hover,
    .st-key-go_config_empty button:hover {
        background: var(--blue) !important;
    }

    div.stDownloadButton > button {
        background: var(--navy2) !important;
        color: white !important;
        border-radius: 13px !important;
        border: none !important;
        font-weight: 850 !important;
        min-height: 52px !important;
        white-space: normal !important;
    }

    div.stDownloadButton > button:hover {
        background: var(--blue) !important;
    }

    .divider-blue {
        height: 5px;
        background: linear-gradient(90deg, var(--navy2), var(--blue), transparent);
        border-radius: 999px;
        margin: 26px 0 22px;
    }

    div[data-testid="stFileUploader"] {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 14px;
    }

    div[data-baseweb="select"] > div {
        border-radius: 14px !important;
        border-color: #B8CCE5 !important;
        min-height: 48px;
    }

    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 16px;
        overflow: hidden;
        background: #FFFFFF;
    }

    div[data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 14px;
    }

    .table-title {
        font-size: 1.25rem;
        color: var(--navy2);
        font-weight: 900;
        margin: 12px 0 8px;
    }

    .table-help {
        color: var(--muted);
        font-size: 0.94rem;
        line-height: 1.6;
        margin-bottom: 10px;
    }

    @media (max-width: 980px) {
        .hero-grid,
        .step-row {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 2.55rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 5. NAVEGACIÓN SUPERIOR
# ==========================================================

def nav_key(page_name: str):
    active = st.session_state["page"] == page_name
    clean = (
        page_name.lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace(" ", "_")
    )
    return f"nav_{clean}_{'active' if active else 'inactive'}"


def view_key(view_name: str):
    active = st.session_state["result_view"] == view_name
    clean = view_name.lower().replace(" ", "_")
    return f"view_{clean}_{'active' if active else 'inactive'}"


def render_topbar():
    col_brand, col_1, col_2, col_3 = st.columns([3.8, 1.15, 1.45, 1.7], gap="small")

    with col_brand:
        ui("""
        <div class="brand-box">
            <div class="brand-mark">SM</div>
            <div>
                <div class="brand-name">StockMatch</div>
                <div class="brand-sub">Auditoría de inventarios no estructurados</div>
            </div>
        </div>
        """)

    with col_1:
        if st.button("Inicio", use_container_width=True, key=nav_key("Inicio")):
            change_page("Inicio")
            st.rerun()

    with col_2:
        if st.button("Configuración", use_container_width=True, key=nav_key("Configuración")):
            change_page("Configuración")
            st.rerun()

    with col_3:
        if st.button("Análisis y reportes", use_container_width=True, key=nav_key("Análisis")):
            change_page("Análisis")
            st.session_state["result_view"] = "Resumen"
            st.rerun()

    ui('<div class="top-separator"></div>')

    scroll_to_top()


# ==========================================================
# 6. KPI
# ==========================================================

def render_kpis(items, columns=4):
    cols = st.columns(columns, gap="medium")

    for col, item in zip(cols, items):
        variant = escape(str(item.get("variant", "")))
        label = escape(str(item.get("label", "")))
        value = escape(str(item.get("value", "")))
        note = escape(str(item.get("note", "")))

        with col:
            st.markdown(
                f'<div class="kpi-card {variant}">'
                f'<div class="kpi-label">{label}</div>'
                f'<div class="kpi-value">{value}</div>'
                f'<div class="kpi-note">{note}</div>'
                f'</div>',
                unsafe_allow_html=True
            )


# ==========================================================
# 7. NORMALIZACIÓN Y SIMILITUD
# ==========================================================

def normalizar_texto(valor) -> str:
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caracter for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def similitud_textual(valor_a, valor_b) -> float:
    texto_a = normalizar_texto(valor_a)
    texto_b = normalizar_texto(valor_b)

    if not texto_a and not texto_b:
        return 100.0

    if not texto_a or not texto_b:
        return 0.0

    return round(SequenceMatcher(None, texto_a, texto_b).ratio() * 100, 2)


def clasificar_confianza(similitud: float) -> str:
    if similitud >= 95:
        return "Alta"
    if similitud >= 88:
        return "Media"
    return "Revisión manual"


def comparar_dos_registros(fila_a, fila_b, columnas_comparacion):
    detalle = []

    for columna in columnas_comparacion:
        valor_a = fila_a[columna]
        valor_b = fila_b[columna]
        similitud = similitud_textual(valor_a, valor_b)

        detalle.append({
            "Campo": columna,
            "Valor en registro A": str(valor_a),
            "Valor en registro B": str(valor_b),
            "Similitud (%)": similitud
        })

    similitud_promedio = round(
        sum(item["Similitud (%)"] for item in detalle) / len(detalle),
        2
    )

    detalle_ordenado = sorted(
        detalle,
        key=lambda item: item["Similitud (%)"],
        reverse=True
    )

    mejores = detalle_ordenado[:2]

    motivo = "; ".join(
        f"{item['Campo']}: {item['Similitud (%)']:.0f}%"
        for item in mejores
    )

    return similitud_promedio, motivo, pd.DataFrame(detalle)


# ==========================================================
# 8. AGRUPACIÓN POR TRANSITIVIDAD
# ==========================================================

class UnionFind:
    def __init__(self, elementos):
        self.padre = {elemento: elemento for elemento in elementos}

    def encontrar(self, elemento):
        if self.padre[elemento] != elemento:
            self.padre[elemento] = self.encontrar(self.padre[elemento])
        return self.padre[elemento]

    def unir(self, elemento_a, elemento_b):
        raiz_a = self.encontrar(elemento_a)
        raiz_b = self.encontrar(elemento_b)

        if raiz_a != raiz_b:
            self.padre[raiz_b] = raiz_a

    def obtener_grupos(self):
        grupos = {}

        for elemento in self.padre:
            raiz = self.encontrar(elemento)
            grupos.setdefault(raiz, []).append(elemento)

        return list(grupos.values())


# ==========================================================
# 9. MOTOR PRINCIPAL
# ==========================================================

def analizar_inventario(df, columna_id, columnas_comparacion, umbral):
    df_trabajo = df.copy().reset_index(drop=True)
    indices = list(df_trabajo.index)

    estructura_grupos = UnionFind(indices)
    pares_internos = []
    detalles_por_par = {}

    for i, j in combinations(indices, 2):
        similitud, motivo, detalle = comparar_dos_registros(
            df_trabajo.loc[i],
            df_trabajo.loc[j],
            columnas_comparacion
        )

        if similitud >= umbral:
            estructura_grupos.unir(i, j)

            pares_internos.append({
                "_i": i,
                "_j": j,
                "ID A": df_trabajo.loc[i, columna_id],
                "Registro A": df_trabajo.loc[i, columnas_comparacion[0]],
                "ID B": df_trabajo.loc[j, columna_id],
                "Registro B": df_trabajo.loc[j, columnas_comparacion[0]],
                "Similitud promedio (%)": similitud,
                "Confianza": clasificar_confianza(similitud),
                "Motivo principal": motivo
            })

            detalles_por_par[(i, j)] = detalle

    grupos_crudos = estructura_grupos.obtener_grupos()
    grupos_validos = sorted(
        [sorted(grupo) for grupo in grupos_crudos if len(grupo) > 1],
        key=lambda grupo: min(grupo)
    )

    indice_a_grupo = {}

    for numero, grupo in enumerate(grupos_validos, start=1):
        for indice in grupo:
            indice_a_grupo[indice] = numero

    for par in pares_internos:
        numero_grupo = indice_a_grupo.get(par["_i"], "")
        par["Grupo"] = f"G-{numero_grupo}" if numero_grupo else ""

    tabla_pares_interna = pd.DataFrame(pares_internos)

    columnas_pares = [
        "Grupo",
        "ID A",
        "Registro A",
        "ID B",
        "Registro B",
        "Similitud promedio (%)",
        "Confianza",
        "Motivo principal"
    ]

    if not tabla_pares_interna.empty:
        tabla_pares = tabla_pares_interna[columnas_pares].copy()
    else:
        tabla_pares = pd.DataFrame(columns=columnas_pares)

    filas_grupos = []

    for numero, grupo in enumerate(grupos_validos, start=1):
        ids = [str(df_trabajo.loc[indice, columna_id]) for indice in grupo]
        registros = [
            str(df_trabajo.loc[indice, columnas_comparacion[0]])
            for indice in grupo
        ]

        sims_grupo = [
            par["Similitud promedio (%)"]
            for par in pares_internos
            if par["_i"] in grupo and par["_j"] in grupo
        ]

        promedio_grupo = round(sum(sims_grupo) / len(sims_grupo), 2) if sims_grupo else ""

        filas_grupos.append({
            "Grupo": f"G-{numero}",
            "Cantidad": len(grupo),
            "IDs relacionados": ", ".join(ids),
            "Registros relacionados": " | ".join(registros),
            "Similitud promedio del grupo (%)": promedio_grupo,
            "Acción sugerida": "Revisar antes de unificar"
        })

    tabla_grupos = pd.DataFrame(filas_grupos)

    reporte_completo = df_trabajo.copy()
    grupos_sugeridos = []
    similitud_maxima = []
    coincidencias = []

    for indice in indices:
        grupo = indice_a_grupo.get(indice, "")
        grupos_sugeridos.append(f"G-{grupo}" if grupo else "")

        sims = []
        coincidentes = []

        for par in pares_internos:
            if par["_i"] == indice:
                sims.append(par["Similitud promedio (%)"])
                coincidentes.append(f"{par['ID B']} ({par['Similitud promedio (%)']}%)")
            elif par["_j"] == indice:
                sims.append(par["Similitud promedio (%)"])
                coincidentes.append(f"{par['ID A']} ({par['Similitud promedio (%)']}%)")

        similitud_maxima.append(max(sims) if sims else "")
        coincidencias.append("; ".join(coincidentes))

    reporte_completo.insert(0, "Grupo sugerido", grupos_sugeridos)
    reporte_completo["Similitud máxima (%)"] = similitud_maxima
    reporte_completo["Coincidencias detectadas"] = coincidencias
    reporte_completo["Acción sugerida"] = reporte_completo["Grupo sugerido"].apply(
        lambda grupo: "Revisar posible duplicado" if grupo else "Sin coincidencias detectadas"
    )

    resumen = {
        "registros": len(df_trabajo),
        "columnas": len(df_trabajo.columns),
        "pares_comparados": len(df_trabajo) * (len(df_trabajo) - 1) // 2,
        "pares_detectados": len(tabla_pares),
        "grupos_detectados": len(tabla_grupos)
    }

    return {
        "resumen": resumen,
        "tabla_pares": tabla_pares,
        "tabla_pares_interna": tabla_pares_interna,
        "tabla_grupos": tabla_grupos,
        "reporte_completo": reporte_completo,
        "detalles_por_par": detalles_por_par,
        "grupos_validos": grupos_validos,
        "df_trabajo": df_trabajo
    }


# ==========================================================
# 10. CSV Y DATOS DE DEMOSTRACIÓN
# ==========================================================

def leer_csv(archivo):
    try:
        archivo.seek(0)
        return pd.read_csv(archivo, encoding="utf-8-sig")
    except UnicodeDecodeError:
        archivo.seek(0)
        return pd.read_csv(archivo, encoding="latin-1")


def inventario_ejemplo():
    return pd.DataFrame({
        "codigo": [
            "SKU-001", "SKU-002", "SKU-003",
            "SKU-004", "SKU-005", "SKU-006",
            "SKU-007", "SKU-008", "SKU-009",
            "SKU-010", "SKU-011", "SKU-012"
        ],
        "nombre": [
            "Coca Cola 500 ml",
            "Coca-Cola 500ml",
            "Coca Cola 500 ML",
            "Leche Entera 1 L",
            "Leche entera 1L",
            "Leche Entera 1 litro",
            "Arroz Extra 1 kg",
            "Arroz Extra 1kg",
            "Arroz extra 1000 g",
            "Aceite vegetal 1 L",
            "Aceite Vegetal 1 litro",
            "Aceite vegetal botella 1L"
        ],
        "marca": [
            "Coca-Cola", "Coca Cola", "Coca-Cola",
            "La Lechera", "La Lechera", "La Lechera",
            "Don Pepe", "Don Pepe", "Don Pepe",
            "Ideal", "Ideal", "Ideal"
        ],
        "categoria": [
            "Bebidas", "Bebidas", "Bebidas",
            "Lácteos", "Lacteos", "Lácteos",
            "Granos", "Granos", "Granos",
            "Aceites", "Aceites", "Aceites"
        ],
        "descripcion": [
            "Bebida gaseosa sabor cola botella 500 ml",
            "Bebida gaseosa sabor cola, botella de 500 ml",
            "Gaseosa sabor cola botella 500ml",
            "Leche entera UHT en envase de 1 litro",
            "Leche entera UHT envase 1 litro",
            "Leche entera UHT en caja de 1 L",
            "Arroz blanco extra seleccionado funda 1 kg",
            "Arroz blanco extra seleccionado, funda de 1 kg",
            "Arroz blanco extra seleccionado funda 1000 g",
            "Aceite vegetal botella de 1 litro",
            "Aceite vegetal comestible presentación 1 L",
            "Aceite vegetal en botella de un litro"
        ],
        "stock": [48, 32, 20, 40, 25, 18, 60, 44, 30, 22, 17, 10]
    })


def sugerir_columna_id(columnas):
    claves = ["codigo", "id", "sku", "cod"]

    for i, columna in enumerate(columnas):
        if normalizar_texto(columna) in claves:
            return i

    return 0


def sugerir_columnas_comparacion(columnas, columna_id):
    claves = ["nombre", "producto", "marca", "categoria", "descripcion", "detalle"]
    sugeridas = []

    for columna in columnas:
        if columna == columna_id:
            continue

        if normalizar_texto(columna) in claves:
            sugeridas.append(columna)

    if sugeridas:
        return sugeridas

    return [columna for columna in columnas if columna != columna_id][:3]


# ==========================================================
# 11. PÁGINA INICIO
# ==========================================================

def page_inicio():
    ui("""
    <div class="hero">
        <div class="hero-grid">
            <div>
                <div class="hero-pill">Auditoría de inventarios</div>
                <div class="hero-title">StockMatch</div>
                <div class="hero-text">
                    Plataforma para detectar posibles registros duplicados en inventarios
                    no estructurados. El sistema compara productos, agrupa coincidencias
                    y genera reportes de revisión sin modificar el archivo original.
                </div>
            </div>
            <div class="hero-panel">
                <div class="hero-panel-title">Flujo del análisis</div>
                <div class="flow-row"><span>Cargar inventario</span><span class="flow-tag">CSV</span></div>
                <div class="flow-row"><span>Seleccionar columnas</span><span class="flow-tag">π</span></div>
                <div class="flow-row"><span>Comparar registros</span><span class="flow-tag">×</span></div>
                <div class="flow-row"><span>Filtrar coincidencias</span><span class="flow-tag">σ</span></div>
                <div class="flow-row"><span>Descargar reportes</span><span class="flow-tag">CSV</span></div>
            </div>
        </div>
    </div>
    """)

    render_kpis([
        {"label": "Datos originales", "value": "0 cambios", "note": "La app no elimina registros.", "variant": ""},
        {"label": "Control de decisión", "value": "Humano", "note": "El usuario valida cada grupo.", "variant": "blue"},
        {"label": "Salida principal", "value": "CSV", "note": "Reportes listos para revisar.", "variant": "teal"},
        {"label": "Modelo aplicado", "value": "π × σ", "note": "Álgebra relacional.", "variant": "gold"},
    ], columns=4)

    ui("""
    <div class="card">
        <div class="label">Uso del sistema</div>
        <div class="card-title">Proceso de trabajo</div>
        <div class="card-text">
            StockMatch está diseñado para que el usuario cargue un inventario,
            elija los campos que desea comparar y obtenga reportes claros de
            posibles duplicados.
        </div>
    </div>
    """)

    ui("""
    <div class="step-row">
        <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-title">Subir CSV</div>
            <div class="step-text">Carga un archivo con encabezados en la primera fila.</div>
        </div>
        <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-title">Configurar</div>
            <div class="step-text">Selecciona identificador, columnas de comparación y umbral.</div>
        </div>
        <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-title">Analizar</div>
            <div class="step-text">El sistema compara pares y forma grupos de revisión.</div>
        </div>
        <div class="step-card">
            <div class="step-num">4</div>
            <div class="step-title">Descargar</div>
            <div class="step-text">Exporta reportes para revisar los resultados.</div>
        </div>
    </div>
    """)

    st.write("")

    if st.button("Comenzar configuración", use_container_width=True, key="main_start"):
        change_page("Configuración")
        st.rerun()


# ==========================================================
# 12. PÁGINA CONFIGURACIÓN
# ==========================================================

def page_configuracion():
    st.title("Configuración del análisis")

    ui("""
    <div class="info-box">
        Carga un inventario en formato CSV y define qué columnas usará StockMatch
        para comparar los registros.
    </div>
    """)

    col_left, col_right = st.columns([1.05, 0.95], gap="large")

    with col_left:
        ui("""
        <div class="card-tight">
            <div class="label">Paso 1</div>
            <div class="card-title">Carga del inventario</div>
            <div class="card-text">
                Puedes subir un archivo CSV o utilizar datos de demostración para probar el sistema.
            </div>
        </div>
        """)

        usar_ejemplo = st.checkbox("Usar inventario de demostración", value=False)

        archivo = None

        if not usar_ejemplo:
            archivo = st.file_uploader("Subir archivo CSV", type=["csv"])

    if usar_ejemplo:
        df = inventario_ejemplo()
    elif archivo is not None:
        df = leer_csv(archivo)
    else:
        with col_right:
            ui("""
            <div class="empty-box">
                <div class="empty-title">Inventario pendiente</div>
                <div class="empty-text">
                    Sube un archivo CSV o activa el inventario de demostración para continuar.
                </div>
            </div>
            """)
        return

    if df.empty:
        st.error("El archivo cargado no contiene registros.")
        return

    columnas = list(df.columns)

    with col_right:
        ui(f"""
        <div class="card-tight">
            <div class="label">Archivo cargado</div>
            <div class="card-title">Inventario detectado</div>
            <div class="card-text">
                El archivo contiene <strong>{len(df)}</strong> registros y
                <strong>{len(columnas)}</strong> columnas.
            </div>
        </div>
        """)

        render_kpis([
            {"label": "Registros", "value": len(df), "note": "Filas cargadas", "variant": ""},
            {"label": "Columnas", "value": len(columnas), "note": "Campos disponibles", "variant": "blue"},
            {"label": "Estado", "value": "Listo", "note": "Pendiente de configurar", "variant": "teal"},
            {"label": "Formato", "value": "CSV", "note": "Archivo aceptado", "variant": "gold"},
        ], columns=2)

    with st.expander("Vista previa del inventario", expanded=False):
        vista = df.head(15)
        st.dataframe(
            vista,
            use_container_width=True,
            hide_index=True,
            height=altura_tabla(vista, maximo=360)
        )

    ui("""
    <div class="divider-blue"></div>
    <div class="card">
        <div class="label">Paso 2</div>
        <div class="card-title">Parámetros del modelo</div>
        <div class="card-text">
            Selecciona la columna identificadora, los campos que se compararán
            y el umbral mínimo de similitud.
        </div>
    </div>
    """)

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        indice_id = sugerir_columna_id(columnas)
        columna_id = st.selectbox(
            "Columna identificadora",
            columnas,
            index=indice_id
        )

    with col_b:
        umbral = st.slider(
            "Umbral mínimo de similitud (%)",
            min_value=50,
            max_value=100,
            value=82,
            step=1
        )

    columnas_disponibles = [columna for columna in columnas if columna != columna_id]
    columnas_sugeridas = sugerir_columnas_comparacion(columnas, columna_id)

    columnas_comparacion = st.multiselect(
        "Columnas para comparar",
        columnas_disponibles,
        default=columnas_sugeridas
    )

    if not columnas_comparacion:
        st.warning("Selecciona al menos una columna para comparar.")
        return

    render_kpis([
        {"label": "Columna ID", "value": columna_id, "note": "Identificador seleccionado", "variant": ""},
        {"label": "Campos comparados", "value": len(columnas_comparacion), "note": ", ".join(columnas_comparacion[:3]), "variant": "blue"},
        {"label": "Umbral", "value": f"{umbral}%", "note": "Condición de selección", "variant": "teal"},
        {"label": "Pares estimados", "value": len(df) * (len(df) - 1) // 2, "note": "n(n−1)/2", "variant": "gold"},
    ], columns=4)

    if st.button("Guardar configuración y continuar al análisis", use_container_width=True, key="save_config"):
        st.session_state["df"] = df.copy()
        st.session_state["columna_id"] = columna_id
        st.session_state["columnas_comparacion"] = columnas_comparacion
        st.session_state["umbral"] = umbral
        st.session_state["resultado"] = None
        st.session_state["result_view"] = "Resumen"
        change_page("Análisis")
        st.rerun()


# ==========================================================
# 13. PÁGINA ANÁLISIS
# ==========================================================

def render_result_nav():
    labels = ["Resumen", "Grupos", "Pares", "Desglose", "Descargas"]
    cols = st.columns(len(labels), gap="small")

    for col, label in zip(cols, labels):
        with col:
            if st.button(label, use_container_width=True, key=view_key(label)):
                change_view(label)
                st.rerun()


def page_analisis():
    st.title("Análisis y reportes")

    if "df" not in st.session_state:
        ui("""
        <div class="empty-box">
            <div class="empty-title">No hay inventario configurado</div>
            <div class="empty-text">
                Para ejecutar el análisis primero debes subir un archivo CSV,
                seleccionar la columna identificadora, escoger las columnas de comparación
                y guardar la configuración.
            </div>
        </div>
        """)

        if st.button("Ir a configuración", use_container_width=True, key="go_config_empty"):
            change_page("Configuración")
            st.rerun()

        return

    df = st.session_state["df"]
    columna_id = st.session_state["columna_id"]
    columnas_comparacion = st.session_state["columnas_comparacion"]
    umbral = st.session_state["umbral"]

    ui("""
    <div class="info-box">
        Ejecuta el análisis para identificar pares relacionados, grupos de revisión
        y reportes descargables. El inventario original no se modifica.
    </div>
    """)

    render_kpis([
        {"label": "Registros cargados", "value": len(df), "note": "Elementos del conjunto", "variant": ""},
        {"label": "Umbral", "value": f"{umbral}%", "note": "Criterio de selección", "variant": "blue"},
        {"label": "Columnas comparadas", "value": len(columnas_comparacion), "note": "Proyección aplicada", "variant": "teal"},
        {"label": "Pares posibles", "value": len(df) * (len(df) - 1) // 2, "note": "Comparación por pares", "variant": "gold"},
    ], columns=4)

    ui(f"""
    <div class="card-tight">
        <div class="label">Configuración activa</div>
        <div class="card-text">
            <strong>Columna identificadora:</strong> {escape(str(columna_id))}<br>
            <strong>Columnas comparadas:</strong> {escape(", ".join(columnas_comparacion))}
        </div>
    </div>
    """)

    if st.button("Ejecutar análisis", use_container_width=True, key="run_analysis"):
        with st.spinner("Analizando registros y formando grupos de revisión..."):
            st.session_state["resultado"] = analizar_inventario(
                df=df,
                columna_id=columna_id,
                columnas_comparacion=columnas_comparacion,
                umbral=umbral
            )
            st.session_state["result_view"] = "Resumen"

    resultado = st.session_state.get("resultado")

    if resultado is None:
        ui("""
        <div class="empty-box">
            <div class="empty-title">Análisis pendiente</div>
            <div class="empty-text">
                Presiona el botón “Ejecutar análisis” para generar los pares relacionados,
                grupos de revisión y reportes descargables.
            </div>
        </div>
        """)
        return

    resumen = resultado["resumen"]
    tabla_pares = resultado["tabla_pares"]
    tabla_pares_interna = resultado["tabla_pares_interna"]
    tabla_grupos = resultado["tabla_grupos"]
    reporte_completo = resultado["reporte_completo"]
    detalles_por_par = resultado["detalles_por_par"]
    grupos_validos = resultado["grupos_validos"]
    df_trabajo = resultado["df_trabajo"]

    st.markdown("## Resultados generados")

    render_kpis([
        {"label": "Registros analizados", "value": resumen["registros"], "note": "Total revisado", "variant": ""},
        {"label": "Pares comparados", "value": resumen["pares_comparados"], "note": "Producto cartesiano reducido", "variant": "blue"},
        {"label": "Pares seleccionados", "value": resumen["pares_detectados"], "note": "Superan el umbral", "variant": "teal"},
        {"label": "Grupos detectados", "value": resumen["grupos_detectados"], "note": "Revisión recomendada", "variant": "gold"},
    ], columns=4)

    render_result_nav()

    view = st.session_state["result_view"]

    if view == "Resumen":
        ui("""
        <div class="card">
            <div class="label">Vista general</div>
            <div class="card-title">Resumen del análisis</div>
            <div class="card-text">
                Esta sección muestra los grupos detectados y una vista previa de los pares
                que superaron el umbral de similitud.
            </div>
        </div>
        """)

        st.markdown('<div class="table-title">Grupos de revisión detectados</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="table-help">Cada fila representa un conjunto de registros que podrían corresponder al mismo producto.</div>',
            unsafe_allow_html=True
        )

        if tabla_grupos.empty:
            st.info("No se formaron grupos de revisión con el umbral actual.")
        else:
            tabla_resumen = tabla_grupos[
                [
                    "Grupo",
                    "Cantidad",
                    "IDs relacionados",
                    "Similitud promedio del grupo (%)",
                    "Acción sugerida"
                ]
            ]
            st.dataframe(
                tabla_resumen,
                use_container_width=True,
                hide_index=True,
                height=altura_tabla(tabla_resumen, maximo=360)
            )

        ui('<div class="divider-blue"></div>')

        st.markdown('<div class="table-title">Vista previa de pares relacionados</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="table-help">Estos son algunos pares que cumplen el criterio de selección por similitud.</div>',
            unsafe_allow_html=True
        )

        if tabla_pares.empty:
            st.info("No se detectaron pares relacionados.")
        else:
            vista_pares = tabla_pares.head(12)
            st.dataframe(
                vista_pares,
                use_container_width=True,
                hide_index=True,
                height=altura_tabla(vista_pares, maximo=360)
            )

    elif view == "Grupos":
        ui("""
        <div class="card">
            <div class="label">Resultado principal</div>
            <div class="card-title">Grupos de revisión</div>
            <div class="card-text">
                Aquí se muestran todos los grupos de posibles coincidencias. La acción sugerida
                siempre es revisar antes de unificar registros.
            </div>
        </div>
        """)

        if tabla_grupos.empty:
            st.info("No se formaron grupos de revisión.")
        else:
            st.dataframe(
                tabla_grupos,
                use_container_width=True,
                hide_index=True,
                height=altura_tabla(tabla_grupos, maximo=430)
            )

    elif view == "Pares":
        ui("""
        <div class="card">
            <div class="label">Detalle del análisis</div>
            <div class="card-title">Pares relacionados</div>
            <div class="card-text">
                Esta tabla contiene los pares de registros que superaron el umbral de similitud.
                Cada par forma parte de la relación de posible duplicidad.
            </div>
        </div>
        """)

        if tabla_pares.empty:
            st.warning("No se detectaron pares con el umbral seleccionado.")
        else:
            st.dataframe(
                tabla_pares,
                use_container_width=True,
                hide_index=True,
                height=altura_tabla(tabla_pares, maximo=500)
            )

    elif view == "Desglose":
        ui("""
        <div class="card">
            <div class="label">Auditoría por grupo</div>
            <div class="card-title">Desglose de similitud</div>
            <div class="card-text">
                Selecciona un grupo para revisar sus registros, los pares directos detectados
                y la comparación campo por campo.
            </div>
        </div>
        """)

        if tabla_grupos.empty:
            st.info("No hay grupos para desglosar.")
        else:
            opciones_grupo = [
                f"G-{i + 1} — {len(grupo)} registros"
                for i, grupo in enumerate(grupos_validos)
            ]

            seleccion_grupo = st.selectbox(
                "Selecciona un grupo de revisión",
                opciones_grupo
            )

            numero_grupo = int(seleccion_grupo.split(" — ")[0].replace("G-", ""))
            grupo = grupos_validos[numero_grupo - 1]
            nombre_grupo = f"G-{numero_grupo}"

            ui(f"""
            <div class="card-tight">
                <div class="label">Grupo seleccionado</div>
                <div class="card-title">{nombre_grupo}</div>
                <div class="card-text">
                    Este grupo contiene {len(grupo)} registros relacionados.
                </div>
            </div>
            """)

            st.markdown('<div class="table-title">Registros del grupo</div>', unsafe_allow_html=True)

            columnas_vista = [columna_id] + [
                columna for columna in columnas_comparacion
                if columna != columna_id
            ]

            columnas_vista = [
                columna for columna in columnas_vista
                if columna in df_trabajo.columns
            ]

            tabla_registros_grupo = df_trabajo.loc[grupo, columnas_vista]

            st.dataframe(
                tabla_registros_grupo,
                use_container_width=True,
                hide_index=True,
                height=altura_tabla(tabla_registros_grupo, maximo=260)
            )

            ui('<div class="divider-blue"></div>')

            st.markdown('<div class="table-title">Pares directos detectados</div>', unsafe_allow_html=True)

            pares_grupo = tabla_pares_interna[
                tabla_pares_interna["Grupo"] == nombre_grupo
            ]

            if pares_grupo.empty:
                st.info("No hay pares directos registrados para este grupo.")
            else:
                pares_visibles = pares_grupo[
                    [
                        "ID A",
                        "Registro A",
                        "ID B",
                        "Registro B",
                        "Similitud promedio (%)",
                        "Confianza",
                        "Motivo principal"
                    ]
                ]

                st.dataframe(
                    pares_visibles,
                    use_container_width=True,
                    hide_index=True,
                    height=altura_tabla(pares_visibles, maximo=300)
                )

                ui('<div class="divider-blue"></div>')

                opciones = []

                for _, fila in pares_grupo.iterrows():
                    etiqueta = (
                        f"{fila['ID A']} ↔ {fila['ID B']} "
                        f"({fila['Similitud promedio (%)']}%)"
                    )
                    opciones.append({
                        "etiqueta": etiqueta,
                        "i": int(fila["_i"]),
                        "j": int(fila["_j"])
                    })

                seleccion = st.selectbox(
                    "Selecciona un par para ver la comparación campo por campo",
                    [opcion["etiqueta"] for opcion in opciones]
                )

                opcion = next(
                    item for item in opciones
                    if item["etiqueta"] == seleccion
                )

                detalle = detalles_por_par[(opcion["i"], opcion["j"])]

                st.markdown('<div class="table-title">Comparación campo por campo</div>', unsafe_allow_html=True)

                st.dataframe(
                    detalle,
                    use_container_width=True,
                    hide_index=True,
                    height=altura_tabla(detalle, maximo=300)
                )

    elif view == "Descargas":
        ui("""
        <div class="card">
            <div class="label">Exportación</div>
            <div class="card-title">Reportes descargables</div>
            <div class="card-text">
                Descarga los resultados para revisarlos fuera de la aplicación.
                Ningún archivo modifica el inventario original.
            </div>
        </div>
        """)

        d1, d2, d3 = st.columns(3, gap="large")

        with d1:
            st.download_button(
                label="Reporte completo",
                data=reporte_completo.to_csv(index=False).encode("utf-8-sig"),
                file_name="stockmatch_reporte_completo.csv",
                mime="text/csv",
                use_container_width=True
            )

        with d2:
            if not tabla_pares.empty:
                st.download_button(
                    label="Pares relacionados",
                    data=tabla_pares.to_csv(index=False).encode("utf-8-sig"),
                    file_name="stockmatch_pares_relacionados.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No hay pares para descargar.")

        with d3:
            if not tabla_grupos.empty:
                st.download_button(
                    label="Grupos de revisión",
                    data=tabla_grupos.to_csv(index=False).encode("utf-8-sig"),
                    file_name="stockmatch_grupos_revision.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No hay grupos para descargar.")


# ==========================================================
# 14. EJECUCIÓN
# ==========================================================

render_topbar()

if st.session_state["page"] == "Inicio":
    page_inicio()
elif st.session_state["page"] == "Configuración":
    page_configuracion()
else:
    page_analisis()
