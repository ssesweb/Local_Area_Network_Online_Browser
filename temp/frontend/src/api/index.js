/**
 * API服务索引
 * 统一导出所有API服务，方便前端组件使用
 */

import fileService from './fileService';
import mediaService from './mediaService';
import uiService from './uiService';

/**
 * API服务对象
 * 包含所有前端API服务
 */
const apiServices = {
  /**
   * 文件服务
   * 负责文件系统相关操作
   */
  file: fileService,
  
  /**
   * 媒体服务
   * 负责媒体文件相关操作
   */
  media: mediaService,
  
  /**
   * 用户界面服务
   * 负责处理用户界面交互和状态管理
   */
  ui: uiService
};

// 导出API服务对象
export default apiServices;

// 单独导出各服务，方便按需引入
export { fileService, mediaService, uiService };