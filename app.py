# ==========================================================
# STOCKMATCH
# Auditoría de inventarios no estructurados
# Matemáticas Discretas - Álgebra Relacional
# ==========================================================

import re
import unicodedata
from difflib import SequenceMatcher
from itertools import combinations

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

st.set_page_config(
    page_title="StockMatch | Auditoría de Inventarios",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# ESTADO DE LA APP
# ==========================================================

if "page" not in st.session_state:
    st.session_state["page"] = "Inicio"

if "result_view" not in st.session_state:
    st.session_state["result_view"] = "Resumen"

if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

if "scroll_top" not in st.session_state:
    st.session_state["scroll_top"] = False


# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>
:root {
    --navy: #020B1F;
    --navy2: #061A33;
    --blue: #123E73;
    --blue2: #1E5C99;
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
    background: linear-gradient(180deg, #F8FBFF 0%, #EFF5FB 100%);
    color: var(--text);
}

.block-container {
    max-width: 1240px;
    padding-top: 2.6rem;
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
    font-size: 2.35rem !important;
    font-weight: 850 !important;
    letter-spacing: -0.04em !important;
    margin-bottom: 0.7rem !important;
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

.app-header {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 28px rgba(6, 26, 51, 0.07);
}

.brand-row {
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand-mark {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--navy), var(--blue));
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-weight: 900;
    font-size: 15px;
}

.brand-title {
    font-size: 1.35rem;
    font-weight: 900;
    color: var(--navy2);
    line-height: 1.1;
}

.brand-subtitle {
    color: var(--muted);
    font-size: 0.86rem;
    margin-top: 3px;
}

.hero {
    background:
        radial-gradient(circle at 83% 18%, rgba(31, 92, 153, 0.95) 0%, rgba(6, 26, 51, 0.92) 36%, rgba(2, 11, 31, 1) 100%);
    color: white;
    border-radius: 28px;
    padding: 48px 52px;
    margin: 22px 0 26px;
    box-shadow: 0 22px 52px rgba(2, 11, 31, 0.24);
}

.hero-grid {
    display: grid;
    grid-template-columns: 1.35fr 0.85fr;
    gap: 38px;
    align-items: center;
}

.hero-pill {
    display: inline-block;
    padding: 8px 15px;
    border-radius: 999px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.20);
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

.info-box {
    background: #EAF2FF;
    border: 1px solid #C7D9F0;
    border-left: 6px solid var(--blue);
    border-radius: 18px;
    padding: 16px 18px;
    margin: 10px 0 22px;
    color: #1E293B;
    line-height: 1.65;
}

.card-title-small {
    color: var(--muted);
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    font-weight: 900;
    margin-bottom: 8px;
}

.card-heading {
    color: var(--navy2);
    font-size: 1.28rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    margin-bottom: 8px;
}

.card-text {
    color: #334155;
    font-size: 0.98rem;
    line-height: 1.68;
}

.kpi-wrapper {
    border-top: 6px solid var(--navy2);
    background: #FFFFFF;
    border-radius: 18px;
    border-left: 1px solid var(--border);
    border-right: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 18px 18px 16px;
    min-height: 120px;
    box-shadow: 0 8px 20px rgba(6, 26, 51, 0.06);
}

.kpi-wrapper.blue { border-top-color: var(--blue); }
.kpi-wrapper.teal { border-top-color: var(--teal); }
.kpi-wrapper.gold { border-top-color: var(--gold); }
.kpi-wrapper.red { border-top-color: var(--red); }

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
    font-size: 1.8rem;
    font-weight: 950;
    letter-spacing: -0.05em;
    line-height: 1.08;
    word-break: break-word;
}

.kpi-note {
    color: #64748B;
    font-size: 0.84rem;
    margin-top: 8px;
    line-height: 1.45;
}

.empty-box {
    background: #FFFFFF;
    border: 1px dashed #9DB8D8;
    border-radius: 22px;
    padding: 44px 32px;
    text-align: center;
    margin: 22px 0;
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
    max-width: 690px;
    margin: 0 auto;
}

.blue-line {
    height: 5px;
    background: linear-gradient(90deg, var(--navy2), var(--blue), transparent);
    border-radius: 999px;
    margin: 26px 0 24px;
}

.table-note {
    color: var(--muted);
    font-size: 0.93rem;
    line-height: 1.55;
    margin-bottom: 12px;
}

/* Segmentos / botones de navegación */
div[data-testid="stSegmentedControl"] {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 10px;
    box-shadow: 0 8px 20px rgba(6,26,51,0.055);
}

div[data-testid="stSegmentedControl"] button {
    min-height: 46px !important;
    border-radius: 13px !important;
    font-weight: 850 !important;
    color: var(--navy2) !important;
}

div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
    background: var(--navy2) !important;
    color: white !important;
}

div.stButton > button {
    background: var(--navy2);
    color: white;
    border-radius: 13px;
    border: none;
    font-weight: 850;
    height: 48px;
}

div.stButton > button:hover {
    background: var(--blue);
    color: white;
    border: none;
}

div.stDownloadButton > button {
    background: var(--navy2);
    color: white;
    border-radius: 13px;
    border: none;
    font-weight: 850;
    min-height: 50px;
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

@media (max-width: 980px) {
    .hero-grid {
        grid-template-columns: 1fr;
    }
    .hero-title {
        font-size: 2.55rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# UTILIDADES DE NAVEGACIÓN
# ==========================================================

def scroll_to_top_if_needed():
    if st.session_state.get("scroll_top"):
        components.html(
            """
            <script>
            window.parent.scrollTo({top: 0, behavior: "smooth"});
            </script>
            """,
            height=0
        )
        st.session_state["scroll_top"] = False


def change_page(page_name):
    st.session_state["page"] = page_name
    st.session_state["scroll_top"] = True
    st.rerun()


def change_result_view(view_name):
    st.session_state["result_view"] = view_name
    st.session_state["scroll_top"] = True
    st.rerun()


def segmented_control(label, options, current_value, key):
    if key not in st.session_state:
        st.session_state[key] = current_value

    if st.session_state[key] not in options:
        st.session_state[key] = current_value

    if hasattr(st, "segmented_control"):
        return st.segmented_control(
            label,
            options,
            default=st.session_state[key],
            key=key,
            label_visibility="collapsed"
        )

    return st.radio(
        label,
        options,
        index=options.index(st.session_state[key]),
        horizontal=True,
        key=key,
        label_visibility="collapsed"
    )


def render_header():
    st.markdown("""
<div class="app-header">
    <div class="brand-row">
        <div class="brand-mark">SM</div>
        <div>
            <div class="brand-title">StockMatch</div>
            <div class="brand-subtitle">Auditoría de inventarios no estructurados</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    selected = segmented_control(
        "Navegación",
        ["Inicio", "Configuración", "Análisis y reportes"],
        st.session_state["page"],
        "nav_control"
    )

    if selected != st.session_state["page"]:
        change_page(selected)


def kpi_card(label, value, note, color_class=""):
    st.markdown(
        f"""
<div class="kpi-wrapper {color_class}">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div>
    <div class="kpi-note">{note}</div>
</div>
""",
        unsafe_allow_html=True
    )


def render_kpis(items):
    cols = st.columns(len(items), gap="medium")
    for col, item in zip(cols, items):
        with col:
            kpi_card(
                label=item["label"],
                value=item["value"],
                note=item["note"],
                color_class=item.get("color", "")
            )


# ==========================================================
# LÓGICA DEL PROTOTIPO
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
                "Grupo": "",
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
# PÁGINAS
# ==========================================================

def page_inicio():
    st.markdown("""
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
""", unsafe_allow_html=True)

    render_kpis([
        {"label": "Datos originales", "value": "Sin cambios", "note": "La app no elimina registros.", "color": ""},
        {"label": "Control de decisión", "value": "Humano", "note": "El usuario valida cada grupo.", "color": "blue"},
        {"label": "Salida principal", "value": "CSV", "note": "Reportes listos para revisar.", "color": "teal"},
        {"label": "Modelo aplicado", "value": "π × σ", "note": "Álgebra relacional.", "color": "gold"},
    ])

    st.markdown("## Uso del sistema")
    st.write(
        "StockMatch permite cargar un inventario, configurar los campos de comparación, "
        "ejecutar el análisis y descargar reportes de posibles duplicados."
    )

    p1, p2, p3, p4 = st.columns(4, gap="medium")

    with p1:
        with st.container(border=True):
            st.markdown("### 1. Subir CSV")
            st.write("Carga un archivo con encabezados en la primera fila.")

    with p2:
        with st.container(border=True):
            st.markdown("### 2. Configurar")
            st.write("Selecciona identificador, campos y umbral.")

    with p3:
        with st.container(border=True):
            st.markdown("### 3. Analizar")
            st.write("El sistema compara pares y forma grupos.")

    with p4:
        with st.container(border=True):
            st.markdown("### 4. Descargar")
            st.write("Exporta reportes en formato CSV.")

    st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)

    if st.button("Comenzar configuración", use_container_width=True):
        st.session_state["page"] = "Configuración"
        st.session_state["nav_control"] = "Configuración"
        st.session_state["scroll_top"] = True
        st.rerun()


def page_configuracion():
    st.title("Configuración del análisis")

    st.markdown("""
<div class="info-box">
Carga un inventario en formato CSV y define qué columnas usará StockMatch para comparar los registros.
</div>
""", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        with st.container(border=True):
            st.markdown("### Carga del inventario")
            st.write("Sube un archivo CSV o utiliza datos de demostración para probar el sistema.")

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
            st.markdown("""
<div class="empty-box">
    <div class="empty-title">Inventario pendiente</div>
    <div class="empty-text">
        Sube un archivo CSV o activa el inventario de demostración para continuar.
    </div>
</div>
""", unsafe_allow_html=True)
        return

    if df.empty:
        st.error("El archivo cargado no contiene registros.")
        return

    columnas = list(df.columns)

    with col_right:
        with st.container(border=True):
            st.markdown("### Inventario detectado")
            st.write(f"El archivo contiene **{len(df)} registros** y **{len(columnas)} columnas**.")

            render_kpis([
                {"label": "Registros", "value": len(df), "note": "Filas cargadas", "color": ""},
                {"label": "Columnas", "value": len(columnas), "note": "Campos disponibles", "color": "blue"},
            ])

    with st.expander("Vista previa del inventario", expanded=False):
        st.dataframe(df.head(15), use_container_width=True, hide_index=True, height=340)

    st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)

    st.markdown("## Parámetros del modelo")
    st.write("Selecciona la columna identificadora, los campos que se compararán y el umbral mínimo de similitud.")

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
        {"label": "Columna ID", "value": columna_id, "note": "Identificador seleccionado", "color": ""},
        {"label": "Campos comparados", "value": len(columnas_comparacion), "note": ", ".join(columnas_comparacion[:3]), "color": "blue"},
        {"label": "Umbral", "value": f"{umbral}%", "note": "Condición de selección", "color": "teal"},
        {"label": "Pares estimados", "value": len(df) * (len(df) - 1) // 2, "note": "n(n−1)/2", "color": "gold"},
    ])

    if st.button("Guardar configuración y continuar al análisis", use_container_width=True):
        st.session_state["df"] = df.copy()
        st.session_state["columna_id"] = columna_id
        st.session_state["columnas_comparacion"] = columnas_comparacion
        st.session_state["umbral"] = umbral
        st.session_state["resultado"] = None
        st.session_state["page"] = "Análisis y reportes"
        st.session_state["nav_control"] = "Análisis y reportes"
        st.session_state["result_view"] = "Resumen"
        st.session_state["result_control"] = "Resumen"
        st.session_state["scroll_top"] = True
        st.rerun()


def page_analisis():
    st.title("Análisis y reportes")

    if "df" not in st.session_state:
        st.markdown("""
<div class="empty-box">
    <div class="empty-title">No hay inventario configurado</div>
    <div class="empty-text">
        Para ejecutar el análisis primero debes subir un archivo CSV, seleccionar la columna identificadora,
        escoger las columnas de comparación y guardar la configuración.
    </div>
</div>
""", unsafe_allow_html=True)

        if st.button("Ir a configuración", use_container_width=True):
            st.session_state["page"] = "Configuración"
            st.session_state["nav_control"] = "Configuración"
            st.session_state["scroll_top"] = True
            st.rerun()

        return

    df = st.session_state["df"]
    columna_id = st.session_state["columna_id"]
    columnas_comparacion = st.session_state["columnas_comparacion"]
    umbral = st.session_state["umbral"]

    st.markdown("""
<div class="info-box">
Ejecuta el análisis para identificar pares relacionados, grupos de revisión y reportes descargables.
El inventario original no se modifica.
</div>
""", unsafe_allow_html=True)

    render_kpis([
        {"label": "Registros cargados", "value": len(df), "note": "Elementos del conjunto", "color": ""},
        {"label": "Umbral", "value": f"{umbral}%", "note": "Criterio de selección", "color": "blue"},
        {"label": "Columnas comparadas", "value": len(columnas_comparacion), "note": "Proyección aplicada", "color": "teal"},
        {"label": "Pares posibles", "value": len(df) * (len(df) - 1) // 2, "note": "Comparación por pares", "color": "gold"},
    ])

    with st.container(border=True):
        st.markdown("### Configuración activa")
        st.write(f"**Columna identificadora:** {columna_id}")
        st.write(f"**Columnas comparadas:** {', '.join(columnas_comparacion)}")

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
        st.markdown("""
<div class="empty-box">
    <div class="empty-title">Análisis pendiente</div>
    <div class="empty-text">
        Presiona el botón “Ejecutar análisis” para generar los pares relacionados,
        grupos de revisión y reportes descargables.
    </div>
</div>
""", unsafe_allow_html=True)
        return

    resumen = resultado["resumen"]
    tabla_pares = resultado["tabla_pares"]
    tabla_pares_interna = resultado["tabla_pares_interna"]
    tabla_grupos = resultado["tabla_grupos"]
    reporte_completo = resultado["reporte_completo"]
    detalles_por_par = resultado["detalles_por_par"]
    grupos_validos = resultado["grupos_validos"]
    df_trabajo = resultado["df_trabajo"]

    st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)
    st.markdown("## Resultados generados")

    render_kpis([
        {"label": "Registros analizados", "value": resumen["registros"], "note": "Total revisado", "color": ""},
        {"label": "Pares comparados", "value": resumen["pares_comparados"], "note": "Producto cartesiano reducido", "color": "blue"},
        {"label": "Pares seleccionados", "value": resumen["pares_detectados"], "note": "Superan el umbral", "color": "teal"},
        {"label": "Grupos detectados", "value": resumen["grupos_detectados"], "note": "Revisión recomendada", "color": "gold"},
    ])

    selected_view = segmented_control(
        "Secciones de resultados",
        ["Resumen", "Pares relacionados", "Desglose", "Descargas"],
        st.session_state["result_view"],
        "result_control"
    )

    if selected_view != st.session_state["result_view"]:
        st.session_state["result_view"] = selected_view
        st.session_state["scroll_top"] = False
        st.rerun()

    view = st.session_state["result_view"]

    if view == "Resumen":
        st.markdown("### Tabla 1. Grupos de revisión")
        st.markdown(
            '<div class="table-note">Muestra los grupos formados por registros relacionados. Cada grupo debe revisarse antes de unificar información.</div>',
            unsafe_allow_html=True
        )

        if tabla_grupos.empty:
            st.info("No se formaron grupos de revisión con el umbral actual.")
        else:
            st.dataframe(tabla_grupos, use_container_width=True, hide_index=True, height=430)

        st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)

        st.markdown("### Tabla 2. Primeros pares relacionados")
        st.markdown(
            '<div class="table-note">Muestra una vista rápida de los pares que superaron el umbral de similitud.</div>',
            unsafe_allow_html=True
        )

        if tabla_pares.empty:
            st.info("No se detectaron pares relacionados.")
        else:
            st.dataframe(tabla_pares.head(15), use_container_width=True, hide_index=True, height=430)

    elif view == "Pares relacionados":
        st.markdown("### Pares que cumplen el criterio de selección")
        st.markdown(
            '<div class="table-note">Cada fila representa dos registros que alcanzaron o superaron el umbral configurado.</div>',
            unsafe_allow_html=True
        )

        if tabla_pares.empty:
            st.warning("No se detectaron pares con el umbral seleccionado.")
        else:
            st.dataframe(tabla_pares, use_container_width=True, hide_index=True, height=620)

    elif view == "Desglose":
        st.markdown("### Desglose por grupo")
        st.markdown(
            '<div class="table-note">Selecciona un grupo para revisar sus registros, pares directos y comparación campo por campo.</div>',
            unsafe_allow_html=True
        )

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

            with st.container(border=True):
                st.markdown(f"### Grupo seleccionado: {nombre_grupo}")
                st.write(f"Este grupo contiene **{len(grupo)} registros relacionados**.")

            st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)

            st.markdown("### Registros del grupo")

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
                height=260
            )

            st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)

            st.markdown("### Pares directos detectados")

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
                    height=290
                )

                st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)

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

                st.markdown("### Comparación campo por campo")
                st.dataframe(
                    detalle,
                    use_container_width=True,
                    hide_index=True,
                    height=300
                )

    elif view == "Descargas":
        st.markdown("### Reportes descargables")
        st.write(
            "Descarga los resultados para revisarlos fuera de la aplicación. "
            "Ningún archivo modifica el inventario original."
        )

        d1, d2, d3 = st.columns(3, gap="large")

        with d1:
            with st.container(border=True):
                st.markdown("#### Reporte completo")
                st.write("Incluye todos los registros con grupo sugerido, similitud y acción recomendada.")
                st.download_button(
                    label="Descargar CSV",
                    data=reporte_completo.to_csv(index=False).encode("utf-8-sig"),
                    file_name="stockmatch_reporte_completo.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with d2:
            with st.container(border=True):
                st.markdown("#### Pares relacionados")
                st.write("Incluye los pares que superaron el umbral de similitud.")
                if not tabla_pares.empty:
                    st.download_button(
                        label="Descargar CSV",
                        data=tabla_pares.to_csv(index=False).encode("utf-8-sig"),
                        file_name="stockmatch_pares_relacionados.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("No hay pares para descargar.")

        with d3:
            with st.container(border=True):
                st.markdown("#### Grupos de revisión")
                st.write("Incluye los grupos formados por transitividad.")
                if not tabla_grupos.empty:
                    st.download_button(
                        label="Descargar CSV",
                        data=tabla_grupos.to_csv(index=False).encode("utf-8-sig"),
                        file_name="stockmatch_grupos_revision.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("No hay grupos para descargar.")


# ==========================================================
# EJECUCIÓN
# ==========================================================

render_header()
scroll_to_top_if_needed()

if st.session_state["page"] == "Inicio":
    page_inicio()
elif st.session_state["page"] == "Configuración":
    page_configuracion()
else:
    page_analisis()
