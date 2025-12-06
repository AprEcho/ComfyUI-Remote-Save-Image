# ComfyUI 模块化上传节点

这是一个将远程上传功能模块化的 ComfyUI 自定义节点集合。它将上传配置与图像处理完全分离，提供了极大的灵活性和可复用性。

## 概述

本插件包含两个核心节点：
1.  **`Upload Config`**: 一个用于定义远程服务器信息（地址、模式、凭据）的配置节点。
2.  **`Preview & Upload Image`**: 一个用于预览图像并根据传入的配置执行上传的执行节点。

这种设计允许您在工作流中创建一个配置，然后将其连接到多个 `Preview & Upload Image` 节点，实现配置的统一管理。

## 特性

-   **模块化设计**：将配置与执行分离，使工作流更清晰、更易于管理。
-   **原生预览体验**：`Preview & Upload Image` 节点完美复刻了原生 `PreviewImage` 的功能，可立即在界面上显示结果。
-   **时间戳命名**：文件名将根据生成时间自动命名（例如 `20251206192803123_000.png`），清晰明了。
-   **元数据保留**：自动将完整的工作流元数据嵌入到 PNG 文件中。
-   **统一认证**：无论是 `HTTP POST`（基本认证）还是 `WebDAV`，都使用统一的用户名/密码输入。
-   **WebDAV 查重**：在 WebDAV 模式下，上传前会检查文件是否存在，避免重复上传。
-   **可选上传**：如果 `Preview & Upload Image` 节点没有连接 `Upload Config`，它就只作为一个标准的预览节点使用。

## 安装

1.  将此仓库克隆到您的 ComfyUI 的 `custom_nodes` 目录中。
2.  安装所需的依赖项: `pip install -r requirements.txt`。
3.  重启 ComfyUI。

## 使用方法

安装后，您将在 `image/upload` 类别中找到两个新节点。

### 1. `Upload Config` 节点
这个节点用来定义您的上传目标。

-   **upload_url**: 远程服务器地址。
-   **upload_mode**: 上传模式 (`HTTP_POST` 或 `WEBDAV`)。
-   **username**: 用户名。
-   **password**: 密码。

它会输出一个 `UPLOAD_CONFIG` 对象。

### 2. `Preview & Upload Image` 节点
这个节点负责处理和预览图像。

-   **images (输入)**: 连接到图像生成节点的输出。
-   **upload_config (输入, 可选)**: 连接到 `Upload Config` 节点的输出。

### 示例工作流

1.  在您的工作流中添加一个 `Upload Config` 节点，并填入您的服务器信息。
2.  在 KSampler 等节点的输出后面，添加一个 `Preview & Upload Image` 节点。
3.  将 `Upload Config` 节点的 `UPLOAD_CONFIG` 输出连接到 `Preview & Upload Image` 节点的 `upload_config` 输入。

现在，每次运行工作流时，图片都会先在本地预览，然后自动上传到您配置的服务器。如果您想暂时禁用上传，只需断开两个节点之间的连接即可。

## 许可证

[MIT 许可证](LICENSE)
