import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import authentication, pdf_extract, pdf_highlight, pdf_status
from fastapi.staticfiles import StaticFiles
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

# Make sure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# FastAPI app setup with metadata and tags
# {"name": "Authentication", "description": "Endpoints for user login & token management"},

app = FastAPI(
    title="Loan Book Agency API",
    description="OpenAPI Specification for LoanBook Agency PDF Processing Platform",
    version="1.0.0",
    openapi_tags=[
        {"name": "PDF Extraction", "description": "Extract and format content from PDFs"},
        {"name": "PDF Status", "description": "Check status of PDF extraction jobs"},
        {"name": "PDF Highlight", "description": "Highlight text in PDF files"},
    ],
    components={   # ✅ fixed: previously openapi_components
        "securitySchemes": security_scheme
    },
    security=[{"bearerAuth": []}]   # ✅ fixed: previously openapi_security
)

# CORS middleware (adjust origins for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # add prod frontend URLs later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register authentication routes (enable when ready)
# app.include_router(authentication.router, prefix="/auth", tags=["Authentication"])

# Static files (uploaded PDFs)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register PDF routes
app.include_router(pdf_extract.router, prefix="/pdf", tags=["PDF Extraction"])
app.include_router(pdf_highlight.router, prefix="/pdf", tags=["PDF Highlight"])
app.include_router(pdf_status.router, prefix="/pdf", tags=["PDF Status"])

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
