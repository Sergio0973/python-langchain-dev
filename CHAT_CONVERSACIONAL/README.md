# Chat conversacional RAG

Aplicación Streamlit que responde preguntas sobre las bases y condiciones de
la promoción de Nestlé mediante OpenAI, embeddings y Chroma.

## Ejecución local

1. Crea el archivo de configuración:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Agrega tu `OPENAI_API_KEY` en `.env`.

3. Instala las dependencias:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Inicia la aplicación:

   ```powershell
   streamlit run app.py
   ```

La interfaz estará disponible en `http://localhost:8501`.

## Ejecución con Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

## Funcionamiento

- El PDF se carga desde `data/basesycondicionesnestle.pdf`.
- Los fragmentos utilizan `chunk_size=1000` y `chunk_overlap=200`.
- Los embeddings se guardan en `storage/chroma`.
- El historial vive en la sesión de Streamlit.
- Cada respuesta permite consultar los fragmentos y páginas recuperadas.

