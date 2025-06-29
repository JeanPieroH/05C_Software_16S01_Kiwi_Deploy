from fastapi import APIRouter, Request, Depends, HTTPException, status
from schemas import *
from utils.auth import verify_token_role_student
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(dependencies=[Depends(verify_token_role_student)])

classrooms_url = os.getenv("CLASSROOMS_URL", "http://localhost:8003")
quices_url = os.getenv("QUICES_URL", "http://localhost:8002/api/v1")
users_url = os.getenv("USERS_URL", "http://localhost:8001")

@router.get("/me", response_model=Student)
async def getStudent(request:Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{users_url}/student/me",headers=dict(request.headers))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
@router.patch("/me", response_model=Student)
async def patchStudent(request:Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f"{users_url}/student/me",headers=dict(request.headers))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
@router.post("/classroom/{classroom_id}/quiz-submit", status_code=status.HTTP_201_CREATED)
async def submmitted_answer(classroom_id: int, quiz_submit: QuizSubmission,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            quiz_submit_dict = quiz_submit.model_dump()
            quiz_response = await client.post(f"{quices_url}/quiz/submit_answers",json=quiz_submit_dict,timeout=60)
            quiz_response.raise_for_status()
            response = await client.patch(f"{classrooms_url}/classrooms/{classroom_id}/student-quiz-points",json=quiz_response.json())
            response.raise_for_status()
            response.json()
            await client.post(f"""{users_url}/student/{quiz_submit.student_id}/add-coins/{quiz_response.json().get("obtained_points")}""", headers={"Authorization": request.headers.get("authorization")})

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.get("/classroom/{classroom_id}/student/{student_id}/quiz-list", response_model=List[QuizWithAttemptStatusOutput])
async def get_quiz_list(classroom_id: int,student_id:int, request:Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{quices_url}/quiz/classroom/{classroom_id}/student/{student_id}",headers=dict(request.headers))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)