from fastapi import APIRouter
from src.api.v1.financials import router as financials_router
from src.api.v1.analysis import router as analysis_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(financials_router)
api_v1_router.include_router(analysis_router)
