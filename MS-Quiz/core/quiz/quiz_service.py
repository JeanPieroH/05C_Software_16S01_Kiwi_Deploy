from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import selectinload,joinedload,with_polymorphic

from typing import List, Optional, Dict, Any
import logging
import json

from db.models.quiz import *
from schemas.quiz import QuizCreateInput, QuizSubmissionInput, QuizBasicOutput,QuizDetailOutput,QuestionDetailOutput,AnswerBaseDetailOutput# Usaremos un schema nuevo para la entrada
from schemas.quiz import (
    QuizResultDetailOutput, QuestionResultDetailOutput, AnswerBaseDetailOutput,
    AnswerSubmittedDetailOutput
)
# from core.quiz.quiz_generator import QuizGenerator

logger = logging.getLogger(__name__)

class QuizService:
    @staticmethod
    async def create_full_quiz(db: AsyncSession, quiz_data: QuizCreateInput) -> Dict[str, Any]:
        
        # Obtener los datetimes de Pydantic. Pydantic los convierte a aware si la cadena JSON lo tiene.
        # Luego, asegurar que sean timezone-naive para la BD.
        start_time_aware = quiz_data.start_time
        end_time_aware = quiz_data.end_time

        # Convertir a timezone-naive ANTES de pasarlos al modelo de SQLAlchemy
        start_time_naive = start_time_aware.replace(tzinfo=None) if start_time_aware else None
        end_time_naive = end_time_aware.replace(tzinfo=None) if end_time_aware else None

        if start_time_naive and end_time_naive and start_time_naive >= end_time_naive:
            raise ValueError("La hora de inicio no puede ser igual o posterior a la hora de fin.")
        
        new_quiz = Quiz(
            id_classroom=quiz_data.classroom_id,
            title=quiz_data.title,
            instruction=quiz_data.instruction,
            start_time=start_time_naive, # <- Usar la versión timezone-naive
            end_time=end_time_naive      # <- Usar la versión timezone-naive
        )
        db.add(new_quiz)
        await db.flush()

        total_quiz_points = 0
        output_questions = []

        for q_data in quiz_data.questions:
            answer_base_type = q_data.answer_base.type
            answer_base_instance = None

            if answer_base_type == "base_text":
                answer_base_instance = Base_Text(type="base_text")
            elif answer_base_type == "base_multiple_option":
                options = q_data.answer_base.options
                if not options: 
                    raise ValueError("Las opciones para 'base_multiple_option' no pueden estar vacías.")
                answer_base_instance = Base_Multiple_Option(
                    type="base_multiple_option",
                    options=json.dumps(options)
                )
            else:
                raise ValueError(f"Tipo de respuesta base '{answer_base_type}' no soportado.")
            
            db.add(answer_base_instance)
            await db.flush()

            new_question = Question(
                quiz_id=new_quiz.id,
                statement=q_data.statement,
                answer_correct=q_data.answer_correct,
                points=q_data.points,
                id_answer=answer_base_instance.id,
                competences_id=q_data.competences_id
            )
            db.add(new_question)
            await db.flush()

            total_quiz_points += new_question.points
            output_questions.append({
                "question_id": new_question.id,
                "points": new_question.points,
                "competences_id": new_question.competences_id
            })

        new_quiz.total_points = total_quiz_points
        return {
            "quiz_id": new_quiz.id,
            "total_points": new_quiz.total_points,
            "questions": output_questions
        }
    
    @staticmethod
    def _calculate_question_feedback(question: Question, submitted_answer_data: Dict[str, Any]) -> str:
        # Asume que submitted_answer_data es un diccionario con 'type', 'answer_written' o 'option_select'
        if submitted_answer_data["type"] == "submitted_text":
            if submitted_answer_data.get("answer_written") == question.answer_correct:
                return "¡Correcto! Tu respuesta es precisa."
            else:
                return f"Incorrecto. La respuesta esperada era: '{question.answer_correct}'."
        elif submitted_answer_data["type"] == "submitted_multiple_option":
            if submitted_answer_data.get("option_select") == question.answer_correct:
                return "¡Muy bien! Esa es la opción correcta."
            else:
                return f"Incorrecto. La opción correcta era: '{question.answer_correct}'."
        return "Feedback no disponible para este tipo de respuesta."

    @staticmethod
    def _calculate_general_feedback(quiz: Quiz, total_obtained_points: int) -> str:
        if quiz.total_points is None or quiz.total_points == 0:
            return "Feedback general no disponible (puntos del quiz no definidos)."

        percentage = (total_obtained_points / quiz.total_points) * 100 if quiz.total_points > 0 else 0

        if percentage == 100:
            return "¡Felicidades! Has respondido todas las preguntas correctamente y obtenido la máxima puntuación."
        elif percentage >= 75:
            return "Excelente trabajo, has demostrado un gran conocimiento."
        elif percentage >= 50:
            return "Buen esfuerzo, has obtenido una puntuación satisfactoria."
        else:
            return "Necesitas repasar algunos conceptos. ¡Sigue practicando para mejorar!"

    @staticmethod
    async def process_student_submission(db: AsyncSession, submission_data: QuizSubmissionInput) -> Dict[str, Any]:
        
        quiz = (await db.execute(select(Quiz).filter_by(id=submission_data.quiz_id))).scalar_one_or_none()
        if not quiz:
            raise ValueError(f"Quiz con ID {submission_data.quiz_id} no encontrado.")

        quiz_student = (await db.execute(
            select(Quiz_Student).filter_by(id_quiz=submission_data.quiz_id, id_student=submission_data.student_id)
        )).scalar_one_or_none()

        if not quiz_student:
            quiz_student = Quiz_Student(
                id_quiz=submission_data.quiz_id,
                id_student=submission_data.student_id,
                is_present_quiz=submission_data.is_present,
                points_obtained=0, # Se actualizará después
                feedback_general_automated=None, # Se calculará después
                feedback_general_teacher=None    # Inicializar con NULL
            )
            db.add(quiz_student)
        else:
            quiz_student.is_present_quiz = submission_data.is_present
            quiz_student.points_obtained = 0 # Reiniciar para recalcular
            quiz_student.feedback_general_teacher = None # Mantener/Reiniciar a NULL
        
        await db.flush()

        total_obtained_points = 0
        output_question_students = []
        
        for q_sub_data in submission_data.questions:
            question = (await db.execute(
                select(Question).filter_by(id=q_sub_data.question_id, quiz_id=submission_data.quiz_id)
            )).scalar_one_or_none()
            if not question:
                raise ValueError(f"Pregunta con ID {q_sub_data.question_id} no encontrada o no pertenece al quiz {submission_data.quiz_id}.")

            answer_base = (await db.execute(
                select(Answer_Base).filter_by(id=question.id_answer)
            )).scalar_one_or_none()
            if not answer_base:
                raise ValueError(f"Respuesta base para la pregunta {q_sub_data.question_id} no encontrada.")

            submitted_type = q_sub_data.answer_submitted.type
            submitted_answer_instance = None
            student_points_for_question = 0
            
            # Convertir Pydantic sub-model a dict para pasar a _calculate_question_feedback
            submitted_answer_dict = q_sub_data.answer_submitted.model_dump()
            
            question_feedback_message = QuizService._calculate_question_feedback(
                question, submitted_answer_dict
            )

            if submitted_type == "submitted_text":
                submitted_answer_instance = Submitted_Text(
                    type="submitted_text",
                    answer_written=q_sub_data.answer_submitted.answer_written
                )
                if q_sub_data.answer_submitted.answer_written == question.answer_correct:
                    student_points_for_question = question.points
            elif submitted_type == "submitted_multiple_option":
                submitted_answer_instance = Submitted_Multiple_Option(
                    type="submitted_multiple_option",
                    option_select=q_sub_data.answer_submitted.option_select
                )
                if not q_sub_data.answer_submitted.option_select: 
                    raise ValueError(f"La opción seleccionada para la pregunta {q_sub_data.question_id} no puede estar vacía.")
                if q_sub_data.answer_submitted.option_select == question.answer_correct:
                    student_points_for_question = question.points
            else:
                raise ValueError(f"Tipo de respuesta enviada '{submitted_type}' no soportado.")
            
            db.add(submitted_answer_instance)
            await db.flush()

            total_obtained_points += student_points_for_question

            question_student = Question_Student(
                id_student=submission_data.student_id,
                id_question=q_sub_data.question_id,
                id_answer_submitted=submitted_answer_instance.id,
                points_obtained=student_points_for_question,
                feedback_automated=question_feedback_message, # Asignar el feedback
                feedback_teacher=None # Inicializar con NULL
            )
            db.add(question_student)

            output_question_students.append({
                "question_id": q_sub_data.question_id,
                "obtained_points": student_points_for_question
            })
        
        quiz_student.points_obtained = total_obtained_points
        quiz_student.feedback_general_automated = QuizService._calculate_general_feedback(
            quiz, total_obtained_points
        )

        return {
            "quiz_id": quiz_student.id_quiz,
            "student_id": quiz_student.id_student,
            "obtained_points": quiz_student.points_obtained,
            "question_student": output_question_students
        }
    
    @staticmethod
    async def get_quizzes_by_ids(db: AsyncSession, quiz_ids: List[int]) -> List[QuizBasicOutput]:
        if not quiz_ids:
            raise ValueError("Se debe proporcionar al menos un ID de quiz.")
        
        for q_id in quiz_ids:
            if not isinstance(q_id, int) or q_id <= 0:
                raise ValueError("Todos los IDs de quiz deben ser enteros positivos.")
        
        result = await db.execute(
            select(Quiz).filter(Quiz.id.in_(quiz_ids))
        )
        quizzes_db = result.scalars().all()
        
        return [QuizBasicOutput.model_validate(quiz) for quiz in quizzes_db]

    
    @staticmethod
    async def get_quiz_with_details_by_id(db: AsyncSession, quiz_id: int) -> Optional[QuizDetailOutput]:
        try:
            if not isinstance(quiz_id, int) or quiz_id <= 0:
                raise ValueError("El ID del quiz debe ser un entero positivo.")

            answer_base_poly = with_polymorphic(Answer_Base, [Base_Text, Base_Multiple_Option], flat=True)
            result = await db.execute(
                select(Quiz)
                .options(
                    selectinload(Quiz.questions)
                    .joinedload(Question.answer_base.of_type(answer_base_poly))
                )
                .where(Quiz.id == quiz_id)
            )
            quiz_db = result.scalars().first()

            if not quiz_db:
                return None

            questions_output: List[QuestionDetailOutput] = []
            for question_db in quiz_db.questions:
                answer_base_options: Optional[List[str]] = None
                
                if isinstance(question_db.answer_base, Base_Multiple_Option):
                    if question_db.answer_base.options is not None:
                        try:
                            answer_base_options = json.loads(question_db.answer_base.options)
                        except json.JSONDecodeError:
                            answer_base_options = []
                
                answer_base_detail = AnswerBaseDetailOutput(
                    id_answer=question_db.answer_base.id,
                    type=question_db.answer_base.type,
                    options=answer_base_options
                )
                
                questions_output.append(
                    QuestionDetailOutput(
                        id=question_db.id,
                        statement=question_db.statement,
                        answer_correct=question_db.answer_correct,
                        points=question_db.points,
                        answer_base=answer_base_detail,
                        competences_id=question_db.competences_id
                    )
                )

            return QuizDetailOutput(
                id=quiz_db.id,
                title=quiz_db.title,
                instruction=quiz_db.instruction,
                start_time=quiz_db.start_time,
                end_time=quiz_db.end_time,
                created_at=quiz_db.created_at,
                updated_at=quiz_db.updated_at,
                questions=questions_output
            )
        except Exception as e:
            logger.error(f"Error interno del servidor al obtener el quiz con ID {quiz_id}: {e}", exc_info=True)
            raise e
    @staticmethod
    async def get_quiz_and_student_results(db: AsyncSession, quiz_id: int, student_id: int) -> Optional[QuizResultDetailOutput]:
        try:
            if not isinstance(quiz_id, int) or quiz_id <= 0:
                raise ValueError("El ID del quiz debe ser un entero positivo.")
            if not isinstance(student_id, int) or student_id <= 0:
                raise ValueError("El ID del estudiante debe ser un entero positivo.")

            answer_base_poly = with_polymorphic(Answer_Base, [Base_Text, Base_Multiple_Option], flat=True)
            answer_submitted_poly = with_polymorphic(Answer_Submitted, [Submitted_Text, Submitted_Multiple_Option], flat=True)
            
            result = await db.execute(
                select(Quiz)
                .options(
                    selectinload(Quiz.questions).joinedload(Question.answer_base.of_type(answer_base_poly)),
                    selectinload(Quiz.quiz_students.and_(Quiz_Student.id_student == student_id))
                )
                .where(Quiz.id == quiz_id)
            )
            quiz_db = result.scalars().first()

            if not quiz_db:
                return None
            
            quiz_student_db = next((qs for qs in quiz_db.quiz_students if qs.id_student == student_id), None)
            
            question_students_map = {}
            if quiz_student_db:
                q_s_results = await db.execute(
                    select(Question_Student)
                    .options(joinedload(Question_Student.answer_submitted.of_type(answer_submitted_poly)))
                    .where(
                        Question_Student.id_student == student_id,
                        Question_Student.id_question.in_([q.id for q in quiz_db.questions])
                    )
                )
                for qs in q_s_results.scalars().all():
                    question_students_map[qs.id_question] = qs


            questions_output: List[QuestionResultDetailOutput] = []
            for question_db in quiz_db.questions:
                answer_base_options: Optional[List[str]] = None
                if isinstance(question_db.answer_base, Base_Multiple_Option):
                    if question_db.answer_base.options is not None:
                        try:
                            answer_base_options = json.loads(question_db.answer_base.options)
                        except json.JSONDecodeError:
                            answer_base_options = []
                
                answer_base_detail = AnswerBaseDetailOutput(
                    id_answer=question_db.answer_base.id,
                    type=question_db.answer_base.type,
                    options=answer_base_options
                )

                answer_submitted_detail: Optional[AnswerSubmittedDetailOutput] = None
                question_feedback_automated: Optional[str] = None
                question_feedback_teacher: Optional[str] = None
                question_points_obtained: int = 0

                question_student_db = question_students_map.get(question_db.id)
                if question_student_db:
                    question_feedback_automated = question_student_db.feedback_automated
                    question_feedback_teacher = question_student_db.feedback_teacher
                    question_points_obtained = question_student_db.points_obtained

                    if question_student_db.answer_submitted:
                        if isinstance(question_student_db.answer_submitted, Submitted_Text):
                            answer_submitted_detail = AnswerSubmittedDetailOutput(
                                id=question_student_db.answer_submitted.id,
                                type=question_student_db.answer_submitted.type,
                                answer_written=question_student_db.answer_submitted.answer_written,
                                option_select=None 
                            )
                        elif isinstance(question_student_db.answer_submitted, Submitted_Multiple_Option):
                            answer_submitted_detail = AnswerSubmittedDetailOutput(
                                id=question_student_db.answer_submitted.id,
                                type=question_student_db.answer_submitted.type,
                                answer_written=None,
                                option_select=question_student_db.answer_submitted.option_select
                            )
                
                questions_output.append(
                    QuestionResultDetailOutput(
                        id=question_db.id,
                        statement=question_db.statement,
                        answer_correct=question_db.answer_correct,
                        points=question_db.points,
                        answer_base=answer_base_detail,
                        feedback_automated=question_feedback_automated,
                        feedback_teacher=question_feedback_teacher,
                        points_obtained=question_points_obtained,
                        answer_submitted=answer_submitted_detail,
                        competences_id=question_db.competences_id
                    )
                )

            quiz_feedback_automated: Optional[str] = None
            quiz_feedback_teacher: Optional[str] = None
            quiz_points_obtained: int = 0
            if quiz_student_db:
                quiz_feedback_automated = quiz_student_db.feedback_general_automated
                quiz_feedback_teacher = quiz_student_db.feedback_general_teacher
                quiz_points_obtained = quiz_student_db.points_obtained

            return QuizResultDetailOutput(
                id=quiz_db.id,
                title=quiz_db.title,
                instruction=quiz_db.instruction,
                start_time=quiz_db.start_time,
                end_time=quiz_db.end_time,
                created_at=quiz_db.created_at,
                updated_at=quiz_db.updated_at,
                feedback_automated=quiz_feedback_automated,
                feedback_teacher=quiz_feedback_teacher,
                points_obtained=quiz_points_obtained,
                questions=questions_output
            )
        except Exception as e:
            raise e
    
    # @staticmethod
    # def _serialize_quiz(quiz: Quiz) -> Dict[str, Any]:
    #     """
    #     Serializa un objeto Quiz y sus relaciones para evitar problemas de lazy loading
        
    #     Args:
    #         quiz: Objeto Quiz a serializar
            
    #     Returns:
    #         Diccionario con los datos del quiz serializados
    #     """
    #     if not quiz:
    #         return None
            
    #     quiz_dict = {
    #         "id": quiz.id,
    #         "title": quiz.title,
    #         "instructions": quiz.instructions,
    #         "id_classroom": quiz.id_classroom,
    #         "id_teacher": quiz.id_teacher,
    #         "start_time": quiz.start_time,
    #         "end_time": quiz.end_time,
    #         "created_at": quiz.created_at if hasattr(quiz, "created_at") else None,
    #         "updated_at": quiz.updated_at if hasattr(quiz, "updated_at") else None,
    #         "questions": []
    #     }
        
    #     if hasattr(quiz, "questions") and quiz.questions is not None:
    #         for question in quiz.questions:
    #             question_dict = {
    #                 "id": question.id,
    #                 "statement": question.statement,
    #                 "question_type": question.question_type,
    #                 "points": question.points,
    #                 "answer_correct": question.answer_correct,
    #                 "quiz_id": quiz.id,
    #                 "created_at": question.created_at if hasattr(question, "created_at") else None,
    #                 "options": []
    #             }
                
    #             if hasattr(question, "options") and question.options is not None:
    #                 for option in question.options:
    #                     option_dict = {
    #                         "id": option.id,
    #                         "option_text": option.option_text,
    #                         "is_correct": bool(option.is_correct),
    #                         "question_id": question.id
    #                     }
    #                     question_dict["options"].append(option_dict)
                
    #             quiz_dict["questions"].append(question_dict)
        
    #     return quiz_dict
    
    # @staticmethod
    # async def create_quiz_from_text(
    #     db: AsyncSession,
    #     title: str,
    #     description: str,
    #     id_classroom: int,
    #     id_teacher: int,
    #     num_questions: int = None
    # ) -> Dict[str, Any]:
    #     """
    #     Crea un quiz a partir de una descripción de texto utilizando IA
        
    #     Args:
    #         db: Sesión de base de datos
    #         title: Título del quiz
    #         description: Descripción o instrucciones del quiz
    #         id_classroom: ID del aula
    #         id_teacher: ID del profesor
    #         num_questions: Número de preguntas a generar
            
    #     Returns:
    #         Diccionario con los datos del quiz creado
    #     """
    #     # Generar el quiz usando el QuizGenerator
    #     quiz = await QuizGenerator.create_quiz_from_text(
    #         db, title, description, id_classroom, id_teacher, num_questions
    #     )
        
    #     # Obtener el quiz completo con todas sus relaciones cargadas
    #     result = await db.execute(
    #         select(Quiz)
    #         .where(Quiz.id == quiz.id)
    #         .options(
    #             selectinload(Quiz.questions).selectinload(Question.options)
    #         )
    #     )
    #     complete_quiz = result.scalar_one_or_none()
        
    #     # Serializar el quiz para evitar problemas de lazy loading
    #     return QuizService._serialize_quiz(complete_quiz)
    
    # @staticmethod
    # async def create_quiz_from_pdf(
    #     db: AsyncSession,
    #     title: str,
    #     pdf_content: bytes,
    #     id_classroom: int,
    #     id_teacher: int,
    #     num_questions: int = None,
    #     description: str = None
    # ) -> Dict[str, Any]:
    #     """
    #     Crea un quiz a partir del contenido de un PDF utilizando IA
        
    #     Args:
    #         db: Sesión de base de datos
    #         title: Título del quiz
    #         pdf_content: Contenido del archivo PDF en bytes
    #         id_classroom: ID del aula
    #         id_teacher: ID del profesor
    #         num_questions: Número de preguntas a generar
    #         description: Descripción opcional sobre qué tipo de preguntas generar
            
    #     Returns:
    #         Diccionario con los datos del quiz creado
    #     """
    #     # Generar el quiz usando el QuizGenerator
    #     quiz = await QuizGenerator.create_quiz_from_pdf(
    #         db, title, pdf_content, id_classroom, id_teacher, num_questions, description
    #     )
        
    #     # Obtener el quiz completo con todas sus relaciones cargadas
    #     result = await db.execute(
    #         select(Quiz)
    #         .where(Quiz.id == quiz.id)
    #         .options(
    #             selectinload(Quiz.questions).selectinload(Question.options)
    #         )
    #     )
    #     complete_quiz = result.scalar_one_or_none()
        
    #     # Serializar el quiz para evitar problemas de lazy loading
    #     return QuizService._serialize_quiz(complete_quiz)
    
    # @staticmethod
    # async def get_quiz_by_id(db: AsyncSession, quiz_id: int) -> Dict[str, Any]:
    #     """
    #     Obtiene un quiz por su ID
        
    #     Args:
    #         db: Sesión de base de datos
    #         quiz_id: ID del quiz
            
    #     Returns:
    #         Diccionario con los datos del quiz o None si no existe
    #     """
    #     # Use selectinload to eagerly load relationships
    #     result = await db.execute(
    #         select(Quiz)
    #         .where(Quiz.id == quiz_id)
    #         .options(
    #             selectinload(Quiz.questions).selectinload(Question.options)
    #         )
    #     )
    #     quiz = result.scalar_one_or_none()
        
    #     # Serializar el quiz para evitar problemas de lazy loading
    #     return QuizService._serialize_quiz(quiz)
    
    # @staticmethod
    # async def get_quizzes_by_classroom(db: AsyncSession, classroom_id: int) -> List[Dict[str, Any]]:
    #     """
    #     Obtiene todos los quizzes de un aula
        
    #     Args:
    #         db: Sesión de base de datos
    #         classroom_id: ID del aula
            
    #     Returns:
    #         Lista de diccionarios con los datos de los quizzes
    #     """
    #     result = await db.execute(
    #         select(Quiz)
    #         .where(Quiz.id_classroom == classroom_id)
    #         .options(
    #             selectinload(Quiz.questions).selectinload(Question.options)
    #         )
    #     )
    #     quizzes = result.scalars().all()
        
    #     # Serializar los quizzes para evitar problemas de lazy loading
    #     return [QuizService._serialize_quiz(quiz) for quiz in quizzes]
    
    # @staticmethod
    # async def get_quizzes_by_teacher(db: AsyncSession, teacher_id: int) -> List[Dict[str, Any]]:
    #     """
    #     Obtiene todos los quizzes de un profesor
        
    #     Args:
    #         db: Sesión de base de datos
    #         teacher_id: ID del profesor
            
    #     Returns:
    #         Lista de diccionarios con los datos de los quizzes
    #     """
    #     result = await db.execute(
    #         select(Quiz)
    #         .where(Quiz.id_teacher == teacher_id)
    #         .options(
    #             selectinload(Quiz.questions).selectinload(Question.options)
    #         )
    #     )
    #     quizzes = result.scalars().all()
        
    #     # Serializar los quizzes para evitar problemas de lazy loading
    #     return [QuizService._serialize_quiz(quiz) for quiz in quizzes]
    
    # @staticmethod
    # async def update_quiz(db: AsyncSession, quiz_id: int, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     Actualiza un quiz existente
        
    #     Args:
    #         db: Sesión de base de datos
    #         quiz_id: ID del quiz a actualizar
    #         quiz_data: Datos actualizados del quiz
            
    #     Returns:
    #         Diccionario con el quiz actualizado o None si no existe
    #     """
    #     # Verificar si el quiz existe
    #     quiz = await db.execute(
    #         select(Quiz)
    #         .where(Quiz.id == quiz_id)
    #     )
    #     quiz = quiz.scalar_one_or_none()
        
    #     if not quiz:
    #         return None
        
    #     # Filtrar solo los campos actualizables
    #     update_data = {}
    #     for key in ["title", "instructions", "start_time", "end_time"]:
    #         if key in quiz_data and quiz_data[key] is not None:
    #             update_data[key] = quiz_data[key]
        
    #     # Actualizar el quiz
    #     if update_data:
    #         await db.execute(
    #             update(Quiz)
    #             .where(Quiz.id == quiz_id)
    #             .values(**update_data)
    #         )
        
    #     # Obtener el quiz actualizado con todas sus relaciones
    #     result = await db.execute(
    #         select(Quiz)
    #         .where(Quiz.id == quiz_id)
    #         .options(
    #             selectinload(Quiz.questions).selectinload(Question.options)
    #         )
    #     )
    #     updated_quiz = result.scalar_one_or_none()
        
    #     # Serializar el quiz para evitar problemas de lazy loading
    #     return QuizService._serialize_quiz(updated_quiz)

    # @staticmethod
    # async def delete_quiz(db: AsyncSession, quiz_id: int) -> bool:
    #     """
    #     Elimina un quiz
        
    #     Args:
    #         db: Sesión de base de datos
    #         quiz_id: ID del quiz a eliminar
            
    #     Returns:
    #         True si se eliminó correctamente, False si no existía
    #     """
    #     # Verificar si el quiz existe
    #     quiz = await QuizService.get_quiz_by_id(db, quiz_id)
    #     if not quiz:
    #         return False
        
    #     try:
    #         # Obtenemos las preguntas asociadas al quiz
    #         result = await db.execute(
    #             select(Question)
    #             .where(Question.quiz_id == quiz_id)
    #         )
    #         questions = result.scalars().all()
            
    #         # Coleccionamos los IDs de las preguntas
    #         question_ids = [q.id for q in questions]
            
    #         if question_ids:
    #             # Eliminar las respuestas de los estudiantes asociadas a estas preguntas
    #             await db.execute(
    #                 delete(StudentAnswer)
    #                 .where(StudentAnswer.question_id.in_(question_ids))
    #             )
                
    #             # Eliminar las presentaciones de los estudiantes asociadas al quiz
    #             await db.execute(
    #                 delete(StudentQuiz)
    #                 .where(StudentQuiz.quiz_id == quiz_id)
    #             )
                
    #             # Eliminar las opciones de las preguntas asociadas a este quiz
    #             await db.execute(
    #                 delete(QuestionOption)
    #                 .where(QuestionOption.question_id.in_(question_ids))
    #             )
                
    #             # Eliminar las preguntas asociadas al quiz
    #             await db.execute(
    #                 delete(Question)
    #                 .where(Question.quiz_id == quiz_id)
    #             )
            
    #         # Finalmente eliminamos el quiz (Muy feo esta hvda necesita optimizacion)
    #         await db.execute(
    #             delete(Quiz)
    #             .where(Quiz.id == quiz_id)
    #         )
            
    #         return True
    #     except Exception as e:
    #         logger.error(f"Error deleting quiz {quiz_id}: {str(e)}")
    #         await db.rollback()
    #         raise
    
    # @staticmethod
    # async def get_quiz_with_questions(db: AsyncSession, quiz_id: int) -> Dict[str, Any]:
    #     """
    #     Obtiene un quiz por su ID con todas sus preguntas y opciones precargadas
        
    #     Args:
    #         db: Sesión de base de datos
    #         quiz_id: ID del quiz
            
    #     Returns:
    #         Diccionario con los datos del quiz o None si no existe
    #     """
    #     result = await db.execute(
    #         select(Quiz)
    #         .where(Quiz.id == quiz_id)
    #         .options(
    #             selectinload(Quiz.questions).selectinload(Question.options)
    #         )
    #     )
    #     quiz = result.scalar_one_or_none()
        
    #     return QuizService._serialize_quiz(quiz)
    
    # @staticmethod
    # async def submit_student_answers(
    #     db: AsyncSession, 
    #     student_id: int, 
    #     quiz_id: int, 
    #     answers: List[Dict[str, Any]]
    # ) -> StudentQuiz:
    #     """
    #     Registra las respuestas de un estudiante a un quiz y las califica
        
    #     Args:
    #         db: Sesión de base de datos
    #         student_id: ID del estudiante
    #         quiz_id: ID del quiz
    #         answers: Lista de respuestas del estudiante
            
    #     Returns:
    #         Objeto StudentQuiz creado con la información de la presentación
    #     """
    #     quiz_data = await QuizService.get_quiz_with_questions(db, quiz_id)
    #     if not quiz_data:
    #         raise ValueError("El quiz no existe")
        
    #     student_quiz = StudentQuiz(
    #         student_id=student_id,
    #         quiz_id=quiz_id,
    #         is_present=1,  # El estudiante ha presentado el quiz
    #     )
        
    #     db.add(student_quiz)
    #     await db.flush()
        
    #     # Procesamiento de respuestas y puntuación
    #     total_points = 0
    #     obtained_points = 0
        
    #     # Mapa para acceder rápidamente a la información de las preguntas
    #     question_map = {q["id"]: q for q in quiz_data["questions"]}
        
    #     for answer_data in answers:
    #         question_id = answer_data.question_id if hasattr(answer_data, "question_id") else answer_data.get("question_id")
    #         answer_text = answer_data.answer_text if hasattr(answer_data, "answer_text") else answer_data.get("answer_text")
    #         option_selected_id = answer_data.option_selected_id if hasattr(answer_data, "option_selected_id") else answer_data.get("option_selected_id")
            
    #         # Verificar que la pregunta pertenece al quiz
    #         if question_id not in question_map:
    #             continue
            
    #         question = question_map[question_id]
    #         total_points += question["points"]
            
    #         # Crear la respuesta del estudiante
    #         student_answer = StudentAnswer(
    #             student_quiz_id=student_quiz.id,
    #             question_id=question_id,
    #             answer_text=answer_text,
    #             option_selected_id=option_selected_id
    #         )
            
    #         # Evaluar si la respuesta es correcta según el tipo de pregunta
    #         if question["question_type"] == "multiple_choice" and student_answer.option_selected_id:
    #             # Para preguntas de opción múltiple, verificar si la opción seleccionada es correcta
    #             correct_option = next(
    #                 (opt for opt in question["options"] if opt["is_correct"]), 
    #                 None
    #             )
                
    #             if correct_option and student_answer.option_selected_id == correct_option["id"]:
    #                 student_answer.is_correct = 1
    #                 student_answer.points_obtained = question["points"]
    #                 obtained_points += question["points"]
        
    #         elif question["question_type"] == "text" and student_answer.answer_text:
    #             # Para preguntas de texto, se marca como pendiente de revisión
    #             # En una implementación más avanzada, se podría usar IA para evaluar respuestas abiertas
    #             student_answer.is_correct = 0
    #             student_answer.points_obtained = 0
            
    #         db.add(student_answer)
        
    #     # Actualizar los puntos obtenidos en el registro del estudiante
    #     student_quiz.points_obtained = obtained_points
        
    #     # TODO: Generar feedback automatizado utilizando IA
        
    #     return student_quiz
