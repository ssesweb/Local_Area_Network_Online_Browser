/**
 * 文件服务API
 * 负责与后端API通信，获取文件系统数据
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
 * 文件服务类
 */
class FileService {
  /**
   * 获取所有驱动器
   * @returns {Promise<Array>} 驱动器列表
   */
  async getDrives() {
    try {
      const response = await apiClient.get('/drives');
      return response.data.drives;
    } catch (error) {
      console.error('获取驱动器失败:', error);
      throw error;
    }
  }

  /**
   * 获取系统文件夹
   * @returns {Promise<Object>} 系统文件夹对象
   */
  async getSystemFolders() {
    try {
      const response = await apiClient.get('/system-folders');
      return response.data.system_folders;
    } catch (error) {
      console.error('获取系统文件夹失败:', error);
      throw error;
    }
  }

  /**
   * 浏览指定路径
   * @param {string} path - 要浏览的路径
   * @returns {Promise<Object>} 包含文件和目录的对象
   */
  async browse(path) {
    try {
      const response = await apiClient.get('/browse', {
        params: { path }
      });
      return response.data;
    } catch (error) {
      console.error('浏览路径失败:', error);
      throw error;
    }
  }

  /**
   * 获取文件下载URL
   * @param {string} path - 文件路径
   * @returns {string} 下载URL
   */
  getDownloadUrl(path) {
    return `${API_BASE_URL}/download?path=${encodeURIComponent(path)}`;
  }

  /**
   * 获取缩略图URL
   * @param {string} path - 缩略图路径
   * @returns {string} 缩略图URL
   */
  getThumbnailUrl(path) {
    return `${API_BASE_URL}/thumbnail?path=${encodeURIComponent(path)}`;
  }

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
}

// 导出文件服务实例
export default new FileService();