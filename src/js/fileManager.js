class FileManager {
  // ...现有文件获取代码...

  // 新增分页处理（对应功能7）
  async getPaginatedFiles(page = 1, pageSize = 50) {
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    return {
      items: this.files.slice(start, end),
      total: this.files.length,
      currentPage: page
    };
  }
}