#!/usr/bin/env python3
"""
通用游戏数据收集脚本模板 / Universal Game Data Collection Script Template

使用方法 / Usage:
1. 修改游戏特定的配置参数
2. 运行脚本并进入游戏
3. 使用快捷键收集数据
"""

import time
import mss
import cv2
import win32api
import os
import numpy as np
import re
from pynput import mouse, keyboard
from threading import Thread
from multiprocessing import Manager
from PIL import ImageGrab

# ==================== 游戏配置 / Game Configuration ====================

# 游戏名称 - 修改为你的游戏
GAME_NAME = "YourGame"

# 截图区域配置 (可根据游戏调整)
SCREENSHOT_WIDTH = 640   # 截图宽度
SCREENSHOT_HEIGHT = 640  # 截图高度

# 类别配置 - 根据你的游戏修改
CATEGORIES = {
    0: "TEAM_A",     # 第一个类别，如：敌方、T方、攻击方等
    1: "TEAM_B",     # 第二个类别，如：友方、CT方、防守方等
    # 2: "TEAM_C",   # 可添加更多类别
}

# 按键配置
SCREENSHOT_KEY = "'f'"    # 截图按键
SWITCH_KEY = "'`'"        # 切换类别按键
EXIT_KEY = "'esc'"        # 退出按键（可选）

# 数据保存路径
DATA_DIR = f"./data/{GAME_NAME.lower()}"

# ==================== 工具函数 / Utility Functions ====================

def sanitize_filename(filename):
    """清理文件名，防止路径遍历攻击"""
    filename = re.sub(r'[<>:"/\\|?*]', '', str(filename))
    filename = filename[:50] if len(filename) > 50 else filename
    return filename

def create_directories():
    """创建数据目录"""
    for category_id, category_name in CATEGORIES.items():
        dir_path = os.path.join(DATA_DIR, category_name)
        os.makedirs(dir_path, exist_ok=True)
        print(f"创建目录: {dir_path}")

def get_screenshot_region():
    """计算截图区域"""
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    
    # 以屏幕中心为基准
    left = int((screen_width / 2) - (SCREENSHOT_WIDTH / 2))
    top = int((screen_height / 2) - (SCREENSHOT_HEIGHT / 2))
    
    return {
        'left': left, 
        'top': top, 
        'width': SCREENSHOT_WIDTH, 
        'height': SCREENSHOT_HEIGHT
    }

# ==================== 主要类 / Main Classes ====================

class GameDataCollector:
    def __init__(self, share_dict):
        self.share_dict = share_dict
        self.share_dict['collecting'] = False
        self.share_dict['current_category'] = 0
        self.share_dict['running'] = True
        
        # 统计信息
        self.share_dict['stats'] = {cat_id: 0 for cat_id in CATEGORIES.keys()}
        
        print(f"=== {GAME_NAME} 数据收集器已启动 ===")
        print("按键说明:")
        print(f"  {SCREENSHOT_KEY[1:-1].upper()} - 截图")
        print(f"  {SWITCH_KEY[1:-1]} - 切换类别")
        print(f"  ESC - 退出")
        print()
        
        current_cat = CATEGORIES[self.share_dict['current_category']]
        print(f"当前收集类别: {current_cat}")

    def on_press(self, key):
        key_str = str(key)
        
        # 截图
        if key_str == SCREENSHOT_KEY:
            self.share_dict['collecting'] = True
            current_cat = CATEGORIES[self.share_dict['current_category']]
            print(f"📸 截图中... (类别: {current_cat})")

        # 切换类别
        elif key_str == SWITCH_KEY:
            category_ids = list(CATEGORIES.keys())
            current_idx = category_ids.index(self.share_dict['current_category'])
            next_idx = (current_idx + 1) % len(category_ids)
            self.share_dict['current_category'] = category_ids[next_idx]
            
            current_cat = CATEGORIES[self.share_dict['current_category']]
            print(f"🔄 切换到类别: {current_cat}")

        # 退出
        elif key_str == EXIT_KEY:
            print("正在退出...")
            self.share_dict['running'] = False

    def on_release(self, key):
        key_str = str(key)
        if key_str == SCREENSHOT_KEY:
            self.share_dict['collecting'] = False

    def listen(self):
        with keyboard.Listener(
            on_press=self.on_press, 
            on_release=self.on_release
        ) as listener:
            listener.join()

    def start_listening(self):
        t = Thread(target=self.listen)
        t.daemon = True
        t.start()

def screenshot_worker(share_dict):
    """截图工作进程"""
    create_directories()
    
    # 创建截图对象
    sct = mss.mss()
    monitor = get_screenshot_region()
    
    print(f"截图区域: {monitor}")
    
    while share_dict['running']:
        if share_dict['collecting']:
            try:
                # 截图
                img = sct.grab(monitor)
                img = np.array(img)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # 转换颜色格式
                
                # 获取当前类别
                current_category = share_dict['current_category']
                category_name = CATEGORIES[current_category]
                
                # 生成安全的文件名
                timestamp = sanitize_filename(str(time.time()))
                filename = f"{timestamp}.jpg"
                
                # 保存图片
                output_dir = os.path.join(DATA_DIR, category_name)
                output_path = os.path.join(output_dir, filename)
                
                success = cv2.imwrite(output_path, img)
                
                if success:
                    share_dict['stats'][current_category] += 1
                    total = sum(share_dict['stats'].values())
                    print(f"✅ 已保存: {filename} (类别: {category_name}, 总计: {total})")
                else:
                    print(f"❌ 保存失败: {filename}")
                
                # 重置采集状态
                share_dict['collecting'] = False
                
            except Exception as e:
                print(f"截图错误: {e}")
                share_dict['collecting'] = False
        
        # 短暂休眠避免CPU占用过高
        time.sleep(0.01)
    
    # 显示最终统计
    print("\n=== 收集统计 ===")
    total = 0
    for cat_id, count in share_dict['stats'].items():
        cat_name = CATEGORIES[cat_id]
        print(f"{cat_name}: {count} 张图片")
        total += count
    print(f"总计: {total} 张图片")

# ==================== 主函数 / Main Function ====================

def main():
    """主函数"""
    print(f"=== {GAME_NAME} 数据收集脚本 ===")
    print("准备启动数据收集器...")
    
    # 创建共享字典
    manager = Manager()
    share_dict = manager.dict()
    
    # 创建数据收集器
    collector = GameDataCollector(share_dict)
    
    # 启动键盘监听
    collector.start_listening()
    
    print("数据收集器已启动，请切换到游戏窗口...")
    print("按任意键开始收集数据...")
    input()
    
    # 启动截图工作进程
    screenshot_worker(share_dict)

if __name__ == '__main__':
    main()