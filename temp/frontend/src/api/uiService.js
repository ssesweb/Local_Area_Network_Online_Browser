/**
 * 用户界面服务API
 * 负责处理用户界面交互和状态管理
 */

import fileService from './fileService';
import mediaService from './mediaService';

/**
 * 用户界面服务类
 */
class UIService {
  /**
   * 格式化文件大小
   * @param {number} size - 文件大小（字节）
   * @returns {string} 格式化后的文件大小
   */
  formatFileSize(size) {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let formattedSize = size;
    let unitIndex = 0;
    
    while (formattedSize >= 1024 && unitIndex < units.length - 1) {
      formattedSize /= 1024;
      unitIndex++;
    }
    
    return `${formattedSize.toFixed(1)} ${units[unitIndex]}`;
  }

  /**
   * 获取文件图标
   * @param {string} filename - 文件名
   * @returns {string} 文件图标类名
   */
  getFileIcon(filename) {
    const ext = this.getFileExtension(filename).toLowerCase();
    const iconMap = {
      '.pdf': 'fa-file-pdf',
      '.doc': 'fa-file-word',
      '.docx': 'fa-file-word',
      '.xls': 'fa-file-excel',
      '.xlsx': 'fa-file-excel',
      '.ppt': 'fa-file-powerpoint',
      '.pptx': 'fa-file-powerpoint',
      '.jpg': 'fa-file-image',
      '.jpeg': 'fa-file-image',
      '.png': 'fa-file-image',
      '.gif': 'fa-file-image',
      '.mp4': 'fa-file-video',
      '.avi': 'fa-file-video',
      '.mov': 'fa-file-video',
      '.mkv': 'fa-file-video',
      '.mp3': 'fa-file-audio',
      '.wav': 'fa-file-audio',
      '.zip': 'fa-file-archive',
      '.rar': 'fa-file-archive',
    };
    return iconMap[ext] || 'fa-file';
  }

  /**
   * 获取文件颜色
   * @param {string} filename - 文件名
   * @returns {string} 文件颜色类名
   */
  getFileColor(filename) {
    const ext = this.getFileExtension(filename).toLowerCase();
    const colorMap = {
      '.pdf': 'danger',
      '.doc': 'primary',
      '.docx': 'primary',
      '.xls': 'success',
      '.xlsx': 'success',
      '.ppt': 'warning',
      '.pptx': 'warning',
      '.jpg': 'info',
      '.jpeg': 'info',
      '.png': 'info',
      '.gif': 'info',
      '.mp4': 'dark',
      '.avi': 'dark',
      '.mov': 'dark',
      '.mkv': 'dark',
      '.mp3': 'secondary',
      '.wav': 'secondary',
      '.zip': 'secondary',
      '.rar': 'secondary',
    };
    return colorMap[ext] || 'light';
  }

  /**
   * 获取文件扩展名
   * @param {string} filename - 文件名
   * @returns {string} 文件扩展名
   */
  getFileExtension(filename) {
    return filename.substring(filename.lastIndexOf('.'));
  }

  /**
   * 构建面包屑导航
   * @param {string} path - 当前路径
   * @returns {Array} 面包屑导航数组
   */
  buildBreadcrumbs(path) {
    const parts = path.split('\\').filter(part => part);
    const breadcrumbs = [];
    let currentPath = '';
    
    // 添加根目录
    if (parts.length > 0 && parts[0].includes(':')) {
      currentPath = parts[0] + '\\';
      breadcrumbs.push({
        name: parts[0],
        path: currentPath
      });
    }
    
    // 添加子目录
    for (let i = 1; i < parts.length; i++) {
      currentPath += parts[i] + '\\';
      breadcrumbs.push({
        name: parts[i],
        path: currentPath
      });
    }
    
    return breadcrumbs;
  }

  /**
   * 处理文件浏览响应数据
   * @param {Object} data - 浏览响应数据
   * @returns {Object} 处理后的数据
   */
  processBrowseResponse(data) {
    // 构建面包屑导航
    const breadcrumbs = this.buildBreadcrumbs(data.current_path);
    
    // 处理文件和目录
    const files = data.files.map(file => ({
      ...file,
      isImage: mediaService.isImage(file.name),
      isVideo: mediaService.isVideo(file.name),
      isAudio: mediaService.isAudio(file.name),
      icon: this.getFileIcon(file.name),
      color: this.getFileColor(file.name)
    }));
    
    return {
      ...data,
      breadcrumbs,
      files
    };
  }
}

// 导出用户界面服务实例
export default new UIService();