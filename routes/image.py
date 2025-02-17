from flask import Blueprint, request, jsonify, current_app
from services.image_service import ImageService
from services.patient_service import PatientService
from utils import async_handler
from services.prediction_service import PredictionService
import tempfile
import os

image_bp = Blueprint('image', __name__)

# Add prediction_service as a global variable
prediction_service = PredictionService()

@image_bp.route('/upload-retinal-image/<patient_id>', methods=['POST'])
@async_handler
async def upload_image(patient_id):
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file part'
            }), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No selected file'
            }), 400
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        # Get prediction first
        prediction_result = await prediction_service.predict_dr_grade(temp_path)
        
        # Upload image to Cloudinary
        image_service = ImageService()
        image_url = await image_service.upload_image(temp_path, patient_id)
        
        # Clean up temp file
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        # Update patient record
        async with PatientService(current_app.db) as service:
            await service.update_image_url(patient_id, image_url)
            await service.update_prediction(patient_id, prediction_result)
        
        return jsonify({
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
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 