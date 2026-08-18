# ==========================================================
# STOCKMATCH
# Prototipo para identificar y agrupar posibles registros
# duplicados en inventarios no estructurados.
#
# Materia: Matemáticas Discretas
# Tema: Álgebra Relacional aplicada a la identificación y
# agrupación de registros duplicados.
#
# La parte visual usa Streamlit + estilos CSS.
# La parte lógica está desarrollada en Python.
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
    layout="wide"
)


# ==========================================================
# 2. DISEÑO VISUAL
# ==========================================================
# Este bloque solo mejora la apariencia de la página.
# No afecta el modelo matemático ni el análisis de datos.

st.markdown(
    """
    <style>
    :root {
        --navy: #020B1F;
        --navy-2: #061A33;
        --navy-3: #0A2240;
        --blue: #123E73;
        --blue-soft: #EAF2FF;
        --gray-bg: #F3F6FA;
        --gray-text: #64748B;
        --border: #D6E0EF;
        --white: #FFFFFF;
        --green: #0F766E;
    }

    .stApp {
        background: linear-gradient(180deg, #F3F6FA 0%, #EDF2F8 100%);
        color: #172033;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    html, body, [class*="css"] {
        font-family: "Segoe UI", "Inter", Arial, sans-serif;
    }

    h1, h2, h3 {
        color: var(--navy);
        font-weight: 800;
    }

    .hero {
        background: radial-gradient(circle at 85% 20%, #1B4D89 0%, #061A33 38%, #020B1F 100%);
        border-radius: 22px;
        padding: 42px 46px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 18px 42px rgba(2, 11, 31, 0.25);
        position: relative;
        overflow: hidden;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.5fr 0.8fr;
        gap: 28px;
        align-items: center;
    }

    .brand-pill {
        display: inline-block;
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.22);
        padding: 7px 13px;
        border-radius: 999px;
        color: #CFE3FF;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: .12em;
        font-weight: 750;
        margin-bottom: 16px;
    }

    .hero-title {
        font-size: 48px;
        font-weight: 900;
        letter-spacing: -1.2px;
        line-height: 1.05;
        margin-bottom: 12px;
    }

    .hero-subtitle {
        font-size: 21px;
        line-height: 1.45;
        color: #E6F0FF;
        max-width: 760px;
        margin-bottom: 18px;
    }

    .hero-text {
        color: #BFD5F2;
        font-size: 15px;
        line-height: 1.7;
        max-width: 820px;
    }

    .math-panel {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 18px;
        padding: 24px 22px;
        text-align: center;
        backdrop-filter: blur(8px);
    }

    .math-symbols {
        font-size: 42px;
        font-weight: 900;
        color: #FFFFFF;
        letter-spacing: 6px;
        margin-bottom: 8px;
    }

    .math-caption {
        color: #CFE3FF;
        font-size: 13px;
        line-height: 1.6;
    }

    .notice {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-left: 6px solid var(--navy-3);
        border-radius: 14px;
        padding: 17px 19px;
        margin-bottom: 22px;
        box-shadow: 0 8px 22px rgba(10, 34, 64, 0.07);
        line-height: 1.65;
        color: #1E293B;
    }

    .section-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 24px 26px;
        margin-bottom: 22px;
        box-shadow: 0 10px 26px rgba(10, 34, 64, 0.07);
    }

    .section-label {
        color: var(--gray-text);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: .12em;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .section-title {
        color: var(--navy);
        font-size: 24px;
        font-weight: 850;
        margin-bottom: 10px;
    }

    .section-desc {
        color: #475569;
        line-height: 1.65;
        font-size: 15px;
    }

    .process-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        margin-top: 18px;
    }

    .process-step {
        background: #F8FBFF;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px;
        min-height: 132px;
    }

    .step-number {
        background: var(--navy-3);
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .step-title {
        font-weight: 800;
        color: var(--navy);
        margin-bottom: 6px;
        font-size: 14px;
    }

    .step-text {
        color: #64748B;
        font-size: 13px;
        line-height: 1.55;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 18px 18px;
        box-shadow: 0 8px 18px rgba(10, 34, 64, 0.07);
    }

    div[data-testid="stMetric"] label {
        color: #64748B !important;
        font-weight: 750;
    }

    div[data-testid="stMetric"] div {
        color: var(--navy) !important;
        font-weight: 850;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020B1F 0%, #061A33 100%);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #F8FAFC !important;
    }

    [data-testid="stSidebar"] .stCaptionContainer {
        color: #CFE3FF !important;
    }

    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #020B1F, #0A2240);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 800;
        height: 46px;
        letter-spacing: .02em;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #0A2240, #123E73);
        color: white;
        border: none;
    }

    div.stDownloadButton > button {
        background: #123E73;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 800;
        height: 45px;
    }

    div.stDownloadButton > button:hover {
        background: #020B1F;
        color: white;
        border: none;
    }

    .footer-note {
        text-align: center;
        color: #64748B;
        font-size: 13px;
        margin-top: 18px;
    }

    @media (max-width: 900px) {
        .hero-grid {
            grid-template-columns: 1fr;
        }

        .process-grid {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 38px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 3. NORMALIZACIÓN DE TEXTO
# ==========================================================

def normalizar_texto(valor) -> str:
    """
    Normaliza un texto para compararlo de manera justa.

    Ejemplo:
    "Coca-Cola 500 ML" se transforma en "coca cola 500 ml".

    Esta etapa elimina diferencias superficiales:
    mayúsculas, tildes, signos y espacios repetidos.
    """

    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()

    # Quitar tildes y signos diacríticos.
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caracter for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    # Dejar solo letras, números y espacios.
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)

    # Quitar espacios repetidos.
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def similitud_textual(texto_a, texto_b) -> float:
    """
    Calcula la similitud entre dos textos.

    Se usa SequenceMatcher, una función de Python que compara dos
    secuencias y devuelve un valor entre 0 y 1. Aquí se multiplica
    por 100 para expresarlo como porcentaje.
    """

    texto_a = normalizar_texto(texto_a)
    texto_b = normalizar_texto(texto_b)

    if not texto_a and not texto_b:
        return 100.0

    if not texto_a or not texto_b:
        return 0.0

    return round(SequenceMatcher(None, texto_a, texto_b).ratio() * 100, 2)


# ==========================================================
# 4. COMPARACIÓN ENTRE DOS REGISTROS
# ==========================================================

def comparar_dos_registros(fila_a, fila_b, columnas_comparacion):
    """
    Compara dos registros usando las columnas seleccionadas.

    Relación con Matemáticas Discretas:
    Cada registro es un elemento del conjunto inventario.
    Si dos registros superan el umbral de similitud, forman parte
    de la relación de posible duplicidad.
    """

    resultados = []

    for columna in columnas_comparacion:
        valor_a = fila_a[columna]
        valor_b = fila_b[columna]
        similitud = similitud_textual(valor_a, valor_b)
        resultados.append((columna, similitud))

    similitud_promedio = round(
        sum(sim for _, sim in resultados) / len(resultados),
        2
    )

    resultados_ordenados = sorted(
        resultados,
        key=lambda x: x[1],
        reverse=True
    )

    mejores_campos = resultados_ordenados[:2]

    motivo = "; ".join(
        f"{columna}: {sim:.0f}%"
        for columna, sim in mejores_campos
    )

    return similitud_promedio, motivo


# ==========================================================
# 5. AGRUPACIÓN POR TRANSITIVIDAD
# ==========================================================

class UnionFind:
    """
    Estructura de conjuntos disjuntos.

    Sirve para agrupar registros relacionados directa o indirectamente.

    Ejemplo:
    Si A se relaciona con B, y B se relaciona con C,
    entonces A, B y C quedan dentro del mismo grupo.

    Esto representa la transitividad dentro del prototipo.
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
# 6. MOTOR PRINCIPAL DEL ANÁLISIS
# ==========================================================

def analizar_inventario(df, columna_id, columnas_comparacion, umbral):
    """
    Ejecuta el análisis del inventario.

    Etapas matemáticas:

    1. Conjunto:
       El inventario completo se considera un conjunto de registros.

    2. Proyección:
       Se seleccionan únicamente las columnas relevantes.

    3. Producto cartesiano:
       Se comparan pares de registros. Computacionalmente se usa
       combinations(), que evita pares repetidos.

    4. Selección:
       Se conservan solo los pares cuya similitud es mayor o igual
       al umbral elegido.

    5. Transitividad:
       Los registros relacionados se agrupan mediante Union-Find.

    6. Reporte:
       Se genera una salida para revisión humana.
    """

    indices = list(df.index)
    estructura_grupos = UnionFind(indices)

    pares_detectados = []

    for i, j in combinations(indices, 2):

        similitud, motivo = comparar_dos_registros(
            df.loc[i],
            df.loc[j],
            columnas_comparacion
        )

        if similitud >= umbral:
            estructura_grupos.unir(i, j)

            pares_detectados.append({
                "ID A": df.loc[i, columna_id],
                "Registro A": df.loc[i, columnas_comparacion[0]],
                "ID B": df.loc[j, columna_id],
                "Registro B": df.loc[j, columnas_comparacion[0]],
                "Similitud (%)": similitud,
                "Motivo principal": motivo
            })

    grupos = estructura_grupos.obtener_grupos()
    grupos_validos = [grupo for grupo in grupos if len(grupo) > 1]

    reporte_grupos = []

    for numero_grupo, grupo in enumerate(grupos_validos, start=1):

        ids = [
            str(df.loc[indice, columna_id])
            for indice in grupo
        ]

        registros = [
            str(df.loc[indice, columnas_comparacion[0]])
            for indice in grupo
        ]

        reporte_grupos.append({
            "Grupo": f"G-{numero_grupo}",
            "Cantidad de registros": len(grupo),
            "IDs relacionados": ", ".join(ids),
            "Registros relacionados": " | ".join(registros),
            "Acción sugerida": "Revisar antes de unificar"
        })

    resumen = {
        "registros": len(df),
        "pares_comparados": len(df) * (len(df) - 1) // 2,
        "pares_detectados": len(pares_detectados),
        "grupos_detectados": len(reporte_grupos)
    }

    tabla_pares = pd.DataFrame(pares_detectados)
    tabla_grupos = pd.DataFrame(reporte_grupos)

    return resumen, tabla_pares, tabla_grupos


# ==========================================================
# 7. LECTURA DE ARCHIVOS
# ==========================================================

def leer_csv(archivo):
    """
    Lee un archivo CSV cargado por el usuario.

    Primero intenta leerlo como UTF-8. Si falla, intenta Latin-1.
    Esto ayuda cuando el archivo fue exportado desde Excel.
    """

    try:
        archivo.seek(0)
        return pd.read_csv(archivo, encoding="utf-8-sig")
    except UnicodeDecodeError:
        archivo.seek(0)
        return pd.read_csv(archivo, encoding="latin-1")


def inventario_ejemplo():
    """
    Inventario de prueba para demostrar el funcionamiento del prototipo.
    La aplicación también acepta cualquier CSV cargado por el usuario.
    """

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


# ==========================================================
# 8. TABLAS DE APOYO PARA LA DEFENSA
# ==========================================================

def tabla_matematica():
    """
    Tabla para explicar cómo cada concepto de Matemáticas Discretas
    se aplica dentro del prototipo.
    """

    return pd.DataFrame({
        "Concepto": [
            "Conjunto",
            "Elemento",
            "Proyección (π)",
            "Producto cartesiano (×)",
            "Selección (σ)",
            "Relación binaria",
            "Transitividad",
            "Clase de equivalencia"
        ],
        "Aplicación en StockMatch": [
            "El inventario completo cargado desde el archivo CSV.",
            "Cada fila o registro del inventario.",
            "Selección de columnas relevantes para comparar.",
            "Comparación entre pares de registros del inventario.",
            "Filtro de pares que superan el umbral de similitud.",
            "Par de registros considerado como posible coincidencia.",
            "Agrupación de registros conectados directa o indirectamente.",
            "Grupo de registros que podrían representar el mismo producto."
        ]
    })


def tabla_guia_defensa():
    """
    Preguntas probables y respuestas breves para apoyar la defensa.
    """

    return pd.DataFrame({
        "Pregunta posible": [
            "¿Dónde aparece el álgebra relacional?",
            "¿Qué representa el producto cartesiano?",
            "¿Qué hace el umbral?",
            "¿Por qué no se eliminan registros automáticamente?",
            "¿Dónde se observa la transitividad?"
        ],
        "Respuesta sugerida": [
            "En la proyección de columnas, comparación de pares y selección por condición.",
            "La comparación de pares de registros del inventario.",
            "Define qué pares tienen similitud suficiente para entrar a la relación.",
            "Porque pueden existir falsos positivos y la decisión debe ser humana.",
            "En la agrupación: si A se relaciona con B y B con C, quedan en el mismo grupo."
        ]
    })


def sugerir_columna_id(columnas):
    """
    Sugiere una columna identificadora si encuentra nombres comunes.
    """

    nombres_normalizados = {
        columna: normalizar_texto(columna)
        for columna in columnas
    }

    palabras_clave = ["codigo", "id", "sku", "cod"]

    for i, columna in enumerate(columnas):
        if nombres_normalizados[columna] in palabras_clave:
            return i

    return 0


def sugerir_columnas_comparacion(columnas, columna_id):
    """
    Sugiere columnas útiles para comparar productos.
    """

    palabras_clave = [
        "nombre",
        "producto",
        "marca",
        "categoria",
        "descripcion",
        "detalle"
    ]

    sugeridas = []

    for columna in columnas:
        if columna == columna_id:
            continue

        nombre_normalizado = normalizar_texto(columna)

        if nombre_normalizado in palabras_clave:
            sugeridas.append(columna)

    if sugeridas:
        return sugeridas

    return [col for col in columnas if col != columna_id][:3]


# ==========================================================
# 9. ENCABEZADO PRINCIPAL
# ==========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-grid">
            <div>
                <div class="brand-pill">Auditoría de inventarios · Matemáticas Discretas</div>
                <div class="hero-title">StockMatch</div>
                <div class="hero-subtitle">
                    Detección y agrupación de posibles registros duplicados
                    en inventarios no estructurados.
                </div>
                <div class="hero-text">
                    Prototipo basado en álgebra relacional, comparación de similitud
                    y propiedades de relaciones. La herramienta identifica coincidencias
                    probables, forma grupos de revisión y conserva siempre el control humano
                    sobre la decisión final.
                </div>
            </div>
            <div class="math-panel">
                <div class="math-symbols">π × σ</div>
                <div class="math-caption">
                    Proyección de atributos<br>
                    Comparación de pares<br>
                    Selección por umbral
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="notice">
        <strong>Principio de seguridad y responsabilidad:</strong>
        StockMatch no elimina ni modifica el archivo original. El sistema genera
        reportes de posibles coincidencias para que el responsable del inventario
        revise cada caso antes de tomar una decisión.
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 10. MAPA DEL PROCESO
# ==========================================================

st.markdown(
    """
    <div class="section-card">
        <div class="section-label">Flujo del prototipo</div>
        <div class="section-title">Proceso de análisis</div>
        <div class="section-desc">
            La aplicación sigue un flujo simple y defendible: carga de datos,
            selección de columnas, comparación de registros, filtro por umbral
            y agrupación de posibles coincidencias.
        </div>

        <div class="process-grid">
            <div class="process-step">
                <div class="step-number">1</div>
                <div class="step-title">Carga CSV</div>
                <div class="step-text">El inventario se carga como conjunto de registros.</div>
            </div>
            <div class="process-step">
                <div class="step-number">2</div>
                <div class="step-title">Proyección</div>
                <div class="step-text">Se eligen las columnas relevantes para comparar.</div>
            </div>
            <div class="process-step">
                <div class="step-number">3</div>
                <div class="step-title">Comparación</div>
                <div class="step-text">Se comparan pares únicos de registros.</div>
            </div>
            <div class="process-step">
                <div class="step-number">4</div>
                <div class="step-title">Selección</div>
                <div class="step-text">Se conservan pares que superan el umbral.</div>
            </div>
            <div class="process-step">
                <div class="step-number">5</div>
                <div class="step-title">Agrupación</div>
                <div class="step-text">Los registros relacionados forman grupos de revisión.</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 11. BARRA LATERAL
# ==========================================================

st.sidebar.title("Configuración")
st.sidebar.write("Carga el inventario y ajusta el modelo de comparación.")

usar_ejemplo = st.sidebar.checkbox(
    "Usar inventario de ejemplo",
    value=False
)

archivo = None

if not usar_ejemplo:
    archivo = st.sidebar.file_uploader(
        "Subir archivo CSV",
        type=["csv"]
    )


# ==========================================================
# 12. CARGA DE DATOS
# ==========================================================

if usar_ejemplo:
    df = inventario_ejemplo()
elif archivo is not None:
    df = leer_csv(archivo)
else:
    st.warning(
        "Para iniciar, sube un archivo CSV desde la barra lateral "
        "o activa el inventario de ejemplo."
    )

    with st.expander("Ver relación del prototipo con Matemáticas Discretas"):
        st.dataframe(
            tabla_matematica(),
            use_container_width=True,
            hide_index=True
        )

    st.stop()


if df.empty:
    st.error("El archivo cargado no contiene registros.")
    st.stop()


columnas = list(df.columns)

st.success(
    f"Inventario cargado correctamente: {len(df)} registros "
    f"y {len(columnas)} columnas."
)


# ==========================================================
# 13. CONFIGURACIÓN DEL MODELO
# ==========================================================

st.sidebar.markdown("---")
st.sidebar.subheader("Modelo de comparación")

indice_id = sugerir_columna_id(columnas)

columna_id = st.sidebar.selectbox(
    "Columna identificadora",
    columnas,
    index=indice_id
)

columnas_disponibles = [
    columna for columna in columnas
    if columna != columna_id
]

columnas_sugeridas = sugerir_columnas_comparacion(
    columnas,
    columna_id
)

columnas_comparacion = st.sidebar.multiselect(
    "Columnas para comparar",
    columnas_disponibles,
    default=columnas_sugeridas
)

umbral = st.sidebar.slider(
    "Umbral mínimo de similitud (%)",
    min_value=50,
    max_value=100,
    value=82,
    step=1
)

st.sidebar.caption(
    "Un umbral alto exige mayor similitud. Un umbral bajo detecta más posibles coincidencias, pero puede generar falsos positivos."
)

if not columnas_comparacion:
    st.error("Selecciona al menos una columna para comparar.")
    st.stop()


# ==========================================================
# 14. PESTAÑAS PRINCIPALES
# ==========================================================

tab_inicio, tab_modelo, tab_defensa = st.tabs(
    [
        "Panel de análisis",
        "Modelo matemático",
        "Guía de defensa"
    ]
)


with tab_inicio:

    st.markdown(
        """
        <div class="section-card">
            <div class="section-label">Datos cargados</div>
            <div class="section-title">Resumen del inventario</div>
            <div class="section-desc">
                Antes de ejecutar el análisis, verifica que el archivo y las columnas
                seleccionadas correspondan al inventario que deseas revisar.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Registros cargados", len(df))

    with c2:
        st.metric("Columnas disponibles", len(columnas))

    with c3:
        st.metric("Umbral seleccionado", f"{umbral}%")

    with st.expander("Vista previa del inventario", expanded=False):
        st.dataframe(
            df.head(15),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("### Configuración seleccionada")

    conf1, conf2 = st.columns(2)

    with conf1:
        st.write("**Columna identificadora:**", columna_id)

    with conf2:
        st.write("**Columnas comparadas:**", ", ".join(columnas_comparacion))

    st.write(
        "Los pares comparados se calculan con la fórmula "
        "**n(n−1)/2**, porque se comparan pares únicos sin repetir el orden."
    )

    ejecutar = st.button("Ejecutar análisis", use_container_width=True)

    if ejecutar:

        resumen, tabla_pares, tabla_grupos = analizar_inventario(
            df=df,
            columna_id=columna_id,
            columnas_comparacion=columnas_comparacion,
            umbral=umbral
        )

        st.markdown("## Resultados del análisis")

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Registros analizados", resumen["registros"])

        with m2:
            st.metric("Pares comparados", resumen["pares_comparados"])

        with m3:
            st.metric("Pares seleccionados", resumen["pares_detectados"])

        with m4:
            st.metric("Grupos detectados", resumen["grupos_detectados"])

        if resumen["pares_comparados"] > 0:
            chart_data = pd.DataFrame({
                "Categoría": [
                    "Pares comparados",
                    "Pares seleccionados",
                    "Grupos detectados"
                ],
                "Cantidad": [
                    resumen["pares_comparados"],
                    resumen["pares_detectados"],
                    resumen["grupos_detectados"]
                ]
            }).set_index("Categoría")

            st.markdown("### Visualización ejecutiva del resultado")
            st.bar_chart(chart_data)

        resultado_tab1, resultado_tab2, resultado_tab3 = st.tabs(
            [
                "Pares relacionados",
                "Grupos de revisión",
                "Descargas"
            ]
        )

        with resultado_tab1:
            st.subheader("Pares que cumplen el criterio de selección")

            if tabla_pares.empty:
                st.warning(
                    "No se detectaron pares de registros con el umbral seleccionado."
                )
            else:
                st.dataframe(
                    tabla_pares,
                    use_container_width=True,
                    hide_index=True
                )

        with resultado_tab2:
            st.subheader("Grupos de posibles coincidencias")

            if tabla_grupos.empty:
                st.info("No se formaron grupos de revisión.")
            else:
                st.dataframe(
                    tabla_grupos,
                    use_container_width=True,
                    hide_index=True
                )

            st.info(
                "Estos grupos son sugerencias de revisión. No representan "
                "eliminación automática ni modificación del inventario original."
            )

        with resultado_tab3:
            st.subheader("Reportes descargables")

            if not tabla_pares.empty:
                st.download_button(
                    label="Descargar detalle de pares relacionados",
                    data=tabla_pares.to_csv(index=False).encode("utf-8-sig"),
                    file_name="stockmatch_pares_relacionados.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            if not tabla_grupos.empty:
                st.download_button(
                    label="Descargar reporte de grupos",
                    data=tabla_grupos.to_csv(index=False).encode("utf-8-sig"),
                    file_name="stockmatch_grupos_revision.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            if tabla_pares.empty and tabla_grupos.empty:
                st.write(
                    "No hay reportes disponibles porque no se encontraron "
                    "coincidencias con el umbral seleccionado."
                )

    else:
        st.info(
            "Cuando la configuración esté lista, presiona "
            "“Ejecutar análisis” para aplicar el modelo."
        )


with tab_modelo:

    st.markdown(
        """
        <div class="section-card">
            <div class="section-label">Fundamento académico</div>
            <div class="section-title">Aplicación de Matemáticas Discretas</div>
            <div class="section-desc">
                Esta sección resume cómo los conceptos del curso se traducen
                en operaciones dentro del prototipo.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        tabla_matematica(),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Formalización breve")

    st.latex(r"I = \{r_1, r_2, r_3, \ldots, r_n\}")

    st.write(
        "El inventario se modela como un conjunto de registros. "
        "Cada registro contiene atributos como nombre, marca, categoría "
        "o descripción."
    )

    st.latex(r"\pi_{atributos}(I)")

    st.write(
        "La proyección selecciona únicamente los atributos relevantes "
        "para comparar los registros."
    )

    st.latex(r"R = \{(r_i,r_j) \in I \times I : similitud(r_i,r_j) \geq \theta\}")

    st.write(
        "La relación de posible duplicidad se forma con los pares de registros "
        "cuya similitud supera el umbral θ."
    )

    st.latex(r"(r_i,r_j) \in R \land (r_j,r_k) \in R \Rightarrow r_i, r_j, r_k \text{ pertenecen al mismo grupo}")

    st.write(
        "La transitividad se utiliza para formar grupos de revisión cuando "
        "los registros están conectados directa o indirectamente."
    )


with tab_defensa:

    st.markdown(
        """
        <div class="section-card">
            <div class="section-label">Preparación oral</div>
            <div class="section-title">Preguntas probables de defensa</div>
            <div class="section-desc">
                Esta tabla sirve como apoyo para explicar el prototipo sin depender
                de una explicación línea por línea del código.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        tabla_guia_defensa(),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Explicación corta recomendada")

    st.write(
        "El inventario se representa como un conjunto de registros. "
        "Primero se aplica una proyección al seleccionar las columnas relevantes. "
        "Luego se comparan pares únicos de registros, lo que representa el producto "
        "cartesiano de forma optimizada. Después, mediante un umbral de similitud, "
        "se aplica una selección para conservar solo los pares que cumplen la condición. "
        "Finalmente, los pares relacionados se agrupan usando transitividad, formando "
        "grupos de posibles duplicados que deben ser revisados por una persona."
    )

    st.markdown("### Idea ética clave")

    st.write(
        "El prototipo no elimina registros automáticamente porque una coincidencia "
        "alta no garantiza que dos productos sean exactamente iguales. Por eso, "
        "StockMatch funciona como herramienta de auditoría y apoyo a la decisión, "
        "manteniendo la revisión humana como etapa final."
    )


st.markdown(
    """
    <div class="footer-note">
        StockMatch · Prototipo académico de Matemáticas Discretas · Auditoría de inventarios
    </div>
    """,
    unsafe_allow_html=True
)
