import base64
import os
import io
import hashlib
import torch
import numpy as np
from PIL import Image, ImageOps
import folder_paths

class Base64ImageLoader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        # This defines what the "API workflow" JSON expects for this node.
        return {
            "required": {
                "image_base64": ("STRING", {"multiline": True, "default": ""}),
                "image_name": ("STRING", {"default": "input_image.png"}),
            },
            "optional": {
                "image_path": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"
    CATEGORY = "image"

    def load_image(self, image_base64, image_name, image_path=""):
        if not image_base64:
            # Return empty tensors (1x64x64) if no data is provided to prevent crashes
            return (torch.zeros((1, 64, 64, 3)), torch.zeros((64, 64)))

        # 1. Decode and Hash for Reuse
        # Strips data URI prefix if the user accidentally includes it
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
            
        image_data = base64.b64decode(image_base64)
        image_hash = hashlib.sha256(image_data).hexdigest()
        
        # 2. Storage Logic
        # Saves to ComfyUI's standard temp folder for automatic cleanup
        temp_dir = folder_paths.get_temp_directory()
        file_ext = os.path.splitext(image_name)[1] or ".png"
        save_filename = f"b64_{image_hash}{file_ext}"
        save_path = os.path.join(temp_dir, save_filename)

        # Hashing logic ensures we don't write the same file multiple times
        if not os.path.exists(save_path):
            with open(save_path, "wb") as f:
                f.write(image_data)

        # 3. Processing into ComfyUI Tensors
        img = Image.open(save_path)
        img = ImageOps.exif_transpose(img) # Corrects orientation
        
        # Convert to RGB and normalize to 0.0 - 1.0 range
        image = img.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        # Add batch dimension: [1, H, W, 3]
        image = torch.from_numpy(image)[None,]
        
        # 4. Correct Mask Handling
        if 'A' in img.getbands():
            mask = np.array(img.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            # Create a blank mask matching the image dimensions
            mask = torch.zeros((image.shape[1], image.shape[2]), dtype=torch.float32)
        
        return (image, mask)

# These mappings are what ComfyUI looks for to "add" the node to the system
NODE_CLASS_MAPPINGS = {
    "Base64ImageLoader": Base64ImageLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Base64ImageLoader": "Base64 Image Loader"
}