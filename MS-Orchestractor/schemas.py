from pydantic import BaseModel, EmailStr, Field
from typing import Optional,Union, List,Literal 
from datetime import datetime
import enum


class Role(str,enum.Enum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"


class Emotional(str,enum.Enum):
    FELIZ = "FELIZ"
    TRISTE = "TRISTE"
    CANSADO = "CANSADO"
    EMOCIONADO = "EMOCIONADO"

class DtoUserRegister(BaseModel):
    name: Optional[str] = Field(None, example="Juan")
    last_name: Optional[str] = Field(None, example="Pérez")
    email: EmailStr = Field(..., example="juan.perez@example.com")
    password: str = Field(..., min_length=3, max_length=16, example="MiClave123")
    role: Optional[Role] = Field(None, example="STUDENT")

class DtoUserLogin(BaseModel):
    email: EmailStr = Field(..., example="juan.perez@example.com")
    password: str = Field(..., min_length=3, max_length=16, example="MiClave123")

class Token(BaseModel):
    token: str

class Email(BaseModel):
    email: EmailStr = Field(..., example="juan.perez@example.com")

class Feedback(BaseModel):
    feedback: str = Field(..., example="Estuvo bien el marcado mejorar en uso de articulos")


class User(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID del usuario")
    name: Optional[str] = Field(None, example="Juan", description="Nombre del usuario")
    last_name: Optional[str] = Field(None, example="Pérez", description="Apellido del usuario")
    email: Optional[str] = Field(None, example="juan.perez@example.com", description="Correo electrónico")
    password: Optional[str] = Field(None, example="securePass123", description="Contraseña del usuario")
    cel_phone: Optional[str] = Field(None, example="+56912345678", description="Número de teléfono celular")
    registration_date: Optional[datetime] = Field(None, example="2024-07-01")
    role: Optional[Role] = Field(..., example="STUDENT")


class Student(User):
    emotion: Optional[Emotional] = Field(None, example="FELIZ")
    coin_earned: Optional[int] = Field(0, example=150)
    coin_available: Optional[int] = Field(0, example=120)

class Teacher(User):
    pass


class DtoUser(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID del usuario")
    name: Optional[str] = Field(None, example="Juan", description="Nombre del usuario")
    last_name: Optional[str] = Field(None, example="Pérez", description="Apellido del usuario")
    email: Optional[str] = Field(None, example="juan.perez@example.com", description="Correo electrónico")
    cel_phone: Optional[str] = Field(None, example="+56912345678", description="Número de teléfono celular")
    role: Optional[Role] = Field(..., example="STUDENT")


class DtoStudent(DtoUser):
    emotion: Optional[Emotional] = Field(None, example="FELIZ")
    coin_earned: Optional[int] = Field(0, example=150)
    coin_available: Optional[int] = Field(0, example=120)

class DtoTeacher(DtoUser):
    pass

class DtoCompetenceCreate(BaseModel):
    name: Optional[str] = Field(None, example="Lógica matemática", description="Nombre")
    description: Optional[str] = Field(None, example="Descripción de la competencia")

class Competence(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID de competencia")
    name: Optional[str] = Field(None, example="Lógica matemática", description="Nombre")
    description: Optional[str] = Field(None, example="Descripción de la competencia")

class CompetenceService(BaseModel):
    id_competence: Optional[int] = Field(None, example=1, description="ID de competencia")
    name: Optional[str] = Field(None, example="Lógica matemática", description="Nombre")
    description: Optional[str] = Field(None, example="Descripción de la competencia")

class DtoClassroomCreate(BaseModel):
    name: str = Field(..., example="4to Básico")
    description: Optional[str] = Field(None, example="Clase de matemáticas")

class Classroom(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID de classroom")
    name: str = Field(..., example="4to Básico")
    description: Optional[str] = Field(None, example="Clase de matemáticas")

class ListEmail(BaseModel):
    emails: List[str] = Field(..., example=["correo1@example.com", "correo2@example.com"], description="Lista de correos electrónicos")

class CompetenceIdsRequest(BaseModel):
    competences_id: List[int] = Field(..., example=[1, 2])
#-----------------------------------------------------------------
class QuizBase(BaseModel):
    id: int = Field(..., example=1, description="ID único del quiz")
    title: str = Field(..., example="titulo 1", description="Título del quiz")
    instruction: Optional[str] = Field(None, example="Esta es la instruccion", description="Instrucciones del quiz")
    total_points: int = Field(..., example=20, description="Puntaje total del quiz")
    start_time: datetime = Field(..., example="2025-06-09T15:30:00", description="Fecha y hora de inicio del quiz")
    end_time: datetime = Field(..., example="2025-06-09T16:30:00", description="Fecha y hora de fin del quiz")
    created_at: datetime = Field(..., example="2025-06-09T16:17:59.020901", description="Fecha de creación del quiz")
    updated_at: datetime = Field(..., example="2025-06-09T16:17:59.108990", description="Fecha de última actualización del quiz")


class CompetenceBase(BaseModel):
    id: int = Field(..., example=1, description="ID único de la competencia")
    name: str = Field(..., example="Resolución de problemas", description="Nombre de la competencia")
    description: str = Field(..., example="Aplicación lógica y estructurada", description="Descripción de la competencia")


class ClassroomBase(BaseModel):
    id: int = Field(..., example=1, description="ID único de la clase")
    name: str = Field(..., example="Clase de Biología", description="Nombre de la clase")
    description: Optional[str] = Field(None, example="Estudio de organismos vivos", description="Descripción de la clase")
    quiz: List[QuizBase] = Field(..., description="Lista de quizzes asociados a la clase")
    competences: List[CompetenceBase] = Field(..., description="Lista de competencias de la clase")

#-------------------------------------
class AnswerBaseText(BaseModel):
    # 'Literal["base_text"]' indica que el valor de 'type' debe ser exactamente la cadena "base_text".
    # Pydantic usa esto para la discriminación.
    type: Literal["base_text"] = "base_text"

# BaseModel para el tipo de respuesta de opción múltiple
class AnswerBaseMultipleOption(BaseModel):
    # 'Literal["base_multiple_option"]' indica que el valor de 'type' debe ser exactamente la cadena "base_multiple_option".
    type: Literal["base_multiple_option"] = "base_multiple_option"
    options: List[str] = Field(..., example=["1810", "1821", "1910", "1857"], description="Opciones de respuesta")


# Pregunta en el quiz
class QuestionCreate(BaseModel):
    statement: str = Field(..., example="¿Cuál es la capital de Francia?", description="Enunciado de la pregunta")
    answer_correct: str = Field(..., example="París", description="Respuesta correcta")
    points: int = Field(..., example=10, description="Puntos que vale la pregunta")
    
    # La unión de los tipos de respuesta concretos.
    # Pydantic inferirá el discriminador automáticamente a partir del campo 'type' con Literals.
    answer_base: Union[AnswerBaseText, AnswerBaseMultipleOption] = Field(..., description="Configuración de tipo de respuesta")
    
    competences_id: List[int] = Field(..., example=[1, 2], description="IDs de competencias asociadas")


# Modelo principal para crear el quiz
class DtoQuizCreate(BaseModel):
    classroom_id: int = Field(..., example=1, description="ID del aula a la que pertenece el quiz")
    title: str = Field(..., example="Título del Quiz", description="Título del quiz")
    instruction: Optional[str] = Field(None, example="Lee cuidadosamente y responde", description="Instrucciones del quiz")
    start_time: datetime = Field(..., example="2025-06-09T15:30:00Z", description="Inicio del quiz")
    end_time: datetime = Field(..., example="2025-06-09T16:30:00Z", description="Fin del quiz")
    questions: List[QuestionCreate] = Field(..., description="Lista de preguntas del quiz")


#-----------------------------------
class AnswerSubmittedText(BaseModel):
    type: str = Field(..., example="submitted_text", description="Tipo de respuesta enviada: texto")
    answer_written: str = Field(..., example="mi respuesta", description="Texto escrito por el estudiante")

class AnswerSubmittedMultipleOption(BaseModel):
    type: str = Field(..., example="submitted_multiple_option", description="Tipo de respuesta enviada: opción múltiple")
    option_select: str = Field(..., example="1810", description="Opción seleccionada por el estudiante")

class SubmittedQuestion(BaseModel):
    question_id: int = Field(..., example=1, description="ID de la pregunta respondida")
    answer_submitted: Union[AnswerSubmittedText, AnswerSubmittedMultipleOption] = Field(
        ..., description="Respuesta enviada a la pregunta"
    )

class QuizSubmission(BaseModel):
    quiz_id: int = Field(..., example=1, description="ID del quiz que se responde")
    student_id: int = Field(..., example=2, description="ID del estudiante que responde")
    is_present: bool = Field(..., example=True, description="Indica si el estudiante estuvo presente")
    questions: List[SubmittedQuestion] = Field(..., description="Lista de preguntas respondidas")

#------------------------------------

# Esquema para la generación de quizzes con IA
class TypeQuestionFlags(BaseModel):
    textuales: bool = Field(..., description="Indica si se incluyen preguntas textuales")
    inferenciales: bool = Field(..., description="Indica si se incluyen preguntas inferenciales")
    críticas: bool = Field(..., description="Indica si se incluyen preguntas críticas")

class CompetenceInfo(BaseModel):
    id: int = Field(..., example=1, description="ID de la competencia")
    name: str = Field(..., example="Escritura en español", description="Nombre de la competencia")
    description: str = Field(..., example="Esta competencia aborda sobre escribir español", description="Descripción")

class QuizAutoGenerateRequest_PDF(BaseModel):
    classroom_id: int = Field(..., example=1, description="ID del aula")
    num_question: int = Field(..., example=5, description="Número de preguntas a generar")
    point_max: int = Field(..., example=20, description="Puntaje máximo del quiz")
    competences: List[CompetenceInfo] = Field(..., description="Lista de competencias relacionadas")
    type_question: TypeQuestionFlags = Field(..., description="Tipos de preguntas a incluir")

class QuizAutoGenerateRequest_TEXT(BaseModel):
    classroom_id: int = Field(..., example=1, description="ID del aula")
    num_question: int = Field(..., example=5, description="Número de preguntas a generar")
    text: str= Field(..., example="Genera un quiz de la segunda guerra mundial", description="Es lo que envia el docente como texto para generar el quiz")
    point_max: int = Field(..., example=20, description="Puntaje máximo del quiz")
    competences: List[CompetenceInfo] = Field(..., description="Lista de competencias relacionadas")
    type_question: TypeQuestionFlags = Field(..., description="Tipos de preguntas a incluir")
#----------------------------------------------------
class Answer_Created_Base(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID base de respuesta")
    type: str = Field(..., description="Tipo de respuesta (texto o multiple_opcion)")

class AnswerText(Answer_Created_Base):
    pass

class AnswerMultipleOption(Answer_Created_Base):
    options: Optional[list[str]] = Field(None, example=["Rojo", "Azul"], description="Opciones disponibles")

class Question(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID de la pregunta")
    statement: Optional[str] = Field(None, example="¿Cuál es 2 + 2?", description="Enunciado")
    answer_correct: Optional[str] = Field(None, example="4", description="Respuesta correcta")
    points: Optional[int] = Field(None, example=10, description="Puntos")
    answer: Optional[AnswerText | AnswerMultipleOption] =Field(None, description="tipo de respuesta condigurada")

class Quiz(BaseModel):
    quiz_id: int = Field(..., example=1, description="ID del quiz que se responde")
    student_id: int = Field(..., example=2, description="ID del estudiante que responde")
    is_present: bool = Field(..., example=True, description="Indica si el estudiante estuvo presente")
    questions: List[SubmittedQuestion] = Field(..., description="Lista de preguntas respondidas")

class Answer_Submitted_Base(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID de respuesta enviada")
    type: str = Field(..., description="Tipo de respuesta enviada (texto_respuesta o opcion_multiple_respuesta)")

class Text(Answer_Submitted_Base):
    answer_written: Optional[str] = Field(None, example="Mi respuesta escrita", description="Respuesta del estudiante")

class MultipleOption(Answer_Submitted_Base):
    option_select: Optional[int] = Field(None, example=2, description="Opción seleccionada")

class Classroom_Quiz(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID del aula")
    name: Optional[str] = Field(None, example="4to Básico", description="Nombre del aula")
    description: Optional[str] = Field(None, example="Clase de matemáticas", description="Descripción")
    quicces: Optional[list[Quiz]] =Field(None, description="Lista de quizzes asociados a la clase")



class Quiz_Question(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID del quiz")
    title: Optional[str] = Field(None, example="Evaluación Matemática", description="Título del quiz")
    instructions: Optional[str] = Field(None, example="Responde todas las preguntas", description="Instrucciones")
    start_time: Optional[str] = Field(None, example="2025-06-01T10:00:00", description="Inicio")
    end_time: Optional[str] = Field(None, example="2025-06-01T10:30:00", description="Fin")
    questions: Optional[list[Question]] =Field(None, description="Lista de questions asociadas al quiz")

class Student_Competence(BaseModel):
    id_competence: Optional[int] = Field(None, example=1, description="id de la competencia")
    student: Optional[DtoStudent] =Field(None, description="Estudiantes del classroom")
    obtained_points: Optional[int] = Field(None, example=10, description="puntos obtenidos por competencia")
    total_points: Optional[int] = Field(None, example=50, description="puntos totales posibles por competencia")

class Classroom_Student_Competence(BaseModel):
    competences: Optional[list[Competence]] =Field(None, description="Lista de competences asociadas al classroom")
    students_competence: Optional[list[Student_Competence]] =Field(None, description="Lista de competences asociadas al classroom por cada estudiante")
    
class Quiz_Student(BaseModel):
    id_quiz: Optional[int] = Field(None, example=1, description="id del quiz")
    student: Optional[DtoStudent] =Field(None, description="Estudiantes que rindieron el quiz")
    feedback_general_automated : Optional[str] =Field(None, description="feedback generador por la IA")
    feedback_general_teacher : Optional[str] =Field(None, description="feedback generador por el docente")
    total_points : Optional[int] =Field(None, description="puntos posibles en el quiz")
    points_obtained : Optional[int] =Field(None, description="puntos obtenidos en el quiz")
    is_present_quiz: Optional[bool] =Field(None, description="el estudiante rindio o no el quiz")

class Student_Question(BaseModel):
    student: Optional[DtoStudent] =Field(None, description="Estudiantes que rindieron el quiz")
    id_question: Optional[int] =Field(None, description="id de la question")
    answer_subtmitted: Optional[Text | MultipleOption] =Field(None, description="respuesta enviada")
    feedback_automated : Optional[str] =Field(None, description="feedback generador por la IA")
    feedback_teacher : Optional[str] =Field(None, description="feedback generador por el docente")
    total_points : Optional[int] =Field(None, description="puntos posibles en la question")
    points_obtained : Optional[int] =Field(None, description="puntos obtenidos en la question")

class Student_Quiz(BaseModel):
    id_quiz: Optional[int] = Field(None, example=1, description="id del quiz")
    student: Optional[DtoStudent] =Field(None, description="Estudiantes que rindieron el quiz")
    student_question: Optional[list[Student_Question]]= Field(None, description="lista de preguntas respondidas por el estudiante")

#---------------------------------------------------------------
# Esquema para el tipo de respuesta de texto con ID
class AnswerBaseTextDetail(BaseModel):
    id_answer: Optional[int] = Field(None, example=1, description="ID único de la configuración de respuesta")
    type: Literal["base_text"] = "base_text"

# Esquema para el tipo de respuesta de opción múltiple con ID y opciones
class AnswerBaseMultipleOptionDetail(BaseModel):
    id_answer: Optional[int] = Field(None, example=2, description="ID único de la configuración de respuesta")
    type: Literal["base_multiple_option"] = "base_multiple_option"
    options: List[str] = Field(..., example=["1810", "1821", "1910", "1857"], description="Opciones de respuesta")

# Unión de los tipos de respuesta base para ser usados en QuestionDetail
AnswerBaseDetail = Union[AnswerBaseTextDetail, AnswerBaseMultipleOptionDetail]


# Esquema para los detalles completos de una pregunta en el QuizDetail
class QuestionDetail(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID único de la pregunta")
    statement: str = Field(..., example="enunciado de la pregunta 1", description="Enunciado de la pregunta")
    answer_correct: str = Field(..., example="esta es la respuesta correcta", description="Respuesta correcta a la pregunta")
    points: int = Field(..., example=10, description="Puntos que otorga la pregunta")
    # Usa la unión de los esquemas de respuesta base detallados
    answer_base: AnswerBaseDetail = Field(..., description="Detalles de la configuración de la respuesta")
    competences_id: List[int] = Field(..., example=[1, 2], description="Lista de IDs de competencias asociadas a la pregunta")


# Esquema principal para el detalle completo del Quiz
class QuizDetail(BaseModel):
    id: int = Field(..., example=1, description="ID único del quiz")
    title: str = Field(..., example="titulo 1", description="Título del quiz")
    instruction: Optional[str] = Field(None, example="Esta es la instruccion", description="Instrucciones del quiz")
    start_time: datetime = Field(..., example="2025-06-09T15:30:00Z", description="Fecha y hora de inicio del quiz")
    end_time: datetime = Field(..., example="2025-06-09T16:40:00Z", description="Fecha y hora de fin del quiz")
    created_at: datetime = Field(..., example="2025-06-09T15:30:00Z", description="Fecha de creación del quiz")
    updated_at: datetime = Field(..., example="2025-06-09T16:30:00Z", description="Fecha de última actualización del quiz")
    # Una lista de las preguntas con sus detalles completos
    questions: List[QuestionDetail] = Field(..., description="Lista de preguntas detalladas en el quiz")
# -----------------------------------------------------------------
class ResultAnswerBaseText(BaseModel):
    id_answer: Optional[int] = Field(None, example=1, description="ID único de la configuración de respuesta")
    type: Literal["base_text"] = "base_text"

class ResultAnswerBaseMultipleOption(BaseModel):
    id_answer: Optional[int] = Field(None, example=2, description="ID único de la configuración de respuesta")
    type: Literal["base_multiple_option"] = "base_multiple_option"
    options: List[str] = Field(..., example=["1810", "1821", "1910", "1857"], description="Opciones de respuesta")

# Unión de los tipos de respuesta base
ResultAnswerBaseDetail = Union[ResultAnswerBaseText, ResultAnswerBaseMultipleOption]

# --- Respuestas Enviadas por el Estudiante ---

# Clase para la respuesta enviada por el estudiante (tipo texto)
class ResultAnswerSubmittedText(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID de la respuesta enviada por el estudiante")
    type: Literal["submitted_text"] = "submitted_texts" # Usar Literal para el discriminador
    answer_written: str = Field(..., example="es mi respuesta", description="Texto escrito por el estudiante")

# Clase para la respuesta enviada por el estudiante (tipo opción múltiple)
class ResultAnswerSubmittedMultipleOption(BaseModel):
    id: Optional[int] = Field(None, example=2, description="ID de la respuesta enviada por el estudiante")
    type: Literal["submitted_multiple_option"] = "submitted_multiple_options" # Usar Literal para el discriminador
    option_select: str = Field(..., example="1810", description="Opción seleccionada por el estudiante")

# Unión de los tipos de respuesta enviada por el estudiante
ResultAnswerSubmittedDetail = Union[ResultAnswerSubmittedText, ResultAnswerSubmittedMultipleOption]

# --- Detalles de Pregunta en el Resultado del Quiz ---

class ResultQuestionDetail(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID único de la pregunta")
    statement: str = Field(..., example="enunciado de la pregunta 1", description="Enunciado de la pregunta")
    answer_correct: str = Field(..., example="esta es la respuesta correcta", description="Respuesta correcta a la pregunta")
    points: int = Field(..., example=10, description="Puntos máximos que valía la pregunta")
    
    answer_base: ResultAnswerBaseDetail = Field(..., description="Detalles de la configuración original de la respuesta")
    
    feedback_automated: Optional[str] = Field(None, example="es el feedback automatico", description="Feedback automático para la pregunta")
    feedback_teacher: Optional[str] = Field(None, example="es el feedback del teacher", description="Feedback del profesor para la pregunta")
    points_obtained: Optional[int] = Field(None, example=10, description="Puntos obtenidos en esta pregunta")
    
    answer_submitted: Optional[ResultAnswerSubmittedDetail] = Field(None, description="Respuesta enviada por el estudiante")
    
    competences_id: List[int] = Field(..., example=[1, 2], description="Lista de IDs de competencias asociadas a la pregunta")

# --- Modelo Principal: QuizResultDetail ---

class QuizResultDetail(BaseModel):
    id: int = Field(..., example=1, description="ID único del quiz")
    title: str = Field(..., example="titulo 1", description="Título del quiz")
    instruction: Optional[str] = Field(None, example="Esta es la instruccion", description="Instrucciones del quiz")
    start_time: datetime = Field(..., example="2025-06-09T15:30:00Z", description="Fecha y hora de inicio del quiz")
    end_time: datetime = Field(..., example="2025-06-09T16:40:00Z", description="Fecha y hora de fin del quiz")
    created_at: datetime = Field(..., example="2025-06-09T15:30:00Z", description="Fecha de creación del quiz")
    updated_at: datetime = Field(..., example="2025-06-09T16:30:00Z", description="Fecha de última actualización del quiz")
    
    feedback_automated: Optional[str] = Field(None, example="es el feedback automatico", description="Feedback automático general del quiz")
    feedback_teacher: Optional[str] = Field(None, example="es el feedback del teacher", description="Feedback general del profesor para el quiz")
    points_obtained: Optional[int] = Field(None, example=15, description="Puntos obtenidos en el quiz total")

    questions: List[ResultQuestionDetail] = Field(..., description="Lista de preguntas detalladas en el quiz, incluyendo respuestas y feedback")
#------------------------------------------------------

class EnrichedStudentRankingEntry(BaseModel):
    ranking: int = Field(..., example=1, description="Posición del estudiante en el ranking.")
    obtained_points: int = Field(..., example=329, description="Puntos obtenidos por el estudiante.")
    student: DtoStudent = Field(..., description="La informacion del estudiante")
    
class StudentRankingEntry(BaseModel):
    ranking: int = Field(..., example=1, description="Posición del estudiante en el ranking.")
    obtained_points: int = Field(..., example=329, description="Puntos obtenidos por el estudiante.")
    student: int = Field(..., description="La informacion del estudiante")



#-----------------------------------------------------------------------
class Character(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID del personaje")
    sexo: Optional[str] = Field(None, example="Masculino", description="Sexo del personaje")
    hair: Optional[int] = Field(None, example=2, description="ID del peinado")
    shoes: Optional[int] = Field(None, example=3, description="ID de zapatos")
    upper_clothes_activated: Optional[int] = Field(None, example=1, description="Ropa superior activa")
    lower_clothes_activated: Optional[int] = Field(None, example=1, description="Ropa inferior activa")
    hair_activated: Optional[int] = Field(None, example=1, description="Peinado activo")
    shoes_activated: Optional[int] = Field(None, example=1, description="Zapatos activos")
    accesories_activated: Optional[list[int]] = Field(None, description="IDs de accesorios activos")

class Accessory(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID del accesorio")
    name: Optional[str] = Field(None, example="Gafas", description="Nombre del accesorio")
    model: Optional[str] = Field(None, example="BlenderFile001", description="Modelo 3D")

class UpperClothes(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID ropa superior")
    name: Optional[str] = Field(None, example="Camisa", description="Nombre de la prenda")
    model: Optional[str] = Field(None, example="BlenderFile002", description="Modelo 3D")

class LowerClothes(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID ropa inferior")
    name: Optional[str] = Field(None, example="Pantalones", description="Nombre de la prenda")
    model: Optional[str] = Field(None, example="BlenderFile003", description="Modelo 3D")

class Hair(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID del peinado")
    name: Optional[str] = Field(None, example="Corto", description="Nombre del peinado")
    model: Optional[str] = Field(None, example="BlenderFile004", description="Modelo 3D")

class Shoes(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID de los zapatos")
    name: Optional[str] = Field(None, example="Zapatillas", description="Nombre del calzado")
    model: Optional[str] = Field(None, example="BlenderFile005", description="Modelo 3D")

class Store(BaseModel):
    upperClothes: Optional[list[UpperClothes]]= Field(None, description="lista de upper clothes en la tienda")
    lowerClothes: Optional[list[LowerClothes]]= Field(None, description="lista de lower clothes en la tienda")
    hair: Optional[list[Hair]]= Field(None, description="lista de hair  en la tienda")
    shoes: Optional[list[Shoes]]= Field(None, description="lista de shoes en la tienda")
    accesory: Optional[list[Accessory]]= Field(None, description="lista de accesory en la tienda")


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

class CharacterPurchase(BaseModel):
    characterId: int
    userId: int

class CharacterSetPrincipal(BaseModel):
    userId: int
    oldCharacterId: int
    newCharacterId: int

class StudentDetailOutput(BaseModel):
    id: int = Field(..., description="ID único del estudiante.")
    name: str = Field(..., description="Nombre del estudiante.")
    last_name: str = Field(..., description="Apellido del estudiante.")
    email: str = Field(..., description="Correo electrónico del estudiante.")
    cel_phone: Optional[str] = Field(None, description="Número de teléfono celular del estudiante.")
    role: str = Field(..., description="Rol del usuario (ej. 'STUDENT').")
    emotion: Optional[str] = Field(None, description="Emoción actual del estudiante.")
    coin_earned: int = Field(..., description="Monedas ganadas por el estudiante.")
    coin_available: int = Field(..., description="Monedas disponibles para el estudiante.")
    points_obtained: int = Field(..., description="Puntos obtenidos por el estudiante en el quiz.")

    class Config:
        from_attributes = True


