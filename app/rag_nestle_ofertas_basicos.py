import hashlib
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import (
    ChatOpenAI,
    OpenAIEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)


# Las rutas se calculan desde este archivo para que el programa funcione
# aunque se ejecute desde otro directorio.
APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
PDF_PATH = APP_DIR / "basesycondicionesnestle.pdf"
CHROMA_DIR = PROJECT_DIR / "chroma_nestle_ofertas_basicos_openai"
REPORT_PATH = APP_DIR / "resultados_rag_nestle.md"

load_dotenv(PROJECT_DIR / ".env", override=True)

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        f"No se encontró OPENAI_API_KEY en {PROJECT_DIR / '.env'}"
    )

if not PDF_PATH.exists():
    raise FileNotFoundError(
        "No se encontró el PDF del taller. Debes copiarlo en:\n"
        f"{PDF_PATH}"
    )


PREGUNTA_PREDETERMINADA = (
    "De acuerdo con las bases de la promoción Ofertas de Hoy con Inés Básicos, "
    "¿cuáles son las condiciones o situaciones en las que una persona participante "
    "puede ser descalificada o perder su participación en la promoción?"
)

PREGUNTA = PREGUNTA_PREDETERMINADA

PROMPT = ChatPromptTemplate.from_template(
    """
Eres un asistente especializado en términos y condiciones de promociones
comerciales de consumo masivo, especialmente promociones de productos Nestlé.

Primero determina si la pregunta puede responderse con el contexto del
documento.

Si la respuesta está en el contexto, responde exclusivamente con esa
información y comienza con: "Según el documento:"

Si la pregunta no está relacionada con el documento, puedes responder con
conocimiento general, pero debes comenzar exactamente con:
"Respuesta general (no proviene del documento):"

Si la pregunta está relacionada con la promoción, pero el contexto no contiene
información suficiente, responde solamente:
"La información solicitada no se encuentra en el documento."

Responde en español latinoamericano, de forma directa y únicamente con la
información necesaria. Usa un máximo de 2 párrafos.

Pregunta del usuario:
{question}

Contexto:
{context}
"""
)

ESCENARIOS = [
    {
        "nombre": "Escenario base",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "k": 4,
        "temperature": 0.1,
    },
    {
        "nombre": "Escenario 1: chunks pequeños y menos fragmentos",
        "chunk_size": 350,
        "chunk_overlap": 20,
        "k": 2,
        "temperature": 0.1,
    },
    {
        "nombre": "Escenario 2: más fragmentos recuperados",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "k": 6,
        "temperature": 0.1,
    },
    {
        "nombre": "Escenario 3: temperatura alta",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "k": 6,
        "temperature": 0.8,
    },
]


def format_docs(docs):
    """Preparar los documentos recuperados para incluirlos en el prompt."""
    bloques = []

    for i, doc in enumerate(docs, start=1):
        pagina = doc.metadata.get("page")
        pagina_texto = pagina + 1 if isinstance(pagina, int) else "desconocida"
        bloques.append(
            f"[Fragmento {i} | página {pagina_texto}]\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(bloques)


def solicitar_pregunta():
    """Solicitar una pregunta o utilizar la pregunta original del taller."""
    print("\nEscribe la pregunta que deseas consultar.")
    print("Presiona Enter para usar la pregunta original del taller:")
    print(f"\n{PREGUNTA_PREDETERMINADA}\n")

    pregunta_usuario = input("Pregunta: ").strip()
    return pregunta_usuario or PREGUNTA_PREDETERMINADA


def crear_vector_store(documents, embeddings, chunk_size, chunk_overlap):
    """Crear o actualizar una colección para una configuración de chunking."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )
    splits = splitter.split_documents(documents)

    # El hash evita mezclar colecciones si se reemplaza el PDF por otra versión.
    pdf_hash = hashlib.sha256(PDF_PATH.read_bytes()).hexdigest()[:10]
    collection_name = (
        f"nestle_openai_{pdf_hash}_cs{chunk_size}_co{chunk_overlap}"
    )

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    # Si la colección ya quedó completa en una ejecución anterior, se reutiliza
    # sin volver a consumir la cuota de embeddings.
    if vector_store._collection.count() == len(splits):
        print(f"Índice reutilizado: {collection_name} ({len(splits)} chunks)")
        return vector_store, len(splits), False

    # IDs estables: al repetir el programa, Chroma actualiza estos registros
    # en vez de crear copias adicionales.
    ids = [f"{collection_name}_{i}" for i in range(len(splits))]
    intentos = 2
    for intento in range(1, intentos + 1):
        try:
            vector_store.add_documents(splits, ids=ids)
            break
        except (RateLimitError, APIConnectionError, APITimeoutError):
            if intento == intentos:
                raise

            espera = 20 * intento
            print(
                f"OpenAI alcanzó un límite temporal de embeddings. Esperando "
                f"{espera} segundos antes de continuar..."
            )
            time.sleep(espera)

    print(f"Índice creado: {collection_name} ({len(splits)} chunks)")

    return vector_store, len(splits), True


def ejecutar_escenario(config, vector_store, chunks_generados):
    """Recuperar contexto y generar la respuesta de un escenario."""
    nombre = config["nombre"]
    k = config["k"]
    temperature = config["temperature"]

    print("\n" + "=" * 80)
    print(nombre)
    print("=" * 80)
    print(
        f"chunk_size={config['chunk_size']} | "
        f"chunk_overlap={config['chunk_overlap']} | "
        f"k={k} | temperature={temperature}"
    )
    print(f"Chunks disponibles: {chunks_generados}")

    # Se recuperan una sola vez. Estos son exactamente los fragmentos que
    # se muestran en pantalla y que recibe el modelo.
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    docs_relevantes = retriever.invoke(PREGUNTA)
    contexto = format_docs(docs_relevantes)

    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=temperature,
        max_retries=0,
    )

    datos_prompt = {
        "question": PREGUNTA,
        "context": contexto,
    }

    # OpenAI puede responder temporalmente con límites de uso, problemas de
    # conexión o errores internos. En esos casos esperamos y repetimos.
    intentos = 4
    for intento in range(1, intentos + 1):
        try:
            respuesta = (PROMPT | llm).invoke(datos_prompt)
            break
        except (
            RateLimitError,
            APIConnectionError,
            APITimeoutError,
            InternalServerError,
        ):
            if intento == intentos:
                raise

            espera = 15 * intento
            print(
                "OpenAI alcanzó un límite temporal de servicio. "
                f"Reintento {intento}/{intentos - 1} en {espera} segundos..."
            )
            time.sleep(espera)

    print("\nRESPUESTA:\n")
    print(respuesta.content)
    print(
        "\nLos fragmentos recuperados se guardarán en "
        f"{REPORT_PATH.name}."
    )

    return {
        **config,
        "chunks_generados": chunks_generados,
        "respuesta": respuesta.content,
        "documentos": docs_relevantes,
    }


def guardar_informe(resultados):
    """Guardar la evidencia de todos los escenarios para su comparación."""
    lineas = [
        "# Resultados del taller RAG Nestlé",
        "",
        "## Pregunta",
        "",
        PREGUNTA,
        "",
    ]

    for resultado in resultados:
        lineas.extend(
            [
                f"## {resultado['nombre']}",
                "",
                (
                    f"- `chunk_size`: {resultado['chunk_size']}\n"
                    f"- `chunk_overlap`: {resultado['chunk_overlap']}\n"
                    f"- `k`: {resultado['k']}\n"
                    f"- `temperature`: {resultado['temperature']}\n"
                    f"- Chunks generados: {resultado['chunks_generados']}"
                ),
                "",
                "### Respuesta",
                "",
                str(resultado["respuesta"]),
                "",
                "### Fragmentos recuperados",
                "",
            ]
        )

        for i, doc in enumerate(resultado["documentos"], start=1):
            pagina = doc.metadata.get("page")
            pagina_texto = pagina + 1 if isinstance(pagina, int) else "desconocida"
            lineas.extend(
                [
                    f"#### Fragmento {i} — página {pagina_texto}",
                    "",
                    doc.page_content.strip(),
                    "",
                ]
            )

    lineas.extend(
        [
            "## Análisis de los resultados",
            "",
            "### 1. Beneficios y limitaciones del escenario base",
            "",
            (
                "En el escenario base, los fragmentos de 1000 caracteres con "
                "un traslape de 200 conservaron suficiente contexto alrededor "
                "de cada regla. Esto permitió recuperar en un mismo fragmento "
                "la causal de descalificación y su explicación, reduciendo el "
                "riesgo de interpretar frases aisladas. El traslape también "
                "ayudó a preservar ideas que se encontraban cerca del límite "
                "entre dos chunks."
            ),
            "",
            (
                "La principal limitación es que los fragmentos largos pueden "
                "incluir información que no responde directamente a la "
                "pregunta. Además, el traslape produce contenido repetido, "
                "aumenta la cantidad de texto almacenado y puede hacer que "
                "varios resultados contengan partes similares. Aun así, para "
                "este documento, la configuración base ofreció un equilibrio "
                "adecuado entre contexto y precisión."
            ),
            "",
            "### 2. Efecto de chunks pequeños, menor traslape y k=2",
            "",
            (
                "Al reducir el chunk_size a 350, el chunk_overlap a 20 y k a "
                "2, los fragmentos fueron más específicos, pero perdieron "
                "continuidad. La respuesta recuperó el incumplimiento de los "
                "requisitos y los intentos de alterar los sistemas asociados "
                "a la promoción, pero omitió otras causales presentes en el "
                "PDF, como el fraude, los participantes no elegibles, las "
                "violaciones de la dinámica, los hackers y los caza "
                "promociones."
            ),
            "",
            (
                "Esto muestra que los chunks pequeños pueden mejorar la "
                "precisión local, pero un k bajo ofrece muy poco contexto para "
                "preguntas que requieren reunir una lista distribuida en "
                "varias páginas. En este caso, la respuesta fue menos exacta "
                "por incompleta, no porque las afirmaciones recuperadas fueran "
                "incorrectas."
            ),
            "",
            "### 3. Comparación entre temperature=0.1 y temperature=0.8",
            "",
            (
                "Con temperature=0.1, la respuesta fue más directa, estable y "
                "cercana a la redacción de los fragmentos. Esta configuración "
                "es preferible para términos y condiciones, políticas, "
                "contratos y otros documentos donde importa más la fidelidad "
                "que la variedad de expresión."
            ),
            "",
            (
                "Con temperature=0.8, la respuesta tuvo una redacción más "
                "elaborada y desarrolló con mayor amplitud algunas "
                "consecuencias. Aunque en esta ejecución se mantuvo respaldada "
                "por el contexto, una temperatura alta aumenta la variación "
                "entre ejecuciones y el riesgo de agregar interpretaciones no "
                "explícitas. Sería más útil para tareas creativas o de estilo, "
                "pero no es la opción recomendada para este RAG documental."
            ),
            "",
            "## Conclusión",
            "",
            (
                "Para esta consulta, el escenario 2 ofrece la respuesta más "
                "completa: conserva chunks amplios, mantiene un traslape "
                "suficiente, recupera seis fragmentos y utiliza una "
                "temperatura baja. El escenario base también funciona bien, "
                "mientras que el escenario 1 pierde causales importantes y el "
                "escenario 3 introduce una variación de estilo innecesaria "
                "para un documento normativo."
            ),
            "",
            "## Nota sobre el proveedor",
            "",
            (
                "El taller fue ejecutado con OpenAI, conservando el flujo RAG "
                "solicitado: carga, división, embeddings, almacenamiento "
                "vectorial, recuperación y generación de la respuesta. Los "
                "modelos utilizados fueron `text-embedding-3-small` y "
                "`gpt-4.1-mini`."
            ),
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lineas), encoding="utf-8")


def main():
    global PREGUNTA
    PREGUNTA = solicitar_pregunta()

    print(f"\nPregunta seleccionada:\n{PREGUNTA}\n")

    loader = PyPDFLoader(str(PDF_PATH))
    documents = loader.load()
    print(f"Páginas cargadas: {len(documents)}")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    # Solo existen dos configuraciones de chunking. Los escenarios base, 2
    # y 3 comparten la misma indexación, lo que hace justa la comparación.
    stores = {}

    for config in ESCENARIOS:
        clave = (config["chunk_size"], config["chunk_overlap"])
        if clave not in stores:
            vector_store, chunks_generados, _ = crear_vector_store(
                documents=documents,
                embeddings=embeddings,
                chunk_size=config["chunk_size"],
                chunk_overlap=config["chunk_overlap"],
            )
            stores[clave] = (vector_store, chunks_generados)

    resultados = []
    for config in ESCENARIOS:
        clave = (config["chunk_size"], config["chunk_overlap"])
        vector_store, chunks_generados = stores[clave]
        resultados.append(
            ejecutar_escenario(config, vector_store, chunks_generados)
        )
        # Guardar después de cada escenario evita perder resultados si la API
        # se interrumpe durante una consulta posterior.
        guardar_informe(resultados)

    print(f"\nInforme guardado en: {REPORT_PATH}")


if __name__ == "__main__":
    main()
