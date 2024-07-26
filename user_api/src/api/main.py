from fastapi import APIRouter

from src.api.routes import login

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
