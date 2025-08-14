import os
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from app.api import pdf_extract, pdf_status

# Load env
load_dotenv(dotenv_path=".env")

app = FastAPI()

# Register PDF routes
app.include_router(pdf_extract.router, prefix="/pdf")
app.include_router(pdf_status.router, prefix="/pdf")

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
