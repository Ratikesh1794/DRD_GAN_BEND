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
            Based on the following patient information and examination results, generate a comprehensive medical report:

            {patient_info}

            Examination Results:
            - DR Status: {dr_status}
            - Severity Level: {severity_level}
            - Confidence: {confidence:.1f}%
            - Detailed Predictions: {detailed_predictions}

            Please provide a structured medical report with the following sections:

            1. Patient Medical Assessment
            Provide a concise summary of the patient's current medical status, including visual acuity and relevant health metrics.

            2. DR Status Analysis
            Analyze the detected diabetic retinopathy status and its implications.

            3. Classification Details
            Detail the specific classification findings and their clinical significance.

            4. Vulnerable Areas Analysis
            Identify and describe areas of concern in the retinal examination.

            5. Risk Assessment
            Evaluate the patient's risk factors and potential progression of the condition.

            6. Recommendations
            Provide specific medical recommendations and lifestyle modifications.

            7. Follow-up Plan
            Outline a clear follow-up schedule and monitoring plan.

            Format each section with clear headings and professional medical terminology. Maintain a formal, clinical tone throughout the report.
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
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