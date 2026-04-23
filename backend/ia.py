import os
from dotenv import load_dotenv
import google.generativeai as genai
import unicodedata

# ------------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------------

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("No se encontró la GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-pro" # Excelente elección para estabilidad

GENERATION_CONFIG = {
    "temperature": 0.3,        # Un poco más baja para máxima fidelidad al texto
    "top_p": 0.95,             # Ayuda a que la selección de palabras sea coherente
    "max_output_tokens": 8192  # El máximo permitido para no cortar respuestas largas
}

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=GENERATION_CONFIG
)

def analisis(full_prompt):
    response = model.generate_content(
        full_prompt,
        stream=False
    )

    # Accede al contenido del primer candidato
    candidate = response.candidates[0]

    # candidate.content.parts es una lista con los textos
    content_text = "".join([part.text for part in candidate.content.parts])

    # Extraer JSON si tu prompt lo envuelve en ```json ... ```
    import json, re
    try:
        match = re.search(r"```json\s*(\{.*\})\s*```", content_text, re.DOTALL)
        if match:
            content_text = match.group(1)
        result_json = json.loads(content_text)
    except Exception as e:
        print("⚠️ No se pudo parsear JSON, devolviendo como texto")
        result_json = {"result": content_text}

    return result_json