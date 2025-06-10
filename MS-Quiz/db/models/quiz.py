from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr, as_declarative
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from db.database import Base # Asumo que 'db.database' es donde tienes tu 'Base'

# --- Modelos de Entidades ---

class Quiz(Base):
    """
    Modelo para almacenar la información básica de un quiz
    """
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    id_classroom = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    instruction = Column(Text, nullable=True) # Renombrado de 'instructions' a 'instruction'
    total_points = Column(Integer, default=0) # Nuevo campo 'total_points'
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    # 'questions' y 'students' (mapeado a quiz_students)
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    quiz_students = relationship("Quiz_Student", back_populates="quiz", cascade="all, delete-orphan")

class Quiz_Student(Base):
    """
    Modelo para la relación de un estudiante con un quiz.
    Clave primaria compuesta: (id_student, id_quiz).
    """
    __tablename__ = "quiz_students"

    id_student = Column(Integer, primary_key=True, index=True)
    id_quiz = Column(Integer, ForeignKey("quizzes.id"), primary_key=True)
    feedback_general_automated = Column(Text, nullable=True)
    feedback_general_teacher = Column(Text, nullable=True)
    points_obtained = Column(Integer, default=0)
    is_present_quiz = Column(Boolean, default=False) # Usar Boolean para tipo booleano

    # Relaciones
    quiz = relationship("Quiz", back_populates="quiz_students")
    # 'id_student' es una FK de otro microservicio, no necesita relación ORM explícita aquí.

class Question(Base):
    """
    Modelo para almacenar las preguntas de un quiz.
    """
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    # Se añade quiz_id para la relación con Quiz, necesario para que 'questions' en Quiz funcione.
    quiz_id = Column(Integer, ForeignKey("quizzes.id")) 
    id_answer = Column(Integer, ForeignKey("answer_bases.id"), nullable=True) # FK a Answer_Base (tabla base de la herencia unida)
    statement = Column(Text, nullable=False)
    answer_correct = Column(Text, nullable=True) # Mantenido según tu diagrama
    points = Column(Integer, default=1)
    # 'question_type' eliminado ya que Answer_Base.type y Answer_Submitted.type gestionan la variedad de respuestas
    created_at = Column(DateTime, default=datetime.now)
    
    # Relaciones
    quiz = relationship("Quiz", back_populates="questions")
    
    # Relación con Answer_Base para la respuesta correcta (ahora apunta a la base de la herencia unida)
    answer_base = relationship("Answer_Base", back_populates="question", uselist=False, cascade="all, delete-orphan", single_parent=True)
    
    # Relación con Question_Student (q_students en tu diagrama)
    students = relationship("Question_Student", back_populates="question", cascade="all, delete-orphan")
    
    competences_id = Column(ARRAY(Integer), default=[])
    # 'students': List<Student> - id_student de otro microservicio, no se mapea aquí directamente.
    # 'comp_option': List<Competence_Question> - No se ha definido un modelo para Competence_Question.

class Question_Student(Base):
    """
    Modelo para la relación de la respuesta de un estudiante a una pregunta.
    Clave primaria compuesta: (id_student, id_question, id_answer_submitted).
    """
    __tablename__ = "question_students"
    
    id_student = Column(Integer, primary_key=True, index=True) # FK de otro microservicio
    id_question = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    id_answer_submitted = Column(Integer, ForeignKey("answer_submitteds.id"), primary_key=True)
    feedback_automated = Column(Text, nullable=True)
    feedback_teacher = Column(Text, nullable=True)
    points_obtained = Column(Integer, default=0)
    
    # Relaciones
    question = relationship("Question", back_populates="students")
    answer_submitted = relationship("Answer_Submitted", back_populates="question_students", uselist=False)



### Modelos para Respuestas (Herencia de Tabla Unida)

class Answer_Base(Base):
    """
    Modelo base para almacenar la información común de la respuesta correcta de una pregunta.
    Tabla principal en la herencia de tabla unida.
    """
    __tablename__ = "answer_bases" # Nombre de la tabla base

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False) # Columna discriminadora

    # Relación inversa con Question. 'Question.id_answer' debe apuntar a esta tabla.
    question = relationship("Question", back_populates="answer_base")

    __mapper_args__ = {
        'polymorphic_identity': 'answer_base',
        'polymorphic_on': type # Columna que actúa como discriminador
    }

class Base_Text(Answer_Base):
    """
    Respuesta correcta de tipo texto, hereda de Answer_Base (tabla unida).
    """
    __tablename__ = "base_texts" # Tabla específica para Base_Text

    # La PK es también una FK a la tabla base, creando la relación uno a uno
    id = Column(Integer, ForeignKey('answer_bases.id'), primary_key=True) 
    # El campo `answer_written` del diagrama original se ha eliminado de Base_Text,
    # ya que no aparece en tu último modelo para Base_Text.
    # Si se necesita un campo 'answer_written' aquí, debe ser especificado en el diagrama.

    __mapper_args__ = {
        'polymorphic_identity': 'base_text',
        'inherit_condition': (id == Answer_Base.id) # Condición de unión
    }

class Base_Multiple_Option(Answer_Base):
    """
    Respuesta correcta de tipo opción múltiple, hereda de Answer_Base (tabla unida).
    """
    __tablename__ = "base_multiple_options" # Tabla específica para Base_Multiple_Option

    # La PK es también una FK a la tabla base, creando la relación uno a uno
    id = Column(Integer, ForeignKey('answer_bases.id'), primary_key=True)
    options = Column(Text, nullable=False) # Almacenar como un string JSON o similar
    
    __mapper_args__ = {
        'polymorphic_identity': 'base_multiple_option',
        'inherit_condition': (id == Answer_Base.id) # Condición de unión
    }

class Answer_Submitted(Base):
    """
    Modelo base para almacenar la respuesta enviada por un estudiante (abstracta).
    Tabla principal en la herencia de tabla unida.
    """
    __tablename__ = "answer_submitteds" # Nombre de la tabla base

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False) # Columna discriminadora

    question_students = relationship("Question_Student", back_populates="answer_submitted")

    __mapper_args__ = {
        'polymorphic_identity': 'answer_submitted',
        'polymorphic_on': type # Columna que actúa como discriminador
    }

class Submitted_Text(Answer_Submitted):
    """
    Respuesta de estudiante de tipo texto, hereda de Answer_Submitted (tabla unida).
    """
    __tablename__ = "submitted_texts" # Tabla específica para Submitted_Text

    # La PK es también una FK a la tabla base, creando la relación uno a uno
    id = Column(Integer, ForeignKey('answer_submitteds.id'), primary_key=True)
    answer_written = Column(Text, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'submitted_text',
        'inherit_condition': (id == Answer_Submitted.id) # Condición de unión
    }

class Submitted_Multiple_Option(Answer_Submitted):
    """
    Respuesta de estudiante de tipo opción múltiple, hereda de Answer_Submitted (tabla unida).
    """
    __tablename__ = "submitted_multiple_options" # Tabla específica para Submitted_Multiple_Option

    # La PK es también una FK a la tabla base, creando la relación uno a uno
    id = Column(Integer, ForeignKey('answer_submitteds.id'), primary_key=True)
    option_select = Column(Text, nullable=True) # Podría ser un índice o el ID de la opción seleccionada

    __mapper_args__ = {
        'polymorphic_identity': 'submitted_multiple_option',
        'inherit_condition': (id == Answer_Submitted.id) # Condición de unión
    }