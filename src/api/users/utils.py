from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def resize_avatar(image, size=(200, 200)):
    """Resize an uploaded avatar image"""
    if not image:
        return None
        
    img = Image.open(image)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.thumbnail(size)
    output = BytesIO()
    img.save(output, format='JPEG', quality=85)
    output.seek(0)
    
    return InMemoryUploadedFile(
        output, 'ImageField', 
        f"{image.name.split('.')[0]}.jpg", 
        'image/jpeg', 
        sys.getsizeof(output), None
    )