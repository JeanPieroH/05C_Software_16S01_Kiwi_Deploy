from fastapi import APIRouter, Request, Depends, HTTPException, status,UploadFile,File,Form
from schemas import *
from utils.auth import verify_token_role_teacher
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(dependencies=[Depends(verify_token_role_teacher)])

classrooms_url = os.getenv("CLASSROOMS_URL", "http://localhost:8003")
quices_url = os.getenv("QUICES_URL", "http://localhost:8002/api/v1")
users_url = os.getenv("USERS_URL", "http://localhost:8001")

@router.get("/me", response_model=Teacher)

async def geTeacher(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{users_url}/teacher/me",headers=dict(request.headers))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

#Vista principal
@router.patch("/me", response_model=Teacher)
async def updateTeacher(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f"{users_url}/teacher/me",headers=dict(request.headers))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
        
@router.post("/{teacher_id}/classroom", status_code=status.HTTP_201_CREATED)
async def createClassroom(teacher_id: int, classroom: DtoClassroomCreate):
    async with httpx.AsyncClient() as client:
        try:
            classroom_dict = dict(classroom)
            classroom_dict['teachers'] = [teacher_id]
            response = await client.post(f"{classrooms_url}/classrooms",json=classroom_dict)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/classroom/{classroom_id}/add-users", status_code=status.HTTP_201_CREATED)
async def createClassroom(classroom_id: int, emails: ListEmail,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            students_id = await client.post(f"{users_url}/student/ids-by-email",json=emails.model_dump(), headers={"Authorization": request.headers.get("authorization")})
            students_id.raise_for_status()
            teachers_id = await client.post(f"{users_url}/teacher/ids-by-email",json=emails.model_dump(), headers={"Authorization": request.headers.get("authorization")})
            teachers_id.raise_for_status()
            response = await client.post(f"{classrooms_url}/classrooms/{classroom_id}/add-students",json=students_id.json())
            response.raise_for_status()
            response = await client.post(f"{classrooms_url}/classrooms/{classroom_id}/add-teachers",json=teachers_id.json())
            response.raise_for_status()
        
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.post("/{teacher_id}/competences", status_code=status.HTTP_201_CREATED)
async def createClassroom(teacher_id: int, classroom: DtoCompetenceCreate):
    async with httpx.AsyncClient() as client:
        try:
            classroom_dict = dict(classroom)
            classroom_dict['id_teacher'] = teacher_id
            response = await client.post(f"{classrooms_url}/competences",json=classroom_dict)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        

@router.get("/{teacher_id}/competences", response_model=List[Competence])
async def get_classroom_teachers(teacher_id: int,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{classrooms_url}/competences/teacher/{teacher_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
@router.post("/classroom/{classroom_id}/competences-associate", status_code=status.HTTP_201_CREATED)
async def associate_competence(classroom_id: int, competencesId: CompetenceIdsRequest,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            competencesId_dict = dict(competencesId)
            response = await client.post(f"{classrooms_url}/classrooms/{classroom_id}/competences/associate",json=competencesId_dict)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.post("/classroom/{classroom_id}/quiz/create", status_code=status.HTTP_201_CREATED)
async def createQuiz(classroom_id: int, quiz_create: DtoQuizCreate,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            print(quiz_create.model_dump_json())
            quiz_response = await client.post(f"{quices_url}/quiz/create",content=quiz_create.model_dump_json(),headers={"Content-Type": "application/json"})
            quiz_response.raise_for_status()
            quiz_response.json()
            response = await client.patch(f"{classrooms_url}/classrooms/{classroom_id}/quizzes-competences",json=quiz_response.json())
            response.raise_for_status()
            response.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        

@router.post("/quiz/generate-from-pdf", status_code=status.HTTP_201_CREATED, response_model=DtoQuizCreate)
async def generate_quiz_from_pdf(request_quiz: str=File(alias="input_data_json"),file: UploadFile =File(alias="pdf_file")):
    try:
        pdf_content = await file.read()  # Serializa el Pydantic model a string JSON
        #input_data_json_str=request_quiz.json()
        files = {
            "pdf_file": (file.filename, pdf_content, file.content_type),
            "input_data_json": (None, request_quiz, "application/json"),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{quices_url}/quiz/generate-from-pdf", files=files,timeout=30.0)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/quiz/generate-from-text", status_code=status.HTTP_201_CREATED, response_model=DtoQuizCreate)
async def generate_quiz_from_text(request_quiz: QuizAutoGenerateRequest_TEXT):
    try:
        input_data_json_str = request_quiz.json()  # Serializa el Pydantic model a string JSON

        files = {
            "input_data_json": (None, input_data_json_str, "application/json"),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{quices_url}/quiz/generate-from-text", files=files,timeout=30.0)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)