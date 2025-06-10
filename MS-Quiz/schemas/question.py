from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class QuestionOptionBase(BaseModel):
    option_text: str
    is_correct: bool

class QuestionOptionCreate(QuestionOptionBase):
    pass

class QuestionOption(QuestionOptionBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    statement: str
    question_type: str = "text"  # text, opcion multiple
    points: int = 1
    answer_correct: Optional[str] = None

class QuestionCreate(QuestionBase):
    options: Optional[List[QuestionOptionCreate]] = None

class QuestionUpdate(BaseModel):
    statement: Optional[str] = None
    question_type: Optional[str] = None
    points: Optional[int] = None
    answer_correct: Optional[str] = None

class Question(QuestionBase):
    id: int
    quiz_id: int
    
    class Config:
        from_attributes = True

class QuestionWithOptions(Question):
    options: List[QuestionOption]
    
    class Config:
        from_attributes = True
