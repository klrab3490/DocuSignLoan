from fastapi import APIRouter
from .pdf_extract import router as extract_router
from .pdf_status import router as status_router
from .pdf_highlight import router as highlight_router
from .authentication import router as auth_router


api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(extract_router, prefix="/pdf", tags=["PDF Extraction"])
api_router.include_router(status_router, prefix="/pdf", tags=["PDF Status"])
api_router.include_router(highlight_router, prefix="/pdf", tags=["PDF Highlight"])