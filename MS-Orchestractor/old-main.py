from fastapi import FastAPI, HTTPException, status, Response, Request, Form, File, UploadFile
import httpx
from schemas import *
from typing import List, Optional, Dict, Any
import os

app = FastAPI()

# Configuración de las url de los microservicios
#users_url = os.getenv("USERS_API_URL")
users_url="http://localhost:8080"
# classrooms_url = os.getenv("CLASSROOMs_API_URL")
quices_url = os.getenv("QUICES_API_URL", "http://localhost:8001/api/v1")
classrooms_url="http://localhost:3000"
# quices_url = os.getenv("QUICES_API_URL")
# characters_url = os.getenv("CHARACTERS_API_URL")



# Health check endpoint
@app.get("/")
def get_echo_test():
    return {"message": "Echo Test OK"}

# ----- CRUD Operations for auth -----
@app.post("/auth/login", response_model=Token)

async def login(userLogin:DtoUserLogin):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{users_url}/auth/login",json=userLogin.model_dump())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.post("/auth/register", response_model=Token)

async def register(userRegister:DtoUserRegister):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{users_url}/auth/register",json=userRegister.model_dump())
            response.raise_for_status()
            print(userRegister)
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


# ----- CRUD Operations for teacher -----

#Vista principal
@app.get("/teacher/me", response_model=Teacher)

async def geTeacher(request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{users_url}/teacher/me",headers=forward_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

#Vista principal
@app.patch("/teacher/me", response_model=Teacher)
async def updateTeacher(request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f"{users_url}/teacher/me",headers=forward_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
# Barra Lateral
@app.get("/teacher/{teacher_id}/competence", response_model=List[Competence])
async def get_teacher_competences(teacher_id: int,request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            validate_response = await client.post(f"{users_url}/auth/validate-token/teacher",headers=forward_headers)
            validate_response.raise_for_status()  

            patch_response = await client.get(f"{classrooms_url}/competences/teacher/{teacher_id}",headers=forward_headers)
            patch_response.raise_for_status()

            return patch_response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


# Vista principal
@app.get("/competence/{competence_id}", response_model=Competence)
async def get_teacher_competence_detail(teacher_id: int, competence_id: int,request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            validate_response = await client.post(f"{users_url}/auth/validate-token/teacher",headers=forward_headers)
            validate_response.raise_for_status()  

            response = await client.get(f"{classrooms_url}/competences/{competence_id}",headers=forward_headers)
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


# Vista principal
@app.get("/teacher/{teacher_id}/classroom", response_model=List[Classroom])
async def get_teacher_classrooms(teacher_id: int,request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            validate_response = await client.post(f"{users_url}/auth/validate-token/teacher",headers=forward_headers)
            validate_response.raise_for_status()  

            response = await client.get(f"{classrooms_url}/classrooms/teacher/{teacher_id}",headers=forward_headers)
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


# Vista principal

@app.get("/classroom/{classroom_id}", response_model=Classroom_Quiz)
async def get_classroom_detail(classroom_id: int,request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            validate_response = await client.post(f"{users_url}/auth/validate-token",headers=forward_headers)
            validate_response.raise_for_status()  

            response = await client.get(f"{classrooms_url}/classrooms/{classroom_id}",headers=forward_headers)
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


# Pestaña
@app.get("/classroom/{classroom_id}/teacher", response_model=List[Teacher])
async def get_classroom_teachers(classroom_id: int,request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            validate_response = await client.post(f"{users_url}/auth/validate-token",headers=forward_headers)
            validate_response.raise_for_status()  

            teacher_ids = await client.get(f"{classrooms_url}/classrooms/{classroom_id}/teacher",headers=forward_headers)
            response = await client.post(f"{users_url}/teacher/all-id",headers=forward_headers,json=teacher_ids.json())

            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


# Pestaña
@app.get("/classroom/{classroom_id}/student", response_model=List[Student])
async def get_classroom_students(classroom_id: int,request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            validate_response = await client.post(f"{users_url}/auth/validate-token",headers=forward_headers)
            validate_response.raise_for_status()  

            student_ids = await client.get(f"{classrooms_url}/classrooms/{classroom_id}/student",headers=forward_headers)
            response = await client.post(f"{users_url}/student/all-id",headers=forward_headers,json=student_ids.json())
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
        
@app.post("/classroom/{classroom_id}/competence/{competence_id}", status_code=status.HTTP_201_CREATED)
async def addCompetenceInClassroom(classroom_id:int , competence_id: int,request:Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            validate_response = await client.post(f"{users_url}/auth/validate-token/teacher",headers=forward_headers)
            validate_response.raise_for_status()  

            response = await client.post(f"{classrooms_url}/classrooms/{classroom_id}/competences/{competence_id}/associate",headers=forward_headers)

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)



# Pestaña
@app.get("/teacher/{teacher_id}/classroom/{classroom_id}/competence", response_model=Classroom_Student_Competence)
async def get_classroom_competences(teacher_id: int, classroom_id: int):
    pass


# Vista principal
@app.get("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}", response_model=Quiz_Question)
async def get_quiz_detail(teacher_id: int, classroom_id: int, quiz_id: int, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            # Obtener el quiz con sus preguntas
            response = await client.get(f"{quices_url}/quiz/{quiz_id}", headers=forward_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

# Vista principal
@app.get("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}/results", response_model=List[Quiz_Student])
async def get_quiz_results(teacher_id: int, classroom_id: int, quiz_id: int, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            # Obtener los resultados de todos los estudiantes que han presentado el quiz
            response = await client.get(f"{quices_url}/quiz/{quiz_id}/results", headers=forward_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

# Pestaña
@app.get("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}/results/student/{student_id}", response_model=Student_Quiz)
async def get_student_quiz_result(teacher_id: int, classroom_id: int, quiz_id: int, student_id: int, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            # Obtener el resultado específico de un estudiante
            response = await client.get(f"{quices_url}/quiz/{quiz_id}/results/student/{student_id}", headers=forward_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.post("/teacher/{teacher_id}/competence",status_code=status.HTTP_201_CREATED)
async def createCompetence(teacher_id: int, competence: Competence):
    pass

@app.post("/teacher/{teacher_id}/classroom", status_code=status.HTTP_201_CREATED)
async def createClassroom(teacher_id: int, classroom: Classroom):
    pass

@app.post("/teacher/{teacher_id}/classroom/{classroom_id}/students-email",status_code=status.HTTP_201_CREATED)

async def addStudentEmail(teacher_id: int, classroom_id:int ,email: list[Email]):
    pass

@app.post("/teacher/{teacher_id}/classroom/{classroom_id}/quiz", status_code=status.HTTP_201_CREATED)
async def createQuiz(teacher_id: int, classroom_id: int, quiz: Quiz, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            quiz_data = quiz.model_dump()
            quiz_data["id_classroom"] = classroom_id
            quiz_data["id_teacher"] = teacher_id
            
            response = await client.post(f"{quices_url}/quiz", json=quiz_data, headers=forward_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.post("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/generate", status_code=status.HTTP_201_CREATED)
async def generateQuiz(teacher_id: int, classroom_id: int, input_data: QuizGenerationInput, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            generation_data = input_data.model_dump()
            generation_data["id_classroom"] = classroom_id
            generation_data["id_teacher"] = teacher_id
            
            response = await client.post(f"{quices_url}/quiz/generate", json=generation_data, headers=forward_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.post("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/generate-from-pdf", status_code=status.HTTP_201_CREATED)
async def generateQuizFromPdf(
    teacher_id: int, 
    classroom_id: int,
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    num_questions: Optional[int] = Form(5),
    file: UploadFile = File(...)
):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            form_data = {
                "title": title,
                "id_classroom": str(classroom_id),
                "id_teacher": str(teacher_id),
                "num_questions": str(num_questions)
            }
            
            # Añadir descripción si se proporciona
            if description:
                form_data["description"] = description
            
            file_content = await file.read()
            
            files = {
                "file": (file.filename, file_content, file.content_type)
            }
            
            response = await client.post(
                f"{quices_url}/quiz/generate-from-pdf",
                data=form_data,
                files=files,
                headers=forward_headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.post("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}/question", status_code=status.HTTP_201_CREATED)
async def createQuestion(teacher_id: int, classroom_id: int, quiz_id: int, question: Question, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{quices_url}/question/quiz/{quiz_id}", 
                json=question.model_dump(), 
                headers=forward_headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.post("/teacher/{teacher_id}/classroom/{classroom_id}/competence/{competence_id}", status_code=status.HTTP_201_CREATED)
async def addCompetenceInClassroom(teacher_id: int, classroom_id:int , competence_id: int):
    pass

@app.post("/teacher/{teacher_id}/classroom/{classroom_id}/competence/result/student/{student_id}/{competence_id}/add-points/{points}", status_code=status.HTTP_201_CREATED)
async def addPointsStudent(teacher_id: int, classroom_id:int , student_id: int ,competence_id:int,points:int):
    pass


@app.patch("/teacher/{teacher_id}/classroom/{classroom_id}/students-email",status_code=status.HTTP_201_CREATED)
async def updateStudent(teacher_id: int, classroom_id:int ,email: list[Email]):
    pass

@app.patch("/teacher/{teacher_id}/classroom/{classroom_id}", status_code=status.HTTP_200_OK)
async def updateClassroom(teacher_id: int, classroom: Classroom):
    pass

@app.patch("/teacher/{teacher_id}/competence/{competence_id}", status_code=status.HTTP_200_OK)
async def updateCompetence(teacher_id: int, competence: Competence):
    pass

@app.patch("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}", status_code=status.HTTP_200_OK)
async def updateQuiz(teacher_id: int, classroom_id: int, quiz_id: int, quiz: Quiz, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            # Actualizar quiz existente
            response = await client.put(
                f"{quices_url}/quiz/{quiz_id}", 
                json=quiz.model_dump(), 
                headers=forward_headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.patch("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}/question/{question_id}", status_code=status.HTTP_200_OK)
async def updateQuestion(teacher_id: int, classroom_id: int, quiz_id: int, question_id: int, question: Question, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            # Actualizar pregunta existente
            response = await client.put(
                f"{quices_url}/question/{question_id}", 
                json=question.model_dump(), 
                headers=forward_headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.patch("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}/student/{student_id}/feedback", status_code=status.HTTP_200_OK)
async def updateQuizFeedback(teacher_id: int, classroom_id: int, quiz_id: int, student_id: int, feedback: Feedback, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            # Actualizar feedback del profesor para el quiz de un estudiante
            response = await client.patch(
                f"{quices_url}/quiz/{quiz_id}/student/{student_id}/feedback", 
                json=feedback.model_dump(), 
                headers=forward_headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.patch("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}/student/{student_id}/question/{question_id}/feedback", status_code=status.HTTP_200_OK)
async def updateQuestionFeedback(teacher_id: int, classroom_id: int, quiz_id: int, student_id: int, question_id: int, feedback: Feedback, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            # Actualizar feedback del profesor para una pregunta específica
            response = await client.patch(
                f"{quices_url}/question/{question_id}/student/{student_id}/feedback", 
                json=feedback.model_dump(), 
                headers=forward_headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.delete("/teacher/{teacher_id}/competence/{competence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher_competence(teacher_id: int, competence_id: int):
    pass 

@app.delete("/teacher/{teacher_id}/classroom/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher_classroom(teacher_id: int, classroom_id: int):
    pass 

@app.delete("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom_quiz(teacher_id: int, classroom_id: int, quiz_id: int, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            # Eliminar un quiz completo
            response = await client.delete(f"{quices_url}/quiz/{quiz_id}", headers=forward_headers)
            response.raise_for_status()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@app.delete("/teacher/{teacher_id}/classroom/{classroom_id}/quiz/{quiz_id}/question/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz_question(teacher_id: int, classroom_id: int, quiz_id: int, question_id: int, request: Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            # Eliminar una pregunta específica
            response = await client.delete(f"{quices_url}/question/{question_id}", headers=forward_headers)
            response.raise_for_status()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

# ----- CRUD Operations for student -----

@app.get("/student/me", response_model=Student)

async def getStudent(request:Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{users_url}/student/me",headers=forward_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
@app.patch("/student/me", response_model=Student)

async def patchStudent(request:Request):
    forward_headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f"{users_url}/student/me",headers=forward_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


# Personaje
@app.get("/student/{student_id}/character", response_model=Character)
async def get_student_character(student_id: int):
    pass

@app.get("/student/{student_id}/character/accesory", response_model=List[Accessory])
async def get_student_character_accessories(student_id: int):
    pass

@app.get("/student/{student_id}/character/accesory/{accesory_id}", response_model=Accessory)
async def get_student_accessory_detail(student_id: int, accesory_id: int):
    pass

# Tienda
@app.get("/student/{student_id}/store", response_model=Store)
async def get_student_store(student_id: int):
    pass

@app.get("/student/{student_id}/store/upper-clothes", response_model=List[UpperClothes])
async def get_upper_clothes(student_id: int):
    pass

@app.get("/student/{student_id}/store/lower-clothes", response_model=List[LowerClothes])
async def get_lower_clothes(student_id: int):
    pass

@app.get("/student/{student_id}/store/hair", response_model=List[Hair])
async def get_hair_options(student_id: int):
    pass

@app.get("/student/{student_id}/store/shoes", response_model=List[Shoes])
async def get_shoes_options(student_id: int):
    pass

@app.get("/student/{student_id}/stoe/accesory", response_model=List[Accessory])  # (OJO: "stoe" parece un typo de "store")
async def get_store_accessories(student_id: int):
    pass

# Clases y Quices
@app.get("/student/{student_id}/classroom", response_model=List[Classroom])
async def get_student_classrooms(student_id: int):
    pass

@app.get("/student/{student_id}/classroom/{classroom_id}", response_model=Classroom_Quiz)
async def get_student_classroom_detail(student_id: int, classroom_id: int):
    pass

@app.get("/student/{student_id}/classroom/{classroom_id}/quiz", response_model=Quiz_Question)
async def get_classroom_quizzes(student_id: int, classroom_id: int):
    pass

@app.get("/student/{student_id}/classroom/{classroom_id}/result", response_model=List[Quiz_Student])
async def get_classroom_quiz_results(student_id: int, classroom_id: int):
    pass

@app.get("/student/{student_id}/classroom/{classroom_id}/result/quiz/{quiz_id}", response_model=Quiz_Student)
async def get_student_quiz_result(student_id: int, classroom_id: int, quiz_id: int):
    pass

# Acciones (POST)
@app.post("/student/{student_id}/classroom/{classroom_id}/quiz/{quiz_id}/question/{question_id}/answer", status_code=status.HTTP_201_CREATED)
async def submit_answer(student_id: int, classroom_id: int, quiz_id: int, question_id: int):
    pass

@app.post("/student/{student_id}/store/upper-clothes/{upper_clothes_id}", status_code=status.HTTP_201_CREATED)
async def buy_upper_clothes(student_id: int, upper_clothes_id: int):
    pass

@app.post("/student/{student_id}/store/lower-clothes/{lower_clothes_id}", status_code=status.HTTP_201_CREATED)
async def buy_lower_clothes(student_id: int, lower_clothes_id: int):
    pass

@app.post("/student/{student_id}/store/hair/{hair_id}", status_code=status.HTTP_201_CREATED)
async def buy_hair(student_id: int, hair_id: int):
    pass

@app.post("/student/{student_id}/store/shoes/{shoes_id}", status_code=status.HTTP_201_CREATED)
async def buy_shoes(student_id: int, shoes_id: int):
    pass

@app.post("/student/{student_id}/store/accesory/{accesory_id}", status_code=status.HTTP_201_CREATED)
async def buy_accessory(student_id: int, accesory_id: int):
    pass

# Actualizar apariencia
@app.patch("/student/{student_id}/update-appareance", status_code=status.HTTP_204_NO_CONTENT)
async def update_student_appareance(student_id: int):
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)