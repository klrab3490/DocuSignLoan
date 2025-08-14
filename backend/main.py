import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import pdf_extract, pdf_status, authentication
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv(dotenv_path=".env")

# Security scheme for Swagger UI Authorize button
security_scheme = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
}

# FastAPI app setup with metadata and tags
app = FastAPI(
    title="Loan Book Agency API",
    description="OpenAPI Specification for LoanBook Agency PDF Processing Platform",
    version="1.0.0",
    openapi_tags=[
        {"name": "Authentication", "description": "Endpoints for user login & token management"},
        {"name": "PDF Extraction", "description": "Extract and format content from PDFs"},
        {"name": "PDF Status", "description": "Check status of PDF extraction jobs"}
    ],
    openapi_components={
        "securitySchemes": security_scheme
    },
    openapi_security=[{"bearerAuth": []}]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register authentication routes
app.include_router(authentication.router, prefix="/auth", tags=["Authentication"])

# Register PDF routes
app.include_router(pdf_extract.router, prefix="/pdf", tags=["PDF Extraction"])
app.include_router(pdf_status.router, prefix="/pdf", tags=["PDF Status"])

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
