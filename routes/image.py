from flask import Blueprint, request, jsonify, current_app
from services.image_service import ImageService
from services.patient_service import PatientService
from utils import async_handler

image_bp = Blueprint('image', __name__)

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
            
        # Upload image to Cloudinary
        image_service = ImageService()
        image_url = await image_service.upload_image(file, patient_id)
        
        # Update patient record with image URL
        async with PatientService(current_app.db) as service:
            await service.update_image_url(patient_id, image_url)
        
        return jsonify({
            'status': 'success',
            'message': 'Image uploaded successfully',
            'image_url': image_url
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 