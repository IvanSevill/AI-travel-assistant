# 🗺️ AI Travel Itinerary Planner (Gemini & Streamlit)

Esta es una aplicación web interactiva desarrollada con **Streamlit** que genera itinerarios de viaje detallados día por día. Utiliza el modelo **Google Gemini** para la planificación, la validación estricta de la salida con Pydantic/JSON Schema, y se integra con las APIs de Google para enriquecer la experiencia.

## ✨ Características Principales

* **Planificación con IA:** Genera itinerarios detallados utilizando el modelo **Gemini** (vía `response_schema` forzada).
* **Validación Estricta:** Implementación de modelos de datos (Pydantic) para asegurar que la salida JSON de la IA es siempre válida.
* **Integración de Herramientas (Tools):** Utiliza las APIs de Google Maps/Places para obtener detalles en tiempo real de ubicaciones y calcular tiempos de viaje entre actividades.
* **Audio Resumen (TTS):** Genera resúmenes de audio de alta calidad para cada día utilizando la API de **Google Cloud Text-to-Speech (TTS)**.
* **UI Dinámica:** Interfaz de usuario intuitiva con Streamlit, incluyendo pestañas por día y reproductor de audio.

## ⚙️ Tecnologías y Requisitos

La aplicación requiere la configuración de varias claves de API de Google para funcionar completamente.

### Requisitos Locales

* **Python 3.10+**
* **Git**

### Claves de API Necesarias

Debes obtener y configurar las siguientes claves:

1.  **GEMINI_API_KEY:** Para la planificación de itinerarios y la generación de texto del resumen diario (`agents.py`).
2.  **GOOGLE_MAPS_API_KEY:** Para las funciones de `get_location_details` y `calculate_travel_time` (`tools.py`).
3.  **GOOGLE CLOUD CREDENTIALS:** Para usar la API de Text-to-Speech (TTS). Esto requiere configurar la **API de Cloud Text-to-Speech** en Google Cloud Platform y la autenticación de la cuenta de servicio (típicamente a través de `gcloud auth application-default login`).

---

## 📦 Instalación y Configuración

### 1. Clonar el Repositorio

Abre tu terminal o CMD:

```bash
git clone [https://github.com/tu-usuario/nombre-del-repositorio.git](https://github.com/tu-usuario/nombre-del-repositorio.git)
cd nombre-del-repositorio