# Paso 0 — Importar librerías necesarias
import os
from pathlib import Path
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

def imprimir_resultados(results, titulo="Resultados"):
    print("="*90)
    print(titulo)
    print("="*90)
    # results['ids'], ['documents'], ['distances'] vienen anidados por consulta
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for i, (rid, rdoc, rdist) in enumerate(zip(ids, docs, dists), start=1):
        print(f"Top {i} | ID: {rid:<28} | Distancia: {rdist:.4f}")
        snippet = (rdoc[:180] + "…") if len(rdoc) > 180 else rdoc
        print(f"       Snippet: {snippet}\n")

    print("Nota: menor distancia = mayor similitud semántica.")

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path, override=True)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key or api_key.startswith("tu_api_key"):
    raise RuntimeError(
        "OPENAI_API_KEY no esta configurada con una clave real. "
        f"Revise el archivo {env_path} o la variable de entorno OPENAI_API_KEY."
    )

PERSIST_DIR_OPENAI = "./db_chroma_banco_andino_openai"
os.makedirs(PERSIST_DIR_OPENAI, exist_ok=True)

print("Carpeta de persistencia (OpenAI):", os.path.abspath(PERSIST_DIR_OPENAI))

# Paso 2 — Crear cliente persistente de Chroma para esta base
client_chroma_openai = chromadb.PersistentClient(path=PERSIST_DIR_OPENAI)

# Colección específica para estos embeddings
collection_openai = client_chroma_openai.get_or_create_collection(
    name="banco_andino_openai"
)

# Paso 3 — Configurar el cliente de OpenAI
OPENAI_API_KEY = api_key
client_openai = OpenAI(api_key=OPENAI_API_KEY)

# Paso 4 — Función para generar embeddings usando OpenAI
def embed_openai(textos):
    response = client_openai.embeddings.create(
        input=textos,
        model="text-embedding-3-small"
    )
    return [item.embedding for item in response.data]

documentos_banco_andino = [
    {
        "id": "consumo_clasico",
        "texto": """
Crédito de consumo clásico dirigido a personas asalariadas con al menos 12 meses de estabilidad laboral.
Monto: USD 1,000 a 10,000. Plazo: 6 a 36 meses.
Requisitos: comprobante de ingresos, sin mora mayor a 30 días en los últimos 12 meses.
La cuota mensual no debe superar el 35% del ingreso neto del cliente.
"""
    },
    {
        "id": "nomina_convenio",
        "texto": """
Crédito con descuento por nómina para empleados de empresas con convenio vigente con el banco.
No requiere codeudor. Antigüedad mínima: 6 meses.
Monto máximo: hasta 8 veces el salario neto mensual.
El pago se realiza vía deducción automática en planilla.
"""
    },
    {
        "id": "hipotecario_primera_vivienda",
        "texto": """
Crédito hipotecario para primera vivienda.
Financia hasta el 80% del valor de tasación del inmueble. Plazo hasta 20 años.
Requisitos: enganche mínimo del 20%, sin registros negativos en los últimos 24 meses.
Las obligaciones mensuales totales (incluida la hipoteca) no deben superar el 40% del ingreso familiar neto.
"""
    },
    {
        "id": "pyme_capital_trabajo",
        "texto": """
Crédito PYME Capital de Trabajo para empresas con al menos 2 años de operación formal.
Montos desde USD 5,000 hasta USD 200,000. Plazo hasta 24 meses.
Requiere estados financieros, flujo de caja proyectado y, según el riesgo, garantías reales o fideicomisos.
"""
    },
    {
        "id": "politica_riesgo_general",
        "texto": """
Política general de riesgo de crédito.
Se evalúan estabilidad laboral o del negocio, nivel de endeudamiento, score interno y externo,
y comportamiento histórico con el banco.
Solicitudes con endeudamiento total superior al 45% del ingreso neto se consideran solo de forma excepcional.
No se aprueban créditos con moras activas mayores a 90 días al momento de la evaluación.
"""
    },
]

docs_banco_andino = {
    "ids": [d["id"] for d in documentos_banco_andino],
    "documents": [d["texto"] for d in documentos_banco_andino]
}

# Paso 8 — Embeddings para todos los documentos
embeddings_docs = embed_openai(docs_banco_andino["documents"])

print("Documentos:", len(docs_banco_andino["documents"]))
print("Embeddings generados:", len(embeddings_docs))
print("Dimensión de embedding:", len(embeddings_docs[0]))

# Paso 9 — Insertar documentos + embeddings en Chroma
collection_openai.upsert(
    ids=docs_banco_andino["ids"],
    documents=docs_banco_andino["documents"],
    embeddings=embeddings_docs,
)

print("Documentos almacenados en Chroma con embeddings de OpenAI.")

# Paso 10 — Pregunta de prueba (usted puede cambiarla)
pregunta = "¿Cuál es el monto máximo que puedo solicitar con descuento por nómina?"

embedding_pregunta = embed_openai([pregunta])[0]

resultado_openai = collection_openai.query(
    query_embeddings=[embedding_pregunta],
    n_results=3
)

imprimir_resultados(resultado_openai)

# ================================================================
# Paso 11 — Recuperar los fragmentos relevantes desde resultado_openai
# ================================================================
# De resultado_openai vamos a tomar SOLO los textos de los documentos
# (primer elemento [0] porque Chroma devuelve listas anidadas por consulta)
docs_relevantes = resultado_openai["documents"][0]
print("Fragmentos relevantes recuperados:", len(docs_relevantes))
for i, doc in enumerate(docs_relevantes, start=1):
    print(f"\n--- Fragmento {i} ---")
    print(doc[:400], "..." if len(doc) > 400 else "")  # solo una parte para que no se haga eterno

# ================================================================
# Paso 12 — Construir el contexto que enviaremos al LLM
# ================================================================
# Podemos decidir cuántos fragmentos usar en el contexto (por ejemplo, los 3 primeros)
k_contexto = 3
docs_para_contexto = docs_relevantes[:k_contexto]
# Concatenamos los textos en un solo string, separados por una línea
contexto = "\n\n---\n\n".join(docs_para_contexto)
print("\n=== Contexto que enviaremos al LLM (recortado) ===\n")
print(contexto[:1000], "..." if len(contexto) > 1000 else "")

# ================================================================
# Paso 13 — Definir el prompt para el LLM (sistema + usuario)
# ================================================================
# Mensaje de sistema: quién es el asistente y cómo debe responder
mensaje_sistema = (
    "Eres un asistente virtual del Banco Andino especializado en productos de crédito. "
    "Responde únicamente usando la información del contexto que te proporciono. "
    "Si el contexto no contiene la respuesta, di explícitamente que no tienes información suficiente. "
    "Responde en un máximo de 3 frases, en español claro y conciso."
)
# Mensaje de usuario: mezclamos contexto + pregunta original
mensaje_usuario = (
    "Contexto:\n"
    f"{contexto}\n\n"
    "Pregunta del cliente:\n"
    f"{pregunta}"
)
# ================================================================
# Paso 14 — Llamar al modelo de lenguaje de OpenAI para generar la respuesta
# ================================================================
# Usamos el mismo cliente_openai que configuramos en pasos anteriores
respuesta_chat = client_openai.chat.completions.create(
    model="gpt-4.1-mini",  # puede cambiar a otro modelo compatible
    messages=[
        {"role": "system", "content": mensaje_sistema},
        {"role": "user", "content": mensaje_usuario}
    ]
)

respuesta_final = respuesta_chat.choices[0].message.content

print("\n=== Respuesta final del asistente Banco Andino ===\n")
print(respuesta_final)