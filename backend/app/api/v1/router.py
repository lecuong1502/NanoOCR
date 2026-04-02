from fastapi import APIRouter
from app.api.v1.endpoints import documents, ocr, search

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])