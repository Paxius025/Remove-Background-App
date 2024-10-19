from rembg import remove
from PIL import Image
import os
import time

def remove_background(input_path, export_path):
    try:
        # Open the image
        input_image = Image.open(input_path)
        # Get the original size of the image
        original_size = input_image.size
        
        # Process the image using rembg and U-2-Net model
        output_image = remove(input_image)

        # Resize the output image to match the original size
        output_image = output_image.resize(original_size, Image.Resampling.LANCZOS)

        # Create a unique file name based on the current timestamp and original file name
        base_name = os.path.basename(input_path)
        name, ext = os.path.splitext(base_name)
        timestamp = int(time.time())

        # Save as PNG if transparency (RGBA) exists, otherwise save as JPEG
        if output_image.mode == "RGBA":
            new_name = f"{name}_{timestamp}.png"
            output_file = os.path.join(export_path, new_name)
            output_image.save(output_file, format="PNG", quality=95)
        else:
            new_name = f"{name}_{timestamp}.jpg"
            output_file = os.path.join(export_path, new_name)
            output_image = output_image.convert("RGB")  # Convert to RGB for JPEG
            output_image.save(output_file, format="JPEG", quality=95)

        return output_file
    except Exception as e:
        print(f"Error removing background: {e}")
        return None
