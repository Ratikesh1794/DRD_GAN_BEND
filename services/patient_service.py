from models.patient_model import Patient, PatientModel
from datetime import datetime


class PatientService:
    def __init__(self, db=None):
        self.patient_model = PatientModel(db)
        self.db = db
        
    async def initialize(self):
        if self.patient_model is not None:
            await self.patient_model.initialize(self.db)
        
    async def create_patient(self, patient_data: Patient):
        try:
            if self.patient_model.collection is None:
                await self.initialize()
            return await self.patient_model.create(patient_data)
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.patient_model is not None:
            await self.patient_model.close()
        
    async def update_image_url(self, patient_id: str, image_url: str):
        try:
            if self.patient_model.collection is None:
                await self.initialize()
            
            result = await self.patient_model.collection.update_one(
                {"patient_id": patient_id},
                {"$set": {"image_url": image_url}}
            )
            
            if result.modified_count == 0:
                raise Exception("Patient not found or image URL not updated")
            
            return True
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    async def update_prediction(self, patient_id: str, prediction_result: dict):
        try:
            if self.patient_model.collection is None:
                await self.initialize()
            
            result = await self.patient_model.collection.update_one(
                {"patient_id": patient_id},
                {"$set": {
                    "dr_detection_result": prediction_result['dr_status'],
                    "severity_level": prediction_result['severity_level'],
                    "prediction_confidence": prediction_result['confidence'],
                    "detailed_predictions": prediction_result['predictions'],
                    "updated_at": datetime.utcnow()
                }}
            )
            
            if result.modified_count == 0:
                raise Exception("Patient not found or prediction not updated")
            
            return True
        except Exception as e:
            raise Exception(f"Database error: {str(e)}") 