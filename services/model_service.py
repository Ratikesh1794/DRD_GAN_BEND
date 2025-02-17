import boto3
import os
import io
import torch
from pathlib import Path
from keras._tf_keras.keras.models import load_model
import tempfile

class ModelService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        
    async def download_model_from_s3(self, key):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except Exception as e:
            raise Exception(f"Error downloading model from S3: {str(e)}")
            
    async def load_gan_model(self, generator, device):
        try:
            model_bytes = await self.download_model_from_s3('enhanced_gan_models.pth')
            checkpoint = torch.load(io.BytesIO(model_bytes), map_location=device)
            generator.load_state_dict(checkpoint['model_state_dict'])
            return generator
        except Exception as e:
            raise Exception(f"Error loading GAN model: {str(e)}")
            
    async def load_cnn_model(self):
        try:
            model_bytes = await self.download_model_from_s3('DR_model_final.h5')
            
            # Create a temporary file to save the model
            with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as temp_model_file:
                temp_model_file.write(model_bytes)
                temp_model_path = temp_model_file.name
            
            try:
                # Load the model from the temporary file
                model = load_model(temp_model_path)
                return model
            finally:
                # Clean up the temporary file
                os.remove(temp_model_path)
            
        except Exception as e:
            raise Exception(f"Error loading CNN model: {str(e)}") 