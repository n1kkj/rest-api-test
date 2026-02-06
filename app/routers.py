from fastapi import APIRouter
from app.views.organization import router as organizations_router
from app.views.building import router as buildings_router
from app.views.activity import router as activities_router

api_router = APIRouter()
api_router.include_router(organizations_router)
api_router.include_router(buildings_router)
api_router.include_router(activities_router)
