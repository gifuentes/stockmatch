# ==========================================================
# CLEARSTOCK
# Prototipo para identificar y agrupar posibles registros
# repetidos en inventarios no estructurados.
#
# Materia: Matemáticas Discretas
# Tema: Álgebra Relacional aplicada a la identificación y
# agrupación de registros duplicados.
#
# Este código está escrito de forma simple y comentada para
# que pueda explicarse en la defensa del proyecto.
# ==========================================================

import re
import unicodedata
from difflib import SequenceMatcher
from itertools import combinations

import pandas as pd
import streamlit as st


# ==========================================================
# 1. CONFIGURACIÓN GENERAL DE LA APLICACIÓN
# ==========================================================

st.set_page_config(
    page_title="ClearStock | Auditoría de Inventarios",
    page_icon="📦",
    layout="wide"
)

# Estilos mínimos para que el prototipo se vea más formal.
# No es la parte principal del proyecto; solo mejora la presentación.
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F4F7FB;
    }

    h1, h2, h3 {
        color: #0A2240;
    }

    [data-testid="stSidebar"] {
        background-color: #0A2240;
    }

    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #D6E0EF;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 10px rgba(10, 34, 64, 0.06);
    }

    div.stButton > button {
        background-color: #0A2240;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 700;
    }

    div.stDownloadButton > button {
        background-color: #123E73;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 2. NORMALIZACIÓN DE TEXTO
# ==========================================================

def normalizar_texto(valor) -> str:
    """
    Convierte un texto a una forma estándar para compararlo.

    Ejemplo:
    "Coca-Cola 500 ML"  ->  "coca cola 500 ml"

    Esta función elimina diferencias superficiales de escritura:
    mayúsculas, tildes, signos y espacios repetidos.

    Importante:
    No modifica el archivo original; solo crea una versión temporal
    del texto para poder comparar los registros.
    """

    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()

    # Quitar tildes: á -> a, é -> e, í -> i, etc.
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

    Se usa SequenceMatcher, una herramienta de Python que compara
    dos secuencias de texto y devuelve un valor entre 0 y 1.

    En este prototipo se multiplica por 100 para expresarlo como porcentaje.
    """

    texto_a = normalizar_texto(texto_a)
    texto_b = normalizar_texto(texto_b)

    if not texto_a and not texto_b:
        return 100.0

    if not texto_a or not texto_b:
        return 0.0

    return round(SequenceMatcher(None, texto_a, texto_b).ratio() * 100, 2)


# ==========================================================
# 3. COMPARACIÓN ENTRE REGISTROS
# ==========================================================

def comparar_dos_registros(fila_a, fila_b, columnas_comparacion):
    """
    Compara dos registros del inventario usando las columnas seleccionadas.

    Relación con Matemáticas Discretas:
    - Cada fila es un elemento del conjunto de registros.
    - Este procedimiento evalúa si dos elementos pueden pertenecer
      a la relación de posible duplicidad.

    La similitud final se calcula como el promedio de similitud
    entre los campos seleccionados.
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

    # Se toman los dos campos con mayor coincidencia para explicar el motivo.
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
# 4. AGRUPACIÓN POR TRANSITIVIDAD
# ==========================================================

class UnionFind:
    """
    Estructura para formar grupos de elementos relacionados.

    Relación con Matemáticas Discretas:
    Esta estructura permite reflejar la transitividad.

    Ejemplo:
    Si A se relaciona con B, y B se relaciona con C,
    entonces A, B y C quedan dentro del mismo grupo de revisión.

    Esto permite formar clases o grupos de posibles coincidencias.
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

    Etapas matemáticas aplicadas:

    1. Conjunto:
       El inventario completo se considera un conjunto de registros.

    2. Proyección:
       El usuario selecciona solo las columnas relevantes para comparar.

    3. Producto cartesiano:
       Se comparan pares de registros del inventario.
       Para evitar comparaciones repetidas, se usa combinations(),
       que compara pares únicos: (A, B), pero no repite (B, A).

    4. Selección:
       Solo se conservan los pares cuya similitud es mayor o igual
       al umbral definido por el usuario.

    5. Transitividad:
       Los pares relacionados se unen en grupos de posibles coincidencias.

    6. Reporte:
       Se genera una salida para revisión humana.
    """

    indices = list(df.index)
    estructura_grupos = UnionFind(indices)

    pares_detectados = []

    # Producto cartesiano reducido: compara pares únicos de registros.
    for i, j in combinations(indices, 2):

        similitud, motivo = comparar_dos_registros(
            df.loc[i],
            df.loc[j],
            columnas_comparacion
        )

        # Selección: se conserva el par si supera el umbral.
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

    # Obtener grupos formados por transitividad.
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
# 6. LECTURA DE CSV
# ==========================================================

def leer_csv(archivo):
    """
    Lee un archivo CSV cargado por el usuario.

    Se intenta leer con codificación UTF-8 y, si falla,
    se intenta con Latin-1. Esto evita errores comunes
    al abrir archivos exportados desde Excel.
    """

    try:
        archivo.seek(0)
        return pd.read_csv(archivo, encoding="utf-8-sig")
    except UnicodeDecodeError:
        archivo.seek(0)
        return pd.read_csv(archivo, encoding="latin-1")


def inventario_ejemplo():
    """
    Inventario de prueba para mostrar el funcionamiento del prototipo
    sin necesidad de subir un archivo externo.
    """

    return pd.DataFrame({
        "codigo": [
            "SKU-001", "SKU-002", "SKU-003",
            "SKU-004", "SKU-005", "SKU-006",
            "SKU-007", "SKU-008", "SKU-009"
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
            "Arroz extra 1000 g"
        ],
        "marca": [
            "Coca-Cola", "Coca Cola", "Coca-Cola",
            "La Lechera", "La Lechera", "La Lechera",
            "Don Pepe", "Don Pepe", "Don Pepe"
        ],
        "categoria": [
            "Bebidas", "Bebidas", "Bebidas",
            "Lácteos", "Lacteos", "Lácteos",
            "Granos", "Granos", "Granos"
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
            "Arroz blanco extra seleccionado funda 1000 g"
        ],
        "stock": [48, 32, 20, 40, 25, 18, 60, 44, 30]
    })


# ==========================================================
# 7. APOYO PARA DEFENSA: TABLA MATEMÁTICA
# ==========================================================

def tabla_matematica():
    """
    Tabla que muestra cómo cada concepto de Matemáticas Discretas
    se refleja dentro del prototipo.
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
        "Aplicación en el prototipo": [
            "El inventario completo cargado desde el archivo CSV.",
            "Cada fila o registro del inventario.",
            "Selección de columnas relevantes para la comparación.",
            "Comparación entre pares de registros del inventario.",
            "Filtro de pares que superan el umbral de similitud.",
            "Par de registros considerado como posible coincidencia.",
            "Agrupación de registros conectados directa o indirectamente.",
            "Grupo de registros que podrían representar el mismo producto."
        ]
    })


def sugerir_columna_id(columnas):
    """
    Sugiere una columna identificadora si encuentra nombres comunes
    como codigo, código, id o sku.
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
# 8. INTERFAZ DEL PROTOTIPO
# ==========================================================

st.title("ClearStock")
st.subheader("Auditoría de inventarios no estructurados")

st.write(
    "Prototipo desarrollado para identificar y agrupar posibles registros "
    "repetidos en inventarios, aplicando álgebra relacional y propiedades "
    "de relaciones."
)

st.info(
    "ClearStock no elimina ni modifica el archivo original. "
    "El sistema genera sugerencias de revisión para que el encargado del "
    "inventario tome la decisión final."
)

with st.expander("Relación del prototipo con Matemáticas Discretas"):
    st.dataframe(
        tabla_matematica(),
        use_container_width=True,
        hide_index=True
    )


# ==========================================================
# 9. CONFIGURACIÓN EN BARRA LATERAL
# ==========================================================

st.sidebar.title("Configuración")

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
# 10. CARGA DE DATOS
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
    st.stop()


if df.empty:
    st.error("El archivo cargado no contiene registros.")
    st.stop()


columnas = list(df.columns)

st.success(
    f"Inventario cargado correctamente: {len(df)} registros "
    f"y {len(columnas)} columnas."
)

with st.expander("Vista previa del inventario cargado", expanded=False):
    st.dataframe(
        df.head(15),
        use_container_width=True,
        hide_index=True
    )


# ==========================================================
# 11. SELECCIÓN DE COLUMNAS Y UMBRAL
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
    "Mientras más alto sea el umbral, más estricta será la comparación."
)

if not columnas_comparacion:
    st.error("Selecciona al menos una columna para comparar.")
    st.stop()


# ==========================================================
# 12. EJECUCIÓN DEL ANÁLISIS
# ==========================================================

st.markdown("## Configuración seleccionada")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("Columna ID", columna_id)

with col_b:
    st.metric("Columnas comparadas", len(columnas_comparacion))

with col_c:
    st.metric("Umbral", f"{umbral}%")

st.write("Columnas usadas para la proyección:", ", ".join(columnas_comparacion))

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

    st.caption(
        "Los pares comparados se calculan con la fórmula n(n−1)/2, "
        "porque se comparan pares únicos sin repetir el orden."
    )

    tab1, tab2, tab3 = st.tabs([
        "Pares relacionados",
        "Grupos de revisión",
        "Descargas"
    ])

    with tab1:
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

    with tab2:
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
            "Estos grupos no representan una eliminación automática. "
            "Son sugerencias para que el responsable del inventario revise "
            "si las entradas deben unificarse o mantenerse separadas."
        )

    with tab3:
        st.subheader("Reportes descargables")

        if not tabla_pares.empty:
            st.download_button(
                label="Descargar detalle de pares relacionados",
                data=tabla_pares.to_csv(index=False).encode("utf-8-sig"),
                file_name="clearstock_pares_relacionados.csv",
                mime="text/csv",
                use_container_width=True
            )

        if not tabla_grupos.empty:
            st.download_button(
                label="Descargar reporte de grupos",
                data=tabla_grupos.to_csv(index=False).encode("utf-8-sig"),
                file_name="clearstock_grupos_revision.csv",
                mime="text/csv",
                use_container_width=True
            )

        if tabla_pares.empty and tabla_grupos.empty:
            st.write(
                "No hay reportes disponibles porque no se encontraron coincidencias "
                "con el umbral seleccionado."
            )

else:
    st.info(
        "Cuando la configuración esté lista, presiona "
        "“Ejecutar análisis” para aplicar el modelo."
    )
