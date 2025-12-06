"""
ComfyUI-Remote-Save-Image
A custom node for ComfyUI that allows uploading generated images to any HTTP endpoint.
"""

from .remote_image_saver import UploadConfig, RemotePreviewAndUpload

NODE_CLASS_MAPPINGS = {
    "UploadConfig": UploadConfig,
    "RemotePreviewAndUpload": RemotePreviewAndUpload,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UploadConfig": "Upload Config",
    "RemotePreviewAndUpload": "Preview & Upload Image",
}
