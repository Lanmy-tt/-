"""
配置文件 - 存储应用程序的默认配置
"""

# 默认设置
DEFAULT_SETTINGS = {
    # 鼠标连点设置
    'mouse_click': {
        'button': 'left',  # left, right, middle
        'interval': 100,   # 毫秒
        'count': 0,        # 0 表示无限循环
    },
    
    # 键盘连点设置
    'keyboard_click': {
        'key': 'a',
        'interval': 100,
        'count': 0,
    },
    
    # 录制设置
    'recording': {
        'mouse_move_record': True,
        'mouse_click_record': True,
        'keyboard_record': True,
    },
    
    # 回放设置
    'playback': {
        'speed': 1.0,      # 回放速度倍数
        'loop_count': 1,   # 回放循环次数
    }
}

# 快捷键设置
HOTKEYS = {
    'start_stop_click': 'F6',
    'start_recording': 'F9',
    'stop_recording': 'F10',
    'start_playback': 'F11',
    'stop_playback': 'F12',
}

# 支持的键盘按键
SUPPORTED_KEYS = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
    'space', 'enter', 'shift', 'ctrl', 'alt', 'tab', 'esc', 'backspace',
    'delete', 'insert', 'home', 'end', 'page_up', 'page_down',
    'up', 'down', 'left', 'right',
    'caps_lock', 'num_lock', 'scroll_lock',
    'numpad_0', 'numpad_1', 'numpad_2', 'numpad_3', 'numpad_4',
    'numpad_5', 'numpad_6', 'numpad_7', 'numpad_8', 'numpad_9',
    'numpad_add', 'numpad_subtract', 'numpad_multiply', 'numpad_divide',
]

# 组合键支持
COMBO_KEYS = ['ctrl', 'alt', 'shift', 'win']
