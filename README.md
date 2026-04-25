# 📸 Instagram Personality Scraper & AI Analyzer

Este proyecto es una herramienta avanzada de **Arquitectura de Software** que combina Web Scraping, Proxies de Media e Inteligencia Artificial para analizar el comportamiento digital de usuarios en Instagram.

## 🌟 Características principales
- **Extracción de Datos:** Scrapeo automatizado de perfiles, posts, comentarios y engagement mediante `Playwright`.
- **Análisis de Personalidad:** Motor de IA basado en el modelo **Big Five (OCEAN)** utilizando `Google Gemini`.
- **Proxy de Media:** Servidor intermedio para cargar imágenes y videos de Instagram evitando bloqueos de CORS.
- **Dashboard Interactivo:** Interfaz moderna desarrollada con `React` + `Vite`.

---

## 📂 Estructura del Proyecto

```text
SCRAPY-INSTAGRAM/
├── backend/                # Lógica del servidor (FastAPI)
│   ├── fast.py             # Endpoints API y Middlewares (CORS/Proxies)
│   ├── ia.py               # Integración con Google Gemini Pro
│   ├── version3_funcional.py # Core del Scraper (Playwright + Stealth)
│   ├── instagram_state.json # Persistencia de sesión (Cookies)
│   └── resultado.json      # Cache del último análisis
├── frontend/               # Interfaz de usuario (React)
│   ├── src/
│   │   ├── components/     # Componentes: Home.jsx, Information.jsx
│   │   ├── App.jsx         # Enrutamiento y estado global
│   │   └── main.jsx        # Configuración de Vite
│   └── index.html
└── .gitignore              # Archivos excluidos de Git (env, pycache, etc.)

```

🛠️ Requisitos Previos
Python 3.10+
Node.js & npm
Google Gemini API Key (configurada en un archivo .env dentro de backend/)
🚀 Instalación y Configuración
1. Backend (Python)

Entra en la carpeta del backend, activa tu entorno virtual e instala las dependencias:

cd backend
# Instala las librerías necesarias
pip install fastapi uvicorn playwright pydantic google-generativeai python-dotenv requests playwright-stealth

# Instala los navegadores de Playwright
playwright install chromium
Configuración de variables de entorno

Crea un archivo .env dentro de backend/:

GEMINI_API_KEY=tu_api_key_aqui
Ejecución
uvicorn fast:app --reload
2. Frontend (React)

Entra en la carpeta del frontend e instala las dependencias:

cd frontend
npm install
Ejecución
npm run dev
🖥️ Guía de Uso
Inicio: Al abrir la aplicación en http://localhost:5173, verás un formulario.
Entrada: Introduce el username del perfil de Instagram, el número de posts a analizar y el número de comentarios por post.
Proceso: El backend iniciará una instancia de Playwright, extraerá el contenido y lo enviará a Gemini.
Resultados: Se mostrará un dashboard con la información del usuario, sus publicaciones y el análisis detallado de los rasgos de personalidad:
Apertura
Responsabilidad
Extraversión
Amabilidad
Neuroticismo

