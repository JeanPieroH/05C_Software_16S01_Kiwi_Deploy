from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

# Esquemas de QuestionOption
class QuestionOptionBase(BaseModel):
    option_text: str = Field(..., description="Texto de la opción")
    is_correct: bool = Field(False, description="Indica si es la opción correcta")

class QuestionOptionCreate(QuestionOptionBase):
    pass

class QuestionOption(QuestionOptionBase):
    id: int = Field(..., description="ID de la opción")
    
    class Config:
        from_attributes = True

# Esquemas de Question
class QuestionBase(BaseModel):
    statement: str = Field(..., description="Enunciado de la pregunta")
    answer_correct: Optional[str] = Field(None, description="Respuesta correcta (para preguntas abiertas)")
    points: int = Field(1, description="Puntos asignados a la pregunta")
    question_type: str = Field("text", description="Tipo de pregunta (text, multiple_choice)")

class QuestionCreate(QuestionBase):
    options: Optional[List[QuestionOptionCreate]] = Field(None, description="Opciones para preguntas de opción múltiple")

class Question(QuestionBase):
    id: int = Field(..., description="ID de la pregunta")
    quiz_id: int = Field(..., description="ID del quiz al que pertenece")
    options: Optional[List[QuestionOption]] = Field(None, description="Opciones de la pregunta (si es opción múltiple)")
    created_at: datetime = Field(..., description="Fecha de creación")
    
    class Config:
        from_attributes = True

# Esquemas de Quiz
class QuizBase(BaseModel):
    title: str = Field(..., description="Título del quiz")
    instructions: Optional[str] = Field(None, description="Instrucciones del quiz")
    id_classroom: int = Field(..., description="ID del salón de clases")
    id_teacher: int = Field(..., description="ID del profesor")
    start_time: Optional[datetime] = Field(None, description="Fecha y hora de inicio")
    end_time: Optional[datetime] = Field(None, description="Fecha y hora de finalización")

class QuizCreate(QuizBase):
    questions: Optional[List[QuestionCreate]] = Field(None, description="Preguntas del quiz")

class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Título del quiz")
    instructions: Optional[str] = Field(None, description="Instrucciones del quiz")
    start_time: Optional[datetime] = Field(None, description="Fecha y hora de inicio")
    end_time: Optional[datetime] = Field(None, description="Fecha y hora de finalización")

class Quiz(QuizBase):
    id: int = Field(..., description="ID del quiz")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    questions: List[Question] = Field([], description="Preguntas del quiz")
    
    class Config:
        from_attributes = True

# Esquemas para la generación AI
class QuizGenerationInput(BaseModel):
    title: str = Field(..., description="Título del quiz")
    description: str = Field(..., description="Descripción del tema sobre el que generar preguntas")
    num_questions: int = Field(5, description="Número de preguntas a generar")
    id_classroom: int = Field(..., description="ID del salón de clases")
    id_teacher: int = Field(..., description="ID del profesor")

class FileUploadResponse(BaseModel):
    filename: str = Field(..., description="Nombre del archivo subido")
    content_type: str = Field(..., description="Tipo de contenido del archivo")
    quiz_id: Optional[int] = Field(None, description="ID del quiz generado (si se procesó)")

#------------------------------------------------
class AnswerBaseInput(BaseModel):
    """Esquema para la información de la respuesta base de una pregunta."""
    type: str = Field(..., description="Tipo de la respuesta base (ej. 'base_text', 'base_multiple_option').")
    options: Optional[List[str]] = Field(
        None, 
        description="Lista de opciones para preguntas de opción múltiple. Requerido si 'type' es 'base_multiple_option'."
    ) 

class QuestionCreateInput(BaseModel):
    """Esquema para crear una nueva pregunta dentro de un quiz."""
    statement: str = Field(..., description="El enunciado o texto de la pregunta.")
    answer_correct: Optional[str] = Field(
        None, 
        description="La respuesta correcta para la pregunta (especialmente útil para preguntas de texto o referencia)."
    )
    points: int = Field(..., gt=0, description="Puntos otorgados por responder correctamente a la pregunta.")
    answer_base: AnswerBaseInput = Field(..., description="Detalles de la respuesta base de la pregunta, incluyendo su tipo y opciones si aplica.")
    competences_id: Optional[List[int]] = Field(
        [], 
        description="Lista de IDs de competencias asociadas a esta pregunta."
    )

class QuizCreateInput(BaseModel):
    """Esquema de entrada para crear un nuevo quiz con sus preguntas."""
    classroom_id: int = Field(..., description="El ID del aula a la que pertenece el quiz.")
    title: str = Field(..., max_length=255, description="El título del quiz.")
    instruction: Optional[str] = Field(
        None, 
        description="Instrucciones o descripción detallada para el quiz."
    )
    start_time: Optional[datetime] = Field(
        None, 
        description="Fecha y hora de inicio del quiz en formato ISO 8601 (ej. '2025-06-09T15:30:00Z')."
    )
    end_time: Optional[datetime] = Field(
        None, 
        description="Fecha y hora de finalización del quiz en formato ISO 8601 (ej. '2025-06-09T15:30:00Z')."
    )
    questions: List[QuestionCreateInput] = Field(
        ..., 
        min_items=1, 
        description="Lista de preguntas que componen el quiz."
    )

class QuestionOutput(BaseModel):
    """Esquema de salida para una pregunta dentro del resumen de un quiz creado."""
    question_id: int = Field(..., description="El ID único de la pregunta creada.")
    points: int = Field(..., description="Los puntos asignados a la pregunta.")
    competences_id: List[int] = Field(
        ..., 
        description="Lista de IDs de competencias asociadas a la pregunta."
    )

class QuizCreateOutput(BaseModel):
    """Esquema de salida que resume un quiz después de su creación exitosa."""
    quiz_id: int = Field(..., description="El ID único del quiz creado.")
    total_points: Optional[int] = Field(None, description="El total de puntos posibles a obtener en el quiz.")
    questions: List[QuestionOutput] = Field(
        ..., 
        description="Lista de preguntas creadas con sus IDs y puntos asociados."
    )

# -------------------------------
class AnswerSubmittedInput(BaseModel):
    type: str = Field(..., description="Tipo de la respuesta enviada (ej. 'submitted_text', 'submitted_multiple_option').")
    answer_written: Optional[str] = Field(
        None, 
        description="La respuesta escrita por el estudiante para preguntas de texto. Requerido si 'type' es 'submitted_text'."
    )
    option_select: Optional[str] = Field(
        None, 
        description="La opción seleccionada por el estudiante para preguntas de opción múltiple. Requerido si 'type' es 'submitted_multiple_option'."
    )

class QuestionSubmissionInput(BaseModel):
    question_id: int = Field(..., description="El ID de la pregunta a la que se está respondiendo.")
    answer_submitted: AnswerSubmittedInput = Field(..., description="La información de la respuesta enviada por el estudiante para esta pregunta.")

class QuizSubmissionInput(BaseModel):
    quiz_id: int = Field(..., description="El ID del quiz al que el estudiante está respondiendo.")
    student_id: int = Field(..., description="El ID del estudiante que envía las respuestas.")
    is_present: bool = Field(True, description="Indica si el estudiante estuvo presente y completó el quiz.")
    questions: List[QuestionSubmissionInput] = Field(
        ..., 
        min_items=1, 
        description="Lista de respuestas del estudiante para cada pregunta del quiz."
    )

class QuestionSubmittedOutput(BaseModel):
    question_id: int = Field(..., description="El ID de la pregunta.")
    obtained_points: int = Field(..., description="Los puntos que el estudiante obtuvo en esta pregunta.")

class QuizSubmissionOutput(BaseModel):
    quiz_id: int = Field(..., description="El ID del quiz.")
    student_id: int = Field(..., description="El ID del estudiante.")
    obtained_points: int = Field(..., description="El total de puntos obtenidos por el estudiante en el quiz.")
    question_student: List[QuestionSubmittedOutput] = Field(
        ..., 
        description="Lista de los resultados de cada pregunta respondida por el estudiante."
    )

#----------------------------------------------------------
class CompetenceInput(BaseModel):
    id: int = Field(..., description="ID único de la competencia.")
    name: str = Field(..., description="Nombre de la competencia.")
    description: str = Field(..., description="Descripción detallada de la competencia.")

class TypeQuestionInput(BaseModel):
    textuales: bool = Field(False, description="Indica si se deben generar preguntas textuales.")
    inferenciales: bool = Field(False, description="Indica si se deben generar preguntas inferenciales.")
    críticas: bool = Field(False, description="Indica si se deben generar preguntas críticas.")

class QuizGenerationInput(BaseModel):
    classroom_id: int = Field(..., description="ID del aula a la que pertenece el quiz.")
    num_question: int = Field(..., gt=0, description="Número total de preguntas a generar.")
    competences: List[CompetenceInput] = Field(..., description="Lista de competencias disponibles para asignar a las preguntas.")
    type_question: TypeQuestionInput = Field(..., description="Tipos de preguntas que se deben generar.")

class AnswerBaseOutput(BaseModel):
    type: str = Field(..., description="Tipo de respuesta base (ej. 'base_text', 'base_multiple_option').")
    options: Optional[List[str]] = Field(None, description="Opciones para preguntas de opción múltiple.")

class QuestionOutput(BaseModel):
    statement: str = Field(..., description="Enunciado de la pregunta.")
    answer_correct: str = Field(..., description="Respuesta correcta o la opción correcta para opción múltiple.")
    points: int = Field(..., description="Puntos asignados a la pregunta.")
    answer_base: AnswerBaseOutput = Field(..., description="Detalles del tipo de respuesta base.")
    competences_id: List[int] = Field(..., description="Lista de IDs de competencias asociadas a la pregunta.")

class QuizGenerationOutput(BaseModel):
    classroom_id: int = Field(..., description="ID del aula.")
    title: str = Field(..., description="Título del quiz generado.")
    instruction: str = Field(..., description="Instrucciones generales del quiz.")
    start_time: str = Field(..., description="Fecha y hora de inicio del quiz en formato ISO 8601 con zona horaria Z (UTC).")
    end_time: str = Field(..., description="Fecha y hora de fin del quiz en formato ISO 8601 con zona horaria Z (UTC).")
    questions: List[QuestionOutput] = Field(..., description="Lista de preguntas generadas para el quiz.")

# -----------------------------
class CompetenceInput(BaseModel):
    id: int = Field(..., description="ID único de la competencia.")
    name: str = Field(..., min_length=1, description="Nombre de la competencia.")
    description: str = Field(..., min_length=1, description="Descripción detallada de la competencia.")

class TypeQuestionInput(BaseModel):
    textuales: bool = Field(False, description="Indica si se deben generar preguntas textuales.")
    inferenciales: bool = Field(False, description="Indica si se deben generar preguntas inferenciales.")
    críticas: bool = Field(False, description="Indica si se deben generar preguntas críticas.")

class QuizGenerateRequest(BaseModel):
    classroom_id: int = Field(..., description="ID del aula a la que pertenece el quiz.")
    num_question: int = Field(..., ge=1, description="Número de preguntas a generar para el quiz.")
    point_max: int = Field(..., ge=1, description="Puntuación máxima total deseada para el quiz.")
    text: str = Field(..., min_length=10, description="Texto base a partir del cual se generará el quiz. Mínimo 10 caracteres.")
    competences: List[CompetenceInput] = Field(..., min_items=1, description="Lista de competencias con sus IDs, nombres y descripciones. Mínimo una competencia.")
    type_question: TypeQuestionInput = Field(..., description="Tipos de preguntas a incluir (textuales, inferenciales, críticas).")

# Modelos para la respuesta de salida
class AnswerBaseOutput(BaseModel):
    type: str = Field(..., description="Tipo de respuesta: 'base_text' o 'base_multiple_option'.")
    options: Optional[List[str]] = Field(None, description="Lista de opciones si el tipo es 'base_multiple_option'.")

class QuestionOutput(BaseModel):
    statement: str = Field(..., min_length=1, description="Enunciado de la pregunta.")
    answer_correct: str = Field(..., min_length=1, description="Respuesta correcta a la pregunta.")
    points: int = Field(..., ge=1, description="Puntos asignados a esta pregunta.")
    answer_base: AnswerBaseOutput = Field(..., description="Detalles del formato de respuesta.")
    competences_id: List[int] = Field(..., description="Lista de IDs de competencias asociadas a la pregunta.")

class QuizGenerateOutput(BaseModel):
    classroom_id: int = Field(..., description="ID del aula a la que pertenece el quiz.")
    title: str = Field(..., min_length=1, description="Título del quiz generado.")
    instruction: str = Field(..., min_length=1, description="Instrucciones generales para el quiz.")
    start_time: datetime = Field(..., description="Fecha y hora de inicio del quiz en formato ISO 8601 (UTC).")
    end_time: datetime = Field(..., description="Fecha y hora de finalización del quiz en formato ISO 8601 (UTC).")
    questions: List[QuestionOutput] = Field(..., description="Lista de preguntas generadas para el quiz.")

#----------------------------------
class QuizIdsInput(BaseModel):
    """Esquema de entrada para solicitar quizzes por una lista de IDs."""
    quiz_ids: List[int] = Field(..., description="Lista de IDs de los quizzes a recuperar.")

class QuizBasicOutput(BaseModel):
    """Esquema de salida para la información básica de un quiz."""
    id: int = Field(..., description="ID del quiz.")
    title: str = Field(..., description="Título del quiz.")
    instruction: Optional[str] = Field(None, description="Instrucciones del quiz.")
    total_points: Optional[int] = Field(None, description="Puntuación total del quiz.")
    start_time: Optional[datetime] = Field(None, description="Fecha y hora de inicio del quiz.")
    end_time: Optional[datetime] = Field(None, description="Fecha y hora de finalización del quiz.")
    created_at: datetime = Field(..., description="Fecha de creación del quiz.")
    updated_at: Optional[datetime] = Field(None, description="Fecha de la última actualización del quiz.")

    class Config:
        from_attributes = True
#---------------------------------------


# --- Esquemas para la respuesta de Quiz con preguntas y respuestas base ---
class AnswerBaseDetailOutput(BaseModel):
    id_answer: int = Field(...)
    type: str = Field(...)
    options: Optional[List[str]] = Field(None)

class QuestionDetailOutput(BaseModel):
    id: int = Field(...)
    statement: str = Field(...)
    answer_correct: Optional[str] = Field(None)
    points: int = Field(...)
    answer_base: AnswerBaseDetailOutput = Field(...)
    competences_id: List[int] = Field([])

class QuizDetailOutput(BaseModel):
    id: int = Field(...)
    title: str = Field(...)
    instruction: Optional[str] = Field(None)
    start_time: Optional[datetime] = Field(None)
    end_time: Optional[datetime] = Field(None)
    created_at: datetime = Field(...)
    updated_at: Optional[datetime] = Field(None)
    questions: List[QuestionDetailOutput] = Field([])

    class Config:
        from_attributes = True 

#--------------------------------
class AnswerSubmittedDetailOutput(BaseModel):
    id: int = Field(...)
    type: str = Field(...)
    answer_written: Optional[str] = Field(None)
    option_select: Optional[str] = Field(None)

    class Config:
        from_attributes = True

# --- Esquema para la pregunta con detalles de la respuesta del estudiante ---
class QuestionResultDetailOutput(BaseModel):
    id: int = Field(...)
    statement: str = Field(...)
    answer_correct: Optional[str] = Field(None)
    points: int = Field(...)
    answer_base: AnswerBaseDetailOutput = Field(...)
    feedback_automated: Optional[str] = Field(None)
    feedback_teacher: Optional[str] = Field(None)
    points_obtained: int = Field(...)
    answer_submitted: Optional[AnswerSubmittedDetailOutput] = Field(None)
    competences_id: List[int] = Field([])

    class Config:
        from_attributes = True

# --- Esquema de salida principal para el resultado del quiz del estudiante ---
class QuizResultDetailOutput(BaseModel):
    id: int = Field(...)
    title: str = Field(...)
    instruction: Optional[str] = Field(None)
    start_time: Optional[datetime] = Field(None)
    end_time: Optional[datetime] = Field(None)
    created_at: datetime = Field(...)
    updated_at: Optional[datetime] = Field(None)
    feedback_automated: Optional[str] = Field(None)
    feedback_teacher: Optional[str] = Field(None)
    points_obtained: int = Field(...)
    questions: List[QuestionResultDetailOutput] = Field([])

    class Config:
        from_attributes = True


class StudentPointsOutput(BaseModel):
    id_student: int = Field(..., description="ID del estudiante.")
    points_obtained: int = Field(..., description="Puntos obtenidos por el estudiante en el quiz.")

    class Config:
        from_attributes = True

class QuizWithAttemptStatusOutput(BaseModel):
    id: int = Field(...)
    title: str = Field(...)
    instruction: Optional[str] = Field(None)
    total_points: Optional[int] = Field(None)
    start_time: Optional[datetime] = Field(None)
    end_time: Optional[datetime] = Field(None)
    created_at: datetime = Field(...)
    updated_at: Optional[datetime] = Field(None)
    student_has_attemped: bool = Field(..., description="Indica si el estudiante ha intentado este quiz.")

    class Config:
        from_attributes = True

class StudentQuizResultOutput(BaseModel):
    """
    Esquema de salida para representar el ID de un estudiante y los puntos obtenidos en un quiz.
    """
    id_student: int = Field(..., description="ID del estudiante que rindió el quiz.")
    points_obtained: int = Field(..., description="Puntos obtenidos por el estudiante en el quiz.")

    class Config:
        from_attributes = True