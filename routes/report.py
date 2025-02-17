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
        async with PatientService(current_app.db) as service:
            # Get patient prediction data
            prediction_data = await service.get_prediction(patient_id)
            # Get complete patient details
            patient_details = await service.get_patient_details(patient_id)
            
        if not prediction_data:
            return jsonify({
                'status': 'error',
                'message': 'Patient prediction data not found'
            }), 404

        if not patient_details:
            return jsonify({
                'status': 'error',
                'message': 'Patient details not found'
            }), 404

        # Generate report using OpenAI
        openai_service = OpenAIService()
        report_content = await openai_service.generate_report(prediction_data, patient_details)

        # Create report object with all patient details
        report_data = Report(
            report_id=str(uuid.uuid4()),
            patient_id=patient_id,
            patient_name=patient_details['patient_name'],
            date_of_birth=patient_details['date_of_birth'],
            gender=patient_details['gender'],
            vision_problems=patient_details.get('vision_problems'),
            visual_acuity_right=patient_details['visual_acuity_right'],
            visual_acuity_left=patient_details['visual_acuity_left'],
            blood_sugar_fasting=patient_details.get('blood_sugar_fasting'),
            blood_pressure=patient_details.get('blood_pressure'),
            dr_status=prediction_data.get('dr_detection_result', 'Unknown'),
            severity_level=prediction_data.get('severity_level', 'Unknown'),
            confidence=prediction_data.get('prediction_confidence', 0.0),
            patient_medical_assessment=report_content['patient_medical_assessment'],
            dr_status_analysis=report_content['dr_status_analysis'],
            classification_details=report_content['classification_details'],
            vulnerable_areas_analysis=report_content['vulnerable_areas_analysis'],
            risk_assessment=report_content['risk_assessment'],
            recommendations=report_content['recommendations'],
            follow_up_plan=report_content['follow_up_plan'],
            image_url=patient_details.get('image_url'),
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

@report_bp.route('/reports', methods=['GET'])
@async_handler
async def get_all_reports():
    try:
        report_model = ReportModel(current_app.db)
        reports = await report_model.get_all_reports()
        
        # Convert ObjectId to string for JSON serialization
        for report in reports:
            if '_id' in report:
                report['_id'] = str(report['_id'])
        
        return jsonify({
            'status': 'success',
            'reports': reports
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 