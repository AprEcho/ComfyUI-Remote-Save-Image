import json
import io
import time
import requests
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import torch
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

class RemotePreviewSave:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
            },
            "optional": {
                "upload_mode": (["HTTP_POST", "WEBDAV"], {"default": "HTTP_POST"}),
                "upload_url": ("STRING", {"default": ""}),
                # HTTP POST specific
                "image_field_name": ("STRING", {"default": "file"}),
                "headers_json": ("STRING", {"default": "{}", "multiline": True}),
                "extra_data_json": ("STRING", {"default": "{}", "multiline": True}),
                # WebDAV specific
                "webdav_user": ("STRING", {"default": ""}),
                "webdav_password": ("STRING", {"default": "", "multiline": False}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_and_upload"
    OUTPUT_NODE = True
    CATEGORY = "image/upload"

    def save_and_upload(self, images, filename_prefix="ComfyUI", upload_mode="HTTP_POST", upload_url="",
                        image_field_name="file", headers_json="{}", extra_data_json="{}",
                        webdav_user="", webdav_password="", prompt=None, extra_pnginfo=None):

        # Use native ComfyUI filename and path generation
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, _ = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        
        results = []
        for (batch_number, image) in enumerate(images):
            # --- 1. Local Save (for Preview) ---
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            # Generate filename for the current image in the batch
            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            local_filepath = os.path.join(full_output_folder, file)
            
            try:
                img.save(local_filepath, pnginfo=metadata, compress_level=self.compress_level)
                logger.info(f"Saved image locally to: {local_filepath}")
                
                # This result is for the UI preview and is always returned
                results.append({
                    "filename": file,
                    "subfolder": subfolder,
                    "type": self.type
                })
                counter += 1
            except Exception as e:
                logger.error(f"Error saving image locally: {e}\n{traceback.format_exc()}")
                continue # Skip to next image if local save fails

            # --- 2. Remote Upload ---
            if not upload_url:
                logger.info("No upload_url provided, skipping remote upload.")
                continue

            try:
                remote_filename = os.path.basename(local_filepath)
                
                # --- 2a. Check for remote file existence ---
                file_exists = False
                if upload_mode == "WEBDAV":
                    full_remote_url = f"{upload_url.rstrip('/')}/{remote_filename}"
                    auth = (webdav_user, webdav_password) if webdav_user else None
                    try:
                        response = requests.head(full_remote_url, auth=auth, timeout=10)
                        if response.status_code == 200:
                            file_exists = True
                            logger.info(f"Remote file exists, skipping upload: {full_remote_url}")
                    except requests.RequestException as e:
                        logger.warning(f"Could not check for remote file existence: {e}")
                
                if file_exists:
                    continue # Skip upload

                # --- 2b. Perform upload ---
                with open(local_filepath, 'rb') as f:
                    image_bytes = f.read()

                if upload_mode == "WEBDAV":
                    response = requests.put(full_remote_url, data=image_bytes, auth=auth, timeout=60)
                    response.raise_for_status()
                    logger.info(f"Successfully uploaded to {full_remote_url}")
                
                elif upload_mode == "HTTP_POST":
                    headers = json.loads(headers_json)
                    extra_data = json.loads(extra_data_json)
                    files = {image_field_name: (remote_filename, image_bytes, "image/png")}
                    
                    response = requests.post(upload_url, files=files, data=extra_data, headers=headers, timeout=60)
                    response.raise_for_status()
                    logger.info(f"Successfully uploaded via HTTP POST to {upload_url}. Response: {response.text}")

            except Exception as e:
                logger.error(f"Error uploading image: {e}\n{traceback.format_exc()}")
                # Continue to the next image, as local preview is already handled

        return {"ui": {"images": results}}
