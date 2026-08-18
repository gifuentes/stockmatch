# ==========================================================
# STOCKMATCH
# Prototipo para identificar y agrupar posibles registros
# duplicados en inventarios no estructurados.
#
# Materia: Matemáticas Discretas
# Tema: Álgebra Relacional aplicada a la identificación y
# agrupación de registros duplicados.
#
# La app está organizada como una página web:
# 1. Inicio
# 2. Configuración
# 3. Análisis y reportes
# ==========================================================

import re
import unicodedata
from difflib import SequenceMatcher
from itertools import combinations

import pandas as pd
import streamlit as st


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
# 2. ESTILOS VISUALES
# ==========================================================

st.markdown(
    """
    <style>
    :root {
        --navy: #020B1F;
        --navy2: #061A33;
        --navy3: #0A2A52;
        --blue: #123E73;
        --blueSoft: #EAF2FF;
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
        background-color: var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", Arial, sans-serif;
        color: var(--text);
    }

    h1, h2, h3 {
        color: var(--navy2);
        letter-spacing: -0.035em;
    }

    h1 {
        font-size: 2.6rem !important;
        font-weight: 850 !important;
    }

    h2 {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
    }

    h3 {
        font-size: 1.25rem !important;
        font-weight: 760 !important;
    }

    section[data-testid="stSidebar"] {
        display: none !important;
    }

    .topbar {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 18px 22px;
        margin-bottom: 22px;
        box-shadow: 0 8px 22px rgba(6, 26, 51, 0.06);
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-mark {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--navy), var(--blue));
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-weight: 900;
        font-size: 15px;
        letter-spacing: -0.04em;
    }

    .brand-name {
        font-size: 1.25rem;
        font-weight: 850;
        color: var(--navy2);
        line-height: 1.1;
    }

    .brand-sub {
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 2px;
    }

    .hero {
        background: radial-gradient(circle at 85% 18%, #1B4D89 0%, #061A33 42%, #020B1F 100%);
        color: white;
        border-radius: 26px;
        padding: 46px 48px;
        margin-bottom: 24px;
        box-shadow: 0 20px 48px rgba(2, 11, 31, 0.25);
        overflow: hidden;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.45fr 0.85fr;
        gap: 34px;
        align-items: center;
    }

    .hero-pill {
        display: inline-block;
        padding: 7px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.20);
        color: #D8E9FF;
        font-size: 0.78rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 3.45rem;
        font-weight: 920;
        line-height: 1.02;
        letter-spacing: -0.055em;
        margin-bottom: 14px;
    }

    .hero-text {
        font-size: 1.04rem;
        line-height: 1.7;
        color: #DDEBFF;
        max-width: 780px;
    }

    .hero-actions {
        margin-top: 22px;
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }

    .hero-card {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 22px;
        padding: 24px;
        backdrop-filter: blur(8px);
    }

    .hero-card-title {
        color: #FFFFFF;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 16px;
    }

    .flow-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 10px;
        color: #EAF2FF;
        font-weight: 700;
        font-size: 0.92rem;
    }

    .flow-symbol {
        color: #93C5FD;
        font-weight: 900;
    }

    .card {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 26px 28px;
        margin-bottom: 22px;
        box-shadow: 0 10px 26px rgba(6, 26, 51, 0.07);
    }

    .card-compact {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 8px 18px rgba(6, 26, 51, 0.055);
    }

    .label {
        color: var(--muted);
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        font-weight: 850;
        margin-bottom: 6px;
    }

    .card-title {
        color: var(--navy2);
        font-size: 1.45rem;
        font-weight: 850;
        letter-spacing: -0.04em;
        margin-bottom: 8px;
    }

    .card-text {
        color: #334155;
        font-size: 0.98rem;
        line-height: 1.65;
    }

    .step-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }

    .step-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px;
        min-height: 160px;
        box-shadow: 0 8px 18px rgba(6, 26, 51, 0.055);
    }

    .step-num {
        width: 34px;
        height: 34px;
        border-radius: 11px;
        background: var(--navy2);
        color: #FFFFFF;
        font-weight: 900;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 14px;
    }

    .step-title {
        color: var(--navy2);
        font-size: 1.05rem;
        font-weight: 850;
        margin-bottom: 8px;
    }

    .step-text {
        color: var(--muted);
        line-height: 1.6;
        font-size: 0.92rem;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 22px;
    }

    .kpi {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(6, 26, 51, 0.065);
        position: relative;
        overflow: hidden;
    }

    .kpi:before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        height: 5px;
        width: 100%;
        background: var(--navy2);
    }

    .kpi.blue:before { background: var(--blue); }
    .kpi.teal:before { background: var(--teal); }
    .kpi.gold:before { background: var(--gold); }
    .kpi.red:before { background: var(--red); }

    .kpi-label {
        color: var(--muted);
        font-size: 0.80rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 10px;
    }

    .kpi-value {
        color: var(--navy2);
        font-size: 2.05rem;
        font-weight: 900;
        letter-spacing: -0.05em;
        line-height: 1;
    }

    .kpi-note {
        color: #64748B;
        font-size: 0.84rem;
        margin-top: 8px;
    }

    .empty-state {
        background: #FFFFFF;
        border: 1px dashed #AFC1DA;
        border-radius: 22px;
        padding: 42px;
        text-align: center;
        margin-top: 20px;
    }

    .empty-title {
        font-size: 1.6rem;
        font-weight: 850;
        color: var(--navy2);
        margin-bottom: 8px;
    }

    .empty-text {
        color: var(--muted);
        line-height: 1.65;
        max-width: 650px;
        margin: 0 auto;
    }

    .message {
        background: #EAF2FF;
        border: 1px solid #C9DAF2;
        border-left: 6px solid var(--blue);
        border-radius: 16px;
        padding: 16px 18px;
        color: #1E293B;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    .success-box {
        background: #ECFDF5;
        border: 1px solid #BBF7D0;
        border-left: 6px solid var(--teal);
        border-radius: 16px;
        padding: 16px 18px;
        color: #064E3B;
        line-height: 1.6;
        margin-bottom: 20px;
        font-weight: 650;
    }

    .section-switch {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 14px;
        margin: 18px 0 22px;
        box-shadow: 0 8px 18px rgba(6, 26, 51, 0.055);
    }

    div.stButton > button {
        background: var(--navy2);
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: 850;
        height: 48px;
        letter-spacing: -0.01em;
    }

    div.stButton > button:hover {
        background: var(--blue);
        color: white;
        border: none;
    }

    div.stDownloadButton > button {
        background: var(--navy2);
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: 850;
        min-height: 48px;
        white-space: normal;
    }

    div.stDownloadButton > button:hover {
        background: var(--blue);
        color: white;
        border: none;
    }

    div[data-testid="stFileUploader"] {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 14px;
    }

    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 14px;
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

    div[data-baseweb="select"] > div {
        border-radius: 12px;
    }

    @media (max-width: 980px) {
        .hero-grid,
        .step-grid,
        .kpi-grid {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 2.4rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 3. FUNCIONES DE ESTADO Y NAVEGACIÓN
# ==========================================================

if "page" not in st.session_state:
    st.session_state["page"] = "Inicio"

if "section_result" not in st.session_state:
    st.session_state["section_result"] = "Resumen"

if "resultado" not in st.session_state:
    st.session_state["resultado"] = None


def go_to(page_name):
    st.session_state["page"] = page_name
    st.rerun()


def go_section(section_name):
    st.session_state["section_result"] = section_name
    st.rerun()


def render_topbar():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">
                <div class="brand-mark">SM</div>
                <div>
                    <div class="brand-name">StockMatch</div>
                    <div class="brand-sub">Auditoría de inventarios no estructurados</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    nav1, nav2, nav3, spacer = st.columns([1, 1.2, 1.5, 3.3])

    with nav1:
        if st.button("Inicio", use_container_width=True):
            go_to("Inicio")

    with nav2:
        if st.button("Configuración", use_container_width=True):
            go_to("Configuración")

    with nav3:
        if st.button("Análisis y reportes", use_container_width=True):
            go_to("Análisis y reportes")


def render_kpis(items):
    html = '<div class="kpi-grid">'
    for item in items:
        variant = item.get("variant", "")
        label = item["label"]
        value = item["value"]
        note = item.get("note", "")
        html += f"""
        <div class="kpi {variant}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ==========================================================
# 4. NORMALIZACIÓN Y SIMILITUD
# ==========================================================

def normalizar_texto(valor) -> str:
    """
    Normaliza texto para comparar registros.

    Ejemplo:
    'Coca-Cola 500 ML' pasa a 'coca cola 500 ml'.

    No modifica el archivo original; solo crea una versión temporal
    para comparar.
    """
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
    """
    Calcula similitud textual entre dos valores.

    SequenceMatcher devuelve un valor entre 0 y 1.
    Se multiplica por 100 para mostrarlo como porcentaje.
    """
    texto_a = normalizar_texto(valor_a)
    texto_b = normalizar_texto(valor_b)

    if not texto_a and not texto_b:
        return 100.0

    if not texto_a or not texto_b:
        return 0.0

    return round(SequenceMatcher(None, texto_a, texto_b).ratio() * 100, 2)


def clasificar_confianza(similitud):
    if similitud >= 95:
        return "Alta"
    if similitud >= 88:
        return "Media"
    return "Revisión manual"


def comparar_dos_registros(fila_a, fila_b, columnas_comparacion):
    """
    Compara dos registros usando las columnas seleccionadas.

    Matemáticamente, evalúa si dos elementos del conjunto inventario
    pertenecen a la relación de posible duplicidad.
    """
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
# 5. AGRUPACIÓN POR TRANSITIVIDAD
# ==========================================================

class UnionFind:
    """
    Estructura de conjuntos disjuntos.

    Sirve para agrupar elementos relacionados directa o indirectamente.
    Esto representa la transitividad:
    si A se relaciona con B, y B con C, entonces A, B y C quedan en
    el mismo grupo de revisión.
    """

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
# 6. MOTOR PRINCIPAL
# ==========================================================

def analizar_inventario(df, columna_id, columnas_comparacion, umbral):
    """
    Etapas del análisis:

    1. Conjunto:
       El inventario completo se considera un conjunto de registros.

    2. Proyección:
       Se usan solo las columnas elegidas por el usuario.

    3. Producto cartesiano:
       Se comparan pares únicos de registros con combinations().

    4. Selección:
       Se conservan pares cuya similitud supera el umbral.

    5. Transitividad:
       Los pares relacionados se agrupan con UnionFind.

    6. Reporte:
       Se generan tablas y CSV para revisión humana.
    """
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

    if not tabla_pares_interna.empty:
        tabla_pares = tabla_pares_interna[
            [
                "Grupo",
                "ID A",
                "Registro A",
                "ID B",
                "Registro B",
                "Similitud promedio (%)",
                "Confianza",
                "Motivo principal"
            ]
        ].copy()
    else:
        tabla_pares = pd.DataFrame(
            columns=[
                "Grupo",
                "ID A",
                "Registro A",
                "ID B",
                "Registro B",
                "Similitud promedio (%)",
                "Confianza",
                "Motivo principal"
            ]
        )

    filas_grupos = []

    for numero, grupo in enumerate(grupos_validos, start=1):
        ids = [str(df_trabajo.loc[indice, columna_id]) for indice in grupo]
        registros = [str(df_trabajo.loc[indice, columnas_comparacion[0]]) for indice in grupo]

        sims_grupo = []

        for par in pares_internos:
            if par["_i"] in grupo and par["_j"] in grupo:
                sims_grupo.append(par["Similitud promedio (%)"])

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
# 7. CSV Y DATOS DE DEMOSTRACIÓN
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
# 8. PÁGINA DE INICIO
# ==========================================================

def page_inicio():
    st.markdown(
        """
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
                <div class="hero-card">
                    <div class="hero-card-title">Flujo del análisis</div>
                    <div class="flow-item"><span>Cargar inventario</span><span class="flow-symbol">CSV</span></div>
                    <div class="flow-item"><span>Seleccionar columnas</span><span class="flow-symbol">π</span></div>
                    <div class="flow-item"><span>Comparar registros</span><span class="flow-symbol">×</span></div>
                    <div class="flow-item"><span>Filtrar coincidencias</span><span class="flow-symbol">σ</span></div>
                    <div class="flow-item"><span>Descargar reportes</span><span class="flow-symbol">CSV</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_kpis([
        {"label": "Datos originales", "value": "Sin cambios", "note": "La app no elimina registros.", "variant": ""},
        {"label": "Control de decisión", "value": "Humano", "note": "El usuario valida cada grupo.", "variant": "blue"},
        {"label": "Salida principal", "value": "CSV", "note": "Reportes listos para revisar.", "variant": "teal"},
        {"label": "Modelo aplicado", "value": "π × σ", "note": "Álgebra relacional.", "variant": "gold"},
    ])

    st.markdown(
        """
        <div class="card">
            <div class="label">Uso del sistema</div>
            <div class="card-title">Proceso en cuatro pasos</div>
            <div class="card-text">
                StockMatch está diseñado para que cualquier usuario pueda cargar un inventario,
                elegir los campos que desea comparar y obtener reportes de posibles duplicados.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="step-grid">
            <div class="step-card">
                <div class="step-num">1</div>
                <div class="step-title">Subir CSV</div>
                <div class="step-text">Carga un archivo con encabezados en la primera fila.</div>
            </div>
            <div class="step-card">
                <div class="step-num">2</div>
                <div class="step-title">Configurar</div>
                <div class="step-text">Selecciona el identificador, las columnas y el umbral.</div>
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
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Comenzar configuración", use_container_width=True):
        go_to("Configuración")


# ==========================================================
# 9. PÁGINA DE CONFIGURACIÓN
# ==========================================================

def page_configuracion():
    st.title("Configuración del análisis")
    st.markdown(
        """
        <div class="message">
            Carga un inventario en formato CSV y define qué columnas usará StockMatch
            para comparar los registros.
        </div>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns([1.05, 0.95])

    with left:
        st.markdown(
            """
            <div class="card-compact">
                <div class="label">Paso 1</div>
                <div class="card-title">Carga del inventario</div>
                <div class="card-text">
                    Puedes subir un archivo CSV o utilizar datos de demostración para probar el sistema.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        usar_ejemplo = st.checkbox("Usar inventario de demostración", value=False)

        archivo = None

        if not usar_ejemplo:
            archivo = st.file_uploader("Subir archivo CSV", type=["csv"])

        if usar_ejemplo:
            df = inventario_ejemplo()
        elif archivo is not None:
            df = leer_csv(archivo)
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="empty-title">Inventario pendiente</div>
                    <div class="empty-text">
                        Sube un archivo CSV o activa el inventario de demostración para continuar.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            return

    if df.empty:
        st.error("El archivo cargado no contiene registros.")
        return

    columnas = list(df.columns)

    with right:
        st.markdown(
            f"""
            <div class="card-compact">
                <div class="label">Archivo cargado</div>
                <div class="card-title">Inventario detectado</div>
                <div class="card-text">
                    El archivo contiene <strong>{len(df)}</strong> registros y
                    <strong>{len(columnas)}</strong> columnas.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        render_kpis([
            {"label": "Registros", "value": len(df), "note": "Filas cargadas", "variant": ""},
            {"label": "Columnas", "value": len(columnas), "note": "Campos disponibles", "variant": "blue"},
            {"label": "Archivo", "value": "CSV", "note": "Formato aceptado", "variant": "teal"},
            {"label": "Estado", "value": "Listo", "note": "Pendiente de configurar", "variant": "gold"},
        ])

    with st.expander("Vista previa del inventario", expanded=False):
        st.dataframe(df.head(15), use_container_width=True, hide_index=True, height=360)

    st.markdown(
        """
        <div class="card">
            <div class="label">Paso 2</div>
            <div class="card-title">Parámetros del modelo</div>
            <div class="card-text">
                Selecciona la columna identificadora, las columnas que se compararán
                y el umbral mínimo de similitud.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns([1, 1])

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
    ])

    if st.button("Guardar configuración y continuar al análisis", use_container_width=True):
        st.session_state["df"] = df.copy()
        st.session_state["columna_id"] = columna_id
        st.session_state["columnas_comparacion"] = columnas_comparacion
        st.session_state["umbral"] = umbral
        st.session_state["resultado"] = None
        st.session_state["section_result"] = "Resumen"
        go_to("Análisis y reportes")


# ==========================================================
# 10. PÁGINA DE ANÁLISIS
# ==========================================================

def page_analisis():
    st.title("Análisis y reportes")

    if "df" not in st.session_state:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-title">No hay inventario configurado</div>
                <div class="empty-text">
                    Para ejecutar el análisis primero debes subir un archivo CSV,
                    seleccionar la columna identificadora, escoger las columnas de comparación
                    y guardar la configuración.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Ir a configuración", use_container_width=True):
            go_to("Configuración")

        return

    df = st.session_state["df"]
    columna_id = st.session_state["columna_id"]
    columnas_comparacion = st.session_state["columnas_comparacion"]
    umbral = st.session_state["umbral"]

    st.markdown(
        """
        <div class="message">
            Ejecuta el análisis para identificar pares relacionados, grupos de revisión
            y reportes descargables. El inventario original no se modifica.
        </div>
        """,
        unsafe_allow_html=True
    )

    render_kpis([
        {"label": "Registros cargados", "value": len(df), "note": "Elementos del conjunto", "variant": ""},
        {"label": "Umbral", "value": f"{umbral}%", "note": "Criterio de selección", "variant": "blue"},
        {"label": "Columnas comparadas", "value": len(columnas_comparacion), "note": "Proyección aplicada", "variant": "teal"},
        {"label": "Pares posibles", "value": len(df) * (len(df) - 1) // 2, "note": "Comparación por pares", "variant": "gold"},
    ])

    st.markdown(
        f"""
        <div class="card-compact">
            <div class="label">Configuración activa</div>
            <div class="card-text">
                <strong>Columna identificadora:</strong> {columna_id}<br>
                <strong>Columnas comparadas:</strong> {", ".join(columnas_comparacion)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Ejecutar análisis", use_container_width=True):
        with st.spinner("Analizando registros y formando grupos de revisión..."):
            st.session_state["resultado"] = analizar_inventario(
                df=df,
                columna_id=columna_id,
                columnas_comparacion=columnas_comparacion,
                umbral=umbral
            )

    resultado = st.session_state.get("resultado")

    if resultado is None:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-title">Análisis pendiente</div>
                <div class="empty-text">
                    Presiona el botón “Ejecutar análisis” para generar los pares relacionados,
                    grupos de revisión y reportes descargables.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
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
    ])

    st.markdown('<div class="section-switch">', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)

    with b1:
        if st.button("Resumen", use_container_width=True):
            go_section("Resumen")

    with b2:
        if st.button("Pares relacionados", use_container_width=True):
            go_section("Pares relacionados")

    with b3:
        if st.button("Desglose", use_container_width=True):
            go_section("Desglose")

    with b4:
        if st.button("Descargas", use_container_width=True):
            go_section("Descargas")

    st.markdown('</div>', unsafe_allow_html=True)

    section = st.session_state["section_result"]

    if section == "Resumen":
        left, right = st.columns([1, 1])

        with left:
            st.markdown(
                """
                <div class="card">
                    <div class="label">Resultado principal</div>
                    <div class="card-title">Grupos de revisión</div>
                    <div class="card-text">
                        Cada grupo reúne registros que podrían representar el mismo producto.
                        La acción sugerida siempre es revisar antes de unificar.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if tabla_grupos.empty:
                st.info("No se formaron grupos de revisión con el umbral actual.")
            else:
                st.dataframe(tabla_grupos, use_container_width=True, hide_index=True, height=360)

        with right:
            st.markdown(
                """
                <div class="card">
                    <div class="label">Criterio aplicado</div>
                    <div class="card-title">Control humano</div>
                    <div class="card-text">
                        El sistema no elimina registros automáticamente. Solo señala posibles
                        coincidencias para que el responsable valide la información.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if tabla_pares.empty:
                st.info("No se detectaron pares relacionados.")
            else:
                st.dataframe(tabla_pares.head(10), use_container_width=True, hide_index=True, height=360)

    elif section == "Pares relacionados":
        st.markdown("### Pares que cumplen el criterio de selección")

        if tabla_pares.empty:
            st.warning("No se detectaron pares con el umbral seleccionado.")
        else:
            st.dataframe(tabla_pares, use_container_width=True, hide_index=True, height=560)

    elif section == "Desglose":
        st.markdown("### Desglose por grupo")

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

            st.markdown(
                f"""
                <div class="card-compact">
                    <div class="label">Grupo seleccionado</div>
                    <div class="card-title">{nombre_grupo}</div>
                    <div class="card-text">
                        Este grupo contiene {len(grupo)} registros relacionados.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("#### Registros del grupo")

            columnas_vista = [columna_id] + [
                columna for columna in columnas_comparacion
                if columna != columna_id
            ]

            columnas_vista = [
                columna for columna in columnas_vista
                if columna in df_trabajo.columns
            ]

            st.dataframe(
                df_trabajo.loc[grupo, columnas_vista],
                use_container_width=True,
                hide_index=True,
                height=220
            )

            pares_grupo = tabla_pares_interna[
                tabla_pares_interna["Grupo"] == nombre_grupo
            ]

            st.markdown("#### Pares directos detectados")

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
                    height=260
                )

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

                st.markdown("#### Comparación campo por campo")
                st.dataframe(
                    detalle,
                    use_container_width=True,
                    hide_index=True,
                    height=260
                )

    elif section == "Descargas":
        st.markdown("### Reportes descargables")
        st.write(
            "Descarga los resultados para revisarlos fuera de la aplicación. "
            "Ningún archivo modifica el inventario original."
        )

        d1, d2, d3 = st.columns(3)

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
# 11. EJECUCIÓN
# ==========================================================

render_topbar()

if st.session_state["page"] == "Inicio":
    page_inicio()
elif st.session_state["page"] == "Configuración":
    page_configuracion()
else:
    page_analisis()
