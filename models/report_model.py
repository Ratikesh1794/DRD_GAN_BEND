from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from config.database import DatabaseConfig

class Report(BaseModel):
    report_id: str = Field(..., min_length=1)
    patient_id: str = Field(..., min_length=1)
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