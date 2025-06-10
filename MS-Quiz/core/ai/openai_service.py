import openai
from typing import List, Dict, Any, Optional
import json
import logging

from config.settings import get_settings

settings = get_settings()
openai.api_key = settings.OPENAI_API_KEY

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Servicio para interactuar con la API de OpenAI para generar preguntas
    """
    
    @staticmethod
    async def generate_questions_from_text(
        topic: str, 
        description: str, 
        num_questions: int = 5, 
        include_multiple_choice: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Genera preguntas sobre un tema específico usando OpenAI
        
        Args:
            topic: Título o tema principal
            description: Descripción del tema
            num_questions: Número de preguntas a generar
            include_multiple_choice: Si debe incluir preguntas de opción múltiple
            
        Returns:
            Lista de preguntas generadas con sus respuestas
        """
        try:
            # Plantilla para el prompt
            prompt = f"""
            Genera {num_questions} preguntas sobre el siguiente tema: {topic}
            
            Descripción del tema: {description}
            
            Las preguntas deben incluir tanto preguntas literales como críticas. Aproximadamente el 60% deben ser
            preguntas que fomenten el pensamiento crítico y análisis, no solo memorización.
            
            {"Incluye al menos 2 preguntas de opción múltiple con 4 opciones cada una, indicando cuál es la correcta." if include_multiple_choice else ""}
            
            Para cada pregunta, proporciona:
            1. El enunciado de la pregunta
            2. El tipo de pregunta (text o multiple_choice)
            3. La respuesta correcta
            4. Para preguntas de opción múltiple, las opciones disponibles
            5. El puntaje sugerido (de 1 a 5, siendo 5 las preguntas más difíciles)
            
            Formatea tu respuesta como un objeto JSON con una lista de preguntas.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un asistente educativo especializado en crear preguntas para evaluaciones de comunicación."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                json_str = content.strip()
                
            questions_data = json.loads(json_str)
            
            if isinstance(questions_data, dict) and "questions" in questions_data:
                return questions_data["questions"]
            elif isinstance(questions_data, list):
                return questions_data
            else:
                raise ValueError("Formato inesperado en la respuesta de OpenAI")
            
        except Exception as e:
            logger.error(f"Error generando preguntas con OpenAI: {str(e)}")
            raise

    @staticmethod
    async def generate_questions_from_pdf_content(
        topic: str,
        pdf_content: str,
        num_questions: int = 5,
        include_multiple_choice: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Genera preguntas basadas en el contenido de un PDF usando OpenAI
        
        Args:
            topic: Título o tema principal
            pdf_content: Contenido extraído del PDF
            num_questions: Número de preguntas a generar
            include_multiple_choice: Si debe incluir preguntas de opción múltiple
            
        Returns:
            Lista de preguntas generadas con sus respuestas
        """
        try:
            # Limitar el contenido del PDF para no exceder tokens
            max_content_length = 6000
            if len(pdf_content) > max_content_length:
                pdf_content = pdf_content[:max_content_length] + "... (contenido truncado)"
            
            # Plantilla para el prompt
            prompt = f"""
            Genera {num_questions} preguntas basadas en el siguiente contenido extraído de un PDF sobre el tema: {topic}
            
            Contenido del PDF:
            {pdf_content}
            
            Las preguntas deben incluir tanto preguntas literales como críticas. Aproximadamente el 60% deben ser
            preguntas que fomenten el pensamiento crítico y análisis, no solo memorización.
            
            {"Incluye al menos 2 preguntas de opción múltiple con 4 opciones cada una, indicando cuál es la correcta." if include_multiple_choice else ""}
            
            Para cada pregunta, proporciona:
            1. El enunciado de la pregunta
            2. El tipo de pregunta (text o multiple_choice)
            3. La respuesta correcta
            4. Para preguntas de opción múltiple, las opciones disponibles
            5. El puntaje sugerido (de 1 a 5, siendo 5 las preguntas más difíciles)
            
            Formatea tu respuesta como un objeto JSON con una lista de preguntas.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un asistente educativo especializado en crear preguntas para evaluaciones de comunicación basadas en textos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extraer y parsear el contenido JSON de la respuesta
            content = response.choices[0].message.content
            
            # Intentar extraer el bloque JSON si está envuelto en backticks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                json_str = content.strip()
                
            # Parsear el JSON
            questions_data = json.loads(json_str)
            
            # Asegurarse de que tenemos un formato adecuado
            if isinstance(questions_data, dict) and "questions" in questions_data:
                return questions_data["questions"]
            elif isinstance(questions_data, list):
                return questions_data
            else:
                raise ValueError("Formato inesperado en la respuesta de OpenAI")
            
        except Exception as e:
            logger.error(f"Error generando preguntas con OpenAI desde PDF: {str(e)}")
            raise
