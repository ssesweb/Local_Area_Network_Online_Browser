import os
import cv2
from pathlib import Path
import re

def generate_video_thumbnail(video_path, output_dir, thumbnail_name=None):
    """
    生成视频缩略图并保存到指定目录
    :param video_path: 视频文件路径
    :param output_dir: 缩略图输出目录
    :param thumbnail_name: 缩略图文件名(可选)
    :return: 缩略图路径或None(失败时)
    """
    try:
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 读取视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
            
        # 获取视频总帧数和中间帧
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        middle_frame = total_frames // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
        
        # 读取中间帧
        ret, frame = cap.read()
        if not ret:
            return None
            
        # 清理非法字符生成文件名
        safe_name = re.sub(r'[\\/*?:"<>|]', "", os.path.basename(video_path))
        output_path = os.path.join(output_dir, f"thumb_{safe_name}.jpg")
        
        # 保存缩略图
        cv2.imwrite(output_path, frame)
        return output_path
        
    except Exception as e:
        print(f"生成缩略图失败: {e}")
        return None
    finally:
        if 'cap' in locals():
            cap.release()

# 使用示例
if __name__ == "__main__":
    video_path = r"E:\\迅雷\\摄影集锦\\香草少女\\九尾狐狸m-170107Kitty套装\\九尾狐狸m-170107Kitty套装.mp4"
    output_dir = r"D:\Download\Local_Area_Network_Online_Browser-main (1)\Local_Area_Network_Online_Browser\app\static\thumbnails"
    
    result = generate_video_thumbnail(video_path, output_dir)
    if result:
        print(f"缩略图已生成: {result}")
    else:
        print("缩略图生成失败")