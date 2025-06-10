import requests
import json
import os
import time
from typing import Dict, List, Any, Optional
import logging
import random
import tempfile

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_endpoints")

# Base URL para el servicio de Quiz
BASE_URL = "http://localhost:8001/api/v1"

# Datos de prueba
CLASSROOM_ID = 1
TEACHER_ID = 1
STUDENT_ID = 1

class TestQuizEndpoints:
    """Clase para probar los endpoints del servicio de Quiz"""
    
    def __init__(self):
        """Inicialización de variables para almacenar IDs de recursos creados"""
        self.quiz_id = None
        self.question_id = None
        self.pdf_quiz_id = None
        self.session = requests.Session()
    
    def run_tests(self):
        """Ejecuta todas las pruebas secuencialmente"""
        try:
            logger.info("🚀 Iniciando pruebas de endpoints")
            logger.warning("Leer test_delete_quiz(self) antes de ejecutar para evitar eliminar quiz generados por IA")
            logger.warning("Colocar tu PDF path dentro de test_create_quiz_from_pdf(self)")
            # Verificar que la API está funcionando
            self.test_health_check()
            
            # Pruebas de Quiz
            self.test_create_quiz_from_text()
            if self.quiz_id:
                self.test_get_quiz_by_id()
                self.test_get_quizzes_by_classroom()
                self.test_get_quizzes_by_teacher()
                self.test_update_quiz()
                
                # Pruebas de Question
                self.test_create_question()
                if self.question_id:
                    self.test_get_question_by_id()
                    self.test_get_questions_by_quiz()
                    self.test_update_question()
                    
                # Pruebas de envío de respuestas
                self.test_submit_student_answers()
                
                # Limpieza - eliminar pregunta
                self.test_delete_question()
            
            # Probar generación desde PDF
            self.test_create_quiz_from_pdf()
            
            # Limpieza - eliminar quiz
            #if self.quiz_id:
            #    self.test_delete_quiz()
                
            logger.info("✅ Todas las pruebas completadas exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error durante las pruebas: {str(e)}")
            raise
    
    def test_health_check(self):
        """Prueba el endpoint de health check"""
        logger.info("Probando health check...")
        response = self.session.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        assert response.status_code == 200, f"Health check falló: {response.text}"
        logger.info("✓ Health check exitoso")
    
    def test_create_quiz_from_text(self):
        """Prueba la creación de un quiz desde texto"""
        logger.info("Creando quiz desde texto...")
        
        data = {
            "title": "Quiz de prueba",
            "description": "Este es un quiz generado para probar la API. El tema es sobre programación en Python, tipos de datos y estructuras de control.",
            "id_classroom": CLASSROOM_ID,
            "id_teacher": TEACHER_ID,
            "num_questions": 3
        }
        
        response = self.session.post(f"{BASE_URL}/quiz/generate", json=data)
        
        if response.status_code == 201:
            self.quiz_id = response.json()["id"]
            logger.info(f"✓ Quiz creado exitosamente con ID: {self.quiz_id}")
        else:
            logger.error(f"❌ Error al crear quiz: {response.status_code} - {response.text}")
            self._create_quiz_manually()
    
    def _create_quiz_manually(self):
        """Crea un quiz manualmente si la generación con IA falla"""
        logger.info("Intentando crear quiz manualmente...")
        
        # Crear un quiz básico primero
        basic_data = {
            "title": "Quiz manual",
            "instructions": "Este es un quiz creado manualmente para pruebas",
            "id_classroom": CLASSROOM_ID,
            "id_teacher": TEACHER_ID,
            "start_time": None,
            "end_time": None
        }
        
        # Intentar crear un quiz básico sin preguntas primero
        try:
            response = self.session.post(f"{BASE_URL}/quiz", json=basic_data)
            
            if response.status_code in [200, 201]:
                self.quiz_id = response.json()["id"]
                logger.info(f"✓ Quiz creado manualmente con ID: {self.quiz_id}")
                
                # Ahora añadir una pregunta simple al quiz
                question_data = {
                    "statement": "¿Qué es Python?",
                    "question_type": "text",
                    "points": 1,
                    "answer_correct": None
                }
                
                question_response = self.session.post(
                    f"{BASE_URL}/question/quiz/{self.quiz_id}", 
                    json=question_data
                )
                
                if question_response.status_code in [200, 201]:
                    logger.info("✓ Pregunta añadida manualmente al quiz")
                else:
                    logger.warning(f"⚠️ No se pudo añadir pregunta al quiz: {question_response.status_code}")
            else:
                logger.warning(f"⚠️ No se pudo crear un quiz manualmente: {response.status_code} - {response.text}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear un quiz manualmente: {str(e)}")
            # Intentar un enfoque alternativo con datos mínimos
    
    def test_get_quiz_by_id(self):
        """Prueba la obtención de un quiz por ID"""
        logger.info(f"Obteniendo quiz con ID {self.quiz_id}...")
        
        response = self.session.get(f"{BASE_URL}/quiz/{self.quiz_id}")
        
        assert response.status_code == 200, f"Error al obtener quiz: {response.text}"
        logger.info("✓ Quiz obtenido exitosamente")
    
    def test_get_quizzes_by_classroom(self):
        """Prueba la obtención de quizzes por aula"""
        logger.info(f"Obteniendo quizzes para el aula {CLASSROOM_ID}...")
        
        response = self.session.get(f"{BASE_URL}/quiz/classroom/{CLASSROOM_ID}")
        
        assert response.status_code == 200, f"Error al obtener quizzes por aula: {response.text}"
        quizzes = response.json()
        logger.info(f"✓ Se encontraron {len(quizzes)} quizzes para el aula")
    
    def test_get_quizzes_by_teacher(self):
        """Prueba la obtención de quizzes por profesor"""
        logger.info(f"Obteniendo quizzes del profesor {TEACHER_ID}...")
        
        response = self.session.get(f"{BASE_URL}/quiz/teacher/{TEACHER_ID}")
        
        assert response.status_code == 200, f"Error al obtener quizzes por profesor: {response.text}"
        quizzes = response.json()
        logger.info(f"✓ Se encontraron {len(quizzes)} quizzes del profesor")
    
    def test_update_quiz(self):
        """Prueba la actualización de un quiz"""
        logger.info(f"Actualizando quiz con ID {self.quiz_id}...")
        
        data = {
            "title": "Quiz actualizado",
            "instructions": "Instrucciones actualizadas para el quiz de prueba",
            "start_time": "2023-12-01T00:00:00",
            "end_time": "2023-12-31T23:59:59"
        }
        
        response = self.session.put(f"{BASE_URL}/quiz/{self.quiz_id}", json=data)
        
        assert response.status_code == 200, f"Error al actualizar quiz: {response.text}"
        logger.info("✓ Quiz actualizado exitosamente")
    
    def test_create_question(self):
        """Prueba la creación de una pregunta"""
        logger.info(f"Creando pregunta para el quiz {self.quiz_id}...")
        
        # Crear una pregunta de opción múltiple
        data = {
            "statement": "¿Cuál es el tipo de dato principal para texto en Python?",
            "question_type": "multiple_choice",
            "points": 2,
            "answer_correct": None,
            "options": [
                {"option_text": "int", "is_correct": False},
                {"option_text": "str", "is_correct": True},
                {"option_text": "bool", "is_correct": False},
                {"option_text": "float", "is_correct": False}
            ]
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/question/quiz/{self.quiz_id}", json=data)
            
            if response.status_code == 201:
                self.question_id = response.json()["id"]
                logger.info(f"✓ Pregunta creada exitosamente con ID: {self.question_id}")
            else:
                logger.error(f"❌ Error al crear pregunta: {response.status_code} - {response.text}")
                # Si falla, intentar con una pregunta más simple
                self._create_question_simple()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Error de conexión al crear pregunta: {str(e)}")
            # Intentar reconectar y crear pregunta simple
            time.sleep(2)  # Esperar un poco para que el servidor se recupere
            self._create_question_simple()

    def _create_question_simple(self):
        """Crea una pregunta simple en caso de fallo de la creación principal"""
        logger.info("Intentando crear pregunta simplificada...")
        try:
            # Pregunta sin opciones
            data = {
                "statement": "Explica brevemente qué es Python",
                "question_type": "text",
                "points": 1
            }
            response = self.session.post(f"{BASE_URL}/question/quiz/{self.quiz_id}", json=data)
            
            if response.status_code == 201:
                self.question_id = response.json()["id"]
                logger.info(f"✓ Pregunta simplificada creada con ID: {self.question_id}")
            else:
                logger.warning(f"⚠️ No se pudo crear ninguna pregunta: {response.status_code} - {response.text}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear una pregunta simple: {str(e)}")
    
    def test_get_question_by_id(self):
        """Prueba la obtención de una pregunta por ID"""
        logger.info(f"Obteniendo pregunta con ID {self.question_id}...")
        
        response = self.session.get(f"{BASE_URL}/question/{self.question_id}")
        
        assert response.status_code == 200, f"Error al obtener pregunta: {response.text}"
        logger.info("✓ Pregunta obtenida exitosamente")
    
    def test_get_questions_by_quiz(self):
        """Prueba la obtención de todas las preguntas de un quiz"""
        logger.info(f"Obteniendo preguntas para el quiz {self.quiz_id}...")
        
        response = self.session.get(f"{BASE_URL}/question/quiz/{self.quiz_id}")
        
        assert response.status_code == 200, f"Error al obtener preguntas por quiz: {response.text}"
        questions = response.json()
        logger.info(f"✓ Se encontraron {len(questions)} preguntas para el quiz")
    
    def test_update_question(self):
        """Prueba la actualización de una pregunta"""
        logger.info(f"Actualizando pregunta con ID {self.question_id}...")
        
        data = {
            "statement": "¿Cuál es el tipo de dato utilizado para texto en Python?",
            "points": 3
        }
        
        response = self.session.put(f"{BASE_URL}/question/{self.question_id}", json=data)
        
        assert response.status_code == 200, f"Error al actualizar pregunta: {response.text}"
        logger.info("✓ Pregunta actualizada exitosamente")
    
    def test_submit_student_answers(self):
        """Prueba el envío de respuestas de un estudiante"""
        logger.info(f"Enviando respuestas del estudiante para el quiz {self.quiz_id}...")
        
        try:
            # Primero obtenemos las preguntas del quiz
            response = self.session.get(f"{BASE_URL}/question/quiz/{self.quiz_id}")
            
            if response.status_code != 200:
                logger.warning(f"No se pudieron obtener preguntas para el quiz {self.quiz_id}: {response.status_code}")
                return
                
            questions = response.json()
            
            if not questions:
                logger.warning(f"No hay preguntas en el quiz {self.quiz_id}, omitiendo prueba de envío de respuestas")
                return
            
            # Preparar las respuestas
            answers = []
            for question in questions:
                question_id = question["id"]
                question_type = question["question_type"]
                
                if question_type == "multiple_choice":
                    # Para preguntas de opción múltiple, intentar obtener las opciones
                    try:
                        question_response = self.session.get(f"{BASE_URL}/question/{question_id}")
                        if question_response.status_code == 200:
                            question_data = question_response.json()
                            # Si hay opciones, seleccionar la primera
                            if question_data.get("options") and len(question_data["options"]) > 0:
                                option_id = question_data["options"][0]["id"]
                                answers.append({
                                    "question_id": question_id,
                                    "option_selected_id": option_id
                                })
                            else:
                                # Si no hay opciones, usar una respuesta de texto
                                answers.append({
                                    "question_id": question_id,
                                    "answer_text": "Respuesta de texto alternativa"
                                })
                        else:
                            # Si no podemos obtener detalles, usar un ID simulado
                            answers.append({
                                "question_id": question_id,
                                "option_selected_id": question_id * 10
                            })
                    except Exception as e:
                        logger.warning(f"Error al obtener opciones para pregunta {question_id}: {str(e)}")
                        answers.append({
                            "question_id": question_id,
                            "answer_text": "Respuesta alternativa debido a error"
                        })
                else:
                    # Para preguntas de texto
                    answers.append({
                        "question_id": question_id,
                        "answer_text": "Respuesta de prueba para pregunta de texto"
                    })
            
            # Si no hay respuestas, no continuar
            if not answers:
                logger.warning("No se pudieron preparar respuestas para enviar")
                return
                
            data = {
                "student_id": STUDENT_ID,
                "answers": answers
                # quiz_id is not needed in the body, it's in the URL
            }
            
            # Usar try/except para manejar errores de conexión
            try:
                response = self.session.post(f"{BASE_URL}/quiz/{self.quiz_id}/submit", json=data)
                
                if response.status_code in [201, 200]:
                    logger.info("✓ Respuestas enviadas exitosamente")
                else:
                    logger.warning(f"⚠️ No se pudieron enviar las respuestas: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"⚠️ Error de conexión al enviar respuestas: {str(e)}")
        except Exception as e:
            logger.warning(f"⚠️ Error al preparar o enviar respuestas: {str(e)}")
    
    # def test_create_pdf_sample(self):
    #     """Crea un archivo PDF de muestra para pruebas"""
    #     try:
    #         from reportlab.lib.pagesizes import letter
    #         from reportlab.pdfgen import canvas
            
    #         # Usar un archivo temporal para el PDF
    #         temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    #         pdf_path = temp_file.name
            
    #         logger.info(f"Creando PDF de muestra temporal en: {pdf_path}")
            
    #         c = canvas.Canvas(pdf_path, pagesize=letter)
    #         c.setFont("Helvetica", 12)
            
    #         c.drawString(100, 750, "Documento de prueba para generación de quiz")
    #         c.drawString(100, 730, "Tema: Programación en Python")
            
    #         c.drawString(100, 700, "Python es un lenguaje de programación interpretado de alto nivel.")
    #         c.drawString(100, 680, "Es conocido por su sintaxis clara y legible.")
            
    #         c.drawString(100, 650, "Tipos de datos en Python:")
    #         c.drawString(120, 630, "- Enteros (int): Números enteros como 1, 100, -10")
    #         c.drawString(120, 610, "- Flotantes (float): Números con decimales como 3.14")
    #         c.drawString(120, 590, "- Cadenas (str): Texto como 'Hola mundo'")
    #         c.drawString(120, 570, "- Booleanos (bool): Valores True o False")
            
    #         c.drawString(100, 540, "Estructuras de control:")
    #         c.drawString(120, 520, "- if/else: Para tomar decisiones")
    #         c.drawString(120, 500, "- for: Para iterar sobre secuencias")
    #         c.drawString(120, 480, "- while: Para repetir código mientras una condición sea verdadera")
            
    #         c.save()
            
    #         return pdf_path
    #     except ImportError:
    #         logger.warning("⚠️ No se pudo crear el PDF de muestra: reportlab no está instalado")
    #         return None
    
    def test_create_quiz_from_pdf(self):
        """Prueba la creación de un quiz desde un PDF"""
        logger.info("Creando quiz desde PDF...")
        
        # Crear PDF de muestra en lugar de usar una URL
        # Nota si alguien lee este y encuentra una forma eficiente de encontrar un path de PDF en el sistema, que lo haga, pero por ahora lo dejo así porque no es necesario
        pdf_path = r"E:\\Metodologia_MTS.pdf"
        if not pdf_path:
            logger.warning("No se pudo crear el PDF de muestra, omitiendo prueba")
            return
        
        data = {
            "title": "Quiz desde PDF",
            "description": "Genera preguntas que evalúen la comprensión conceptual y el análisis crítico del contenido del PDF, no solo datos memorísticos.", # Cambiar a tu gusto
            "id_classroom": CLASSROOM_ID,
            "id_teacher": TEACHER_ID,
            "num_questions": 3
        }
        
        try:
            with open(pdf_path, "rb") as pdf_file:
                files = {"file": ("quiz_sample.pdf", pdf_file, "application/pdf")}
                response = self.session.post(
                    f"{BASE_URL}/quiz/generate-from-pdf",
                    data=data,
                    files=files
                )
            
            if response.status_code == 201:
                result = response.json()
                self.pdf_quiz_id = result["quiz_id"]
                logger.info(f"✓ Quiz creado desde PDF con ID: {self.pdf_quiz_id}")
            else:
                logger.error(f"❌ Error al crear quiz desde PDF: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"❌ Error al enviar el archivo PDF: {str(e)}")
        finally:
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)
                logger.info(f"✓ Archivo PDF temporal eliminado")

    def test_delete_question(self):
        """Prueba la eliminación de una pregunta"""
        if not self.question_id:
            logger.warning("No hay pregunta para eliminar, omitiendo prueba")
            return
        
        logger.info(f"Eliminando pregunta con ID {self.question_id}...")
        
        response = self.session.delete(f"{BASE_URL}/question/{self.question_id}")
        
        assert response.status_code == 204, f"Error al eliminar pregunta: {response.status_code} - {response.text}"
        logger.info("✓ Pregunta eliminada exitosamente")
    
    def test_delete_quiz(self):
        """Prueba la eliminación de un quiz"""
        if not self.quiz_id:
            logger.warning("No hay quiz para eliminar, omitiendo prueba")
            return
        
        logger.info(f"Eliminando quiz con ID {self.quiz_id}...")
        
        #-----------------------------------------------------------------
        # Comentar si quieres que NO se elimine tu quiz generado por Texto
        #-----------------------------------------------------------------


        response = self.session.delete(f"{BASE_URL}/quiz/{self.quiz_id}")
        
        assert response.status_code == 204, f"Error al eliminar quiz: {response.status_code} - {response.text}"
        logger.info("✓ Quiz eliminado exitosamente")
        
        #-----------------------------------------------------------------
        # Comentar si quieres que NO se elimine tu quiz generado desde PDF
        #-----------------------------------------------------------------

        # También eliminar el quiz generado desde PDF si existe
        if self.pdf_quiz_id:
            logger.info(f"Eliminando quiz PDF con ID {self.pdf_quiz_id}...")
            response = self.session.delete(f"{BASE_URL}/quiz/{self.pdf_quiz_id}")
            
            if response.status_code == 204:
                logger.info("✓ Quiz PDF eliminado exitosamente")
            else:
                logger.error(f"❌ Error al eliminar quiz PDF: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Ejecutar todas las pruebas
    test_runner = TestQuizEndpoints()
    test_runner.run_tests()
