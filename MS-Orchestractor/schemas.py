from pydantic import BaseModel, EmailStr, Field
from typing import Optional,Union
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
    registration_date: Optional[datetime] = Field(None, example="2024-07-01")

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

class DtoTeacher(DtoUser):
    pass

class Competence(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID de competencia")
    id_teacher: Optional[int] = Field(None, example=1, description="ID del profesor")
    name: Optional[str] = Field(None, example="Lógica matemática", description="Nombre")
    description: Optional[str] = Field(None, example="Descripción de la competencia")


class Classroom(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID del aula")
    name: Optional[str] = Field(None, example="4to Básico", description="Nombre del aula")
    description: Optional[str] = Field(None, example="Clase de matemáticas", description="Descripción")




class Quiz(BaseModel):
    id: Optional[int] = Field(None, example=1, description="ID del quiz")
    title: Optional[str] = Field(None, example="Evaluación Matemática", description="Título del quiz")
    instructions: Optional[str] = Field(None, example="Responde todas las preguntas", description="Instrucciones")
    start_time: Optional[str] = Field(None, example="2025-06-01T10:00:00", description="Inicio")
    end_time: Optional[str] = Field(None, example="2025-06-01T10:30:00", description="Fin")




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


