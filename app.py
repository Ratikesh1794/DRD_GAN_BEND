from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from config.database import DatabaseConfig
from config.cloudinary_config import configure_cloudinary
import os
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Diabetic Retinopathy API",
    description="API for Diabetic Retinopathy Detection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Cloudinary
configure_cloudinary()

# Initialize database connection
db_config = DatabaseConfig()

@app.on_event("startup")
async def startup_event():
    app.state.db = await db_config.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await db_config.close()

# Import and include routers
from routes.patient import patient_router
from routes.image import image_router
from routes.report import report_router

# Include routers
app.include_router(patient_router)
app.include_router(image_router)
app.include_router(report_router)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)