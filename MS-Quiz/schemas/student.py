from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Esquemas para respuestas de estudiantes
class StudentAnswerBase(BaseModel):
    question_id: int = Field(..., description="ID de la pregunta")
    answer_text: Optional[str] = Field(None, description="Texto de la respuesta (para preguntas abiertas)")
    option_selected_id: Optional[int] = Field(None, description="ID de la opción seleccionada (para opción múltiple)")

class StudentAnswerCreate(StudentAnswerBase):
    pass

class StudentAnswer(StudentAnswerBase):
    id: int = Field(..., description="ID de la respuesta")
    student_quiz_id: int = Field(..., description="ID de la relación estudiante-quiz")
    is_correct: Optional[bool] = Field(None, description="Indica si la respuesta es correcta")
    points_obtained: Optional[float] = Field(None, description="Puntos obtenidos")
    
    class Config:
        from_attributes = True

# Esquemas para la relación estudiante-quiz
class StudentQuizBase(BaseModel):
    student_id: int = Field(..., description="ID del estudiante")
    quiz_id: int = Field(..., description="ID del quiz")
    is_present: bool = Field(False, description="Indica si el estudiante presentó el quiz")

class StudentQuizCreate(BaseModel):
    student_id: int = Field(..., description="ID del estudiante")
    answers: Optional[List[StudentAnswerBase]] = Field(None, description="Respuestas del estudiante")

class StudentQuiz(StudentQuizBase):
    id: int = Field(..., description="ID de la relación estudiante-quiz")
    feedback_automated: Optional[str] = Field(None, description="Retroalimentación automatizada general")
    feedback_teacher: Optional[str] = Field(None, description="Retroalimentación del profesor general")
    points_obtained: Optional[float] = Field(0, description="Puntos obtenidos")
    created_at: Optional[datetime] = Field(None, description="Fecha de presentación")
    answers: List[StudentAnswer] = Field([], description="Respuestas del estudiante")
    
    class Config:
        from_attributes = True

# Esquema para feedback del profesor
class TeacherFeedback(BaseModel):
    feedback: str = Field(..., description="Retroalimentación del profesor")
