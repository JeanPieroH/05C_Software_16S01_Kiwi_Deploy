import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from utils.auth import verify_token
from schemas import *
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(dependencies=[Depends(verify_token)])
characters_url = os.getenv("CHARACTER_URL", "http://localhost:8004")
users_url = os.getenv("USERS_API_URL", "http://localhost:8001")


@router.get("/store")
async def get_characters(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{characters_url}/store")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al conectar con el servicio de personajes: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_characters(user_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        try:
            user_response = await client.get(
                f"{users_url}/student/{user_id}", 
                headers={"Authorization": request.headers.get("authorization")}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            response = await client.get(f"{characters_url}/characters/user/{user_id}")
            
            if response.status_code != 200:
                if response.status_code == 404:
                    return {"principal": None, "characters": {}}
                raise HTTPException(status_code=response.status_code, detail="Error al obtener los personajes del usuario")
            
            return response.json()
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al conectar con los servicios: {str(e)}")

@router.post("/buy")
async def buy_character(request: Request):
    try:
        body = await request.json()
        
        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="El cuerpo de la solicitud debe ser un objeto JSON")
        
        characterId = body.get("characterId")
        userId = body.get("userId")
        
        if not characterId or not userId:
            raise HTTPException(status_code=400, detail="characterId y userId son requeridos")
        
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{users_url}/student/{userId}", 
                headers={"Authorization": request.headers.get("authorization")}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            user_data = user_response.json()

            character_response = await client.get(f"{characters_url}/store/{characterId}")
            
            if character_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Personaje no encontrado")
            
            character_data = character_response.json()
            
            if user_data.get("coin_available", 0) < character_data.get("price", 0):
                raise HTTPException(
                    status_code=400, 
                    detail="No tienes suficientes monedas para comprar este personaje"
                )
            
            user_characters_response = await client.get(f"{characters_url}/user/{userId}")
            
            if user_characters_response.status_code == 200:
                user_characters = user_characters_response.json()
                all_characters = []
                
                if user_characters.get("principal") and user_characters["principal"].get("id") == characterId:
                    raise HTTPException(status_code=400, detail="Ya posees este personaje")
                
                for char_type, chars in user_characters.get("characters", {}).items():
                    all_characters.extend(chars)
                
                if any(char.get("id") == characterId for char in all_characters):
                    raise HTTPException(status_code=400, detail="Ya posees este personaje")
            
            purchase_response = await client.post(
                f"{characters_url}/store/buy",
                json={"characterId": characterId, "userId": userId}
            )
            
            if purchase_response.status_code != 200:
                raise HTTPException(
                    status_code=purchase_response.status_code, 
                    detail="Error al comprar el personaje"
                )
            
            price = character_data.get('price', 0)
            coins_update_response = await client.post(
                f"{users_url}/student/{userId}/add-coins/{-price}",
                headers={"Authorization": request.headers.get("authorization")}
            )
            
            if coins_update_response.status_code != 200:
                await client.delete(
                    f"{characters_url}/user/{userId}/characters/{characterId}"
                )
                raise HTTPException(status_code=500, detail="Error al actualizar las monedas del usuario")
            
            return {"message": "Personaje comprado con éxito", "character": character_data}
            
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la compra: {str(e)}")

@router.patch("/set-principal")
async def set_principal_character(request: Request):
    try:
        body = await request.json()
        
        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="El cuerpo de la solicitud debe ser un objeto JSON")
        
        userId = body.get("userId")
        oldCharacterId = body.get("oldCharacterId")
        newCharacterId = body.get("newCharacterId")
        
        if not userId or not oldCharacterId or not newCharacterId:
            raise HTTPException(status_code=400, detail="userId, oldCharacterId y newCharacterId son requeridos")
        
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{users_url}/student/{userId}", 
                headers={"Authorization": request.headers.get("authorization")}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            response = await client.patch(
                f"{characters_url}/characters/set-principal",
                json={
                    "userId": userId,
                    "oldCharacterId": oldCharacterId,
                    "newCharacterId": newCharacterId
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail="Error al establecer el personaje principal"
                )
            
            return response.json()
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con el servicio de personajes: {str(e)}")

@router.post("")
async def create_character(request: Request):
    try:
        body = await request.json()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{characters_url}/characters",
                json=body
            )
            
            if response.status_code != 200 and response.status_code != 201:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail="Error al crear el personaje"
                )
            
            return response.json()
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con el servicio de personajes: {str(e)}")

@router.get("/{character_id}")
async def get_character_by_id(character_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{characters_url}/characters/{character_id}")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail="Error al obtener el personaje"
                )
            
            return response.json()
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al conectar con el servicio de personajes: {str(e)}")
