import cloudinary.uploader
from typing import Optional
import os

class ImageService:
    @staticmethod
    async def upload_image(file_path: str, patient_id: str) -> Optional[str]:
        try:
            # Get just the filename from the path
            filename = os.path.basename(file_path)
            
            # Upload to cloudinary
            result = cloudinary.uploader.upload(
                file_path,
                folder="retinal_images",
                public_id=f"patient_{patient_id}_{os.path.splitext(filename)[0]}",
                resource_type="image"
            )
            
            # Return the secure URL
            return result.get('secure_url')
            
        except Exception as e:
            # Include more detailed error information
            raise Exception(f"Error uploading image: {str(e)} for file: {file_path}") 