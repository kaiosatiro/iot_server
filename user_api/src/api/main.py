from fastapi import APIRouter

from src.api.routes import devices, environments, login, messages, users, utils

api_router = APIRouter()
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(utils.router, prefix="/utils")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(
    environments.router, prefix="/environments", tags=["Environments"]
)
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
