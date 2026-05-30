from PIL import Image
import os


def resize_image(image_path, x, y):

    base, ext = os.path.splitext(image_path)
    new_image_path = f"{base}_resized{ext}"
    try:
        x = int(x)
        y = int(y)
    except ValueError:
        x, y = 800, 800 
    try:
        with Image.open(image_path) as img:
            img = img.resize((x, y))
            img.save(new_image_path)
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

def crop_image(image_path, left, upper, right, lower):
    # not implemented for now
    return None
    
def convert_image_format(image_path, target_format):
    # not implemented for now
    return None
