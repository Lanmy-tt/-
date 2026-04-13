"""
键盘控制器 - 处理键盘连点和组合键
"""
import threading
import time
from pynput.keyboard import Controller, Key


class KeyboardController:
    """键盘控制器类"""
    
    def __init__(self):
        self.keyboard = Controller()
        self.is_clicking = False
        self.click_thread = None
        self.click_count = 0
        self.total_clicks = 0
    
    def _parse_key(self, key_str):
        """
        解析按键字符串为 pynput 按键对象
        
        Args:
            key_str: 按键字符串
            
        Returns:
            pynput 按键对象或字符
        """
        key_map = {
            'space': Key.space,
            'enter': Key.enter,
            'shift': Key.shift,
            'ctrl': Key.ctrl,
            'alt': Key.alt,
            'tab': Key.tab,
            'esc': Key.esc,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'insert': Key.insert,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'caps_lock': Key.caps_lock,
            'num_lock': Key.num_lock,
            'scroll_lock': Key.scroll_lock,
        }
        
        # 特殊按键映射
        if key_str.lower() in key_map:
            return key_map[key_str.lower()]
        
        # 功能键 F1-F12
        if key_str.lower().startswith('f') and key_str[1:].isdigit():
            f_num = int(key_str[1:])
            if 1 <= f_num <= 12:
                return getattr(Key, f'f{f_num}')
        
        # 数字键盘
        if key_str.lower().startswith('numpad_'):
            numpad_map = {
                'numpad_0': Key.k0,
                'numpad_1': Key.k1,
                'numpad_2': Key.k2,
                'numpad_3': Key.k3,
                'numpad_4': Key.k4,
                'numpad_5': Key.k5,
                'numpad_6': Key.k6,
                'numpad_7': Key.k7,
                'numpad_8': Key.k8,
                'numpad_9': Key.k9,
                'numpad_add': Key.add,
                'numpad_subtract': Key.subtract,
                'numpad_multiply': Key.multiply,
                'numpad_divide': Key.divide,
            }
            if key_str.lower() in numpad_map:
                return numpad_map[key_str.lower()]
        
        # 普通字符
        return key_str[0] if len(key_str) > 0 else key_str
    
    def start_clicking(self, key='a', interval=100, count=0, modifiers=None):
        """
        开始键盘连点
        
        Args:
            key: 按键
            interval: 点击间隔 (毫秒)
            count: 点击次数 (0 表示无限循环)
            modifiers: 修饰键列表 (如 ['ctrl', 'shift'])
        """
        if self.is_clicking:
            return False
        
        self.is_clicking = True
        self.click_count = 0
        self.total_clicks = count if count > 0 else float('inf')
        interval_seconds = interval / 1000.0
        
        parsed_key = self._parse_key(key)
        modifier_keys = [self._parse_key(m) for m in (modifiers or [])]
        
        def click_loop():
            """点击循环线程"""
            while self.is_clicking and self.click_count < self.total_clicks:
                # 按下修饰键
                for mod in modifier_keys:
                    self.keyboard.press(mod)
                
                # 按下并释放目标键
                self.keyboard.press(parsed_key)
                self.keyboard.release(parsed_key)
                
                # 释放修饰键
                for mod in modifier_keys:
                    self.keyboard.release(mod)
                
                self.click_count += 1
                time.sleep(interval_seconds)
            
            self.is_clicking = False
            self.click_thread = None
        
        self.click_thread = threading.Thread(target=click_loop, daemon=True)
        self.click_thread.start()
        return True
    
    def stop_clicking(self):
        """停止键盘连点"""
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
    
    def press_key(self, key):
        """按下一个键"""
        parsed_key = self._parse_key(key)
        self.keyboard.press(parsed_key)
    
    def release_key(self, key):
        """释放一个键"""
        parsed_key = self._parse_key(key)
        self.keyboard.release(parsed_key)
    
    def type_string(self, text, delay=0.1):
        """
        输入字符串
        
        Args:
            text: 要输入的文本
            delay: 每个字符之间的延迟 (秒)
        """
        for char in text:
            self.keyboard.press(char)
            self.keyboard.release(char)
            time.sleep(delay)
