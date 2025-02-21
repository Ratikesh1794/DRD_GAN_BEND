from fastapi import APIRouter, Depends, HTTPException
from models.patient_model import Patient
from services.patient_service import PatientService
from typing import Dict, Any
from fastapi import Request

# Create router
patient_router = APIRouter(
    tags=["patient"]
)

# Get database from app state
async def get_db(request: Request):
    return request.app.state.db

@patient_router.post("/create-patient", status_code=201)
async def add_patient(patient_data: Patient, db: Any = Depends(get_db)):
    try:
        async with PatientService(db) as service:
            patient_id = await service.create_patient(patient_data)
        
        return {
            'status': 'success',
            'message': 'Patient added successfully',
            'patient_id': patient_id
        }
            
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                'status': 'error',
                'message': str(e),
                'error_type': 'ValidationError'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                'status': 'error',
                'message': str(e),
                'error_type': 'ServerError'
            }
        )

@patient_router.get("/get-prediction/{patient_id}")
async def get_patient_prediction(patient_id: str, db: Any = Depends(get_db)):
    try:
        async with PatientService(db) as service:
            prediction_data = await service.get_prediction(patient_id)
        
        return {
            'status': 'success',
            'prediction_data': prediction_data
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                'status': 'error',
                'message': str(e),
                'error_type': 'ServerError'
            }
        )
