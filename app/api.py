from flask import Blueprint, jsonify, request, send_from_directory, current_app
import os
import subprocess
import tempfile
import hashlib
from datetime import datetime

# 创建API蓝图
api = Blueprint('api', __name__, url_prefix='/api')

# 辅助函数
def format_filesize(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def get_file_icon(filename):
    """获取文件图标"""
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

def get_file_color(filename):
    """获取文件颜色"""
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

def generate_video_thumbnail(video_path):
    """生成视频缩略图"""
    try:
        # 创建缩略图目录
        thumbnails_dir = os.path.join(current_app.root_path, 'static', 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # 使用视频文件的哈希值作为缩略图文件名，确保唯一性
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
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        # 如果提取第5秒失败，则尝试提取首帧
        if result.returncode != 0:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-frames:v', '1',
                '-q:v', '2',
                thumbnail_path
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        # 检查缩略图是否成功生成
        if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
            return thumbnail_filename
        else:
            return None
    except Exception as e:
        print(f"生成视频缩略图失败: {e}")
        return None

# API路由
@api.route('/drives', methods=['GET'])
def get_drives():
    """获取系统盘符"""
    drives = [f"{d}:\\" for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f"{d}:\\")] 
    return jsonify({
        'drives': drives
    })

@api.route('/system-folders', methods=['GET'])
def get_system_folders():
    """获取系统文件夹"""
    import winreg
    # 系统文件夹映射
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
        return jsonify({'error': str(e)}), 500
    
    return jsonify({
        'system_folders': {
            name: {
                'name': name,
                'path': path
            } for name, path in valid_folders.items()
        }
    })

@api.route('/browse', methods=['GET'])
def browse():
    """浏览目录内容"""
    dirpath = request.args.get('path', '')
    if not dirpath or not os.path.exists(dirpath):
        return jsonify({'error': 'Invalid path'}), 404
    
    try:
        items = os.listdir(dirpath)
        files = []
        dirs = []
        
        for item in items:
            full_path = os.path.join(dirpath, item)
            if os.path.isdir(full_path):
                dirs.append({
                    'name': item,
                    'path': full_path,
                    'type': 'directory'
                })
            else:
                # 检查是否为视频文件，如果是则生成缩略图路径
                thumbnail_path = None
                ext = os.path.splitext(item)[1].lower()
                if ext in ['.mp4', '.avi', '.mov', '.mkv']:
                    thumbnail_path = generate_video_thumbnail(full_path)
                
                size = os.path.getsize(full_path)
                modified = os.path.getmtime(full_path)
                
                files.append({
                    'name': item,
                    'path': full_path,
                    'size': size,
                    'size_formatted': format_filesize(size),
                    'modified': modified,
                    'modified_formatted': datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S"),
                    'thumbnail': thumbnail_path,
                    'type': 'file',
                    'icon': get_file_icon(item),
                    'color': get_file_color(item)
                })
        
        # 构建路径部分
        path_parts = []
        for part in dirpath.split('\\'):
            if part:
                path_parts.append(part)
        
        return jsonify({
            'dirs': dirs,
            'files': files,
            'current_path': dirpath,
            'path_parts': path_parts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# MIME类型映射
MIME_MAP = {
    'mp4': 'video/mp4',
    'avi': 'video/x-msvideo',
    'mov': 'video/quicktime',
    'mkv': 'video/x-matroska'
}

@api.route('/download', methods=['GET'])
def download():
    """文件下载"""
    filepath = request.args.get('path', '')
    if not filepath or not os.path.exists(filepath) or os.path.isdir(filepath):
        return jsonify({'error': 'Invalid file path'}), 404
    
    directory, filename = os.path.split(filepath)
    # 设置as_attachment=False以允许浏览器直接显示内容
    response = send_from_directory(directory, filename, as_attachment=False)
    # 添加MIME类型
    ext = filename.split('.')[-1].lower()
    if ext in MIME_MAP:
        response.headers['Content-Type'] = MIME_MAP[ext]
    return response

@api.route('/thumbnail', methods=['GET'])
def thumbnail():
    """提供视频缩略图"""
    filepath = request.args.get('path', '')
    if not filepath:
        return jsonify({'error': 'Invalid thumbnail path'}), 404
    
    # 从static/thumbnails目录提供缩略图
    thumbnails_dir = os.path.join(current_app.root_path, 'static', 'thumbnails')
    return send_from_directory(thumbnails_dir, filepath, mimetype='image/jpeg')

@api.route('/media/info', methods=['GET'])
def media_info():
    """获取媒体文件信息"""
    filepath = request.args.get('path', '')
    if not filepath or not os.path.exists(filepath) or os.path.isdir(filepath):
        return jsonify({'error': 'Invalid file path'}), 404
    
    try:
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()
        
        # 基本文件信息
        info = {
            'name': filename,
            'path': filepath,
            'size': os.path.getsize(filepath),
            'size_formatted': format_filesize(os.path.getsize(filepath)),
            'modified': os.path.getmtime(filepath),
            'modified_formatted': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M:%S"),
            'type': 'unknown'
        }
        
        # 根据文件类型添加特定信息
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            info['type'] = 'image'
            info['preview_url'] = f"/api/download?path={filepath}"
        
        elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
            info['type'] = 'video'
            info['preview_url'] = f"/api/download?path={filepath}"
            thumbnail = generate_video_thumbnail(filepath)
            if thumbnail:
                info['thumbnail'] = f"/api/thumbnail?path={thumbnail}"
        
        elif ext in ['.mp3', '.wav', '.ogg']:
            info['type'] = 'audio'
            info['preview_url'] = f"/api/download?path={filepath}"
        
        return jsonify(info)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500