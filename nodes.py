import torch
import base64
import os
import io
import folder_paths
from PIL import Image, ImageOps
import numpy as np

class Base64ImageLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base64_data": ("STRING", {"multiline": True}),
                "filename": ("STRING", {"default": "api_upload.png"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_base64"
    CATEGORY = "image"

    def load_base64(self, base64_data, filename):
        # 1. Decode Base64
        if "," in base64_data: # Handle data:image/png;base64,... headers
            base64_data = base64_data.split(",")[1]
            
        img_data = base64.b64decode(base64_data)
        img = Image.open(io.BytesIO(img_data))
        
        # 2. Convert to ComfyUI Standard Tensor
        img = ImageOps.exif_transpose(img)
        image = img.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        
        # 3. Create Mask (Standard ComfyUI logic)
        if 'A' in img.getbands():
            mask = np.array(img.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            
        return (image, mask)

NODE_CLASS_MAPPINGS = {"Base64ImageLoader": Base64ImageLoader}
NODE_DISPLAY_NAME_MAPPINGS = {"Base64ImageLoader": "Load Image from Base64"}