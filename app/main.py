from fastapi import FastAPI
from app.routes.user import router as user_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI service!"}

app.include_router(user_router, prefix="/user", tags=["user"])
