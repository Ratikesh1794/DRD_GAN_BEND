from flask import Blueprint, jsonify, current_app
from services.patient_service import PatientService
from services.openai_service import OpenAIService
from models.report_model import Report, ReportModel
from utils import async_handler
import uuid
from datetime import datetime

# Create blueprint without url_prefix
report_bp = Blueprint('report', __name__)

@report_bp.route('/generate-report/<patient_id>', methods=['POST'])
@async_handler
async def generate_report(patient_id):
    try:
        # Get patient prediction data
        async with PatientService(current_app.db) as service:
            prediction_data = await service.get_prediction(patient_id)
            
        if not prediction_data:
            return jsonify({
                'status': 'error',
                'message': 'Patient prediction data not found'
            }), 404

        # Generate report using OpenAI
        openai_service = OpenAIService()
        report_content = await openai_service.generate_report(prediction_data)

        # Create report object
        report_data = Report(
            report_id=str(uuid.uuid4()),
            patient_id=patient_id,
            dr_status=prediction_data['dr_detection_result'],
            severity_level=prediction_data['severity_level'],
            confidence=prediction_data['prediction_confidence'],
            patient_medical_assessment=report_content['patient_medical_assessment'],
            dr_status_analysis=report_content['dr_status_analysis'],
            classification_details=report_content['classification_details'],
            vulnerable_areas_analysis=report_content['vulnerable_areas_analysis'],
            risk_assessment=report_content['risk_assessment'],
            recommendations=report_content['recommendations'],
            follow_up_plan=report_content['follow_up_plan'],
            image_url=prediction_data.get('image_url'),
            created_at=datetime.utcnow()
        )

        # Save report to database
        report_model = ReportModel(current_app.db)
        await report_model.create(report_data)

        return jsonify({
            'status': 'success',
            'report': report_data.dict()
        }), 201

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 