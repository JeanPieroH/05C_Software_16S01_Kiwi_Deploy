from fastapi import APIRouter, HTTPException, Header
from schemas import DtoUserLogin, DtoUserRegister, Token
import httpx
import os

router = APIRouter()
users_url = os.getenv("USERS_API_URL", "http://localhost:8080")
classrooms_url = os.getenv("CLASSROOMS_API_URL", "http://localhost:3000")
quices_url = os.getenv("QUICES_API_URL", "http://localhost:8001/api/v1")

print("USERS_API_URL:", users_url)


@router.post("/login", response_model=Token)
async def login(userLogin: DtoUserLogin):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{users_url}/auth/login", json=userLogin.model_dump())
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/register", response_model=Token)
async def register(userRegister: DtoUserRegister):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{users_url}/auth/register", json=userRegister.model_dump())
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
