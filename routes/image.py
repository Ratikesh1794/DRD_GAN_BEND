from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from services.image_service import ImageService
from services.patient_service import PatientService
from services.prediction_service import PredictionService
from fastapi import Request
import tempfile
import os
from typing import Any

# Create router
image_router = APIRouter(
    tags=["image"]
)

# Add prediction_service as a global variable
prediction_service = PredictionService()

# Get database from app state
async def get_db(request: Request):
    return request.app.state.db

@image_router.post("/upload-retinal-image/{patient_id}", status_code=201)
async def upload_image(
    patient_id: str, 
    file: UploadFile = File(...), 
    db: Any = Depends(get_db)
):
    try:
        if not file:
            raise HTTPException(
                status_code=400,
                detail={
                    'status': 'error',
                    'message': 'No file uploaded'
                }
            )
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        # Write file content
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get prediction first
        prediction_result = await prediction_service.predict_dr_grade(temp_path)
        
        # Upload image to Cloudinary
        image_service = ImageService()
        image_url = await image_service.upload_image(temp_path, patient_id)
        
        # Clean up temp file
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        # Update patient record
        async with PatientService(db) as service:
            await service.update_image_url(patient_id, image_url)
            await service.update_prediction(patient_id, prediction_result)
        
        return {
            'status': 'success',
            'message': 'Image uploaded and analyzed successfully',
            'image_url': image_url,
            'prediction': {
                'dr_status': prediction_result['dr_status'],
                'severity_level': prediction_result['severity_level'],
                'confidence': f"{prediction_result['confidence']*100:.1f}%",
                'detailed_predictions': {
                    k: f"{v*100:.1f}%" 
                    for k, v in prediction_result['predictions'].items()
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                'status': 'error',
                'message': str(e)
            }
        ) 