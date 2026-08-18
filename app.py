# ==========================================================
# STOCKMATCH
# Prototipo para identificar y agrupar posibles registros
# duplicados en inventarios no estructurados.
#
# Materia: Matemáticas Discretas
# Tema: Álgebra Relacional aplicada a la identificación y
# agrupación de registros duplicados.
#
# La aplicación está dividida en tres páginas:
# 1. Inicio
# 2. Configuración
# 3. Análisis y reportes
#
# El objetivo es que el prototipo sea claro, formal y fácil
# de defender oralmente.
# ==========================================================

import re
import unicodedata
from difflib import SequenceMatcher
from itertools import combinations

import pandas as pd
import streamlit as st


# ==========================================================
# 1. CONFIGURACIÓN GENERAL DE LA APP
# ==========================================================

st.set_page_config(
    page_title="StockMatch | Auditoría de Inventarios",
    page_icon="SM",
    layout="wide"
)


# ==========================================================
# 2. ESTILOS VISUALES GENERALES
# ==========================================================
# Este bloque solo cambia la apariencia.
# La lógica matemática y computacional está en las funciones de Python.

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F4F7FB;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    html, body, [class*="css"] {
        font-family: "Segoe UI", Arial, sans-serif;
        color: #0F172A;
    }

    h1 {
        color: #061A33;
        font-size: 2.7rem;
        font-weight: 850;
        letter-spacing: -0.04em;
    }

    h2 {
        color: #061A33;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    h3 {
        color: #061A33;
        font-weight: 750;
    }

    [data-testid="stSidebar"] {
        background-color: #020B1F;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #F8FAFC !important;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #D6E0EF;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(6, 26, 51, 0.06);
    }

    div[data-testid="stMetric"] label {
        color: #475569 !important;
        font-weight: 700;
    }

    div[data-testid="stMetric"] div {
        color: #061A33 !important;
        font-weight: 850;
    }

    div.stButton > button {
        background-color: #061A33;
        color: white;
        border-radius: 9px;
        border: none;
        font-weight: 750;
        height: 45px;
    }

    div.stButton > button:hover {
        background-color: #0A2A52;
        color: white;
        border: none;
    }

    div.stDownloadButton > button {
        background-color: #0A2A52;
        color: white;
        border-radius: 9px;
        border: none;
        font-weight: 750;
        height: 44px;
    }

    div.stDownloadButton > button:hover {
        background-color: #061A33;
        color: white;
        border: none;
    }

    .stDataFrame {
        border: 1px solid #D6E0EF;
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 3. FUNCIONES DE NORMALIZACIÓN Y SIMILITUD
# ==========================================================

def normalizar_texto(valor) -> str:
    """
    Normaliza un texto para poder compararlo mejor.

    Ejemplo:
    "Coca-Cola 500 ML" se transforma en "coca cola 500 ml".

    Esta etapa elimina diferencias superficiales como:
    - Mayúsculas y minúsculas.
    - Tildes.
    - Signos de puntuación.
    - Espacios repetidos.

    No modifica el archivo original. Solo se usa para comparar.
    """

    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()

    # Quitar tildes.
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caracter for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    # Dejar letras, números y espacios.
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)

    # Reducir espacios múltiples.
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def similitud_textual(valor_a, valor_b) -> float:
    """
    Calcula la similitud entre dos textos.

    Se usa SequenceMatcher, una herramienta de Python que compara
    dos secuencias de texto y devuelve un valor entre 0 y 1.

    En esta app se multiplica por 100 para mostrarlo como porcentaje.
    """

    texto_a = normalizar_texto(valor_a)
    texto_b = normalizar_texto(valor_b)

    if not texto_a and not texto_b:
        return 100.0

    if not texto_a or not texto_b:
        return 0.0

    return round(SequenceMatcher(None, texto_a, texto_b).ratio() * 100, 2)


def comparar_dos_registros(fila_a, fila_b, columnas_comparacion):
    """
    Compara dos registros del inventario.

    Relación con Matemáticas Discretas:
    cada registro es un elemento del conjunto inventario. Si dos
    registros alcanzan el umbral, pasan a formar parte de la relación
    de posible duplicidad.

    Retorna:
    - similitud promedio;
    - motivo principal;
    - detalle de similitud por campo.
    """

    detalle = []

    for columna in columnas_comparacion:
        valor_a = fila_a[columna]
        valor_b = fila_b[columna]

        similitud = similitud_textual(valor_a, valor_b)

        detalle.append({
            "Campo comparado": columna,
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
        f"{item['Campo comparado']}: {item['Similitud (%)']:.0f}%"
        for item in mejores
    )

    return similitud_promedio, motivo, pd.DataFrame(detalle)


# ==========================================================
# 4. ESTRUCTURA PARA AGRUPAR POR TRANSITIVIDAD
# ==========================================================

class UnionFind:
    """
    Estructura de conjuntos disjuntos.

    Se usa para formar grupos de registros relacionados directa o
    indirectamente.

    Interpretación matemática:
    si A se relaciona con B, y B se relaciona con C, entonces A, B
    y C deben quedar dentro del mismo grupo de revisión.

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
# 5. MOTOR PRINCIPAL DEL ANÁLISIS
# ==========================================================

def analizar_inventario(df, columna_id, columnas_comparacion, umbral):
    """
    Ejecuta el análisis del inventario.

    Etapas matemáticas:

    1. Conjunto:
       El inventario se toma como un conjunto de registros.

    2. Proyección:
       El usuario selecciona las columnas relevantes.

    3. Producto cartesiano:
       El programa compara pares de registros. Para evitar repeticiones,
       usa combinations(), es decir, compara (A, B), pero no repite (B, A).

    4. Selección:
       Se conservan solo los pares cuya similitud sea mayor o igual
       al umbral definido.

    5. Transitividad:
       Los registros relacionados se agrupan mediante UnionFind.

    6. Reporte:
       Se generan tablas para revisión humana.
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

    filas_grupos = []

    for numero, grupo in enumerate(grupos_validos, start=1):
        ids = [
            str(df_trabajo.loc[indice, columna_id])
            for indice in grupo
        ]

        registros = [
            str(df_trabajo.loc[indice, columnas_comparacion[0]])
            for indice in grupo
        ]

        filas_grupos.append({
            "Grupo": f"G-{numero}",
            "Cantidad de registros": len(grupo),
            "IDs relacionados": ", ".join(ids),
            "Registros relacionados": " | ".join(registros),
            "Acción sugerida": "Revisar antes de unificar"
        })

    tabla_pares_interna = pd.DataFrame(pares_internos)
    tabla_grupos = pd.DataFrame(filas_grupos)

    if not tabla_pares_interna.empty:
        tabla_pares = tabla_pares_interna[
            [
                "Grupo",
                "ID A",
                "Registro A",
                "ID B",
                "Registro B",
                "Similitud promedio (%)",
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
                "Motivo principal"
            ]
        )

    # Reporte completo: conserva todos los registros del archivo.
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
                coincidentes.append(
                    f"{par['ID B']} ({par['Similitud promedio (%)']}%)"
                )
            elif par["_j"] == indice:
                sims.append(par["Similitud promedio (%)"])
                coincidentes.append(
                    f"{par['ID A']} ({par['Similitud promedio (%)']}%)"
                )

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
        "indice_a_grupo": indice_a_grupo,
        "grupos_validos": grupos_validos,
        "df_trabajo": df_trabajo
    }


# ==========================================================
# 6. LECTURA DE CSV Y DATOS DE EJEMPLO
# ==========================================================

def leer_csv(archivo):
    """
    Lee un archivo CSV cargado por el usuario.

    Primero intenta leer en UTF-8. Si el archivo viene de Excel y
    presenta problemas de codificación, intenta leerlo como Latin-1.
    """

    try:
        archivo.seek(0)
        return pd.read_csv(archivo, encoding="utf-8-sig")
    except UnicodeDecodeError:
        archivo.seek(0)
        return pd.read_csv(archivo, encoding="latin-1")


def inventario_ejemplo():
    """
    Inventario de prueba para usar en la exposición.
    La app también recibe cualquier CSV cargado por el usuario.
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
# 7. TABLAS DE APOYO PARA DEFENSA
# ==========================================================

def tabla_matematica():
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
            "Comparación entre pares únicos de registros.",
            "Filtro de pares que superan el umbral de similitud.",
            "Par de registros considerado como posible coincidencia.",
            "Agrupación de registros relacionados directa o indirectamente.",
            "Grupo de registros que podrían representar el mismo producto."
        ]
    })


def tabla_guia_defensa():
    return pd.DataFrame({
        "Pregunta posible": [
            "¿Dónde se aplica el álgebra relacional?",
            "¿Qué representa el producto cartesiano?",
            "¿Qué significa el umbral?",
            "¿Por qué no se eliminan registros automáticamente?",
            "¿Dónde se observa la transitividad?"
        ],
        "Respuesta sugerida": [
            "En la proyección de columnas, comparación de pares y selección por condición.",
            "La comparación entre pares únicos de registros del inventario.",
            "Es la condición mínima de similitud para aceptar un par como posible duplicado.",
            "Porque una coincidencia alta puede ser un falso positivo y debe revisarse manualmente.",
            "En la formación de grupos: si A se relaciona con B y B con C, quedan en el mismo grupo."
        ]
    })


def sugerir_columna_id(columnas):
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

    return [columna for columna in columnas if columna != columna_id][:3]


# ==========================================================
# 8. NAVEGACIÓN
# ==========================================================

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "Inicio"

st.sidebar.title("StockMatch")
st.sidebar.caption("Auditoría de inventarios")

pagina = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Configuración", "Análisis y reportes"],
    key="pagina"
)


# ==========================================================
# 9. PÁGINA DE INICIO
# ==========================================================

def pagina_inicio():
    st.title("StockMatch")
    st.subheader("Auditoría de inventarios no estructurados")

    st.write(
        "Prototipo académico para identificar y agrupar posibles registros "
        "duplicados en inventarios, aplicando álgebra relacional y propiedades "
        "de relaciones."
    )

    col1, col2 = st.columns([1.45, 1])

    with col1:
        with st.container(border=True):
            st.markdown("### Enfoque del sistema")
            st.write(
                "StockMatch no modifica el inventario original. La aplicación "
                "analiza los registros, detecta posibles coincidencias y genera "
                "reportes para revisión humana."
            )

            st.markdown("**Operaciones principales del modelo:**")
            st.write("π Proyección de columnas")
            st.write("× Comparación de pares únicos")
            st.write("σ Selección por umbral de similitud")
            st.write("Transitividad para agrupar registros relacionados")

    with col2:
        with st.container(border=True):
            st.markdown("### Criterios de diseño")
            st.metric("Datos modificados", "0")
            st.metric("Control humano", "100%")
            st.metric("Salida principal", "Reporte CSV")

    st.divider()

    st.markdown("## Flujo de trabajo")

    paso1, paso2, paso3, paso4 = st.columns(4)

    with paso1:
        with st.container(border=True):
            st.markdown("#### 1. Carga")
            st.write("El usuario sube un archivo CSV de inventario.")

    with paso2:
        with st.container(border=True):
            st.markdown("#### 2. Proyección")
            st.write("Se seleccionan las columnas relevantes para comparar.")

    with paso3:
        with st.container(border=True):
            st.markdown("#### 3. Relación")
            st.write("Se comparan pares de registros y se aplica un umbral.")

    with paso4:
        with st.container(border=True):
            st.markdown("#### 4. Reporte")
            st.write("Se generan grupos de revisión y archivos descargables.")

    st.divider()

    with st.container(border=True):
        st.markdown("### Relación con Matemáticas Discretas")
        st.dataframe(
            tabla_matematica(),
            use_container_width=True,
            hide_index=True
        )

    if st.button("Ir a configuración", use_container_width=True):
        st.session_state["pagina"] = "Configuración"
        st.rerun()


# ==========================================================
# 10. PÁGINA DE CONFIGURACIÓN
# ==========================================================

def pagina_configuracion():
    st.title("Configuración del análisis")
    st.write(
        "En esta sección se carga el inventario y se definen los parámetros "
        "del modelo de comparación."
    )

    with st.container(border=True):
        st.markdown("### 1. Carga del archivo")

        usar_ejemplo = st.checkbox(
            "Usar inventario de ejemplo",
            value=False
        )

        archivo = None

        if not usar_ejemplo:
            archivo = st.file_uploader(
                "Subir archivo CSV",
                type=["csv"]
            )

        if usar_ejemplo:
            df = inventario_ejemplo()
        elif archivo is not None:
            df = leer_csv(archivo)
        else:
            st.info("Sube un archivo CSV o activa el inventario de ejemplo.")
            return

    if df.empty:
        st.error("El archivo cargado no contiene registros.")
        return

    columnas = list(df.columns)

    st.success(
        f"Inventario cargado correctamente: {len(df)} registros y "
        f"{len(columnas)} columnas."
    )

    with st.expander("Vista previa del inventario", expanded=False):
        st.dataframe(
            df.head(15),
            use_container_width=True,
            hide_index=True
        )

    with st.container(border=True):
        st.markdown("### 2. Parámetros del modelo")

        col_a, col_b = st.columns(2)

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

        columnas_disponibles = [
            columna for columna in columnas
            if columna != columna_id
        ]

        columnas_sugeridas = sugerir_columnas_comparacion(
            columnas,
            columna_id
        )

        columnas_comparacion = st.multiselect(
            "Columnas para comparar",
            columnas_disponibles,
            default=columnas_sugeridas
        )

        st.caption(
            "Mientras más alto sea el umbral, más estricta será la comparación. "
            "Un umbral bajo detecta más coincidencias, pero puede generar falsos positivos."
        )

    if not columnas_comparacion:
        st.warning("Selecciona al menos una columna para comparar.")
        return

    with st.container(border=True):
        st.markdown("### 3. Resumen de configuración")

        r1, r2, r3 = st.columns(3)

        with r1:
            st.metric("Registros", len(df))

        with r2:
            st.metric("Columnas comparadas", len(columnas_comparacion))

        with r3:
            st.metric("Umbral", f"{umbral}%")

        st.write("**Columna ID:**", columna_id)
        st.write("**Columnas usadas para la proyección:**", ", ".join(columnas_comparacion))

    if st.button("Guardar configuración y continuar", use_container_width=True):
        st.session_state["df"] = df.copy()
        st.session_state["columna_id"] = columna_id
        st.session_state["columnas_comparacion"] = columnas_comparacion
        st.session_state["umbral"] = umbral
        st.session_state["resultado"] = None
        st.session_state["pagina"] = "Análisis y reportes"
        st.rerun()


# ==========================================================
# 11. PÁGINA DE ANÁLISIS Y REPORTES
# ==========================================================

def pagina_analisis():
    st.title("Análisis y reportes")

    if "df" not in st.session_state:
        st.warning("Primero debes cargar un inventario y guardar la configuración.")
        if st.button("Ir a configuración", use_container_width=True):
            st.session_state["pagina"] = "Configuración"
            st.rerun()
        return

    df = st.session_state["df"]
    columna_id = st.session_state["columna_id"]
    columnas_comparacion = st.session_state["columnas_comparacion"]
    umbral = st.session_state["umbral"]

    with st.container(border=True):
        st.markdown("### Configuración activa")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Registros", len(df))

        with c2:
            st.metric("Umbral", f"{umbral}%")

        with c3:
            st.metric("Columnas comparadas", len(columnas_comparacion))

        st.write("**Columna identificadora:**", columna_id)
        st.write("**Columnas comparadas:**", ", ".join(columnas_comparacion))
        st.caption(
            "Los pares comparados se calculan con n(n−1)/2, porque se comparan pares únicos."
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
        st.info("Presiona “Ejecutar análisis” para generar los resultados.")
        return

    resumen = resultado["resumen"]
    tabla_pares = resultado["tabla_pares"]
    tabla_pares_interna = resultado["tabla_pares_interna"]
    tabla_grupos = resultado["tabla_grupos"]
    reporte_completo = resultado["reporte_completo"]
    detalles_por_par = resultado["detalles_por_par"]
    grupos_validos = resultado["grupos_validos"]
    df_trabajo = resultado["df_trabajo"]

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

    tab_pares, tab_grupos, tab_desglose, tab_descargas = st.tabs(
        [
            "Pares relacionados",
            "Grupos de revisión",
            "Desglose",
            "Descargas"
        ]
    )

    with tab_pares:
        st.subheader("Pares que cumplen el criterio de selección")

        if tabla_pares.empty:
            st.warning("No se detectaron pares con el umbral seleccionado.")
        else:
            st.dataframe(
                tabla_pares,
                use_container_width=True,
                hide_index=True
            )

    with tab_grupos:
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
            "Los grupos son sugerencias de revisión. El sistema no elimina "
            "ni modifica registros automáticamente."
        )

    with tab_desglose:
        st.subheader("Desglose de similitud por grupo")

        if tabla_grupos.empty:
            st.info("No hay grupos para desglosar.")
        else:
            for numero, grupo in enumerate(grupos_validos, start=1):
                nombre_grupo = f"G-{numero}"

                with st.expander(
                    f"{nombre_grupo} — {len(grupo)} registros relacionados",
                    expanded=False
                ):
                    columnas_vista = [columna_id] + [
                        columna for columna in columnas_comparacion
                        if columna != columna_id
                    ]

                    columnas_vista = [
                        columna for columna in columnas_vista
                        if columna in df_trabajo.columns
                    ]

                    st.markdown("**Registros del grupo**")
                    st.dataframe(
                        df_trabajo.loc[grupo, columnas_vista],
                        use_container_width=True,
                        hide_index=True
                    )

                    pares_grupo = tabla_pares_interna[
                        tabla_pares_interna["Grupo"] == nombre_grupo
                    ]

                    if pares_grupo.empty:
                        st.write("No hay pares directos registrados para este grupo.")
                    else:
                        st.markdown("**Pares directos detectados**")

                        pares_visibles = pares_grupo[
                            [
                                "ID A",
                                "Registro A",
                                "ID B",
                                "Registro B",
                                "Similitud promedio (%)",
                                "Motivo principal"
                            ]
                        ]

                        st.dataframe(
                            pares_visibles,
                            use_container_width=True,
                            hide_index=True
                        )

                        opciones = []

                        for _, fila in pares_grupo.iterrows():
                            etiqueta = (
                                f"{fila['ID A']} ↔ {fila['ID B']} "
                                f"({fila['Similitud promedio (%)']}%)"
                            )
                            opciones.append(
                                {
                                    "etiqueta": etiqueta,
                                    "i": int(fila["_i"]),
                                    "j": int(fila["_j"])
                                }
                            )

                        etiquetas = [opcion["etiqueta"] for opcion in opciones]

                        seleccion = st.selectbox(
                            "Selecciona un par para ver la comparación campo por campo",
                            etiquetas,
                            key=f"select_{nombre_grupo}"
                        )

                        opcion_seleccionada = next(
                            opcion for opcion in opciones
                            if opcion["etiqueta"] == seleccion
                        )

                        detalle = detalles_por_par[
                            (
                                opcion_seleccionada["i"],
                                opcion_seleccionada["j"]
                            )
                        ]

                        st.markdown("**Comparación campo por campo**")
                        st.dataframe(
                            detalle,
                            use_container_width=True,
                            hide_index=True
                        )

    with tab_descargas:
        st.subheader("Reportes descargables")

        st.write(
            "Estos archivos permiten revisar los resultados fuera de la aplicación. "
            "Ningún reporte modifica el inventario original."
        )

        st.download_button(
            label="Descargar reporte completo de auditoría",
            data=reporte_completo.to_csv(index=False).encode("utf-8-sig"),
            file_name="stockmatch_reporte_completo.csv",
            mime="text/csv",
            use_container_width=True
        )

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
                label="Descargar grupos de revisión",
                data=tabla_grupos.to_csv(index=False).encode("utf-8-sig"),
                file_name="stockmatch_grupos_revision.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.divider()

    with st.expander("Guía rápida para defensa oral"):
        st.dataframe(
            tabla_guia_defensa(),
            use_container_width=True,
            hide_index=True
        )


# ==========================================================
# 12. EJECUTAR PÁGINA SELECCIONADA
# ==========================================================

if pagina == "Inicio":
    pagina_inicio()
elif pagina == "Configuración":
    pagina_configuracion()
else:
    pagina_analisis()
