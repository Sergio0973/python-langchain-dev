import hashlib
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_google_genai._common import GoogleGenerativeAIError
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Las rutas se calculan desde este archivo para que el programa funcione
# aunque se ejecute desde otro directorio.
APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
PDF_PATH = APP_DIR / "basesycondicionesnestle.pdf"
CHROMA_DIR = PROJECT_DIR / "chroma_nestle_ofertas_basicos"
REPORT_PATH = APP_DIR / "resultados_rag_nestle.md"

load_dotenv(PROJECT_DIR / ".env", override=True)

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        f"No se encontró GOOGLE_API_KEY en {PROJECT_DIR / '.env'}"
    )

if not PDF_PATH.exists():
    raise FileNotFoundError(
        "No se encontró el PDF del taller. Debes copiarlo en:\n"
        f"{PDF_PATH}"
    )


PREGUNTA = (
    "De acuerdo con las bases de la promoción Ofertas de Hoy con Inés Básicos, "
    "¿cuáles son las condiciones o situaciones en las que una persona participante "
    "puede ser descalificada o perder su participación en la promoción?"
)

PROMPT = ChatPromptTemplate.from_template(
    """
Eres un asistente especializado en términos y condiciones de promociones
comerciales de consumo masivo, especialmente promociones de productos Nestlé.

Responde EXCLUSIVAMENTE con la información del contexto. No agregues reglas,
condiciones ni conclusiones que no estén respaldadas por los fragmentos.
Responde en español latinoamericano y en un máximo de 4 párrafos.

Si el contexto no contiene información suficiente, indícalo claramente.

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
        f"nestle_{pdf_hash}_cs{chunk_size}_co{chunk_overlap}"
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
        except GoogleGenerativeAIError as error:
            es_limite_temporal = "RESOURCE_EXHAUSTED" in str(error)
            if not es_limite_temporal or intento == intentos:
                raise

            espera = 65
            print(
                f"Cuota temporal de embeddings alcanzada. Esperando "
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

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=temperature,
        max_retries=2,
    )

    respuesta = (PROMPT | llm).invoke(
        {
            "question": PREGUNTA,
            "context": contexto,
        }
    )

    print("\nRESPUESTA:\n")
    print(respuesta.content)

    print("\nFRAGMENTOS RECUPERADOS:")
    for i, doc in enumerate(docs_relevantes, start=1):
        pagina = doc.metadata.get("page")
        pagina_texto = pagina + 1 if isinstance(pagina, int) else "desconocida"
        print(f"\n--- Fragmento {i} | página {pagina_texto} ---")
        print(doc.page_content[:700], "...")

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

    REPORT_PATH.write_text("\n".join(lineas), encoding="utf-8")


def main():
    loader = PyPDFLoader(str(PDF_PATH))
    documents = loader.load()
    print(f"Páginas cargadas: {len(documents)}")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    # Solo existen dos configuraciones de chunking. Los escenarios base, 2
    # y 3 comparten la misma indexación, lo que hace justa la comparación.
    stores = {}
    se_creo_indice_en_esta_ejecucion = False

    for config in ESCENARIOS:
        clave = (config["chunk_size"], config["chunk_overlap"])
        if clave not in stores:
            # El nivel gratuito admite 100 embeddings por minuto. Las dos
            # configuraciones suman 125 chunks, por lo que se espera entre
            # índices para no provocar un error 429.
            if se_creo_indice_en_esta_ejecucion:
                espera = 65
                print(
                    f"Esperando {espera} segundos para respetar la cuota "
                    "gratuita de Gemini..."
                )
                time.sleep(espera)

            vector_store, chunks_generados, indice_creado = crear_vector_store(
                documents=documents,
                embeddings=embeddings,
                chunk_size=config["chunk_size"],
                chunk_overlap=config["chunk_overlap"],
            )
            stores[clave] = (vector_store, chunks_generados)
            se_creo_indice_en_esta_ejecucion = (
                se_creo_indice_en_esta_ejecucion or indice_creado
            )

    resultados = []
    for config in ESCENARIOS:
        clave = (config["chunk_size"], config["chunk_overlap"])
        vector_store, chunks_generados = stores[clave]
        resultados.append(
            ejecutar_escenario(config, vector_store, chunks_generados)
        )

    guardar_informe(resultados)
    print(f"\nInforme guardado en: {REPORT_PATH}")


if __name__ == "__main__":
    main()
