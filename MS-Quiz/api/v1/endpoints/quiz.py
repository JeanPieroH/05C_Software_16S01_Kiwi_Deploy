from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import datetime

from db.database import get_db
from schemas.quiz import *  # Usaremos un schema nuevo para la entrada
from core.quiz.quiz_service import QuizService
from core.quiz.quiz_generator import QuizGenerator
import json
import logging
from config.settings import get_settings


router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/create", response_model=QuizCreateOutput, status_code=status.HTTP_201_CREATED)
async def create_quiz_with_questions(
    quiz_data: QuizCreateInput,
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un nuevo quiz con sus preguntas y respuestas base asociadas.
    """
    try:
        # El servicio maneja toda la lógica de creación y validación
        created_quiz_output = await QuizService.create_full_quiz(db, quiz_data)
        await db.commit()
        return created_quiz_output
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.post("/submit_answers", response_model=QuizSubmissionOutput, status_code=status.HTTP_201_CREATED)
async def submit_quiz_answers(
    submission_data: QuizSubmissionInput,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await QuizService.process_student_submission(db, submission_data)
        await db.commit()
        return result
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/generate-from-pdf", response_model=QuizGenerationOutput, status_code=status.HTTP_200_OK)
async def generate_quiz_from_pdf_endpoint(
    pdf_file: UploadFile = File(..., description="Archivo PDF para generar el quiz."),
    input_data_json: str = File(..., description="JSON con los parámetros de generación del quiz (classroom_id, num_question, competences, type_question).")
):
    """
    Genera un quiz en formato JSON a partir de un archivo PDF y parámetros de configuración,
    utilizando la API de Google Gemini. No almacena datos en la base de datos.
    """
    try:
        input_data = json.loads(input_data_json)
        # Validar que el archivo sea un PDF
        if pdf_file.content_type != "application/pdf":
            raise ValueError("El archivo debe ser un PDF.")
        
        pdf_content = await pdf_file.read()

        # El servicio maneja toda la lógica de procesamiento y validación
        result = await QuizGenerator.create_quiz_from_pdf(
            pdf_content=pdf_content,
            input_data=input_data
        )
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="El 'input_data_json' no es un JSON válido.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    
@router.post("/generate-from-text", response_model=QuizGenerationOutput, status_code=status.HTTP_200_OK)
async def generate_quiz_from_text_endpoint(
    input_data_json: str = File(..., description="JSON con los parámetros de generación del quiz (classroom_id, num_question, competences, type_question).")
):
    """
    Genera un quiz en formato JSON a partir de un archivo PDF y parámetros de configuración,
    utilizando la API de Google Gemini. No almacena datos en la base de datos.
    """
    try:
        input_data = json.loads(input_data_json)
        

        # El servicio maneja toda la lógica de procesamiento y validación
        result = await QuizGenerator.create_quiz_from_text(
            input_data=input_data
        )
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="El 'input_data_json' no es un JSON válido.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.post(
    "/get-by-ids",
    response_model=List[QuizBasicOutput],
    status_code=status.HTTP_200_OK,
    summary="Obtener quizzes por una lista de IDs",
    description="Recupera detalles básicos de uno o más quizzes basándose en una lista de IDs proporcionados."
)
async def get_quizzes_by_ids_endpoint(
    quiz_ids_input: QuizIdsInput, # JSON de entrada: {"quiz_ids": [1, 2, ...]}
    db: AsyncSession = Depends(get_db)
) -> List[QuizBasicOutput]:
    try:
        quizzes = await QuizService.get_quizzes_by_ids(db, quiz_ids_input.quiz_ids)
        return quizzes
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al recuperar los quizzes."
        )

@router.get(
    "/{quiz_id}",
    response_model=QuizDetailOutput,
    status_code=status.HTTP_200_OK,
    summary="Obtener un quiz por ID con todas las preguntas y respuestas base",
    description="Recupera todos los detalles de un quiz específico, incluyendo sus preguntas asociadas y la estructura de sus respuestas base."
)
async def get_quiz_details_by_id_endpoint(
    quiz_id: int,
    db: AsyncSession = Depends(get_db)
) -> QuizDetailOutput:
    try:
        quiz = await QuizService.get_quiz_with_details_by_id(db, quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz con ID {quiz_id} no encontrado."
            )
        return quiz
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error interno del servidor al obtener el quiz con ID {quiz_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al recuperar el quiz."
        )

@router.get(
"/{quiz_id}/student/{student_id}/result",
response_model=QuizResultDetailOutput,
status_code=status.HTTP_200_OK,
summary="Obtener resultado de quiz de estudiante",
description="Recupera los detalles de un quiz junto con las respuestas y el desempeño de un estudiante específico."
)
async def get_quiz_student_result_endpoint(
    quiz_id: int,
    student_id: int,
    db: AsyncSession = Depends(get_db)
) -> QuizResultDetailOutput:
    try:
        quiz_result = await QuizService.get_quiz_and_student_results(db, quiz_id, student_id)
        if not quiz_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resultados no encontrados para el Quiz ID {quiz_id} y Estudiante ID {student_id}."
            )
        return quiz_result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al obtener el resultado del quiz {quiz_id} para el estudiante {student_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al recuperar los resultados del quiz."
        )


@router.get(
    "/{quiz_id}/students-points",
    response_model=List[StudentPointsOutput],
    status_code=status.HTTP_200_OK,
    summary="Obtener puntos de estudiantes por quiz",
    description="Recupera los IDs de los estudiantes y sus puntos obtenidos para un quiz específico."
)
async def get_students_points_endpoint(
    quiz_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[StudentPointsOutput]:
    try:
        students_points = await QuizService.get_students_points_for_quiz(db, quiz_id)
        if not students_points:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron estudiantes o puntos para el Quiz ID {quiz_id}."
            )
        return students_points
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al obtener puntos de estudiantes para el quiz {quiz_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al recuperar los puntos de los estudiantes."
        )
@router.get(
    "/classroom/{classroom_id}/student/{student_id}",
    response_model=List[QuizWithAttemptStatusOutput],
    status_code=status.HTTP_200_OK,
    summary="Obtener quizzes de un aula con estado de intento del estudiante",
    description="Retorna la lista de quizzes de un aula específica, indicando si un estudiante dado ha intentado cada quiz."
)
async def get_quizzes_by_classroom_with_attempt_status_endpoint(
    classroom_id: int,
    student_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[QuizWithAttemptStatusOutput]:
    try:
        quizzes = await QuizService.get_quizzes_by_classroom_with_attempt_status(db, classroom_id, student_id)
        if not quizzes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron quizzes para el Classroom ID {classroom_id} o el Estudiante ID {student_id}."
            )
        return quizzes
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al obtener quizzes para el aula {classroom_id} y estudiante {student_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al recuperar los quizzes."
        )

@router.get("/{quiz_id}/results", response_model=List[StudentQuizResultOutput])
async def get_quiz_student_results(
    quiz_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[StudentQuizResultOutput]:
    """
    Obtiene la lista de estudiantes que rindieron un quiz, junto con sus puntos obtenidos.
    """
    try:
        results = await QuizService.get_students_quiz_results(db, quiz_id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")
# @router.get("/{quiz_id}", response_model=QuizSchema)
# async def get_quiz(
#     quiz_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Obtiene un quiz por su ID
#     """
#     quiz_data = await QuizService.get_quiz_by_id(db, quiz_id)
#     if not quiz_data:
#         raise HTTPException(status_code=404, detail="Quiz no encontrado")
    
#     return quiz_data

# @router.get("/classroom/{classroom_id}", response_model=List[QuizSchema])
# async def get_quizzes_by_classroom(
#     classroom_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Obtiene todos los quizzes de un aula
#     """
#     return await QuizService.get_quizzes_by_classroom(db, classroom_id)

# @router.get("/teacher/{teacher_id}", response_model=List[QuizSchema])
# async def get_quizzes_by_teacher(
#     teacher_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Obtiene todos los quizzes de un profesor
#     """
#     return await QuizService.get_quizzes_by_teacher(db, teacher_id)

# @router.post("/generate", response_model=QuizSchema, status_code=status.HTTP_201_CREATED)
# async def generate_quiz(
#     input_data: QuizGenerationInput,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Genera un nuevo quiz basado en una descripción de texto usando IA
#     """
#     try:
#         quiz_data = await QuizService.create_quiz_from_text(
#             db=db,
#             title=input_data.title,
#             description=input_data.description,
#             id_classroom=input_data.id_classroom,
#             id_teacher=input_data.id_teacher,
#             num_questions=input_data.num_questions
#         )
#         await db.commit()
#         return quiz_data
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error al generar el quiz: {str(e)}")

# @router.post("/generate-from-pdf", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
# async def generate_quiz_from_pdf(
#     title: str = Form(...),
#     id_classroom: int = Form(...),
#     id_teacher: int = Form(...),
#     num_questions: Optional[int] = Form(5),
#     description: Optional[str] = Form(None, description="Descripción sobre qué tipo de preguntas generar o aspectos a enfatizar"),
#     file: UploadFile = File(...),
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Genera un nuevo quiz basado en el contenido de un archivo PDF usando IA
#     """
#     if not file.filename.lower().endswith('.pdf'):
#         raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
#     try:
#         # Leer contenido del archivo
#         pdf_content = await file.read()
        
#         # Generar el quiz
#         quiz_data = await QuizService.create_quiz_from_pdf(
#             db=db,
#             title=title,
#             pdf_content=pdf_content,
#             id_classroom=id_classroom,
#             id_teacher=id_teacher,
#             num_questions=num_questions,
#             description=description  # Pasamos el nuevo parámetro
#         )
        
#         await db.commit()
        
#         return FileUploadResponse(
#             filename=file.filename,
#             content_type=file.content_type,
#             quiz_id=quiz_data["id"]
#         )
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error al generar el quiz desde PDF: {str(e)}")

# @router.put("/{quiz_id}", response_model=QuizSchema)
# async def update_quiz(
#     quiz_id: int,
#     quiz_data: QuizUpdate,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Actualiza un quiz existente
#     """
#     updated_quiz = await QuizService.update_quiz(db, quiz_id, quiz_data.model_dump(exclude_unset=True))
#     if not updated_quiz:
#         raise HTTPException(status_code=404, detail="Quiz no encontrado")
    
#     await db.commit()
#     return updated_quiz

# @router.delete("/{quiz_id}", status_code=204)
# async def delete_quiz(
#     quiz_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Elimina un quiz
#     """
#     success = await QuizService.delete_quiz(db, quiz_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Quiz no encontrado")
    
#     await db.commit()
#     return {"detail": "Quiz eliminado correctamente"}

# @router.post("/{quiz_id}/submit", response_model=StudentQuiz, status_code=status.HTTP_201_CREATED)
# async def submit_quiz(
#     quiz_id: int,
#     student_submission: StudentQuizCreate,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Envía las respuestas de un estudiante a un quiz
#     """
#     try:
#         answers = [answer.dict() for answer in student_submission.answers] if student_submission.answers else []
        
#         student_quiz = await QuizService.submit_student_answers(
#             db=db,
#             student_id=student_submission.student_id,
#             quiz_id=quiz_id,
#             answers=answers
#         )
#         await db.commit()
#         return student_quiz
#     except ValueError as e:
#         await db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error al enviar las respuestas: {str(e)}")

# @router.post("", response_model=QuizSchema, status_code=status.HTTP_201_CREATED)
# async def create_quiz(
#     quiz_data: QuizCreate,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Crea un nuevo quiz manualmente sin usar IA
#     """
#     try:
#         # Crear el quiz básico
#         quiz = QuizModel(
#             title=quiz_data.title,
#             instructions=quiz_data.instructions,
#             id_classroom=quiz_data.id_classroom,
#             id_teacher=quiz_data.id_teacher,
#             start_time=quiz_data.start_time,
#             end_time=quiz_data.end_time
#         )
        
#         db.add(quiz)
#         await db.flush()
        
#         # Si se proporcionaron preguntas, crearlas
#         if quiz_data.questions:
#             for q_data in quiz_data.questions:
#                 question = Question(
#                     quiz_id=quiz.id,
#                     statement=q_data.statement,
#                     answer_correct=q_data.answer_correct,
#                     points=q_data.points,
#                     question_type=q_data.question_type,
#                     created_at=datetime.datetime.now()
#                 )
                
#                 db.add(question)
#                 await db.flush()
                
#                 # Si es de opción múltiple, crear las opciones
#                 if q_data.options:
#                     for opt_data in q_data.options:
#                         option = QuestionOption(
#                             question_id=question.id,
#                             option_text=opt_data.option_text,
#                             is_correct=1 if opt_data.is_correct else 0
#                         )
#                         db.add(option)
        
#         await db.commit()
#         return quiz
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error al crear el quiz: {str(e)}")