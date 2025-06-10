# MS-Quiz

Microservicio para la generación y gestión de quizzes educativos utilizando Google Gemini.

## Configuración

Para utilizar este servicio, asegúrate de configurar las siguientes variables de entorno:

```
GOOGLE_API_KEY=tu_clave_de_api_de_google
GEMINI_MODEL=gemini-2.0-flash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/quizdb
```

## Características

- Generación automática de quizzes a partir de texto o PDF utilizando Google Gemini 2.0 Flash
- Gestión de quizzes, preguntas y respuestas de estudiantes
- API REST para integración con frontend

## Pruebas

Para ejecutar las pruebas de los endpoints:

```bash
# Crea un entorno virtual
python -m venv venv

# Ingresa al entorno virtual
venv\Scripts\activate

# Instala las dependencias necesarias
pip install -r requirements.txt

# Asegúrate que el servicio esté en ejecución
python scripts/test_endpoints.py
```
