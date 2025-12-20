from .base64_loader import Base64ImageLoader

# This tells ComfyUI what classes to register
NODE_CLASS_MAPPINGS = {
    "Base64ImageLoader": Base64ImageLoader
}

# This tells ComfyUI what to show in the UI menu
NODE_DISPLAY_NAME_MAPPINGS = {
    "Base64ImageLoader": "Base64 Image Loader"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']