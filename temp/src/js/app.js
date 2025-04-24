// 模块初始化
const viewController = new ViewController();
const fileManager = new FileManager();
const mediaHandler = new MediaHandler();

// 启动核心功能
document.addEventListener('DOMContentLoaded', () => {
  viewController.initGridSizes();
  mediaHandler.initLazyLoad();
  mediaHandler.initVideoPlayers();
  
  // 分页初始化（对应功能7）
  fileManager.getPaginatedFiles().then(data => {
    new FileGridRenderer().render(data.items);
    new Pagination().init(data.total);
  });
});