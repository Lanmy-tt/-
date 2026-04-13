"""
录制器 - 录制鼠标和键盘操作
"""
import json
import time
import threading
from datetime import datetime
from pynput.mouse import Listener as MouseListener, Button
from pynput.keyboard import Listener as KeyboardListener, Key


class ActionRecorder:
    """动作录制器类 - 支持撤销/重做"""
    
    def __init__(self):
        self.is_recording = False
        self.actions = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.record_thread = None
        
        # 撤销/重做功能
        self.undo_stack = []  # 撤销栈
        self.redo_stack = []  # 重做栈
        self.max_undo_steps = 100  # 最大撤销步数
    
    def start_recording(self, record_mouse_move=True, record_mouse_click=True, record_keyboard=True):
        """
        开始录制
        
        Args:
            record_mouse_move: 是否录制鼠标移动
            record_mouse_click: 是否录制鼠标点击
            record_keyboard: 是否录制键盘操作
            
        Returns:
            bool: 是否成功开始录制
        """
        if self.is_recording:
            return False
        
        self.is_recording = True
        self.actions = []
        self.undo_stack = []  # 清空撤销栈
        self.redo_stack = []  # 清空重做栈
        self.start_time = time.time()
        
        def on_mouse_move(x, y):
            if self.is_recording and record_mouse_move:
                elapsed = time.time() - self.start_time
                self.actions.append({
                    'type': 'mouse_move',
                    'x': x,
                    'y': y,
                    'time': elapsed
                })
        
        def on_mouse_click(x, y, button, pressed):
            if self.is_recording and record_mouse_click:
                elapsed = time.time() - self.start_time
                self.actions.append({
                    'type': 'mouse_click',
                    'x': x,
                    'y': y,
                    'button': str(button),
                    'pressed': pressed,
                    'time': elapsed
                })
        
        def on_mouse_scroll(x, y, dx, dy):
            if self.is_recording and record_mouse_click:
                elapsed = time.time() - self.start_time
                self.actions.append({
                    'type': 'mouse_scroll',
                    'x': x,
                    'y': y,
                    'dx': dx,
                    'dy': dy,
                    'time': elapsed
                })
        
        # 跟踪当前按下的修饰键
        self.modifier_keys = set()
        
        def _get_key_name(key, modifiers=None):
            """获取按键的标准名称"""
            # 优先使用 VK 码判断（更可靠）
            if hasattr(key, 'vk') and key.vk:
                if 65 <= key.vk <= 90:  # A-Z
                    return chr(key.vk + 32)  # 转为小写
                elif 97 <= key.vk <= 122:  # a-z
                    return chr(key.vk)
                elif 48 <= key.vk <= 57:  # 0-9
                    return chr(key.vk)
            
            # 检查 char 属性
            if hasattr(key, 'char') and key.char:
                char_val = key.char
                # 如果是控制字符（Ctrl+ 字母时会出现），根据修饰键推断
                if modifiers and 'ctrl' in modifiers:
                    # Ctrl+A-Z 会产生控制字符 \x01-\x1a
                    if isinstance(char_val, str) and len(char_val) == 1:
                        ascii_val = ord(char_val)
                        if 1 <= ascii_val <= 26:  # Ctrl+A 到 Ctrl+Z
                            return chr(ord('a') + ascii_val - 1)
                # 普通字符直接返回
                if isinstance(char_val, str) and len(char_val) == 1 and char_val.isprintable():
                    return char_val.lower() if len(char_val) == 1 else char_val
            
            # 特殊按键
            key_str = str(key).replace("'", "")
            return key_str
        
        def _get_modifier_prefix(key):
            """获取修饰键前缀"""
            if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r]:
                return 'ctrl'
            elif key in [Key.shift, Key.shift_l, Key.shift_r]:
                return 'shift'
            elif key in [Key.alt, Key.alt_l, Key.alt_r]:
                return 'alt'
            return None
        
        def on_keyboard_press(key):
            if self.is_recording and record_keyboard:
                elapsed = time.time() - self.start_time
                try:
                    # 检查是否是修饰键
                    modifier_prefix = _get_modifier_prefix(key)
                    
                    if modifier_prefix:
                        # 修饰键按下
                        key_str = str(key).replace("'", "")
                        self.modifier_keys.add(modifier_prefix)
                        print(f"录制到修饰键按下：{key_str}, 当前修饰键：{self.modifier_keys} at {elapsed:.2f}s")
                        
                        # 只记录修饰键按下，不记录组合键
                        self.actions.append({
                            'type': 'key_press',
                            'key': key_str,
                            'time': elapsed
                        })
                    else:
                        # 普通键按下
                        key_name = _get_key_name(key, self.modifier_keys.copy() if self.modifier_keys else None)
                        
                        # 如果有修饰键，记录为组合键
                        if self.modifier_keys:
                            # 生成组合键名称，如 "ctrl+c"
                            combo_key = '+'.join(sorted(self.modifier_keys)) + '+' + key_name
                            print(f"录制到组合键：{combo_key} (基础键：{key_name}, VK: {getattr(key, 'vk', None)}, char: {getattr(key, 'char', None)}) at {elapsed:.2f}s")
                            
                            self.actions.append({
                                'type': 'key_press',
                                'key': combo_key,
                                'time': elapsed,
                                'is_combo': True
                            })
                        else:
                            # 没有修饰键，记录普通键
                            print(f"录制到按键按下：{key_name} at {elapsed:.2f}s")
                            self.actions.append({
                                'type': 'key_press',
                                'key': key_name,
                                'time': elapsed
                            })
                except Exception as e:
                    key_str = str(key)
                    print(f"录制按键按下出错：{e}, key: {key_str}")
                    self.actions.append({
                        'type': 'key_press',
                        'key': key_str,
                        'time': elapsed
                    })
        
        def on_keyboard_release(key):
            if self.is_recording and record_keyboard:
                elapsed = time.time() - self.start_time
                try:
                    modifier_prefix = _get_modifier_prefix(key)
                    
                    if modifier_prefix:
                        # 修饰键释放
                        key_str = str(key).replace("'", "")
                        self.modifier_keys.discard(modifier_prefix)
                        print(f"录制到修饰键释放：{key_str}, 剩余修饰键：{self.modifier_keys} at {elapsed:.2f}s")
                        
                        self.actions.append({
                            'type': 'key_release',
                            'key': key_str,
                            'time': elapsed
                        })
                    else:
                        # 普通键释放
                        key_name = _get_key_name(key, self.modifier_keys.copy() if self.modifier_keys else None)
                        print(f"录制到按键释放：{key_name} at {elapsed:.2f}s")
                        
                        self.actions.append({
                            'type': 'key_release',
                            'key': key_name,
                            'time': elapsed
                        })
                except Exception as e:
                    key_str = str(key)
                    print(f"录制按键释放出错：{e}, key: {key_str}")
                    self.actions.append({
                        'type': 'key_release',
                        'key': key_str,
                        'time': elapsed
                    })
        
        # 启动监听器
        self.mouse_listener = MouseListener(
            on_move=on_mouse_move,
            on_click=on_mouse_click,
            on_scroll=on_mouse_scroll
        )
        
        self.keyboard_listener = KeyboardListener(
            on_press=on_keyboard_press,
            on_release=on_keyboard_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        # 等待监听器启动
        time.sleep(0.3)
        
        print(f"录制器状态：is_recording={self.is_recording}")
        print(f"键盘监听器状态：running={self.keyboard_listener.running if self.keyboard_listener else 'None'}")
        print(f"鼠标监听器状态：running={self.mouse_listener.running if self.mouse_listener else 'None'}")
        
        return True
    
    def stop_recording(self):
        """停止录制"""
        self.is_recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        return self.actions
    
    def is_recording_active(self):
        """检查是否正在录制"""
        return self.is_recording
    
    def get_actions(self):
        """获取录制的动作"""
        return self.actions
    
    def save_to_file(self, filename):
        """
        保存录制到文件
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否保存成功
        """
        if not self.actions:
            return False
        
        try:
            data = {
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'action_count': len(self.actions),
                    'duration': self.actions[-1]['time'] if self.actions else 0
                },
                'actions': self.actions
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存失败：{e}")
            return False
    
    def load_from_file(self, filename):
        """
        从文件加载录制
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否加载成功
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.actions = data.get('actions', [])
            return True
        except Exception as e:
            print(f"加载失败：{e}")
            return False
    
    def clear_actions(self):
        """清空动作列表"""
        self.actions = []
        self.undo_stack = []
        self.redo_stack = []
    
    def undo(self):
        """撤销最后一步操作"""
        if not self.actions:
            return False
        
        # 将最后一个动作移到撤销栈
        last_action = self.actions.pop()
        self.undo_stack.append(last_action)
        
        return True
    
    def undo_multiple(self, count):
        """撤销多步操作"""
        undone = 0
        for _ in range(min(count, len(self.actions))):
            if self.undo():
                undone += 1
        return undone
    
    def redo(self):
        """重做上一步撤销的操作"""
        if not self.undo_stack:
            return False
        
        # 从撤销栈恢复到动作列表
        action = self.undo_stack.pop()
        self.actions.append(action)
        
        # 清空重做栈（因为重做后不能再重做了）
        self.redo_stack.clear()
        
        return True
    
    def redo_multiple(self, count):
        """重做多步操作"""
        redone = 0
        for _ in range(min(count, len(self.redo_stack))):
            if self.redo():
                redone += 1
        return redone
    
    def get_undo_count(self):
        """获取可撤销的数量"""
        return len(self.undo_stack)
    
    def get_redo_count(self):
        """获取可重做的数量"""
        return len(self.redo_stack)
    
    def delete_last_n_actions(self, n):
        """删除最后 N 个动作（用于录制错误时重来）"""
        if n <= 0 or not self.actions:
            return 0
        
        deleted = 0
        for _ in range(min(n, len(self.actions))):
            action = self.actions.pop()
            self.undo_stack.append(action)  # 移到撤销栈，以便可以恢复
            deleted += 1
        
        return deleted
    
    def delete_action_at(self, index):
        """删除指定位置的动作"""
        if index < 0 or index >= len(self.actions):
            return False
        
        # 删除指定位置的动作
        action = self.actions.pop(index)
        self.undo_stack.append(action)  # 移到撤销栈
        return True
    
    def clear_all_actions(self):
        """清空所有动作"""
        if not self.actions:
            return 0
        
        deleted = len(self.actions)
        self.actions = []
        self.undo_stack = []
        self.redo_stack = []
        return deleted
