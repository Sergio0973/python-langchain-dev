# Paso 2: Imports principales

# Manejo del sistema operativo (variables de entorno, rutas, etc.)
import os
from pathlib import Path
# Carga de PDFs (document loaders)
from langchain_community.document_loaders import PyPDFLoader

# División de texto en fragmentos (chunking)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Modelos de OpenAI: embeddings y modelo de chat
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Vector store basado en Chroma
from langchain_chroma import Chroma

# Prompting y construcción de la cadena RAG (versión nueva de LangChain)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path, override=True)

api_key = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = api_key

# Ruta relativa del PDF.
# En tu caso:
#   - Carpeta base del proyecto: "bases vectoriales/"
#   - Notebook: "bases vectoriales/LangChain.ipynb"
#   - PDF:      "bases vectoriales/todo_claro/terminosycondicionestodoclaro.pdf"
#
# Como el Notebook está en "bases vectoriales", basta con:
pdf_path = "app/terminosycondicionestodoclaro.pdf" 
# Creamos el loader para PDF
loader = PyPDFLoader(pdf_path)

documents = loader.load()

print(f"Número de páginas cargadas desde el PDF: {len(documents)}")
print("Ejemplo de contenido (primeros 500 caracteres de la primera página):\n")
print(documents[0].page_content[:500], "...")

# Dividir el texto del PDF en fragmentos

# Creamos el text splitter siguiendo el ejemplo oficial:
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,    # tamaño aproximado de cada fragmento en caracteres
    chunk_overlap=200,  # solapamiento entre fragmentos para no perder contexto
    add_start_index=True
)

# Aplicamos el splitter a la lista de documentos cargados
splits = text_splitter.split_documents(documents)

print(f"El PDF se dividió en {len(splits)} fragmentos (chunks).")
print("Ejemplo de fragmento:\n")
print(splits[0].page_content[:500], "...")

# Crear el modelo de embeddings de OpenAI

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"  # puedes usar "text-embedding-3-large" si quieres
)

print("Objeto de embeddings creado correctamente.")

#Crear el vector store con Chroma e indexar los fragmentos

# Directorio donde se va a persistir la base vectorial en disco
persist_directory = "db_todo_claro_langchain"

# Creamos el vector store vacío
vector_store = Chroma(
    collection_name="todo_claro_collection",
    embedding_function=embeddings,
    persist_directory=persist_directory,
)

# Indexamos (añadimos) todos los fragmentos al vector store
document_ids = vector_store.add_documents(splits)

print(f"Se indexaron {len(document_ids)} fragmentos en Chroma.")
print(f"La base vectorial se guardó en la carpeta: {persist_directory}")

# Paso 8: Crear un retriever a partir del vector store

# El retriever es el objeto que sabe buscar fragmentos relevantes
retriever = vector_store.as_retriever(
    search_kwargs={"k": 4}   # número de fragmentos que queremos recuperar por pregunta
)

print("Retriever creado correctamente.")
# Paso 9: Definir el modelo de chat de OpenAI y el prompt para RAG

# Modelo de chat (puedes ajustar el modelo según tu cuenta)
llm = ChatOpenAI(
    model="gpt-4.1-mini",   # o "gpt-4o-mini", etc.
    temperature=0.1         # respuestas más deterministas
)

# Prompt siguiendo la filosofía de la doc RAG:
template = """
Eres un asistente especializado en términos y condiciones de productos de telecomunicaciones.

Usa EXCLUSIVAMENTE la información del contexto para responder en español latinoamericano
y en un máximo de 4 párrafos. Si la pregunta no se puede responder con el contexto,
di claramente que la información no está en el documento.

Pregunta del usuario:
{question}

Contexto:
{context}
"""

prompt = ChatPromptTemplate.from_template(template)

print("Modelo de chat y prompt RAG configurados.")

# Construir la cadena RAG (Retrieve + Generate)

# La idea es:
#  - "question" pasa directamente (RunnablePassthrough)
#  - "context" se obtiene llamando al retriever con esa misma pregunta

rag_chain = (
    {
        "question": RunnablePassthrough(),
        "context": retriever,      # el retriever recibe internamente la pregunta
    }
    | prompt                       # armamos el mensaje para el modelo
    | llm                          # llamamos al modelo de chat
)

print("Cadena RAG construida correctamente.")
# Paso 11: Probar la cadena RAG

pregunta = (
    "Según los términos y condiciones del beneficio Todo Claro, "
    "¿en qué casos un cliente NO puede acceder temporalmente al beneficio "
    "para su servicio hogar Claro?"
)

respuesta = rag_chain.invoke(pregunta)

print("Pregunta:")
print(pregunta)
print("\nRespuesta generada por el modelo:")
print(respuesta.content)

# Paso 12 (opcional): Inspeccionar los fragmentos recuperados

# Usamos la misma pregunta del Paso 11
print("Pregunta de prueba:")
print(pregunta)
print("\nFragmentos recuperados:\n")

docs_relevantes = retriever.invoke(pregunta)  # retriever viene del paso donde hicimos vector_store.as_retriever()

print(f"Se recuperaron {len(docs_relevantes)} fragmentos.\n")

for i, doc in enumerate(docs_relevantes, start=1):
    print(f"--- Fragmento {i} ---")
    # Mostramos solo los primeros 500 caracteres para que no sea tan largo
    print(doc.page_content[:500], "...\n")
    # Si quieres, también puedes mostrar metadatos como la página
    # print("Metadata:", doc.metadata)