import os

import streamlit as st
from dotenv import load_dotenv

from rag_service import (
    DEFAULT_PDF_PATH,
    build_retrieval_query,
    classify_question,
    create_document_chain,
    create_general_chain,
    format_chat_history,
    get_retriever,
)


load_dotenv()

st.set_page_config(
    page_title="Chat RAG Nestlé",
    page_icon="💬",
    layout="centered",
)


def initialize_session() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hola. Puedo responder preguntas sobre las bases y condiciones "
                    "de la promoción de Nestlé."
                ),
                "sources": [],
            }
        ]


def clear_conversation() -> None:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Conversación reiniciada. ¿Qué deseas consultar sobre la promoción?"
            ),
            "sources": [],
        }
    ]


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return

    with st.expander("Fuentes consultadas"):
        for source in sources:
            st.markdown(
                f"**Fragmento {source['number']} · página {source['page']}**"
            )
            st.write(source["content"])


initialize_session()

st.title("💬 Chat conversacional RAG")
st.caption(
    "Consulta las bases y condiciones de la promoción. "
    "Las respuestas se generan usando el contenido del PDF."
)

with st.sidebar:
    st.header("Configuración")

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("OpenAI API Key", type="password")

    model_name = st.text_input("Modelo", value="gpt-4.1-mini")
    temperature = st.slider(
        "Temperatura",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.1,
    )
    top_k = st.slider(
        "Fragmentos recuperados",
        min_value=2,
        max_value=8,
        value=6,
        step=1,
    )

    st.divider()
    st.write(f"Documento: `{DEFAULT_PDF_PATH.name}`")

    if st.button("Nueva conversación", use_container_width=True):
        clear_conversation()
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        render_sources(message.get("sources", []))

question = st.chat_input("Escribe una pregunta sobre la promoción")

if question:
    if not api_key:
        st.error(
            "Configura OPENAI_API_KEY en el archivo .env o ingrésala "
            "temporalmente en la barra lateral."
        )
        st.stop()

    st.session_state.messages.append(
        {"role": "user", "content": question, "sources": []}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Analizando la pregunta..."):
                history = format_chat_history(st.session_state.messages[:-1])
                category = classify_question(
                    question=question,
                    history=history,
                    model_name=model_name,
                    api_key=api_key,
                )
                documents = []
                inputs = {
                    "history": history,
                    "question": question,
                }

                if category == "DOCUMENT":
                    if not DEFAULT_PDF_PATH.exists():
                        raise FileNotFoundError(
                            f"No se encontró el documento: {DEFAULT_PDF_PATH}"
                        )

                    retriever = get_retriever(
                        pdf_path=str(DEFAULT_PDF_PATH),
                        api_key=api_key,
                        top_k=top_k,
                    )
                    retrieval_query = build_retrieval_query(
                        question=question,
                        messages=st.session_state.messages,
                    )
                    documents = retriever.invoke(retrieval_query)
                    inputs["context"] = documents
                    chain = create_document_chain(
                        model_name=model_name,
                        temperature=temperature,
                        api_key=api_key,
                    )
                else:
                    chain = create_general_chain(
                        model_name=model_name,
                        temperature=temperature,
                        api_key=api_key,
                    )

            placeholder = st.empty()
            answer = ""

            for chunk in chain.stream(inputs):
                content = chunk if isinstance(chunk, str) else chunk.content
                if content:
                    answer += content
                    placeholder.markdown(answer + "▌")

            if not answer:
                answer = "No fue posible generar una respuesta."

            placeholder.markdown(answer)

            sources = []

            if category == "DOCUMENT":
                sources = [
                    {
                        "number": index,
                        "page": (
                            document.metadata["page"] + 1
                            if isinstance(document.metadata.get("page"), int)
                            else "desconocida"
                        ),
                        "content": document.page_content.strip(),
                    }
                    for index, document in enumerate(documents, start=1)
                ]

            render_sources(sources)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

        except Exception as error:
            st.error(f"No se pudo procesar la pregunta: {error}")
