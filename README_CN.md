# ComfyUI 远程预览与保存

一个用于 ComfyUI 的自定义节点，它结合了本地即时预览和远程上传备份的功能。

## 概述

本节点旨在提供与 ComfyUI 原生 `PreviewImage` 节点完全一致的使用体验，同时增加了将生成的图片上传到远程服务器（通过 HTTP POST 或 WebDAV）的能力。

它的核心工作流程是：首先将图片保存到本地的临时文件夹以供 ComfyUI 前端即时预览，然后，在后台将该图片上传到您指定的远程位置。

## 特性

- **本地预览优先**：与原生 `PreviewImage` 体验一致，立即在界面上显示生成的图片。
- **高级文件名格式化**：完全支持 ComfyUI 的高级文件名语法，如 `%date:yyyy-MM-dd%` 或引用其他节点的值。
- **元数据保留**：自动将完整的工作流（Prompt, extra_pnginfo）嵌入到 PNG 文件中。
- **双上传模式**：支持通过 `HTTP POST` 和 `WebDAV` 两种方式上传到远程服务器。
- **远程文件查重**：在 WebDAV 模式下，上传前会检查远程服务器是否存在同名文件，如果存在则跳过上传，避免重复。
- **纯 PNG 格式**：为确保元数据完整性，节点只处理和上传 PNG 格式的图片。

## 安装

1.  将此仓库克隆到您的 ComfyUI 的 `custom_nodes` 目录中：
    ```
    cd /path/to/ComfyUI/custom_nodes
    git clone https://github.com/yourusername/ComfyUI-Remote-Save-Image.git
    ```
2.  安装所需的依赖项：
    ```
    cd ComfyUI-Remote-Save-Image
    pip install -r requirements.txt
    ```
3.  重启 ComfyUI

## 使用方法

安装后，您将在 ComfyUI 节点菜单的 `image/upload` 类别中找到 **`Remote Preview & Save`** 节点。

### 节点参数

-   **images**: 连接到图像生成节点的输出。
-   **filename_prefix**: 文件名前缀，支持 ComfyUI 的高级格式化语法。
-   **upload_mode**: 上传模式，选择 `HTTP_POST` 或 `WEBDAV`。
-   **upload_url**: 远程上传的目标地址。
    -   在 **HTTP POST** 模式下，这是接收请求的 API 端点。
    -   在 **WebDAV** 模式下，这是服务器上的目标目录 URL。
-   **image_field_name**: (仅 HTTP POST) 图像文件的表单字段名。
-   **headers_json**: (仅 HTTP POST) 自定义 HTTP 请求头。
-   **extra_data_json**: (仅 HTTP POST) 额外的表单数据。
-   **webdav_user**: (仅 WebDAV) WebDAV 用户名。
-   **webdav_password**: (仅 WebDAV) WebDAV 密码。

**注意**：如果 `upload_url` 为空，节点将只执行本地预览，不会进行远程上传。

## 安全考虑

-   **API 密钥和令牌**：在 `headers_json` 字段中小心处理敏感信息。
-   **数据隐私**：注意您在 `extra_data_json` 字段中发送的数据。

## 许可证

[MIT 许可证](LICENSE)
