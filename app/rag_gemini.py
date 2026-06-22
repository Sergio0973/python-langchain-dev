import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Cargar GOOGLE_API_KEY desde el .env más cercano al directorio de ejecución.
# Funciona tanto en un script como en un notebook.
env_path = find_dotenv(usecwd=True)
load_dotenv(env_path, override=True)

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "No se encontró GOOGLE_API_KEY. Agrégala al archivo .env "
        "o expórtala como variable de entorno."
    )


# Cargar el PDF.
pdf_path = Path("app/terminosycondicionestodoclaro.pdf")
if not pdf_path.exists():
    raise FileNotFoundError(f"No se encontró el PDF en: {pdf_path.resolve()}")

loader = PyPDFLoader(str(pdf_path))
documents = loader.load()

print(f"Número de páginas cargadas desde el PDF: {len(documents)}")
print("Ejemplo de contenido:\n")
print(documents[0].page_content[:500], "...")


# Dividir el documento en fragmentos.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True,
)
splits = text_splitter.split_documents(documents)

print(f"El PDF se dividió en {len(splits)} fragmentos.")


# Generar embeddings con Gemini.
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
)
print("Objeto de embeddings de Gemini creado correctamente.")


# Usar una colección nueva: una base creada con embeddings de OpenAI no es
# compatible con embeddings de Gemini.
persist_directory = "db_todo_claro_gemini"
vector_store = Chroma(
    collection_name="todo_claro_gemini_collection",
    embedding_function=embeddings,
    persist_directory=persist_directory,
)

document_ids = vector_store.add_documents(splits)
print(f"Se indexaron {len(document_ids)} fragmentos en Chroma.")
print(f"La base vectorial se guardó en: {persist_directory}")


# Crear el retriever.
retriever = vector_store.as_retriever(search_kwargs={"k": 4})
print("Retriever creado correctamente.")


# Configurar Gemini como modelo generativo.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.1,
    max_retries=2,
)

template = """
Eres un asistente especializado en términos y condiciones de productos de
telecomunicaciones.

Usa EXCLUSIVAMENTE la información del contexto para responder en español
latinoamericano y en un máximo de 4 párrafos.

Si la pregunta no se puede responder con el contexto, di claramente que la
información no está en el documento.

Pregunta del usuario:
{question}

Contexto:
{context}
"""

prompt = ChatPromptTemplate.from_template(template)


def format_docs(docs):
    """Convertir los documentos recuperados en texto para el prompt."""
    return "\n\n".join(doc.page_content for doc in docs)


# Mantener la misma estructura Retrieve + Generate.
rag_chain = (
    {
        "question": RunnablePassthrough(),
        "context": retriever | format_docs,
    }
    | prompt
    | llm
)

print("Cadena RAG con Gemini construida correctamente.")


# Probar la cadena.
pregunta = (
    "Según los términos y condiciones del beneficio Todo Claro, "
    "¿en qué casos un cliente NO puede acceder temporalmente al beneficio "
    "para su servicio hogar Claro?"
)

respuesta = rag_chain.invoke(pregunta)

print("Pregunta:")
print(pregunta)
print("\nRespuesta generada por Gemini:")
print(respuesta.content)


# Inspeccionar los fragmentos recuperados.
docs_relevantes = retriever.invoke(pregunta)
print(f"\nSe recuperaron {len(docs_relevantes)} fragmentos.\n")

for i, doc in enumerate(docs_relevantes, start=1):
    print(f"--- Fragmento {i} ---")
    print(doc.page_content[:500], "...\n")
