from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import include_all_routers

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Frontend local
        "http://localhost:8080",  # MS Users
        "http://localhost:8001",  # MS Quices
        "http://localhost:3000",  # Otros MS si aplican
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

include_all_routers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
