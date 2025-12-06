# ComfyUI Modular Upload Nodes

A set of custom nodes for ComfyUI that modularizes remote upload functionality. It separates upload configuration from image processing, providing significant flexibility and reusability.

## Overview

This plugin consists of two core nodes:
1.  **`Upload Config`**: A configuration node for defining remote server details (URL, mode, credentials).
2.  **`Preview & Upload Image`**: An execution node that previews an image and performs an upload based on the provided configuration.

This design allows you to create a single configuration in your workflow and connect it to multiple `Preview & Upload Image` nodes for centralized management.

## Features

-   **Modular Design**: Separates configuration from execution, leading to cleaner and more manageable workflows.
-   **Native Preview Experience**: The `Preview & Upload Image` node perfectly replicates the functionality of the native `PreviewImage` node for instant results.
-   **Native Naming Logic**: Fully utilizes ComfyUI's temporary file naming mechanism, eliminating the need for manual filename setup.
-   **Metadata Preservation**: Automatically embeds the full workflow metadata into the PNG file.
-   **Unified Authentication**: Uses a single set of username/password inputs for both `HTTP POST` (Basic Auth) and `WebDAV`.
-   **WebDAV Duplicate Check**: Checks for file existence before uploading in WebDAV mode to prevent duplicates.
-   **Optional Upload**: If the `Preview & Upload Image` node is not connected to an `Upload Config`, it functions solely as a standard preview node.

## Installation

1.  Clone this repository into your ComfyUI `custom_nodes` directory.
2.  Install the required dependencies: `pip install -r requirements.txt`.
3.  Restart ComfyUI.

## Usage

After installation, you will find two new nodes in the `image/upload` category.

### 1. `Upload Config` Node
This node defines your upload destination.

-   **upload_url**: The remote server address.
-   **upload_mode**: The upload mode (`HTTP_POST` or `WEBDAV`).
-   **username**: The username for authentication.
-   **password**: The password for authentication.

It outputs an `UPLOAD_CONFIG` object.

### 2. `Preview & Upload Image` Node
This node processes and previews the image.

-   **images (Input)**: Connect to the output of an image-generating node.
-   **upload_config (Input, Optional)**: Connect to the output of an `Upload Config` node.

### Example Workflow

1.  Add an `Upload Config` node to your workflow and fill in your server details.
2.  After your KSampler (or other image generator), add a `Preview & Upload Image` node.
3.  Connect the `UPLOAD_CONFIG` output from the `Upload Config` node to the `upload_config` input of the `Preview & Upload Image` node.

Now, every time you run the workflow, the image will be previewed locally and then automatically uploaded to your configured server. If you want to disable uploads temporarily, simply disconnect the two nodes.

## License

[MIT License](LICENSE)