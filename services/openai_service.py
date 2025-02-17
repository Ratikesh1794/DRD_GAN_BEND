import os
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)

    async def generate_report(self, prediction_data: dict) -> dict:
        try:
            dr_status = prediction_data.get('dr_detection_result', 'Unknown')
            severity_level = prediction_data.get('severity_level', 'Unknown')
            confidence = prediction_data.get('prediction_confidence', 0.0)
            detailed_predictions = prediction_data.get('detailed_predictions', {})

            prompt = f"""
            Generate a comprehensive medical report for a diabetic retinopathy case with the following details:
            - DR Status: {dr_status}
            - Severity Level: {severity_level}
            - Confidence: {confidence:.1f}%
            - Detailed Predictions: {detailed_predictions}

            Generate a detailed medical report with the following sections:
            1. Patient Medical Assessment (current findings and observations)
            2. DR Status Analysis (detailed analysis of DR status)
            3. Classification Details (breakdown of severity classification)
            4. Vulnerable Areas Analysis (specific affected areas in the retina)
            5. Risk Assessment (potential complications and progression risks)
            6. Recommendations (treatment and management plan)
            7. Follow-up Plan (monitoring schedule and next steps)

            Format the response as a structured medical report with clear sections.
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
            
            # Split the content into sections
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