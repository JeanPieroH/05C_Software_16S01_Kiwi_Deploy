from fastapi import FastAPI
from controllers import auth_controller, classroom_controller, quiz_controller,student_controller,teacher_controller

def include_all_routers(app: FastAPI):
    app.include_router(auth_controller.router, prefix="/auth", tags=["Auth"])
    app.include_router(student_controller.router, prefix="/student", tags=["Student"])
    app.include_router(teacher_controller.router, prefix="/teacher", tags=["Teacher"])
    app.include_router(classroom_controller.router, prefix="/classroom", tags=["Classroom"])
    app.include_router(quiz_controller.router, prefix="/quiz", tags=["Quiz"])


