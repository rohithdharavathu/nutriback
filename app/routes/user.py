from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.utils.auth import get_password_hash, verify_password, create_access_token
from app.database import db
from bson.objectid import ObjectId
from pydantic import BaseModel
import requests
from app.utils.deps import get_current_user
from typing import List

router = APIRouter()

@router.post("/signup", response_model=UserOut)
async def signup(user: UserCreate):
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    user_doc = {"username": user.username, "hashed_password": hashed_password}
    result = await db.users.insert_one(user_doc)
    return UserOut(id=str(result.inserted_id), username=user.username)

@router.post("/login")
async def login(user: UserLogin):
    user_doc = await db.users.find_one({"username": user.username})
    if not user_doc or not verify_password(user.password, user_doc["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

class MealRequest(BaseModel):
    description: str

@router.post("/nutrition")
async def get_nutrition(
    req: MealRequest,
    current_user: str = Depends(get_current_user)
):
    GROQ_API_KEY = "your_groq_api_key_here"
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {
                "role": "system",
                "content": "You are a nutrition expert. Given a meal description, return nutrition per ingredient in JSON with keys: name, calories, protein, carbs, fat, fiber."
            },
            {
                "role": "user",
                "content": req.description
            }
        ],
        "temperature": 0.3
    }
    try:
        response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        result = data["choices"][0]["message"]["content"]
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: str = Depends(get_current_user)):
    user_doc = await db.users.find_one({"username": current_user})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(id=str(user_doc["_id"]), username=user_doc["username"])

class MealHistoryItem(BaseModel):
    description: str
    nutrition: dict

@router.post("/meals", response_model=MealHistoryItem)
async def add_meal(
    meal: MealHistoryItem,
    current_user: str = Depends(get_current_user)
):
    await db.meals.insert_one({
        "username": current_user,
        "description": meal.description,
        "nutrition": meal.nutrition
    })
    return meal

@router.get("/meals", response_model=List[MealHistoryItem])
async def get_meals(current_user: str = Depends(get_current_user)):
    meals = []
    async for meal in db.meals.find({"username": current_user}):
        meals.append(MealHistoryItem(description=meal["description"], nutrition=meal["nutrition"]))
    return meals