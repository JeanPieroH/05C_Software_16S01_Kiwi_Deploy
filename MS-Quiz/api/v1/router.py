from fastapi import APIRouter

from api.v1.endpoints import quiz, question

api_router = APIRouter()

# # # Rutas de los endpoints (TODO decirles en el grupo de wsp que usen los prefijos)
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
# api_router.include_router(question.router, prefix="/question", tags=["Question"])