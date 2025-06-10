import json
import logging
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
import io
import re
from typing import List, Dict, Any, Optional
import datetime
from datetime import datetime, timedelta
import math

from config.settings import get_settings
from db.models.quiz import *

logger = logging.getLogger(__name__)
settings = get_settings()

# Configurar la API de Google Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

class QuizGenerator:
    """
    Clase para generar quizzes utilizando la API de Google Gemini
    """
    @staticmethod
    def _extract_and_fix_json(response_text: str) -> Dict[str, Any]:
        json_patterns = [
            r"```json\s*([\s\S]*?)\s*```",
            r"```\s*([\s\S]*?)\s*```",
            r"\{[\s\S]*\}"
        ]
        
        extracted_json_str = None
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text)
            if matches:
                for match in matches:
                    try:
                        extracted_json_str = match.strip()
                        json.loads(extracted_json_str)
                        return json.loads(extracted_json_str)
                    except json.JSONDecodeError:
                        continue
                if extracted_json_str:
                    break
        
        extracted_json_str = response_text.strip() # Si no se encuentra con regex, usar el texto completo
        
        try:
            return json.loads(extracted_json_str)
        except json.JSONDecodeError:
            try: # Intentar una corrección simple si falla
                fixed_json = extracted_json_str.replace("'", '"')
                return json.loads(fixed_json)
            except json.JSONDecodeError as e:
                logger.error(f"Error severo al parsear/reparar JSON de Gemini: {e}. Texto original: {response_text[:500]}...")
                raise ValueError("La respuesta de Gemini no contiene un JSON válido y no pudo ser reparada.")

    @staticmethod
    async def create_quiz_from_pdf(pdf_content: bytes, input_data: Dict[str, Any]) -> Dict[str, Any]:
        
        # Validaciones de entrada
        if not input_data or not isinstance(input_data, dict):
            raise ValueError("Los datos de entrada para la generación del quiz son inválidos.")
        
        classroom_id = input_data.get("classroom_id")
        num_question = input_data.get("num_question")
        point_max = input_data.get("point_max") # Nuevo campo
        competences = input_data.get("competences")
        type_question_flags = input_data.get("type_question")

        if not isinstance(classroom_id, int):
            raise ValueError("classroom_id es requerido y debe ser un entero.")
        if not isinstance(num_question, int) or num_question <= 0:
            raise ValueError("num_question es requerido y debe ser un entero positivo.")
        if not isinstance(point_max, int) or point_max <= 0: # Nueva validación
            raise ValueError("point_max es requerido y debe ser un entero positivo.")
        if not isinstance(competences, list):
            raise ValueError("competences es requerido y debe ser una lista.")
        if not isinstance(type_question_flags, dict):
            raise ValueError("type_question es requerido y debe ser un objeto.")

        enabled_question_types = [
            q_type for q_type, enabled in type_question_flags.items() if enabled
        ]

        if not enabled_question_types:
            raise ValueError("Al menos un tipo de pregunta debe estar habilitado (true) en 'type_question'.")

        competences_str = json.dumps(competences, ensure_ascii=False)

        current_time = datetime.now()
        end_time = current_time + timedelta(hours=1) # Quiz de 1 hora de duración

        # Definir el prompt para Gemini con las nuevas restricciones
        prompt = f"""
            Analiza el contenido del documento PDF adjunto en profundidad. Tu tarea es generar un quiz educativo con {num_question} preguntas, siguiendo las siguientes directrices y restricciones estrictas:

            **Directrices Generales:**
            1.  El quiz debe tener un **título** y una **instrucción general** relevante al contenido del PDF.
            2.  **Puntos Totales:** La suma total de los "points" de todas las preguntas generadas debe ser **igual o muy cercana a {point_max}**. Distribuye los puntos de manera que se ajuste a este total.
            3.  **Distribución de Preguntas:**
                -   Genera preguntas únicamente de los tipos habilitados en `type_question`: {', '.join(enabled_question_types)}.
                -   Asegura una **distribución lo más equitativa y uniforme posible** de los {num_question} preguntas entre los **tipos de pregunta habilitados** (textuales, inferenciales, críticas) y también entre los **formatos de respuesta** (**"base_text"** para respuestas de texto libre, y **"base_multiple_option"** para opción múltiple).
                -   Si un tipo de pregunta o formato de respuesta no está habilitado, **no lo uses**.
            4.  **Combinación de Competencias:** Para cada pregunta, es **IMPERATIVO** que selecciones **múltiples competencias** (idealmente 2 o más si es relevante y posible) de la lista proporcionada. La selección debe basarse en la afinidad fuerte de la pregunta con la 'description' y 'name' de **todas las competencias seleccionadas**. Busca conectar conceptos en la pregunta con varias áreas de competencia.

            **Estructura de Cada Pregunta:**
            Para cada pregunta, incluye los siguientes campos exactos y con sus tipos de datos correctos:
            -   **"statement"**: El enunciado claro y conciso de la pregunta.
            -   **"answer_correct"**:
                -   Si `answer_base.type` es "base_text", esta es la respuesta completa y correcta a la pregunta abierta.
                -   Si `answer_base.type` es "base_multiple_option", esta debe ser **exactamente uno de los textos de las opciones proporcionadas** en la lista `options`.
            -   **"points"**: Un valor numérico entero y positivo para la pregunta. La suma de estos puntos debe ajustarse a `point_max`.
            -   **"answer_base"**: Un objeto JSON con los detalles del formato de respuesta:
                -   **"type"**: Un string que debe ser **"base_text"** o **"base_multiple_option"**.
                -   **"options"**: (SOLO si "type" es "base_multiple_option") Una lista de strings que contienen las posibles opciones de respuesta. Debe haber **entre 3 y 5 opciones**, y una de ellas debe ser la `answer_correct`.
            -   **"competences_id"**: Una **lista de números enteros** (IDs) de las competencias relevantes para la pregunta. Estos IDs deben ser tomados **EXCLUSIVAMENTE** del listado de competencias que te proporciono.

            **Listado de Competencias Disponibles:**
            {competences_str}

            **Formato de Salida Requerido (JSON Exacto):**
            Devuelve **SOLO un objeto JSON** que siga este formato exacto, sin ningún texto adicional, explicaciones, o bloques de código que no sean el propio JSON, ni antes ni después.

            ```json
            {{
                "classroom_id": {classroom_id},
                "title": "Un título descriptivo para el quiz",
                "instruction": "Instrucciones claras para los estudiantes sobre cómo completar el quiz.",
                "start_time": "{current_time.isoformat()}Z",
                "end_time": "{end_time.isoformat()}Z",
                "questions": [
                    {{
                        "statement": "Enunciado de la primera pregunta, combinando tipos y competencias.",
                        "answer_correct": "Respuesta correcta para esta pregunta.",
                        "points": 10,
                        "answer_base": {{
                            "type": "base_text"
                        }},
                        "competences_id": [1, 2]
                    }},
                    {{
                        "statement": "Pregunta de opción múltiple con enfoque crítico y varias competencias.",
                        "answer_correct": "Opción Correcta A",
                        "points": 10,
                        "answer_base": {{
                            "type": "base_multiple_option",
                            "options": [
                                "Opción Correcta A",
                                "Opción Incorrecta B",
                                "Opción Incorrecta C"
                            ]
                        }},
                        "competences_id": [2]
                    }}
                    // ... más preguntas hasta alcanzar num_question y sume point_max
                ]
            }}
            ```
            Asegúrate de que `start_time` y `end_time` sean fechas y horas ISO 8601 válidas en UTC (terminadas en 'Z'), reflejando el momento actual y una hora después, respectivamente. La calidad de las preguntas, la correcta asignación de puntos para sumar {point_max} y la combinación de competencias es fundamental.
            """

        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            generation_config={"temperature": 0.7, "response_mime_type": "application/json"}
        )
        
        contents = [
            prompt, # Usamos el prompt actualizado
            {"mime_type": "application/pdf", "data": pdf_content}
        ]

        try:
            response = await model.generate_content_async(contents, request_options={"timeout": 600})
            response_text = response.text
            
            generated_quiz_data = QuizGenerator._extract_and_fix_json(response_text)
            
            # Asegurar que classroom_id del output coincida con el input
            generated_quiz_data["classroom_id"] = classroom_id
            
            # --- Lógica de ajuste post-generación (si Gemini no cumple exactamente) ---
            # Aunque Gemini debería seguir las instrucciones, esto es una capa de seguridad.
            
            # Ajustar número de preguntas si es necesario
            if len(generated_quiz_data.get("questions", [])) < num_question:
                for _ in range(num_question - len(generated_quiz_data.get("questions", []))):
                    generated_quiz_data["questions"].append({
                        "statement": "Pregunta de relleno por ajuste de cantidad.",
                        "answer_correct": "Respuesta.",
                        "points": 1, # Puntos bajos para no exceder point_max
                        "answer_base": {"type": "base_text"},
                        "competences_id": []
                    })
            generated_quiz_data["questions"] = generated_quiz_data["questions"][:num_question]

            # Ajustar puntos para que la suma no exceda point_max
            current_total_points = sum(q.get("points", 0) for q in generated_quiz_data["questions"])
            if current_total_points > point_max:
                # Si los puntos exceden, se redistribuyen proporcionalmente o se reducen.
                # Una estrategia simple es reducir los puntos de cada pregunta de forma uniforme.
                reduction_factor = point_max / current_total_points
                for q in generated_quiz_data["questions"]:
                    q["points"] = max(1, round(q.get("points", 1) * reduction_factor)) # Mínimo 1 punto

            # Re-validar la estructura para asegurar que cumple con el schema de salida
            output_questions = []
            for q in generated_quiz_data.get("questions", []):
                q_type = q["answer_base"]["type"]
                q_options = q["answer_base"].get("options", []) if q_type == "base_multiple_option" else []
                
                output_questions.append({
                    "statement": q["statement"],
                    "answer_correct": q["answer_correct"],
                    "points": q["points"],
                    "answer_base": {
                        "type": q_type,
                        **({"options": q_options} if q_options else {})
                    },
                    "competences_id": q.get("competences_id", [])
                })

            return {
                "classroom_id": generated_quiz_data.get("classroom_id", classroom_id),
                "title": generated_quiz_data.get("title", "Quiz Generado"),
                "instruction": generated_quiz_data.get("instruction", "Responde las siguientes preguntas basadas en el documento."),
                "start_time": generated_quiz_data.get("start_time", current_time.isoformat() + "Z"),
                "end_time": generated_quiz_data.get("end_time", end_time.isoformat() + "Z"),
                "questions": output_questions
            }

        except Exception as e:
            logger.error(f"Error al generar quiz desde PDF con IA: {str(e)}")
            raise ValueError(f"Error al procesar el PDF o generar el quiz: {str(e)}")
        
    @staticmethod
    async def create_quiz_from_text(input_data: Dict[str, Any]) -> Dict[str, Any]:
        
        # Validaciones de entrada
        if not input_data or not isinstance(input_data, dict):
            raise ValueError("Los datos de entrada para la generación del quiz son inválidos.")
        
        classroom_id = input_data.get("classroom_id")
        num_question = input_data.get("num_question")
        point_max = input_data.get("point_max") # Nuevo campo
        competences = input_data.get("competences")
        type_question_flags = input_data.get("type_question")
        text=input_data.get("text")

        if not isinstance(classroom_id, int):
            raise ValueError("classroom_id es requerido y debe ser un entero.")
        if not isinstance(num_question, int) or num_question <= 0:
            raise ValueError("num_question es requerido y debe ser un entero positivo.")
        if not isinstance(point_max, int) or point_max <= 0: # Nueva validación
            raise ValueError("point_max es requerido y debe ser un entero positivo.")
        if not isinstance(competences, list):
            raise ValueError("competences es requerido y debe ser una lista.")
        if not isinstance(type_question_flags, dict):
            raise ValueError("type_question es requerido y debe ser un objeto.")

        enabled_question_types = [
            q_type for q_type, enabled in type_question_flags.items() if enabled
        ]

        if not enabled_question_types:
            raise ValueError("Al menos un tipo de pregunta debe estar habilitado (true) en 'type_question'.")

        competences_str = json.dumps(competences, ensure_ascii=False)

        current_time = datetime.now()
        end_time = current_time + timedelta(hours=1) # Quiz de 1 hora de duración

        # Definir el prompt para Gemini con las nuevas restricciones
        prompt = f"""
            Analiza el contenido del documento PDF adjunto en profundidad. Tu tarea es generar un quiz educativo con {num_question} preguntas, siguiendo las siguientes directrices y restricciones estrictas:
            Lo que usaras como resticciones o tema principal para elaboar el quiz es {text}
            **Directrices Generales:**
            1.  El quiz debe tener un **título** y una **instrucción general** relevante al contenido del PDF.
            2.  **Puntos Totales:** La suma total de los "points" de todas las preguntas generadas debe ser **igual o muy cercana a {point_max}**. Distribuye los puntos de manera que se ajuste a este total.
            3.  **Distribución de Preguntas:**
                -   Genera preguntas únicamente de los tipos habilitados en `type_question`: {', '.join(enabled_question_types)}.
                -   Asegura una **distribución lo más equitativa y uniforme posible** de los {num_question} preguntas entre los **tipos de pregunta habilitados** (textuales, inferenciales, críticas) y también entre los **formatos de respuesta** (**"base_text"** para respuestas de texto libre, y **"base_multiple_option"** para opción múltiple).
                -   Si un tipo de pregunta o formato de respuesta no está habilitado, **no lo uses**.
            4.  **Combinación de Competencias:** Para cada pregunta, es **IMPERATIVO** que selecciones **múltiples competencias** (idealmente 2 o más si es relevante y posible) de la lista proporcionada. La selección debe basarse en la afinidad fuerte de la pregunta con la 'description' y 'name' de **todas las competencias seleccionadas**. Busca conectar conceptos en la pregunta con varias áreas de competencia.

            **Estructura de Cada Pregunta:**
            Para cada pregunta, incluye los siguientes campos exactos y con sus tipos de datos correctos:
            -   **"statement"**: El enunciado claro y conciso de la pregunta.
            -   **"answer_correct"**:
                -   Si `answer_base.type` es "base_text", esta es la respuesta completa y correcta a la pregunta abierta.
                -   Si `answer_base.type` es "base_multiple_option", esta debe ser **exactamente uno de los textos de las opciones proporcionadas** en la lista `options`.
            -   **"points"**: Un valor numérico entero y positivo para la pregunta. La suma de estos puntos debe ajustarse a `point_max`.
            -   **"answer_base"**: Un objeto JSON con los detalles del formato de respuesta:
                -   **"type"**: Un string que debe ser **"base_text"** o **"base_multiple_option"**.
                -   **"options"**: (SOLO si "type" es "base_multiple_option") Una lista de strings que contienen las posibles opciones de respuesta. Debe haber **entre 3 y 5 opciones**, y una de ellas debe ser la `answer_correct`.
            -   **"competences_id"**: Una **lista de números enteros** (IDs) de las competencias relevantes para la pregunta. Estos IDs deben ser tomados **EXCLUSIVAMENTE** del listado de competencias que te proporciono.

            **Listado de Competencias Disponibles:**
            {competences_str}

            **Formato de Salida Requerido (JSON Exacto):**
            Devuelve **SOLO un objeto JSON** que siga este formato exacto, sin ningún texto adicional, explicaciones, o bloques de código que no sean el propio JSON, ni antes ni después.

            ```json
            {{
                "classroom_id": {classroom_id},
                "title": "Un título descriptivo para el quiz",
                "instruction": "Instrucciones claras para los estudiantes sobre cómo completar el quiz.",
                "start_time": "{current_time.isoformat()}Z",
                "end_time": "{end_time.isoformat()}Z",
                "questions": [
                    {{
                        "statement": "Enunciado de la primera pregunta, combinando tipos y competencias.",
                        "answer_correct": "Respuesta correcta para esta pregunta.",
                        "points": 10,
                        "answer_base": {{
                            "type": "base_text"
                        }},
                        "competences_id": [1, 2]
                    }},
                    {{
                        "statement": "Pregunta de opción múltiple con enfoque crítico y varias competencias.",
                        "answer_correct": "Opción Correcta A",
                        "points": 10,
                        "answer_base": {{
                            "type": "base_multiple_option",
                            "options": [
                                "Opción Correcta A",
                                "Opción Incorrecta B",
                                "Opción Incorrecta C"
                            ]
                        }},
                        "competences_id": [2]
                    }}
                    // ... más preguntas hasta alcanzar num_question y sume point_max
                ]
            }}
            ```
            Asegúrate de que `start_time` y `end_time` sean fechas y horas ISO 8601 válidas en UTC (terminadas en 'Z'), reflejando el momento actual y una hora después, respectivamente. La calidad de las preguntas, la correcta asignación de puntos para sumar {point_max} y la combinación de competencias es fundamental.
            """

        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            generation_config={"temperature": 0.7, "response_mime_type": "application/json"}
        )
        
        contents = [
            prompt
        ]

        try:
            response = await model.generate_content_async(contents, request_options={"timeout": 600})
            response_text = response.text
            
            generated_quiz_data = QuizGenerator._extract_and_fix_json(response_text)
            
            # Asegurar que classroom_id del output coincida con el input
            generated_quiz_data["classroom_id"] = classroom_id
            
            # --- Lógica de ajuste post-generación (si Gemini no cumple exactamente) ---
            # Aunque Gemini debería seguir las instrucciones, esto es una capa de seguridad.
            
            # Ajustar número de preguntas si es necesario
            if len(generated_quiz_data.get("questions", [])) < num_question:
                for _ in range(num_question - len(generated_quiz_data.get("questions", []))):
                    generated_quiz_data["questions"].append({
                        "statement": "Pregunta de relleno por ajuste de cantidad.",
                        "answer_correct": "Respuesta.",
                        "points": 1, # Puntos bajos para no exceder point_max
                        "answer_base": {"type": "base_text"},
                        "competences_id": []
                    })
            generated_quiz_data["questions"] = generated_quiz_data["questions"][:num_question]

            # Ajustar puntos para que la suma no exceda point_max
            current_total_points = sum(q.get("points", 0) for q in generated_quiz_data["questions"])
            if current_total_points > point_max:
                # Si los puntos exceden, se redistribuyen proporcionalmente o se reducen.
                # Una estrategia simple es reducir los puntos de cada pregunta de forma uniforme.
                reduction_factor = point_max / current_total_points
                for q in generated_quiz_data["questions"]:
                    q["points"] = max(1, round(q.get("points", 1) * reduction_factor)) # Mínimo 1 punto

            # Re-validar la estructura para asegurar que cumple con el schema de salida
            output_questions = []
            for q in generated_quiz_data.get("questions", []):
                q_type = q["answer_base"]["type"]
                q_options = q["answer_base"].get("options", []) if q_type == "base_multiple_option" else []
                
                output_questions.append({
                    "statement": q["statement"],
                    "answer_correct": q["answer_correct"],
                    "points": q["points"],
                    "answer_base": {
                        "type": q_type,
                        **({"options": q_options} if q_options else {})
                    },
                    "competences_id": q.get("competences_id", [])
                })

            return {
                "classroom_id": generated_quiz_data.get("classroom_id", classroom_id),
                "title": generated_quiz_data.get("title", "Quiz Generado"),
                "instruction": generated_quiz_data.get("instruction", "Responde las siguientes preguntas basadas en el documento."),
                "start_time": generated_quiz_data.get("start_time", current_time.isoformat() + "Z"),
                "end_time": generated_quiz_data.get("end_time", end_time.isoformat() + "Z"),
                "questions": output_questions
            }

        except Exception as e:
            logger.error(f"Error al generar quiz desde PDF con IA: {str(e)}")
            raise ValueError(f"Error al procesar el PDF o generar el quiz: {str(e)}")

    
#     @staticmethod
#     def _extract_and_fix_json(response_text: str) -> Dict[str, Any]:
#         """
#         Extrae y corrige el JSON de la respuesta del modelo.
        
#         Args:
#             response_text: Texto de respuesta del modelo
            
#         Returns:
#             Diccionario con los datos del JSON
            
#         Raises:
#             ValueError: Si no se puede extraer un JSON válido
#         """
#         # Intentar encontrar el JSON usando patrones comunes
#         json_patterns = [
#             r"```json\s*([\s\S]*?)\s*```",  # Markdown JSON block
#             r"```\s*([\s\S]*?)\s*```",       # Any Markdown block
#             r"\{[\s\S]*\}"                   # Just find JSON object pattern
#         ]
        
#         extracted_json = None
#         for pattern in json_patterns:
#             matches = re.findall(pattern, response_text)
#             if matches:
#                 # Usar la primera coincidencia que parece un JSON válido
#                 for match in matches:
#                     try:
#                         # Intentar parsear para verificar
#                         extracted_json = match.strip()
#                         json.loads(extracted_json)
#                         logger.info("JSON extraído correctamente mediante patrón regex")
#                         break
#                     except json.JSONDecodeError:
#                         continue
#                 if extracted_json:
#                     break
        
#         # Si no se encuentra con regex, usar el texto completo
#         if not extracted_json:
#             extracted_json = response_text.strip()
            
#         # Intentar parsear el JSON tal como está
#         try:
#             return json.loads(extracted_json)
#         except json.JSONDecodeError as e:
#             logger.warning(f"Error al parsear JSON: {e}")
            
#             # Intentar corregir problemas comunes de JSON
#             try:
#                 # 1. Comillas no cerradas - usar regex más agresivo
#                 fixed_json = re.sub(r'([^\\])"([^"]*?)(?=[,}\]])', r'\1"\2"', extracted_json)
#                 # 2. Comillas simples a dobles
#                 fixed_json = fixed_json.replace("'", '"')
#                 # 3. Intentar cerrar llaves/corchetes si están incompletos
#                 if fixed_json.count('{') > fixed_json.count('}'):
#                     fixed_json += '}' * (fixed_json.count('{') - fixed_json.count('}'))
#                 if fixed_json.count('[') > fixed_json.count(']'):
#                     fixed_json += ']' * (fixed_json.count('[') - fixed_json.count(']'))
                    
#                 return json.loads(fixed_json)
#             except json.JSONDecodeError:
#                 # Si todavía falla, buscar cualquier objeto JSON completo
#                 try:
#                     json_obj_match = re.search(r'(\{(?:[^{}]|(?1))*\})', extracted_json)
#                     if json_obj_match:
#                         return json.loads(json_obj_match.group(0))
#                 except Exception:
#                     pass
                
#                 # Si aún falla, crear un JSON simple con el título y una pregunta
#                 logger.error(f"No se pudo reparar el JSON. Creando un JSON mínimo de respaldo")
#                 return {
#                     "quiz": {
#                         "title": "Quiz generado",
#                         "instructions": "Responde las siguientes preguntas"
#                     },
#                     "questions": [
#                         {
#                             "statement": "Explica el concepto principal del tema",
#                             "question_type": "text",
#                             "answer_correct": None,
#                             "points": 1,
#                             "options": []
#                         }
#                     ]
#                 }
    
#     @staticmethod
#     async def create_quiz_from_text(
#         db: AsyncSession,
#         title: str,
#         description: str,
#         id_classroom: int,
#         id_teacher: int,
#         num_questions: int = None
#     ) -> Quiz:
#         """
#         Crea un quiz a partir de una descripción de texto utilizando IA
        
#         Args:
#             db: Sesión de base de datos
#             title: Título del quiz
#             description: Descripción o instrucciones del quiz
#             id_classroom: ID del aula
#             id_teacher: ID del profesor
#             num_questions: Número de preguntas a generar
            
#         Returns:
#             Objeto Quiz creado
#         """
#         # Usar el número de preguntas predeterminado si no se especifica
#         if num_questions is None:
#             num_questions = settings.DEFAULT_NUM_QUESTIONS
        
#         # Limitar el número de preguntas
#         num_questions = min(max(num_questions, settings.MIN_NUM_QUESTIONS), settings.MAX_NUM_QUESTIONS)
        
#         # Crear el prompt para la IA
#         prompt = f"""
#         Genera {num_questions} preguntas para un quiz educativo sobre el siguiente tema:
        
#         Título: {title}
#         Descripción: {description}
        
#         Por cada pregunta, incluye:
#         1. Enunciado de la pregunta
#         2. Tipo de pregunta (text para respuesta abierta, multiple_choice para opción múltiple)
#         3. Respuesta correcta (para preguntas abiertas)
#         4. Opciones (para preguntas de opción múltiple, marca cuál es la correcta)
#         5. Puntos (valor numérico de la pregunta)
        
#         Devuelve SOLO un objeto JSON con este formato exacto, sin explicaciones adicionales:
#         {{
#             "quiz": {{
#                 "title": "{title}",
#                 "instructions": "Instrucciones generadas para el quiz"
#             }},
#             "questions": [
#                 {{
#                     "statement": "Enunciado de la pregunta 1",
#                     "question_type": "text o multiple_choice",
#                     "answer_correct": "Respuesta correcta (para text)",
#                     "points": 1,
#                     "options": [
#                         {{"option_text": "Opción 1", "is_correct": true/false}},
#                         {{"option_text": "Opción 2", "is_correct": true/false}},
#                         ...
#                     ]
#                 }},
#                 ...
#             ]
#         }}
#         """
        
#         try:
#             # Crear el modelo Gemini con configuración para estructurar mejor las respuestas
#             model = genai.GenerativeModel(
#                 settings.GEMINI_MODEL,
#                 generation_config={"temperature": 0.2}  # Más determinista
#             )
            
#             # Generar el contenido
#             response = model.generate_content(prompt)
            
#             # Procesar la respuesta
#             if not response.text:
#                 raise ValueError("No se generó contenido")
            
#             # Extraer el JSON de la respuesta con manejo mejorado de errores
#             content = QuizGenerator._extract_and_fix_json(response.text)
            
#             # Crear el quiz en la base de datos
#             quiz = Quiz(
#                 title=content["quiz"]["title"],
#                 instructions=content["quiz"].get("instructions", "Contesta las siguientes preguntas"),
#                 id_classroom=id_classroom,
#                 id_teacher=id_teacher
#             )
            
#             db.add(quiz)
#             await db.flush()
            
#             # Crear las preguntas
#             for q_data in content["questions"]:
#                 question = Question(
#                     quiz_id=quiz.id,
#                     statement=q_data["statement"],
#                     answer_correct=q_data.get("answer_correct"),
#                     points=q_data.get("points", 1),
#                     question_type=q_data.get("question_type", "text"),
#                     created_at=datetime.datetime.now()
#                 )
                
#                 db.add(question)
#                 await db.flush()
                
#                 # Si es de opción múltiple, crear las opciones
#                 if question.question_type == "multiple_choice" and "options" in q_data:
#                     for opt_data in q_data["options"]:
#                         option = QuestionOption(
#                             question_id=question.id,
#                             option_text=opt_data["option_text"],
#                             is_correct=1 if opt_data.get("is_correct", False) else 0
#                         )
#                         db.add(option)
            
#             return quiz
            
#         except Exception as e:
#             logger.error(f"Error generando quiz con IA: {str(e)}")
#             raise ValueError(f"Error al generar el quiz: {str(e)}")
    
#     @staticmethod
#     async def create_quiz_from_pdf(
#         db: AsyncSession,
#         title: str,
#         pdf_content: bytes,
#         id_classroom: int,
#         id_teacher: int,
#         num_questions: int = None,
#         description: str = None
#     ) -> Quiz:
#         """
#         Crea un quiz a partir del contenido de un PDF utilizando IA
        
#         Args:
#             db: Sesión de base de datos
#             title: Título del quiz
#             pdf_content: Contenido del archivo PDF en bytes
#             id_classroom: ID del aula
#             id_teacher: ID del profesor
#             num_questions: Número de preguntas a generar
#             description: Descripción opcional sobre qué tipo de preguntas generar
        
#         Returns:
#             Objeto Quiz creado
#         """
#         try:
#             # Usar el número de preguntas predeterminado si no se especifica
#             if num_questions is None:
#                 num_questions = settings.DEFAULT_NUM_QUESTIONS
            
#             # Limitar el número de preguntas
#             num_questions = min(max(num_questions, settings.MIN_NUM_QUESTIONS), settings.MAX_NUM_QUESTIONS)
            
#             # Crear el prompt para la IA
#             prompt = f"""
#             Analiza el PDF adjunto y genera {num_questions} preguntas para un quiz educativo sobre su contenido.
            
#             Título del quiz: {title}
#             {f"Enfoque para las preguntas: {description}" if description else ""}
            
#             Por cada pregunta, incluye:
#             1. Enunciado de la pregunta
#             2. Tipo de pregunta (text para respuesta abierta, multiple_choice para opción múltiple)
#             3. Respuesta correcta (para preguntas abiertas)
#             4. Opciones (para preguntas de opción múltiple, marca cuál es la correcta)
#             5. Puntos (valor numérico de la pregunta)
            
#             Devuelve SOLO un objeto JSON con este formato exacto, sin explicaciones adicionales:
#             {{
#                 "quiz": {{
#                     "title": "{title}",
#                     "instructions": "Instrucciones generadas para el quiz"
#                 }},
#                 "questions": [
#                     {{
#                         "statement": "Enunciado de la pregunta 1",
#                         "question_type": "text o multiple_choice",
#                         "answer_correct": "Respuesta correcta (para text)",
#                         "points": 1,
#                         "options": [
#                             {{"option_text": "Opción 1", "is_correct": true/false}},
#                             {{"option_text": "Opción 2", "is_correct": true/false}},
#                             ...
#                         ]
#                     }},
#                     ...
#                 ]
#             }}
#             """
            
#             # Crear el modelo Gemini con configuración para estructurar mejor las respuestas
#             model = genai.GenerativeModel(
#                 settings.GEMINI_MODEL,
#                 generation_config={"temperature": 0.2}  # Más determinista
#             )
            
#             # Crear el contenido multimodal - texto + PDF
#             content = [
#                 prompt,
#                 {"mime_type": "application/pdf", "data": pdf_content}
#             ]
            
#             # Generar el contenido enviando el PDF directamente
#             response = model.generate_content(content)
            
#             # Procesar la respuesta
#             if not response.text:
#                 raise ValueError("No se generó contenido")
            
#             # Extraer el JSON de la respuesta con manejo mejorado de errores
#             content = QuizGenerator._extract_and_fix_json(response.text)
            
#             # Crear el quiz en la base de datos
#             quiz = Quiz(
#                 title=content["quiz"]["title"],
#                 instructions=content["quiz"].get("instructions", "Contesta las siguientes preguntas sobre el documento"),
#                 id_classroom=id_classroom,
#                 id_teacher=id_teacher
#             )
            
#             db.add(quiz)
#             await db.flush()
            
#             # Crear las preguntas
#             for q_data in content["questions"]:
#                 question = Question(
#                     quiz_id=quiz.id,
#                     statement=q_data["statement"],
#                     answer_correct=q_data.get("answer_correct"),
#                     points=q_data.get("points", 1),
#                     question_type=q_data.get("question_type", "text"),
#                     created_at=datetime.datetime.now()
#                 )
                
#                 db.add(question)
#                 await db.flush()
                
#                 # Si es de opción múltiple, crear las opciones
#                 if question.question_type == "multiple_choice" and "options" in q_data:
#                     for opt_data in q_data["options"]:
#                         option = QuestionOption(
#                             question_id=question.id,
#                             option_text=opt_data["option_text"],
#                             is_correct=1 if opt_data.get("is_correct", False) else 0
#                         )
#                         db.add(option)
            
#             return quiz
            
#         except Exception as e:
#             logger.error(f"Error generando quiz desde PDF con IA: {str(e)}")
#             raise ValueError(f"Error al procesar el PDF: {str(e)}")
