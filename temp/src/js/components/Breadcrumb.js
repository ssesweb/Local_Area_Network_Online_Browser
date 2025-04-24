class Breadcrumb {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.path = [];
  }

  // 更新导航路径（对应功能1.6）
  updatePath(newPath) {
    this.path = newPath.split('/');
    this.render();
  }

  render() {
    this.container.innerHTML = this.path.map((segment, index) => 
      `<a href="#" class="path-segment" data-index="${index}">${segment}</a>`
    ).join(' / ');
  }
}