# backend/main.py
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router

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
)

# 🔒 Custom OpenAPI schema to inject JWT auth into Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = security_scheme
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 🔗 Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change to specific domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📂 Include API routers
app.include_router(api_router)

# 📂 Uploads folder (static serving)
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
