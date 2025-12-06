# ComfyUI Remote Preview & Save

A custom node for ComfyUI that combines the immediate feedback of a local preview with the persistence of a remote upload.

## Overview

This node is designed to replicate the user experience of the native `PreviewImage` node while adding the powerful capability to upload the generated image to a remote server via HTTP POST or WebDAV.

Its core workflow is to first save the image to a local temporary directory for an instant preview in the ComfyUI interface, and then, in the background, upload that same image to your specified remote location.

## Features

-   **Local-First Preview**: Exactly matches the native `PreviewImage` experience, showing your results instantly.
-   **Advanced Filename Formatting**: Fully supports ComfyUI's advanced filename syntax, like `%date:yyyy-MM-dd%` or referencing values from other nodes.
-   **Metadata Preservation**: Automatically embeds the full workflow (Prompt, extra_pnginfo) into the PNG file.
-   **Dual Upload Modes**: Supports uploading via both `HTTP POST` and `WebDAV`.
-   **Remote File-Existence Check**: In WebDAV mode, it checks if a file with the same name already exists on the server and skips the upload to prevent duplicates.
-   **PNG-Only**: To ensure metadata integrity, the node exclusively saves and uploads images in PNG format.

## Installation

1.  Clone this repository into your ComfyUI's `custom_nodes` directory:
    ```
    cd /path/to/ComfyUI/custom_nodes
    git clone https://github.com/yourusername/ComfyUI-Remote-Save-Image.git
    ```
2.  Install the required dependencies:
    ```
    cd ComfyUI-Remote-Save-Image
    pip install -r requirements.txt
    ```
3.  Restart ComfyUI

## Usage

After installation, you will find the **`Remote Preview & Save`** node in the `image/upload` category in the ComfyUI node menu.

### Node Parameters

-   **images**: Connect to the output of an image-generating node.
-   **filename_prefix**: The prefix for the filename, which supports ComfyUI's advanced formatting syntax.
-   **upload_mode**: The upload mode, either `HTTP_POST` or `WEBDAV`.
-   **upload_url**: The destination URL for the remote upload.
    -   In **HTTP POST** mode, this is the API endpoint receiving the request.
    -   In **WebDAV** mode, this is the target directory URL on your server.
-   **image_field_name**: (HTTP POST only) The form field name for the image file.
-   **headers_json**: (HTTP POST only) Custom HTTP headers.
-   **extra_data_json**: (HTTP POST only) Additional form data.
-   **webdav_user**: (WebDAV only) Username for WebDAV authentication.
-   **webdav_password**: (WebDAV only) Password for WebDAV authentication.

**Note**: If `upload_url` is left empty, the node will only perform the local preview and skip the remote upload.

## Security Considerations

-   **API Keys and Tokens**: Be careful with sensitive information in the `headers_json` field.
-   **Data Privacy**: Be mindful of what data you're sending in the `extra_data_json` field.

## License

[MIT License](LICENSE)