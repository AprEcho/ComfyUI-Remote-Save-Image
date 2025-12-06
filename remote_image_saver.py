import json
import io
import requests
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np
import os
import logging
import traceback
import folder_paths
from comfy.cli_args import args
import random

# Configure logging
logger = logging.getLogger('RemotePreviewSave')
logger.setLevel(logging.INFO)
if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

class UploadConfig:
    """A simple node to hold upload configuration."""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "upload_url": ("STRING", {"default": ""}),
                "upload_mode": (["HTTP_POST", "WEBDAV"], {"default": "WEBDAV"}),
                "username": ("STRING", {"default": ""}),
                "password": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("UPLOAD_CONFIG",)
    FUNCTION = "configure"
    CATEGORY = "image/upload"

    def configure(self, upload_url, upload_mode, username, password):
        config = {
            "url": upload_url,
            "mode": upload_mode,
            "user": username,
            "pass": password
        }
        return (config,)

class RemotePreviewAndUpload:
    """
    A node that previews an image locally (like PreviewImage) and optionally uploads it to a remote server.
    """
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
            },
            "optional": {
                "upload_config": ("UPLOAD_CONFIG",)
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "execute"
    OUTPUT_NODE = True
    CATEGORY = "image/upload"

    def execute(self, images, upload_config=None, prompt=None, extra_pnginfo=None):
        full_output_folder = self.output_dir
        subfolder = "" # Temp files don't have subfolders

        results = []
        for (batch_number, image) in enumerate(images):
            # --- 1. Local Save (for Preview) ---
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            metadata = PngInfo()
            if not args.disable_metadata:
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            # Generate filename based on timestamp
            timestamp = time.strftime("%Y%m%d%H%M%S")
            ms = int(time.time() * 1000) % 1000
            file = f"{timestamp}{ms:03d}_{batch_number:03d}.png"
            local_filepath = os.path.join(full_output_folder, file)

            try:
                img.save(local_filepath, pnginfo=metadata, compress_level=self.compress_level)
                logger.info(f"Saved image locally to: {local_filepath}")

                results.append({"filename": file, "subfolder": subfolder, "type": self.type})
            except Exception as e:
                logger.error(f"Error saving image locally: {e}\n{traceback.format_exc()}")
                continue

            # --- 2. Remote Upload (if config is provided) ---
            if not upload_config or not upload_config.get("url"):
                logger.info("No upload configuration provided, skipping remote upload.")
                continue

            try:
                remote_filename = os.path.basename(local_filepath)
                
                # Check for remote file existence
                file_exists = False
                if upload_config["mode"] == "WEBDAV":
                    full_remote_url = f"{upload_config['url'].rstrip('/')}/{remote_filename}"
                    auth = (upload_config["user"], upload_config["pass"]) if upload_config["user"] else None
                    try:
                        response = requests.head(full_remote_url, auth=auth, timeout=10)
                        if response.status_code == 200:
                            file_exists = True
                            logger.info(f"Remote file exists, skipping upload: {full_remote_url}")
                    except requests.RequestException as e:
                        logger.warning(f"Could not check for remote file existence: {e}")
                
                if file_exists:
                    continue

                # Perform upload
                with open(local_filepath, 'rb') as f:
                    image_bytes = f.read()

                if upload_config["mode"] == "WEBDAV":
                    auth = (upload_config["user"], upload_config["pass"]) if upload_config["user"] else None
                    response = requests.put(full_remote_url, data=image_bytes, auth=auth, timeout=60)
                    response.raise_for_status()
                    logger.info(f"Successfully uploaded to {full_remote_url}")
                
                elif upload_config["mode"] == "HTTP_POST":
                    auth = (upload_config["user"], upload_config["pass"]) if upload_config["user"] else None
                    files = {"file": (remote_filename, image_bytes, "image/png")}
                    response = requests.post(upload_config["url"], files=files, auth=auth, timeout=60)
                    response.raise_for_status()
                    logger.info(f"Successfully uploaded via HTTP POST to {upload_config['url']}. Response: {response.text}")

            except Exception as e:
                logger.error(f"Error uploading image: {e}\n{traceback.format_exc()}")

        return {"ui": {"images": results}}
