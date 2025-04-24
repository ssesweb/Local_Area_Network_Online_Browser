# 前后端分离API文档

## 1. 概述

本文档详细说明前后端分离架构中的API接口规范，包括前端API服务层与后端RESTful API的交互方式、数据格式和错误处理机制。

## 2. API基础信息

- **基础URL**: `http://localhost:5000/api`
- **请求格式**: JSON
- **响应格式**: JSON
- **认证方式**: 暂无认证要求

## 3. 前端API服务层

前端API服务层是前端应用与后端API之间的桥梁，负责处理所有与后端的通信，并将数据转换为前端组件可用的格式。

### 3.1 服务模块划分

前端API服务层分为以下几个模块：

#### 3.1.1 文件服务 (fileService.js)

负责文件系统相关操作，包括获取驱动器、系统文件夹、浏览目录等。

```javascript
// 主要方法
getDrives()              // 获取所有驱动器
getSystemFolders()       // 获取系统文件夹
browse(path)             // 浏览指定路径
getDownloadUrl(path)     // 获取文件下载URL
getThumbnailUrl(path)    // 获取缩略图URL
```

#### 3.1.2 媒体服务 (mediaService.js)

负责媒体文件相关操作，包括获取媒体信息、预览URL等。

```javascript
// 主要方法
getMediaInfo(path)                // 获取媒体文件信息
getPreviewUrl(path)              // 获取媒体文件预览URL
getVideoThumbnailUrl(path)       // 获取视频缩略图URL
isImage(filename)                // 判断文件是否为图片
isVideo(filename)                // 判断文件是否为视频
isAudio(filename)                // 判断文件是否为音频
```

#### 3.1.3 用户界面服务 (uiService.js)

负责处理用户界面交互和状态管理。

```javascript
// 主要方法
formatFileSize(size)             // 格式化文件大小
getFileIcon(filename)            // 获取文件图标
getFileColor(filename)           // 获取文件颜色
buildBreadcrumbs(path)           // 构建面包屑导航
processBrowseResponse(data)      // 处理文件浏览响应数据
```

## 4. 后端API端点

### 4.1 文件系统API

#### 4.1.1 获取驱动器

- **URL**: `/api/drives`
- **方法**: `GET`
- **描述**: 获取系统所有可用驱动器
- **响应示例**:
  ```json
  {
    "drives": ["C:\\", "D:\\", "E:\\"]
  }
  ```

#### 4.1.2 获取系统文件夹

- **URL**: `/api/system-folders`
- **方法**: `GET`
- **描述**: 获取系统常用文件夹（桌面、文档等）
- **响应示例**:
  ```json
  {
    "system_folders": {
      "桌面": {
        "name": "桌面",
        "path": "C:\\Users\\Username\\Desktop"
      },
      "文档": {
        "name": "文档",
        "path": "C:\\Users\\Username\\Documents"
      }
    }
  }
  ```

#### 4.1.3 浏览目录

- **URL**: `/api/browse`
- **方法**: `GET`
- **参数**: `path` (要浏览的路径)
- **描述**: 获取指定路径下的文件和目录
- **响应示例**:
  ```json
  {
    "dirs": [
      {
        "name": "folder1",
        "path": "C:\\folder1",
        "type": "directory"
      }
    ],
    "files": [
      {
        "name": "file.txt",
        "path": "C:\\file.txt",
        "size": 1024,
        "size_formatted": "1.0 KB",
        "modified": 1623456789.0,
        "modified_formatted": "2021-06-12 10:30:45",
        "thumbnail": null,
        "type": "file",
        "icon": "fa-file",
        "color": "light"
      }
    ],
    "current_path": "C:\\",
    "path_parts": ["C:"]
  }
  ```

### 4.2 媒体API

#### 4.2.1 获取媒体信息

- **URL**: `/api/media/info`
- **方法**: `GET`
- **参数**: `path` (媒体文件路径)
- **描述**: 获取媒体文件的详细信息
- **响应示例**:
  ```json
  {
    "name": "video.mp4",
    "path": "C:\\video.mp4",
    "size": 10485760,
    "size_formatted": "10.0 MB",
    "modified": 1623456789.0,
    "modified_formatted": "2021-06-12 10:30:45",
    "type": "video",
    "preview_url": "/api/download?path=C:\\video.mp4",
    "thumbnail": "/api/thumbnail?path=abcdef123456.jpg"
  }
  ```

#### 4.2.2 文件下载

- **URL**: `/api/download`
- **方法**: `GET`
- **参数**: `path` (文件路径)
- **描述**: 下载或预览文件
- **响应**: 文件内容流

#### 4.2.3 获取缩略图

- **URL**: `/api/thumbnail`
- **方法**: `GET`
- **参数**: `path` (缩略图文件名)
- **描述**: 获取视频缩略图
- **响应**: 图片内容流

## 5. 错误处理

### 5.1 错误响应格式

所有API错误响应都遵循以下格式：

```json
{
  "error": "错误描述信息"
}
```

### 5.2 HTTP状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

### 5.3 前端错误处理

前端API服务层统一处理错误，并将错误信息传递给UI组件：

```javascript
try {
  const response = await apiClient.get('/endpoint');
  return response.data;
} catch (error) {
  console.error('操作失败:', error);
  throw error; // 将错误传递给调用者
}
```

## 6. 数据模型

### 6.1 文件对象

```json
{
  "name": "文件名",
  "path": "完整路径",
  "size": 文件大小（字节）,
  "size_formatted": "格式化的文件大小",
  "modified": 修改时间戳,
  "modified_formatted": "格式化的修改时间",
  "thumbnail": "缩略图路径（如果有）",
  "type": "文件类型",
  "icon": "图标类名",
  "color": "颜色类名"
}
```

### 6.2 目录对象

```json
{
  "name": "目录名",
  "path": "完整路径",
  "type": "directory"
}
```

### 6.3 媒体信息对象

```json
{
  "name": "文件名",
  "path": "完整路径",
  "size": 文件大小（字节）,
  "size_formatted": "格式化的文件大小",
  "modified": 修改时间戳,
  "modified_formatted": "格式化的修改时间",
  "type": "媒体类型（image/video/audio）",
  "preview_url": "预览URL",
  "thumbnail": "缩略图URL（仅视频）"
}
```

## 7. 前后端交互流程

1. 前端组件调用API服务层方法
2. API服务层构造请求并发送到后端
3. 后端处理请求并返回响应
4. API服务层处理响应数据并返回给前端组件
5. 前端组件更新UI

## 8. 性能优化

- 使用axios实例配置请求超时和基础URL
- 缓存频繁请求的数据
- 错误重试机制
- 请求取消功能（用于导航变更时）

## 9. 安全考虑

- 路径参数进行URL编码
- 错误信息不暴露敏感信息
- 输入验证和过滤