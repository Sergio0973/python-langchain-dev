import hashlib
from pathlib import Path

import streamlit as st
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_PDF_PATH = PROJECT_DIR / "data" / "basesycondicionesnestle.pdf"
CHROMA_DIR = PROJECT_DIR / "storage" / "chroma"

SYSTEM_PROMPT = """
Eres un asistente conversacional especializado en las bases y condiciones de
la promoción de Nestlé descrita en el documento suministrado.

Reglas:
1. Usa el historial únicamente para comprender preguntas de seguimiento.
2. Para afirmaciones sobre la promoción, responde exclusivamente con el
   contexto recuperado.
3. Si el contexto contiene la respuesta, comienza exactamente con:
   "Según el documento:"
4. Si la pregunta se relaciona con la promoción, pero el contexto no permite
   responderla, responde solamente:
   "La información solicitada no se encuentra en el documento."
5. Si la pregunta no tiene relación con el documento, respóndela usando tu
   conocimiento general y comienza exactamente con:
   "Esta pregunta no está relacionada con el documento. Respuesta general:"
   No atribuyas esa respuesta al documento ni inventes fuentes.
6. No inventes requisitos, fechas, premios, restricciones ni excepciones.
7. Responde en español latinoamericano, de forma clara y concisa.
"""

DOCUMENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
Historial reciente:
{history}

Pregunta actual:
{question}

Contexto recuperado:
{context}
""",
        ),
    ]
)

ROUTER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Clasifica la pregunta del usuario en una sola categoría:

- DOCUMENT: pregunta sobre Nestlé, la promoción, sus bases, condiciones,
  participantes, premios, fechas, restricciones o cualquier contenido que
  pueda pertenecer al documento.
- GENERAL: cualquier otra pregunta, aunque solicite información actual,
  conocimiento general, programación, conversación cotidiana u otro tema.

Responde únicamente con DOCUMENT o GENERAL. No expliques la decisión.
""",
        ),
        (
            "human",
            """
Historial reciente:
{history}

Pregunta:
{question}
""",
        ),
    ]
)

GENERAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Eres un asistente útil de propósito general. Responde cualquier pregunta en
español latinoamericano de forma clara y directa.

Comienza exactamente con:
"Esta pregunta no está relacionada con el documento. Respuesta general:"

No menciones el PDF, fragmentos ni fuentes documentales después de ese aviso.
No inventes datos. Si la pregunta requiere información en tiempo real y no
puedes comprobarla, indícalo con claridad y explica cómo verificarla.
""",
        ),
        (
            "human",
            """
Historial reciente:
{history}

Pregunta actual:
{question}
""",
        ),
    ]
)


def format_documents(documents: list[Document]) -> str:
    blocks = []

    for index, document in enumerate(documents, start=1):
        page = document.metadata.get("page")
        page_number = page + 1 if isinstance(page, int) else "desconocida"
        blocks.append(
            f"[Fragmento {index} | página {page_number}]\n"
            f"{document.page_content.strip()}"
        )

    return "\n\n---\n\n".join(blocks)


def format_chat_history(messages: list[dict], max_messages: int = 8) -> str:
    conversation = [
        message
        for message in messages
        if message["role"] in {"user", "assistant"}
    ][-max_messages:]

    if not conversation:
        return "No hay mensajes anteriores."

    return "\n".join(
        (
            f"{'Usuario' if message['role'] == 'user' else 'Asistente'}: "
            f"{message['content']}"
        )
        for message in conversation
    )


def build_retrieval_query(question: str, messages: list[dict]) -> str:
    previous_questions = [
        message["content"]
        for message in messages[:-1]
        if message["role"] == "user"
    ][-2:]

    return "\n".join(previous_questions + [question])


def _collection_name(pdf_path: Path) -> str:
    pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:12]
    return f"nestle_chat_{pdf_hash}_cs1000_co200"


@st.cache_resource(show_spinner=False)
def get_vector_store(pdf_path: str, api_key: str) -> Chroma:
    source_path = Path(pdf_path)
    if not source_path.exists():
        raise FileNotFoundError(f"No se encontró el PDF: {source_path}")

    loader = PyPDFLoader(str(source_path))
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    chunks = splitter.split_documents(pages)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key,
    )
    collection_name = _collection_name(source_path)

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    if vector_store._collection.count() != len(chunks):
        existing_ids = vector_store.get(include=[])["ids"]
        if existing_ids:
            vector_store.delete(ids=existing_ids)

        ids = [f"{collection_name}_{index}" for index in range(len(chunks))]
        vector_store.add_documents(chunks, ids=ids)

    return vector_store


def get_retriever(pdf_path: str, api_key: str, top_k: int):
    vector_store = get_vector_store(pdf_path=pdf_path, api_key=api_key)
    return vector_store.as_retriever(search_kwargs={"k": top_k})


def _create_model(
    model_name: str,
    temperature: float,
    api_key: str,
) -> ChatOpenAI:
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
        max_retries=2,
    )


def classify_question(
    question: str,
    history: str,
    model_name: str,
    api_key: str,
) -> str:
    model = _create_model(
        model_name=model_name,
        temperature=0,
        api_key=api_key,
    )
    result = (ROUTER_PROMPT | model | StrOutputParser()).invoke(
        {"question": question, "history": history}
    )
    category = result.strip().upper()
    return "DOCUMENT" if category.startswith("DOCUMENT") else "GENERAL"


def create_document_chain(
    model_name: str,
    temperature: float,
    api_key: str,
):
    model = _create_model(
        model_name=model_name,
        temperature=temperature,
        api_key=api_key,
    )

    prepare_context = RunnableLambda(
        lambda inputs: {
            **inputs,
            "context": format_documents(inputs["context"]),
        }
    )

    return prepare_context | DOCUMENT_PROMPT | model | StrOutputParser()


def create_general_chain(
    model_name: str,
    temperature: float,
    api_key: str,
):
    model = _create_model(
        model_name=model_name,
        temperature=temperature,
        api_key=api_key,
    )
    return GENERAL_PROMPT | model | StrOutputParser()
