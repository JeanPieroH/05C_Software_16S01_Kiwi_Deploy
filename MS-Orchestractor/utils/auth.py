from fastapi import Request, HTTPException
import httpx
import os

USERS_URL = os.getenv("USERS_API_URL", "http://localhost:8080")
        
async def verify_token(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{USERS_URL}/auth/validate-token", headers={"Authorization": request.headers.get("authorization")})
            res.raise_for_status()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

async def verify_token_role_teacher(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{USERS_URL}/auth/validate-token/teacher", headers={"Authorization": request.headers.get("authorization")})
            res.raise_for_status()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

async def verify_token_role_student(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{USERS_URL}/auth/validate-token/student", headers={"Authorization": request.headers.get("authorization")})
            res.raise_for_status()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
