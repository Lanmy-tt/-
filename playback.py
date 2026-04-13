"""
回放器 - 播放录制的鼠标键盘操作
"""
import json
import time
import threading
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key


class ActionPlayer:
    """动作回放器类"""
    
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.is_playing = False
        self.playback_thread = None
        self.current_action_index = 0
        self.total_actions = 0
        self.playback_speed = 1.0
        self.loop_count = 1
        self.current_loop = 0
    
    def _parse_key(self, key_str):
        """
        解析按键字符串（支持组合键）
        
        Args:
            key_str: 按键字符串，如 "ctrl+c", "shift+a", "a"
            
        Returns:
            tuple: (modifier_keys, key) 组合键返回 ( [Key.ctrl], 'c' )，单键返回 ( [], key )
        """
        key_map = {
            'Key.space': Key.space,
            'Key.enter': Key.enter,
            'Key.shift': Key.shift,
            'Key.shift_l': Key.shift_l,
            'Key.shift_r': Key.shift_r,
            'Key.ctrl': Key.ctrl,
            'Key.ctrl_l': Key.ctrl_l,
            'Key.ctrl_r': Key.ctrl_r,
            'Key.alt': Key.alt,
            'Key.alt_l': Key.alt_l,
            'Key.alt_r': Key.alt_r,
            'Key.tab': Key.tab,
            'Key.esc': Key.esc,
            'Key.backspace': Key.backspace,
            'Key.delete': Key.delete,
            'Key.insert': Key.insert,
            'Key.home': Key.home,
            'Key.end': Key.end,
            'Key.page_up': Key.page_up,
            'Key.page_down': Key.page_down,
            'Key.up': Key.up,
            'Key.down': Key.down,
            'Key.left': Key.left,
            'Key.right': Key.right,
            'Key.caps_lock': Key.caps_lock,
            'Key.num_lock': Key.num_lock,
            'Key.scroll_lock': Key.scroll_lock,
        }
        
        # 检查是否是组合键（包含 + 号）
        if '+' in key_str and not key_str.startswith('Key.'):
            parts = key_str.split('+')
            modifier_keys = []
            main_key = None
            
            for part in parts:
                part = part.strip()
                if part in ['ctrl', 'shift', 'alt']:
                    # 添加对应的修饰键
                    modifier_key = key_map.get(f'Key.{part}', getattr(Key, part))
                    modifier_keys.append(modifier_key)
                else:
                    # 主键
                    if part in key_map:
                        main_key = key_map[part]
                    elif len(part) == 1:
                        main_key = part
                    else:
                        # 尝试解析为功能键
                        clean_part = part.replace("'", "").replace("Key.", "")
                        if clean_part.startswith('f') and clean_part[1:].isdigit():
                            f_num = int(clean_part[1:])
                            if 1 <= f_num <= 12:
                                main_key = getattr(Key, f'f{f_num}')
            
            return (modifier_keys, main_key)
        
        # 普通按键（非组合键）
        if key_str in key_map:
            return ([], key_map[key_str])
        
        # 去掉引号和 Key. 前缀
        clean_key = key_str.replace("'", "").replace("Key.", "")
        
        # 功能键
        if clean_key.startswith('f') and clean_key[1:].isdigit():
            f_num = int(clean_key[1:])
            if 1 <= f_num <= 12:
                return ([], getattr(Key, f'f{f_num}'))
        
        # 普通字符
        return ([], clean_key[0] if len(clean_key) > 0 else None)
    
    def _parse_button(self, button_str):
        """
        解析鼠标按钮字符串
        
        Args:
            button_str: 按钮字符串
            
        Returns:
            pynput Button 对象
        """
        button_map = {
            'Button.left': Button.left,
            'Button.right': Button.right,
            'Button.middle': Button.middle,
        }
        return button_map.get(button_str, Button.left)
    
    def play_actions(self, actions, speed=1.0, loop_count=1):
        """
        播放录制的动作
        
        Args:
            actions: 动作列表
            speed: 回放速度 (1.0 为正常速度)
            loop_count: 循环次数
            
        Returns:
            bool: 是否成功开始播放
        """
        if self.is_playing or not actions:
            return False
        
        self.is_playing = True
        self.playback_speed = speed
        self.loop_count = loop_count
        self.current_loop = 0
        self.total_actions = len(actions)
        
        def playback_loop():
            """回放循环线程"""
            while self.is_playing and self.current_loop < self.loop_count:
                self.current_action_index = 0
                prev_time = 0
                loop_start_time = time.time()  # 记录每轮循环的开始时间
                
                for i, action in enumerate(actions):
                    try:
                        if not self.is_playing:
                            break
                        
                        # 计算延迟（基于录制时的相对时间）
                        current_time = action.get('time', 0)
                        delay = (current_time - prev_time) / speed
                        if delay > 0:
                            time.sleep(delay)
                        prev_time = current_time
                        
                        # 执行动作
                        action_type = action.get('type')
                        
                        if action_type == 'mouse_move':
                            x = action.get('x', 0)
                            y = action.get('y', 0)
                            self.mouse.position = (x, y)
                        
                        elif action_type == 'mouse_click':
                            x = action.get('x', 0)
                            y = action.get('y', 0)
                            button = self._parse_button(action.get('button', 'Button.left'))
                            pressed = action.get('pressed', True)
                            
                            self.mouse.position = (x, y)
                            if pressed:
                                self.mouse.press(button)
                            else:
                                self.mouse.release(button)
                        
                        elif action_type == 'mouse_scroll':
                            x = action.get('x', 0)
                            y = action.get('y', 0)
                            dx = action.get('dx', 0)
                            dy = action.get('dy', 0)
                            
                            self.mouse.position = (x, y)
                            self.mouse.scroll(dx, dy)
                        
                        elif action_type == 'key_press':
                            parsed = self._parse_key(action.get('key', ''))
                            modifier_keys, main_key = parsed
                            
                            # 先按下修饰键
                            for mod_key in modifier_keys:
                                self.keyboard.press(mod_key)
                            
                            # 再按下主键
                            if main_key:
                                self.keyboard.press(main_key)
                        
                        elif action_type == 'key_release':
                            parsed = self._parse_key(action.get('key', ''))
                            modifier_keys, main_key = parsed
                            
                            # 先释放主键
                            if main_key:
                                self.keyboard.release(main_key)
                            
                            # 再释放修饰键
                            for mod_key in modifier_keys:
                                self.keyboard.release(mod_key)
                        
                        self.current_action_index = i + 1
                        
                    except Exception as e:
                        print(f"播放动作 {i+1} 时出错:")
                        print(f"  动作类型: {action.get('type')}")
                        print(f"  错误信息: {str(e)}")
                        print(f"  动作详情: {action}")
                        import traceback
                        print(f"  堆栈跟踪: {traceback.format_exc()}")
                        self.is_playing = False
                        break
                
                self.current_loop += 1
                
                # 如果还有下一轮循环，重置时间
                if self.is_playing and self.current_loop < self.loop_count:
                    prev_time = 0
                    time.sleep(0.1)  # 循环间短暂延迟
            
            self.is_playing = False
            self.playback_thread = None
        
        self.playback_thread = threading.Thread(target=playback_loop, daemon=True)
        self.playback_thread.start()
        return True
    
    def stop_playback(self):
        """停止回放"""
        self.is_playing = False
        if self.playback_thread:
            self.playback_thread.join(timeout=1.0)
            self.playback_thread = None
    
    def is_active(self):
        """检查是否正在回放"""
        return self.is_playing
    
    def get_progress(self):
        """获取回放进度"""
        if not self.total_actions:
            return 0
        return (self.current_action_index / self.total_actions) * 100
    
    def load_from_file(self, filename):
        """
        从文件加载动作
        
        Args:
            filename: 文件名
            
        Returns:
            list: 动作列表，失败返回 None
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('actions', [])
        except Exception as e:
            print(f"加载失败：{e}")
            return None
