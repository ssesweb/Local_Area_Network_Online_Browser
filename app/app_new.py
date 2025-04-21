from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

# 导入API蓝图
from api import api

def create_app(test_config=None):
    # 创建并配置应用
    app = Flask(__name__)
    
    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册API蓝图
    app.register_blueprint(api)
    
    # 添加自定义过滤器
    @app.template_filter('datetime')
    def format_datetime(timestamp, format="%Y-%m-%d %H:%M:%S"):
        return datetime.fromtimestamp(timestamp).strftime(format)
    
    @app.template_filter('filesizeformat')
    def format_filesize(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    # 注册过滤器
    app.jinja_env.filters['filesizeformat'] = format_filesize
    
    # 保留原有的模板渲染路由（过渡期使用）
    @app.route('/')
    def index():
        # 获取系统盘符
        drives = [f"{d}:\\" for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f"{d}:\\")] 
        
        # 获取真实的系统文件夹路径
        import winreg
        # 扩展更多系统文件夹
        system_folders = {
            '桌面': '{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}',
            '文档': '{F42EE2D3-909F-4907-8871-4C22FC0BF756}',
            '下载': '{374DE290-123F-4565-9164-39C4925E467B}',
            '图片': '{3ADD1653-EB32-4CB0-BBD7-DFA0ABB5ACCA}',
            '音乐': '{4BD8D571-6D19-48D3-BE97-422220080E43}',
            '视频': '{18989B1D-99B5-455B-841C-AB7C74E4DDFC}',
            'OneDrive': '{8C5C7F1B-E08F-4FBA-9A28-E64B3E7D72FB}',
            '收藏夹': '{1777F761-68AD-4D8A-87BD-30B759FA33DD}',
            '联系人': '{56784854-C6CB-462B-8169-88E350ACB882}'
        }

        valid_folders = {}
        try:
            # 同时检查32位和64位注册表路径
            reg_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
                r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        for name, guid in system_folders.items():
                            try:
                                path = winreg.QueryValueEx(key, guid)[0]
                                path = os.path.expandvars(path)
                                if os.path.exists(path) and name not in valid_folders:
                                    valid_folders[name] = path
                            except WindowsError:
                                continue
                except FileNotFoundError:
                    continue

            # 补充回退方案
            default_folders = {
                '桌面': ['Desktop', '桌面'],
                '文档': ['Documents', '我的文档'],
                '下载': ['Downloads', '下载'],
                '图片': ['Pictures', '我的图片'],
                '音乐': ['Music', '我的音乐'],
                '视频': ['Videos', '我的视频'],
                'OneDrive': ['OneDrive'],
                '收藏夹': ['Links'],
                '联系人': ['Contacts']
            }

            for name, variants in default_folders.items():
                if name not in valid_folders:
                    for folder_name in variants:
                        path = os.path.join(os.path.expanduser('~'), folder_name)
                        if os.path.exists(path):
                            valid_folders[name] = path
                            break

        except Exception as e:
            print(f"路径获取失败: {e}")
        
        return render_template('index.html', drives=drives, system_folders=valid_folders)
    
    @app.route('/browse/<path:dirpath>')
    def browse(dirpath):
        # 获取目录内容
        try:
            items = os.listdir(dirpath)
            files = []
            dirs = []
            for item in items:
                full_path = os.path.join(dirpath, item)
                if os.path.isdir(full_path):
                    dirs.append({
                        'name': item,
                        'path': full_path
                    })
                else:
                    # 检查是否为视频文件，如果是则生成缩略图路径
                    thumbnail_path = None
                    ext = os.path.splitext(item)[1].lower()
                    if ext in ['.mp4', '.avi', '.mov', '.mkv']:
                        from api import generate_video_thumbnail
                        thumbnail_path = generate_video_thumbnail(full_path)
                    
                    files.append({
                        'name': item,
                        'size': os.path.getsize(full_path),
                        'modified': os.path.getmtime(full_path),
                        'thumbnail': thumbnail_path
                    })
            return render_template('browse.html', dirs=dirs, files=files, current_path=dirpath)
        except Exception as e:
            return str(e), 404
    
    @app.route('/download/<path:filepath>')
    def download(filepath):
        directory, filename = os.path.split(filepath)
        # 设置as_attachment=False以允许浏览器直接显示内容
        response = send_from_directory(directory, filename, as_attachment=False)
        # 添加MIME类型
        ext = filename.split('.')[-1].lower()
        from api import MIME_MAP
        if ext in MIME_MAP:
            response.headers['Content-Type'] = MIME_MAP[ext]
        return response
    
    @app.route('/thumbnail/<path:filepath>')
    def thumbnail(filepath):
        """提供视频缩略图"""
        # 从static/thumbnails目录提供缩略图
        thumbnails_dir = os.path.join(app.root_path, 'static', 'thumbnails')
        return send_from_directory(thumbnails_dir, filepath, mimetype='image/jpeg')
    
    # 在模板中注册文件类型检测函数
    @app.context_processor
    def utility_processor():
        from api import get_file_icon, get_file_color
        return dict(
            get_file_icon=get_file_icon,
            os=os,
            get_file_color=get_file_color,
            now=datetime.now()  # 添加当前时间
        )
    
    return app

# 应用实例
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)