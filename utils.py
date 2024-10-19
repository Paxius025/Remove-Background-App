from rembg import remove
from PIL import Image
import os
import time

def remove_background(input_path, output_path):
    try:
        # Open the image
        input_image = Image.open(input_path)
        # Process the image using rembg
        output_image = remove(input_image)
        # Create a unique file name based on the current timestamp and original file name
        base_name = os.path.basename(input_path)
        name, ext = os.path.splitext(base_name)
        timestamp = int(time.time())
        new_name = f"{name}_{timestamp}{ext}"
        output_file = os.path.join(output_path, new_name)
        # Save the processed image
        output_image.save(output_file)
        return output_file
    except Exception as e:
        print(f"Error removing background: {e}")
        return None
