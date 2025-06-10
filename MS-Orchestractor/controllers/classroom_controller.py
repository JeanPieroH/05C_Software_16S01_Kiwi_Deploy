from fastapi import APIRouter, Request, Depends, HTTPException, status
from schemas import *
from utils.auth import verify_token
import httpx
import os
import json

router = APIRouter(dependencies=[Depends(verify_token)])
classrooms_url = "http://localhost:3000"
quices_url = "http://localhost:8001/api/v1"
users_url = "http://localhost:8080"



# Pestaña
@router.get("/{classroom_id}/student", response_model=List[DtoStudent])
async def get_classroom_students(classroom_id: int,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            student_ids = await client.get(f"{classrooms_url}/classrooms/{classroom_id}/students")

            response = await client.post(f"{users_url}/student/by-ids",json=student_ids.json(), headers={"Authorization": request.headers.get("authorization")})
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.get("/{classroom_id}/teacher", response_model=List[DtoTeacher])
async def get_classroom_teachers(classroom_id: int,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            teacher_ids = await client.get(f"{classrooms_url}/classrooms/{classroom_id}/teachers")

            response = await client.post(f"{users_url}/teacher/by-ids",json=teacher_ids.json(), headers={"Authorization": request.headers.get("authorization")})
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
@router.get("/user/{user_id}", response_model=List[Classroom])
async def get_classroom_users(user_id: int,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{classrooms_url}/classrooms/user/{user_id}")
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.get("/{classroom_id}/competences", response_model=List[CompetenceService])
async def get_classroom_competences(classroom_id: int,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{classrooms_url}/competences/classroom/{classroom_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
@router.get("/{classroom_id}", response_model=ClassroomBase)
async def get_classroom_info(classroom_id: int,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            classroom_response = await client.get(f"{classrooms_url}/classrooms/{classroom_id}")
            classroom_response.raise_for_status()
            classroom_data = classroom_response.json()
            quiz_ids = classroom_data.get("quiz", [])
            if quiz_ids: # Esta condición es True si la lista no está vacía
                quiz_response = await client.post(f"{quices_url}/quiz/get-by-ids",json={"quiz_ids": quiz_ids})
                quiz_response.raise_for_status()
                quiz_details = quiz_response.json()
                classroom_data["quiz"] = quiz_details
            return classroom_data
        
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get("/{classroom_id}/ranking", response_model=List[EnrichedStudentRankingEntry])
async def get_classroom_ranking(classroom_id: int,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            classroom_response = await client.get(f"{classrooms_url}/classrooms/{classroom_id}/ranking")
            classroom_response.raise_for_status()
            ranking_data = [StudentRankingEntry(**item) for item in classroom_response.json()]
            student_ids_list = [entry.student for entry in ranking_data]
            students_details = await client.post(f"{users_url}/student/by-ids",json={"students_id": student_ids_list}, headers={"Authorization": request.headers.get("authorization")})
            student_details_map = {item['id']: DtoStudent(**item) for item in students_details.json()}
        
            enriched_ranking = []
            for entry in ranking_data:
                student_full_detail = student_details_map.get(entry.student)
                if student_full_detail:
                    enriched_ranking.append(EnrichedStudentRankingEntry(ranking=entry.ranking,obtained_points=entry.obtained_points,student=student_full_detail))

            return enriched_ranking
        
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get("/{classroom_id}/competence/{competence_id}/ranking", response_model=List[EnrichedStudentRankingEntry])
async def get_classroom_ranking_competence(classroom_id: int,competence_id:int,request: Request):
    async with httpx.AsyncClient() as client:
        try:
            classroom_response = await client.get(f"{classrooms_url}/classrooms/{classroom_id}/competences/{competence_id}/ranking")
            classroom_response.raise_for_status()
            ranking_data = [StudentRankingEntry(**item) for item in classroom_response.json()]
            student_ids_list = [entry.student for entry in ranking_data]
            students_details = await client.post(f"{users_url}/student/by-ids",json={"students_id": student_ids_list}, headers={"Authorization": request.headers.get("authorization")})
            student_details_map = {item['id']: DtoStudent(**item) for item in students_details.json()}
        
            enriched_ranking = []
            for entry in ranking_data:
                student_full_detail = student_details_map.get(entry.student)
                if student_full_detail:
                    enriched_ranking.append(EnrichedStudentRankingEntry(ranking=entry.ranking,obtained_points=entry.obtained_points,student=student_full_detail))

            return enriched_ranking
        
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)