from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from config.database import DatabaseConfig

class Report(BaseModel):
    report_id: str = Field(..., min_length=1)
    patient_id: str = Field(..., min_length=1)
    patient_name: str
    date_of_birth: date
    gender: str
    vision_problems: Optional[str] = None
    visual_acuity_right: float
    visual_acuity_left: float
    blood_sugar_fasting: Optional[float] = None
    blood_pressure: Optional[str] = None
    dr_status: str
    severity_level: str
    confidence: float
    patient_medical_assessment: str
    dr_status_analysis: str
    classification_details: str
    vulnerable_areas_analysis: str
    risk_assessment: str
    recommendations: str
    follow_up_plan: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }

class ReportModel:
    def __init__(self, db=None):
        self.db = db
        self.collection = None
        self.client = None
        if db is not None:
            self.collection = db.reports

    async def initialize(self, db=None):
        if self.collection is None:
            if db is not None:
                self.db = db
                self.collection = self.db.reports
            else:
                self.db_config = DatabaseConfig()
                self.client = AsyncIOMotorClient(
                    self.db_config.get_uri(),
                    maxPoolSize=50,
                    minPoolSize=10
                )
                self.db = self.client[self.db_config.get_database_name()]
                self.collection = self.db.reports
        return self

    async def create(self, report_data: Report) -> str:
        if self.collection is None:
            await self.initialize()
        
        try:
            report_dict = report_data.dict()
            
            # Convert date objects to ISO format strings
            if isinstance(report_dict['date_of_birth'], date):
                report_dict['date_of_birth'] = report_dict['date_of_birth'].isoformat()
            
            # Convert datetime objects to ISO format strings
            if isinstance(report_dict['created_at'], datetime):
                report_dict['created_at'] = report_dict['created_at'].isoformat()
            
            result = await self.collection.insert_one(report_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    async def get_report(self, report_id: str):
        if self.collection is None:
            await self.initialize()
        
        try:
            report = await self.collection.find_one({"report_id": report_id})
            return report
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    async def get_all_reports(self):
        if self.collection is None:
            await self.initialize()
        
        try:
            cursor = self.collection.find({})
            reports = await cursor.to_list(length=None)
            return reports
        except Exception as e:
            raise Exception(f"Database error: {str(e)}") 