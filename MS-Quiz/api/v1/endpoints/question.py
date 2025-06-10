# from fastapi import APIRouter, Depends, HTTPException, status, Body
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy.orm import selectinload
# from sqlalchemy import update, delete
# from typing import List, Optional, Dict, Any
# import datetime

# from db.database import get_db
# from schemas.question import Question as QuestionSchema, QuestionCreate, QuestionUpdate, QuestionWithOptions
# from db.models.quiz import Question, QuestionOption

# router = APIRouter()

# @router.post("/quiz/{quiz_id}", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
# async def create_question(
#     quiz_id: int,
#     question_data: QuestionCreate,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Crea una nueva pregunta para un quiz
#     """
#     try:
#         Crear la pregunta
#         question = Question(
#             quiz_id=quiz_id,
#             statement=question_data.statement,
#             question_type=question_data.question_type,
#             answer_correct=question_data.answer_correct,
#             points=question_data.points,
#             created_at=datetime.datetime.now()
#         )
        
#         db.add(question)
#         await db.flush()
        
#         Si es de opción múltiple y se proporcionaron opciones, crearlas
#         if question_data.options:
#             for opt_data in question_data.options:
#                 option = QuestionOption(
#                     question_id=question.id,
#                     option_text=opt_data.option_text,
#                     is_correct=1 if opt_data.is_correct else 0
#                 )
#                 db.add(option)
        
#         await db.commit()
        
#         Obtener la pregunta con sus opciones para devolverla
#         result = await db.execute(
#             select(Question)
#             .where(Question.id == question.id)
#             .options(selectinload(Question.options))
#         )
#         created_question = result.scalar_one()
        
#         Convertir a diccionario para incluir opciones
#         response = {
#             "id": created_question.id,
#             "statement": created_question.statement,
#             "question_type": created_question.question_type,
#             "points": created_question.points,
#             "answer_correct": created_question.answer_correct,
#             "quiz_id": created_question.quiz_id,
#             "created_at": created_question.created_at,
#             "options": [{
#                 "id": opt.id,
#                 "option_text": opt.option_text,
#                 "is_correct": bool(opt.is_correct),
#                 "question_id": question.id
#             } for opt in created_question.options]
#         }
        
#         return response
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error al crear la pregunta: {str(e)}")

# @router.get("/{question_id}", response_model=QuestionWithOptions)
# async def get_question(
#     question_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Obtiene una pregunta por su ID con sus opciones
#     """
#     result = await db.execute(
#         select(Question)
#         .where(Question.id == question_id)
#         .options(selectinload(Question.options))
#     )
#     question = result.scalar_one_or_none()
    
#     if not question:
#         raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
#     Convertir a diccionario para incluir opciones
#     response = {
#         "id": question.id,
#         "statement": question.statement,
#         "question_type": question.question_type,
#         "points": question.points,
#         "answer_correct": question.answer_correct,
#         "quiz_id": question.quiz_id,
#         "created_at": question.created_at,
#         "options": [{
#             "id": opt.id,
#             "option_text": opt.option_text,
#             "is_correct": bool(opt.is_correct),
#             "question_id": question.id
#         } for opt in question.options]
#     }
    
#     return response

# @router.get("/quiz/{quiz_id}", response_model=List[QuestionWithOptions])
# async def get_questions_by_quiz(
#     quiz_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Obtiene todas las preguntas de un quiz
#     """
#     result = await db.execute(
#         select(Question)
#         .where(Question.quiz_id == quiz_id)
#         .options(selectinload(Question.options))
#     )
#     questions = result.scalars().all()
    
#     Convertir a formato de respuesta
#     response = []
#     for q in questions:
#         question_dict = {
#             "id": q.id,
#             "statement": q.statement,
#             "question_type": q.question_type,
#             "points": q.points,
#             "answer_correct": q.answer_correct,
#             "quiz_id": q.quiz_id,
#             "created_at": q.created_at,
#             "options": [{
#                 "id": opt.id,
#                 "option_text": opt.option_text,
#                 "is_correct": bool(opt.is_correct),
#                 "question_id": q.id
#             } for opt in q.options]
#         }
#         response.append(question_dict)
    
#     return response

# @router.put("/{question_id}", response_model=QuestionSchema)
# async def update_question(
#     question_id: int,
#     question_data: Dict[str, Any] = Body(...),
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Actualiza una pregunta existente
#     """
#     result = await db.execute(select(Question).where(Question.id == question_id))
#     question = result.scalar_one_or_none()
    
#     if not question:
#         raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
#     Actualizar campos
#     update_data = {}
#     for key in ["statement", "answer_correct", "points", "question_type"]:
#         if key in question_data:
#             update_data[key] = question_data[key]
    
#     await db.execute(
#         update(Question)
#         .where(Question.id == question_id)
#         .values(**update_data)
#     )
    
#     Si se proporcionan opciones y el tipo es multiple_choice, actualizarlas
#     if question_data.get("question_type", question.question_type) == "multiple_choice" and "options" in question_data:
#         Eliminar opciones anteriores
#         await db.execute(
#             update(QuestionOption)
#             .where(QuestionOption.question_id == question_id)
#             .values(deleted_at=datetime.datetime.now())
#         )
        
#         Crear nuevas opciones
#         for option_data in question_data["options"]:
#             option = QuestionOption(
#                 question_id=question_id,
#                 option_text=option_data["option_text"],
#                 is_correct=1 if option_data.get("is_correct", False) else 0
#             )
#             db.add(option)
    
#     await db.commit()
#     await db.refresh(question)
    
#     return question

# @router.delete("/{question_id}", status_code=204)
# async def delete_question(
#     question_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Elimina una pregunta
#     """
#     Verificar si la pregunta existe
#     result = await db.execute(select(Question).where(Question.id == question_id))
#     question = result.scalar_one_or_none()
    
#     if not question:
#         raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
#     Eliminar la pregunta (las opciones se eliminarán en cascada)
#     await db.delete(question)
#     await db.commit()
    
#     return {"detail": "Pregunta eliminada correctamente"}
