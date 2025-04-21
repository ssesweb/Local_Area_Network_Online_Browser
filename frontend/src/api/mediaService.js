/**
 * 媒体服务API
 * 负责与后端API通信，处理媒体文件相关操作
 */

import axios from 'axios';

// API基础URL
const API_BASE_URL = 'http://localhost:5000/api';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

/**
 * 媒体服务类
 */
class MediaService {
  /**
   * 获取媒体文件信息
   * @param {string} path - 媒体文件路径
   * @returns {Promise<Object>} 媒体文件信息
   */
  async getMediaInfo(path) {
    try {
      const response = await apiClient.get('/media/info', {
        params: { path }
      });
      return response.data;
    } catch (error) {
      console.error('获取媒体信息失败:', error);
      throw error;
    }
  }

  /**
   * 获取媒体文件预览URL
   * @param {string} path - 媒体文件路径
   * @returns {string} 预览URL
   */
  getPreviewUrl(path) {
    return `${API_BASE_URL}/download?path=${encodeURIComponent(path)}`;
  }

  /**
   * 获取视频缩略图URL
   * @param {string} thumbnailPath - 缩略图路径
   * @returns {string} 缩略图URL
   */
  getVideoThumbnailUrl(thumbnailPath) {
    return `${API_BASE_URL}/thumbnail?path=${encodeURIComponent(thumbnailPath)}`;
  }

  /**
   * 判断文件是否为图片
   * @param {string} filename - 文件名
   * @returns {boolean} 是否为图片
   */
  isImage(filename) {
    const ext = this.getFileExtension(filename).toLowerCase();
    return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'].includes(ext);
  }

  /**
   * 判断文件是否为视频
   * @param {string} filename - 文件名
   * @returns {boolean} 是否为视频
   */
  isVideo(filename) {
    const ext = this.getFileExtension(filename).toLowerCase();
    return ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'].includes(ext);
  }

  /**
   * 判断文件是否为音频
   * @param {string} filename - 文件名
   * @returns {boolean} 是否为音频
   */
  isAudio(filename) {
    const ext = this.getFileExtension(filename).toLowerCase();
    return ['.mp3', '.wav', '.ogg', '.flac', '.aac'].includes(ext);
  }

  /**
   * 获取文件扩展名
   * @param {string} filename - 文件名
   * @returns {string} 文件扩展名
   */
  getFileExtension(filename) {
    return filename.substring(filename.lastIndexOf('.'));
  }
}

// 导出媒体服务实例
export default new MediaService();