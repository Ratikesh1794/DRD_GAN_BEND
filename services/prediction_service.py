import torch
from PIL import Image, ImageEnhance
import numpy as np
import cv2
from torchvision import transforms
from keras._tf_keras.keras.models import load_model
import io
from models.architecture import Generator
from services.model_service import ModelService

class PredictionService:
    def __init__(self):
        self.device = torch.device('cpu')
        self.model_service = ModelService()
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(256),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
    async def enhance_image(self, image):
        try:
            if not isinstance(image, Image.Image):
                image = Image.fromarray(image)
                
            img_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Load GAN model from S3
            generator = Generator().to(self.device)
            generator = await self.model_service.load_gan_model(generator, self.device)
            generator.eval()
            
            with torch.no_grad():
                enhanced = generator(img_tensor)
            
            enhanced = enhanced.squeeze(0).cpu()
            enhanced = enhanced * torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1) + \
                      torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
            enhanced = enhanced.clamp(0, 1)
            enhanced = transforms.ToPILImage()(enhanced)
            
            # Apply additional enhancements
            enhanced = ImageEnhance.Contrast(enhanced).enhance(1.6)
            enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.7)
            
            return enhanced
            
        except Exception as e:
            raise Exception(f"Error enhancing image: {str(e)}")
        
    async def predict_dr_grade(self, image_path):
        """
        Predict DR grade from a retinal image
        """
        try:
            # Load and process image
            image = Image.open(image_path).convert('RGB')
            enhanced_image = await self.enhance_image(image)
            
            # Prepare for CNN
            img_array = np.array(enhanced_image)
            img_array = cv2.resize(img_array, (224, 224))
            img_array = img_array / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # Load CNN model from S3
            cnn_model = await self.model_service.load_cnn_model()
            
            # Get predictions
            predictions = cnn_model.predict(img_array, verbose=0)[0]
            pred_class = np.argmax(predictions)
            
            # Process results
            categories = ['No DR', 'Mild DR', 'Moderate DR', 'Severe DR', 'Proliferative DR']
            result = {
                "dr_status": "Negative" if pred_class == 0 else "Positive",
                "severity_level": categories[pred_class],
                "confidence": float(predictions[pred_class]),
                "predictions": {cat: float(pred) for cat, pred in zip(categories, predictions)}
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Prediction error: {str(e)}") 