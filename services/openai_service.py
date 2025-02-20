import os
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)

    async def generate_report(self, prediction_data: dict, patient_details: dict) -> dict:
        try:
            dr_status = prediction_data.get('dr_detection_result', 'Unknown')
            severity_level = prediction_data.get('severity_level', 'Unknown')
            confidence = prediction_data.get('prediction_confidence', 0.0)
            detailed_predictions = prediction_data.get('detailed_predictions', {})

            # Format patient details with all available information
            patient_info = f"""
            Patient Information:
            - Name: {patient_details.get('patient_name', 'N/A')}
            - Date of Birth: {patient_details.get('date_of_birth', 'N/A')}
            - Gender: {patient_details.get('gender', 'N/A')}
            - Vision Problems: {patient_details.get('vision_problems', 'N/A')}
            - Visual Acuity (Right): {patient_details.get('visual_acuity_right', 'N/A')}
            - Visual Acuity (Left): {patient_details.get('visual_acuity_left', 'N/A')}
            - Blood Sugar (Fasting): {patient_details.get('blood_sugar_fasting', 'N/A')}
            - Blood Pressure: {patient_details.get('blood_pressure', 'N/A')}
            - Image URL: {patient_details.get('image_url', 'N/A')}
            """

            prompt = f"""
            Based on the following patient information and examination results, generate a comprehensive medical report.
            Ensure each section is clearly separated by line breaks and follows a consistent, formal medical format.

            {patient_info}

            Examination Results:
            - DR Status: {dr_status}
            - Severity Level: {severity_level}
            - Confidence: {confidence:.1f}%
            - Detailed Predictions: {detailed_predictions}

            Generate a structured medical report with the following specific sections:

            1. Patient Medical Assessment
            - Current visual acuity analysis
            - Vital signs evaluation (blood pressure, blood sugar)
            - Reported vision problems and symptoms
            - Overall health status assessment

            2. DR Status Analysis
            - Detailed interpretation of DR detection results
            - Analysis of severity level and its clinical significance
            - Confidence level interpretation
            - Correlation with patient's symptoms

            3. Classification Details
            - Specific findings from the retinal examination
            - Presence of DR-related features
            - Quantitative analysis of detected abnormalities
            - Comparison with standard classification criteria

            4. Vulnerable Areas Analysis
            - Identification of specific affected retinal regions
            - Description of observed pathological changes
            - Assessment of macular involvement
            - Peripheral retina status

            5. Risk Assessment
            - Current risk level evaluation
            - Contributing systemic factors
            - Progression risk factors
            - Complications risk analysis

            6. Recommendations
            - Immediate medical interventions required
            - Lifestyle modifications needed
            - Blood sugar management guidelines
            - Vision protection measures

            7. Follow-up Plan
            - Specific timeline for next examination
            - Required diagnostic tests
            - Monitoring schedule
            - Referral recommendations if needed

            Important guidelines:
            - Use clear, professional medical terminology
            - Maintain a formal clinical tone
            - Provide specific, actionable information
            - Ensure each section is distinct and comprehensive
            - Include quantitative data where available
            - Avoid any special characters or formatting markers
            
            Eg :
            Wrong format:
            {
                "report": {
                    "blood_pressure": "120/80",
                    "blood_sugar_fasting": 95.5,
                    "classification_details": "Patient Name: John Doe\nDOB: 1990-01-01\nGender: Male",
                    "confidence": 0.8788774013519287,
                    "created_at": "Thu, 20 Feb 2025 19:18:06 GMT",
                    "date_of_birth": "Mon, 01 Jan 1990 00:00:00 GMT",
                    "dr_status": "Positive",
                    "dr_status_analysis": "**Patient Medical Assessment**",
                    "follow_up_plan": "**Classification Details**",
                    "gender": "male",
                    "image_url": "https://res.cloudinary.com/dolurenna/image/upload/v1740079032/retinal_images/patient_P12345_test.jpg",
                    "patient_id": "P12345",
                    "patient_medical_assessment": "**Medical Report**",
                    "patient_name": "John Doe",
                    "recommendations": "Retinal examination revealed a positive Diabetic Retinopathy (DR) status. The severity level of DR is graded as severe. The confidence level of the DR diagnosis is 0.9%, indicating a high degree of certainty in the diagnosis. These findings correlate with the patient's main symptom of blurred vision, which is a common manifestation of DR.",
                    "report_id": "90a547f0-f84b-4f43-841e-2d9bdae3345f",
                    "risk_assessment": "**DR Status Analysis**",
                    "severity_level": "Severe DR",
                    "vision_problems": "Blurred vision",
                    "visual_acuity_left": 0.7,
                    "visual_acuity_right": 0.8,
                    "vulnerable_areas_analysis": "John Doe presents with the primary complaint of blurred vision. His visual acuity measurement is 0.8 for the right eye and 0.7 for the left eye, indicating mild vision impairment. Vital signs show a fasting blood sugar of 95.5, which is within a healthy range. Blood pressure measurement is 120/80 mmHg, classified as normal. Overall, apart from the reported vision problem, the patient's general health status appears stable."
                },
                "status": "success"
            }
            Correct Format:
            {
                "report": {
                    "blood_pressure": "120/80",
                    "blood_sugar_fasting": 95.5,
                    "classification_details": "Patient Name: John Doe\nDOB: 1990-01-01\nGender: Male",
                    "confidence": 0.8788774013519287,
                    "created_at": "Thu, 20 Feb 2025 19:18:06 GMT",
                    "date_of_birth": "Mon, 01 Jan 1990 00:00:00 GMT",
                    "dr_status": "Positive",
                    "dr_status_analysis": "Patient Medical Assessment",
                    "follow_up_plan": "Classification Details",
                    "gender": "male",
                    "image_url": "https://res.cloudinary.com/dolurenna/image/upload/v1740079032/retinal_images/patient_P12345_test.jpg",
                    "patient_id": "P12345",
                    "patient_medical_assessment": "Medical Report",
                    "patient_name": "John Doe",
                    "recommendations": "Retinal examination revealed a positive Diabetic Retinopathy (DR) status. The severity level of DR is graded as severe. The confidence level of the DR diagnosis is 0.9%, indicating a high degree of certainty in the diagnosis. These findings correlate with the patient's main symptom of blurred vision, which is a common manifestation of DR.",
                    "report_id": "90a547f0-f84b-4f43-841e-2d9bdae3345f",
                    "risk_assessment": "DR Status Analysis",
                    "severity_level": "Severe DR",
                    "vision_problems": "Blurred vision",
                    "visual_acuity_left": 0.7,
                    "visual_acuity_right": 0.8,
                    "vulnerable_areas_analysis": "John Doe presents with the primary complaint of blurred vision. His visual acuity measurement is 0.8 for the right eye and 0.7 for the left eye, indicating mild vision impairment. Vital signs show a fasting blood sugar of 95.5, which is within a healthy range. Blood pressure measurement is 120/80 mmHg, classified as normal. Overall, apart from the reported vision problem, the patient's general health status appears stable."
                },
                "status": "success"
            }
            """

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )

            report_content = response.choices[0].message.content.strip()
            sections = report_content.split('\n\n')

            return {
                "patient_medical_assessment": sections[0] if len(sections) > 0 else "",
                "dr_status_analysis": sections[1] if len(sections) > 1 else "",
                "classification_details": sections[2] if len(sections) > 2 else "",
                "vulnerable_areas_analysis": sections[3] if len(sections) > 3 else "",
                "risk_assessment": sections[4] if len(sections) > 4 else "",
                "recommendations": sections[5] if len(sections) > 5 else "",
                "follow_up_plan": sections[6] if len(sections) > 6 else ""
            }

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}") 