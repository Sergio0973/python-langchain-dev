import chromadb
def imprimir_resultados(resultados, titulo="Resultados"):
    print("\n" + "=" * 90)
    print(titulo)
    print("=" * 90)

    docs = resultados.get("documents", [[]])[0]
    ids = resultados.get("ids", [[]])[0]
    dists = resultados.get("distances", [[]])[0]

    if not docs:
        print("Sin resultados.")
        return

    for rank, (doc_id, doc_texto, dist) in enumerate(
        zip(ids, docs, dists), start=1
    ):
        snippet = doc_texto.strip().replace("\n", " ")

        if len(snippet) > 220:
            snippet = snippet[:220] + "..."

        print(f"Top {rank} | ID: {doc_id:<26} | Distancia: {dist:.4f}")
        print(f"       Snippet: {snippet}\n")

    print("Nota: menor distancia = mayor similitud semántica.")

client = chromadb.Client()

collection = client.get_or_create_collection(
    name="banco_andino_politicas_credito",
    metadata={"tema": "politicas_credito", "idioma": "es"}
)
# print(collection)
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
ids = [doc["id"] for doc in documentos_banco_andino]
texts = [doc["texto"] for doc in documentos_banco_andino]

collection.add(
    ids=ids,
    documents=texts
)

query_1 = "Cual es el porcentaje máximo del ingreso que puede destinarse a la cuota mensual?"

res_query_1 = collection.query(
    query_texts = [query_1],
    n_results=3
)
imprimir_resultados(res_query_1,titulo="Consulta relacionada - Cuota maxima vs. Ingreso")

consulta_rel_2 = "¿Cuál es el monto máximo que puedo solicitar con descuento por nómina?"
res_rel_2 = collection.query(
    query_texts=[consulta_rel_2],
    n_results=3
)
imprimir_resultados(res_rel_2, titulo="(6B) Consulta relacionada — Monto máximo por nómina")

consulta_off = "¿Cuántas unidades de zapatillas vendimos en la tienda el mes pasado?"
res_off = collection.query(
    query_texts=[consulta_off],
    n_results=3
)
imprimir_resultados(res_off, titulo="(6C) Consulta no relacionada — Retail")