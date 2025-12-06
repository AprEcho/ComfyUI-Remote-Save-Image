"""
ComfyUI-Remote-Save-Image
A custom node for ComfyUI that allows uploading generated images to any HTTP endpoint.
"""

from .remote_image_saver import RemotePreviewSave

NODE_CLASS_MAPPINGS = {
    "RemotePreviewSave": RemotePreviewSave
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RemotePreviewSave": "Remote Preview & Save"
}
