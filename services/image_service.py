import cloudinary.uploader
from typing import Optional
import os

class ImageService:
    @staticmethod
    async def upload_image(file, patient_id: str) -> Optional[str]:
        try:
            # Upload to cloudinary
            result = cloudinary.uploader.upload(
                file,
                folder="retinal_images",
                public_id=f"patient_{patient_id}_{os.path.splitext(file.filename)[0]}",
                resource_type="image"
            )
            
            # Return the secure URL
            return result.get('secure_url')
            
        except Exception as e:
            raise Exception(f"Error uploading image: {str(e)}") 