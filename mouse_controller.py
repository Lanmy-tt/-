"""
鼠标控制器 - 处理鼠标连点和相关操作
"""
import threading
import time
from pynput.mouse import Controller, Button


class MouseController:
    """鼠标控制器类"""
    
    def __init__(self):
        self.mouse = Controller()
        self.is_clicking = False
        self.click_thread = None
        self.click_count = 0
        self.total_clicks = 0
    
    def start_clicking(self, button='left', interval=100, count=0):
        """
        开始鼠标连点
        
        Args:
            button: 鼠标按钮 ('left', 'right', 'middle')
            interval: 点击间隔 (毫秒)
            count: 点击次数 (0 表示无限循环)
        """
        if self.is_clicking:
            return False
        
        self.is_clicking = True
        self.click_count = 0
        self.total_clicks = count if count > 0 else float('inf')
        
        # 映射按钮名称
        button_map = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }
        click_button = button_map.get(button, Button.left)
        interval_seconds = interval / 1000.0
        
        def click_loop():
            """点击循环线程"""
            while self.is_clicking and self.click_count < self.total_clicks:
                self.mouse.click(click_button)
                self.click_count += 1
                time.sleep(interval_seconds)
            
            self.is_clicking = False
            self.click_thread = None
        
        self.click_thread = threading.Thread(target=click_loop, daemon=True)
        self.click_thread.start()
        return True
    
    def stop_clicking(self):
        """停止鼠标连点"""
        self.is_clicking = False
        if self.click_thread:
            self.click_thread.join(timeout=1.0)
            self.click_thread = None
    
    def is_active(self):
        """检查是否正在连点"""
        return self.is_clicking
    
    def get_click_count(self):
        """获取当前点击次数"""
        return self.click_count
    
    def get_position(self):
        """获取鼠标位置"""
        return self.mouse.position
    
    def set_position(self, x, y):
        """设置鼠标位置"""
        self.mouse.position = (x, y)
    
    def move(self, dx, dy):
        """移动鼠标"""
        self.mouse.move(dx, dy)
