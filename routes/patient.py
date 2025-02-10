from flask import Blueprint, request, jsonify, current_app
from models.patient_model import Patient
from services.patient_service import PatientService
from utils import async_handler

# Remove url_prefix as we'll handle it in the main route registration
patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/create-patient', methods=['POST'])
@async_handler
async def add_patient():
    try:
        # Validate request data using Pydantic
        patient_data = Patient(**request.json)
        
        async with PatientService(current_app.db) as service:
            patient_id = await service.create_patient(patient_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Patient added successfully',
            'patient_id': patient_id
        }), 201
            
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'error_type': 'ValidationError'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'error_type': 'ServerError'
        }), 500
