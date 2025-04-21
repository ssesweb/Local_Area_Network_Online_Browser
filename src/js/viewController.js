class ViewController {
  // ...现有视图切换代码...
  
  // 新增宫格尺寸控制（对应功能2.3）
  initGridSizes() {
    this.gridSizes = ['sm', 'md', 'lg', 'xl', '2xl', '3xl'];
    this.currentSize = localStorage.getItem('gridSize') || 'md';
  }

  // 新增视图持久化方法（对应功能2.2）
  saveViewPreference(type, size) {
    localStorage.setItem('viewType', type);
    localStorage.setItem('gridSize', size);
    this.applyViewSettings();
  }
}