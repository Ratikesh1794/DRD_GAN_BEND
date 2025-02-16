from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from config.database import DatabaseConfig
from motor.motor_asyncio import AsyncIOMotorClient

# Patient Schema
class Patient(BaseModel):
    # Required fields for initial screening
    patient_name: str = Field(..., min_length=2)
    patient_id: str = Field(..., min_length=1)
    date_of_birth: date
    gender: str = Field(..., pattern="^(male|female|other)$")
    
    # Vision-related fields
    vision_problems: Optional[str] = None
    visual_acuity_right: float = Field(..., ge=0, le=1)
    visual_acuity_left: float = Field(..., ge=0, le=1)
    
    # Screening result
    dr_detection_result: Optional[str] = None
    
    # Additional health information (optional)
    blood_sugar_fasting: Optional[float] = Field(None, ge=0)
    blood_pressure: Optional[str] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    #image path
    image_url: Optional[str] = None

# Database Model
class PatientModel:
    def __init__(self, db=None):
        self.db = db
        self.collection = None
        self.client = None
        if db is not None:
            self.collection = db.patients
        
    async def initialize(self, db=None):
        if self.collection is None:
            if db is not None:
                self.db = db
                self.collection = self.db.patients
            else:
                self.db_config = DatabaseConfig()
                self.client = AsyncIOMotorClient(
                    self.db_config.get_uri(),
                    maxPoolSize=50,
                    minPoolSize=10
                )
                self.db = self.client[self.db_config.get_database_name()]
                self.collection = self.db.patients
        return self

    async def create(self, patient_data: Patient) -> str:
        if self.collection is None:
            await self.initialize()
            
        try:
            patient_dict = patient_data.dict()
            
            for key, value in patient_dict.items():
                if isinstance(value, date):
                    patient_dict[key] = value.isoformat()
            
            patient_dict['created_at'] = datetime.utcnow()
            patient_dict['updated_at'] = datetime.utcnow()
            
            result = await self.collection.insert_one(patient_dict)
            return str(result.inserted_id)
            
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    async def close(self):
        if self.client:
            await self.client.close()