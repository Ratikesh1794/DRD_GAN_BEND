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
    try:
        app.state.db = await db_config.connect()
    except Exception as e:
        print(f"Failed to initialize database: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, 'db'):
        await db_config.close()

# Import and include routers
from routes.patient import patient_router
from routes.image import image_router
from routes.report import report_router

# Include routers
app.include_router(patient_router)
app.include_router(image_router)
app.include_router(report_router)

# Add a root endpoint
@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Diabetic Retinopathy Detection API is running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Get port from environment variable with a default of 10000 (Render's default)
    port = int(os.getenv('PORT', 10000))
    
    # Ensure host is set to 0.0.0.0 for Render deployment
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False  # Disable reload in production
    )