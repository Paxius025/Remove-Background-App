from rembg import remove
from PIL import Image
import os

def remove_background(image_path, export_path):
    try:
        input_image = Image.open(image_path)
        output = remove(input_image)
        output_file = os.path.join(export_path, "output.png")
        output.save(output_file)
        return output_file
    except Exception as e:
        print(f"Error: {e}")
        return None
