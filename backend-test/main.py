# backend/main.py
import uvicorn, os
from fastapi import FastAPI
from app.api import api_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Security scheme for Swagger UI Authorize button
security_scheme = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
}

app = FastAPI(
    title="Loan Book Agency API",
    description="OpenAPI Specification for LoanBook Agency PDF Processing Platform",
    version="1.0.0",
    openapi_tags=[
        {"name": "Authentication", "description": "Endpoints for user login & token management"},
        {"name": "PDF Extraction", "description": "Extract and format content from PDFs"},
        {"name": "PDF Highlight", "description": "Highlight text in PDF files"},
        {"name": "PDF Status", "description": "Check status of PDF extraction jobs"},
    ],
    components={   # ✅ fixed: previously openapi_components
        "securitySchemes": security_scheme
    },
    security=[{"bearerAuth": []}]   # ✅ fixed: previously openapi_security
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Upload PDF
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT) 