// 保存视图偏好到本地存储
function saveViewPreference(viewType) {
    localStorage.setItem('preferredView', viewType);
}

// 从本地存储加载视图偏好
function loadViewPreference() {
    return localStorage.getItem('preferredView') || 'list';
}

// 初始化视图
function initView() {
    const preferredView = loadViewPreference();
    document.querySelector(`.view-btn[data-view="${preferredView}"]`).click();
}