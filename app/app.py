from flask import Flask, render_template, send_from_directory
import os
import subprocess
import tempfile
from datetime import datetime

app = Flask(__name__)

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

# 视频缩略图生成函数
def generate_video_thumbnail(video_path):
    try:
        # 创建缩略图目录
        thumbnails_dir = os.path.join(app.root_path, 'static', 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # 添加自动清理机制
        clean_thumbnail_cache(thumbnails_dir)
        
        # 使用视频文件的哈希值作为缩略图文件名，确保唯一性
        import hashlib
        video_hash = hashlib.md5(video_path.encode()).hexdigest()
        thumbnail_filename = f"{video_hash}.jpg"
        thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
        
        # 如果缩略图已存在，直接返回
        if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
            return thumbnail_filename
        
        # 尝试提取第5秒的帧
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', '00:00:05',  # 第5秒
            '-frames:v', '1',
            '-q:v', '2',
            thumbnail_path
        ]
        
        # 修改这里：添加encoding参数解决编码问题
        result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', timeout=10)
        
        # 如果提取第5秒失败，则尝试提取首帧
        if result.returncode != 0:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-frames:v', '1',
                '-q:v', '2',
                thumbnail_path
            ]
            subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', timeout=10)
        
        # 检查缩略图是否成功生成
        if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
            return thumbnail_filename
        else:
            return None
    except Exception as e:
        print(f"生成视频缩略图失败: {e}")
        return None

# 在download路由前添加MIME类型映射
MIME_MAP = {
    'mp4': 'video/mp4',
    'avi': 'video/x-msvideo',
    'mov': 'video/quicktime',
    'mkv': 'video/x-matroska'
}

@app.route('/download/<path:filepath>')
def download(filepath):
    directory, filename = os.path.split(filepath)
    # 设置as_attachment=False以允许浏览器直接显示内容
    response = send_from_directory(directory, filename, as_attachment=False)
    # 添加MIME类型
    ext = filename.split('.')[-1].lower()
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
    return dict(
        get_file_icon=get_file_icon,
        os=os,
        get_file_color=get_file_color,
        now=datetime.now()  # 添加当前时间
    )

# 新增文件类型颜色映射函数
def get_file_color(filename):
    ext = os.path.splitext(filename)[1].lower()
    color_map = {
        '.pdf': 'danger',
        '.doc': 'primary',
        '.docx': 'primary',
        '.xls': 'success',
        '.xlsx': 'success',
        '.ppt': 'warning',
        '.pptx': 'warning',
        '.jpg': 'info',
        '.png': 'info',
        '.gif': 'info',
        '.mp4': 'dark',
        '.avi': 'dark',
        '.mp3': 'secondary',
        '.zip': 'secondary',
        '.rar': 'secondary',
    }
    return color_map.get(ext, 'light')

# 文件类型检测函数（保持原有实现）
def get_file_icon(filename):
    ext = os.path.splitext(filename)[1].lower()
    icon_map = {
        '.pdf': 'fa-file-pdf',
        '.doc': 'fa-file-word',
        '.docx': 'fa-file-word',
        '.xls': 'fa-file-excel',
        '.xlsx': 'fa-file-excel',
        '.ppt': 'fa-file-powerpoint',
        '.pptx': 'fa-file-powerpoint',
        '.jpg': 'fa-file-image',
        '.png': 'fa-file-image',
        '.gif': 'fa-file-image',
        '.mp4': 'fa-file-video',
        '.avi': 'fa-file-video',
        '.mp3': 'fa-file-audio',
        '.zip': 'fa-file-archive',
        '.rar': 'fa-file-archive',
    }
    return icon_map.get(ext, 'fa-file')

def clean_thumbnail_cache(cache_dir, max_size_mb=500, min_size_mb=10):
    """清理缓存文件夹，保持大小在合理范围内"""
    try:
        # 计算当前缓存大小(MB)
        total_size = sum(os.path.getsize(f) for f in os.scandir(cache_dir) if f.is_file()) / (1024*1024)
        
        if total_size > max_size_mb:
            print(f"缓存大小 {total_size:.2f}MB 超过限制 {max_size_mb}MB，开始清理...")
            
            # 获取所有文件并按修改时间排序(旧文件在前)
            files = sorted([f for f in os.scandir(cache_dir) if f.is_file()], 
                         key=lambda x: x.stat().st_mtime)
            
            # 逐个删除最旧的文件直到小于min_size_mb
            deleted_size = 0
            for file in files:
                if total_size - deleted_size <= min_size_mb:
                    break
                    
                file_size = os.path.getsize(file) / (1024*1024)
                try:
                    os.remove(file.path)
                    deleted_size += file_size
                    print(f"已删除旧缓存文件: {file.name} (大小: {file_size:.2f}MB)")
                except Exception as e:
                    print(f"删除文件 {file.name} 失败: {e}")
            
            print(f"清理完成，当前缓存大小: {total_size - deleted_size:.2f}MB")
    except Exception as e:
        print(f"清理缓存时出错: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)