"""
主程序入口 - 鼠标键盘操控程序（现代简约风格）
"""
import sys
import os
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QSpinBox, QComboBox, QGroupBox, QFrame
from PyQt5.QtWidgets import QTabWidget, QTextEdit, QFileDialog, QMessageBox, QProgressBar
from PyQt5.QtWidgets import QStackedWidget, QMenu, QAction, QDialog, QCheckBox
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QKeySequence, QPixmap, QPainter, QColor, QPalette, QBrush, QIcon
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QTextCursor

from pynput import keyboard, mouse
from pynput.mouse import Button
from recorder import ActionRecorder
from playback import ActionPlayer
from script_editor import ScriptEditor
from shortcut_editor import ShortcutEditor

# 默认快捷键配置
DEFAULT_SHORTCUTS = {
    "停止所有操作": "F8",
    "开始/停止录制": "F9",
    "停止录制": "F10",
    "开始/停止回放": "F11",
    "停止回放": "F12",
    "保存录制文件": "Ctrl+S",
    "加载录制文件": "Ctrl+O",
    "打开脚本编辑器": "Ctrl+E",
    "撤销录制": "Ctrl+Z",
    "重做录制": "Ctrl+Y",
    "紧急停止": "Esc",
    "暂停/继续定点连点": "F1",
    "全局紧急停止": "F2"
}

# 功能名称到方法名的映射
FUNCTION_METHOD_MAP = {
    "停止所有操作": "stop_all_operations",
    "开始/停止录制": "toggle_recording",
    "停止录制": "stop_recording_only",
    "开始/停止回放": "toggle_playback",
    "停止回放": "stop_playback_only",
    "保存录制文件": "save_recording_file",
    "加载录制文件": "load_recording_file",
    "打开脚本编辑器": "open_script_editor",
    "撤销录制": "undo_recording",
    "重做录制": "redo_recording",
    "紧急停止": "emergency_stop",
    "暂停/继续定点连点": "toggle_pause_auto_click",
    "全局紧急停止": "global_emergency_stop"
}


class GlobalHotkey(QObject):
    """全局快捷键类 - 使用 pynput"""
    hotkeyTriggered = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hotkey_map = {}
        self.listener = None
        self.active_modifiers = set()
    
    def register_hotkey(self, key_combination, callback_name):
        """注册全局快捷键"""
        self.hotkey_map[key_combination.lower()] = callback_name
    
    def start(self):
        """开始监听全局快捷键"""
        if self.listener is None:
            # 在独立线程中运行监听器
            thread = threading.Thread(target=self._run_listener, daemon=True)
            thread.start()
    
    def stop(self):
        """停止监听"""
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def _run_listener(self):
        """运行键盘监听器"""
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        self.listener.join()
    
    def _on_press(self, key):
        """按键按下事件"""
        try:
            # 记录修饰键
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.active_modifiers.add('ctrl')
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.active_modifiers.add('alt')
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.active_modifiers.add('shift')
            
            # 获取按键字符串
            key_str = self._key_to_string(key)
            
            # 构建快捷键字符串
            parts = []
            if 'ctrl' in self.active_modifiers:
                parts.append('ctrl')
            if 'alt' in self.active_modifiers:
                parts.append('alt')
            if 'shift' in self.active_modifiers:
                parts.append('shift')
            if key_str:
                parts.append(key_str)
            
            hotkey_str = '+'.join(parts)
            
            # 检查是否匹配
            if hotkey_str in self.hotkey_map:
                self.hotkeyTriggered.emit(self.hotkey_map[hotkey_str])
            elif key_str and key_str in self.hotkey_map:
                # 没有修饰键的情况
                self.hotkeyTriggered.emit(self.hotkey_map[key_str])
        except Exception as e:
            pass
    
    def _on_release(self, key):
        """按键释放事件"""
        try:
            # 移除修饰键
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.active_modifiers.discard('ctrl')
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.active_modifiers.discard('alt')
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.active_modifiers.discard('shift')
        except Exception as e:
            pass
    
    def _key_to_string(self, key):
        """将按键转换为字符串"""
        try:
            # 功能键
            if isinstance(key, keyboard.Key):
                key_map = {
                    keyboard.Key.f1: 'f1', keyboard.Key.f2: 'f2',
                    keyboard.Key.f3: 'f3', keyboard.Key.f4: 'f4',
                    keyboard.Key.f5: 'f5', keyboard.Key.f6: 'f6',
                    keyboard.Key.f7: 'f7', keyboard.Key.f8: 'f8',
                    keyboard.Key.f9: 'f9', keyboard.Key.f10: 'f10',
                    keyboard.Key.f11: 'f11', keyboard.Key.f12: 'f12',
                    keyboard.Key.enter: 'enter', keyboard.Key.space: 'space',
                    keyboard.Key.tab: 'tab', keyboard.Key.esc: 'esc',
                    keyboard.Key.backspace: 'backspace'
                }
                return key_map.get(key, '')
            else:
                # 字符键
                return str(key).replace("'", "").lower()
        except:
            return ''


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化控制器
        self.recorder = ActionRecorder()
        self.player = ActionPlayer()
        self.script_editor = None
        
        # 脚本文件管理
        self.script_files = []  # 已保存的脚本文件列表
        self.current_script_path = None  # 当前选中的脚本路径
        
        # 初始化全局快捷键
        self.global_hotkey = GlobalHotkey(self)
        self.global_hotkey.hotkeyTriggered.connect(self.handle_global_hotkey)
        
        # 初始化 UI
        self.init_ui()
        
        # 设置快捷键
        self.setup_shortcuts()
        
        # 设置定时器更新状态
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(500)
    
    def init_ui(self):
        """初始化用户界面 - 现代简约风格"""
        self.setWindowTitle('鼠大师')
        self.setGeometry(100, 100, 1100, 750)
        
        # 设置背景图片
        self.set_background_image()
        
        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部标题栏
        self.create_header(main_layout)
        
        # 内容区域
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        content_layout.addWidget(self.tabs)
        
        # 创建各个选项卡
        self.create_auto_click_tab()
        self.create_recorder_tab()
        self.create_playback_tab()
        
        # 添加选项卡
        self.tabs.addTab(self.auto_click_tab, "🎯 定点连点")
        self.tabs.addTab(self.recorder_tab, "📹 录制操作")
        self.tabs.addTab(self.playback_tab, "▶️ 回放操作")
        
        main_layout.addWidget(content_frame)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 状态栏
        self.statusBar().setObjectName("statusBar")
        self.statusBar().showMessage('准备就绪')
        
        # 初始化脚本列表
        self.refresh_script_list()
    
    def set_background_image(self):
        """设置动漫头像为背景"""
        image_path = os.path.join(os.path.dirname(__file__), '动漫头像.png')
        
        if os.path.exists(image_path):
            self.background_image_path = image_path
            self.update_background()
    
    def update_background(self):
        """更新背景图片（自适应窗口大小）"""
        if hasattr(self, 'background_image_path') and os.path.exists(self.background_image_path):
            # 加载并缩放图片
            pixmap = QPixmap(self.background_image_path)
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 创建半透明遮罩
            overlay = QPixmap(scaled_pixmap.size())
            overlay.fill(Qt.transparent)
            
            painter = QPainter(overlay)
            painter.setBrush(QColor(255, 255, 255, 180))
            painter.setPen(Qt.NoPen)
            painter.drawRect(overlay.rect())
            painter.end()
            
            # 合成图片
            painter = QPainter(scaled_pixmap)
            painter.drawPixmap(0, 0, overlay)
            painter.end()
            
            # 设置为背景
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
    
    def resizeEvent(self, event):
        """窗口大小变化时更新背景"""
        super().resizeEvent(event)
        self.update_background()
    
    def create_header(self, layout):
        """创建顶部标题栏"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(70)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 10, 25, 10)
        
        # 标题
        title_label = QLabel("鼠大师")
        title_label.setObjectName("mainTitle")
        header_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("鼠标键盘操控程序")
        subtitle_label.setObjectName("subTitle")
        header_layout.addWidget(subtitle_label)
        
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
    
    def create_auto_click_tab(self):
        """创建定点连点选项卡 - 坐标点自动点击 + 脚本回放"""
        self.auto_click_tab = QWidget()
        self.auto_click_tab.setObjectName("tabContent")
        
        layout = QVBoxLayout(self.auto_click_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 坐标点设置卡片
        points_card, points_layout = self.create_card("坐标点设置")
        
        # 坐标输入
        coord_layout = QHBoxLayout()
        coord_layout.setSpacing(10)
        
        coord_layout.addWidget(self.create_label("X:"))
        self.coord_x_spin = self.create_spinbox(0, 9999, 0)
        coord_layout.addWidget(self.coord_x_spin)
        
        coord_layout.addWidget(self.create_label("Y:"))
        self.coord_y_spin = self.create_spinbox(0, 9999, 0)
        coord_layout.addWidget(self.coord_y_spin)
        
        coord_layout.addWidget(self.create_label("点击类型:"))
        self.click_type_combo = self.create_combo([
            "单击左键", "单击右键", "单击中键",
            "双击左键", "双击右键", "双击中键",
            "向上滚动", "向下滚动"
        ])
        coord_layout.addWidget(self.click_type_combo)
        
        coord_layout.addStretch()
        points_layout.addLayout(coord_layout)
        
        # 添加按钮
        add_btn_layout = QHBoxLayout()
        add_btn_layout.setSpacing(10)
        
        self.add_point_btn = self.create_primary_button("开始添加 (Ctrl+ 左键)")
        self.add_point_btn.clicked.connect(self.toggle_add_mode)
        add_btn_layout.addWidget(self.add_point_btn)
        
        self.stop_add_btn = self.create_danger_button("停止添加 (ESC)")
        self.stop_add_btn.clicked.connect(self.stop_add_mode)
        self.stop_add_btn.setEnabled(False)
        add_btn_layout.addWidget(self.stop_add_btn)
        
        points_layout.addLayout(add_btn_layout)
        
        # 提示标签
        tip_label = QLabel("💡 提示：点击开始添加后窗口将最小化，按住 Alt+ 鼠标左键连续添加点，按 ESC 退出")
        tip_label.setStyleSheet("color: #808080; font-size: 13px; padding: 5px; background-color: rgba(255,255,255,100); border-radius: 3px;")
        points_layout.addWidget(tip_label)
        
        layout.addWidget(points_card)
        
        # 坐标点列表卡片
        list_card, list_layout = self.create_card("坐标点列表")
        
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        self.points_table = QTableWidget()
        self.points_table.setColumnCount(4)
        self.points_table.setHorizontalHeaderLabels(["序号", "X 坐标", "Y 坐标", "点击类型"])
        self.points_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.points_table.verticalHeader().setVisible(False)
        self.points_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.points_table.setMinimumHeight(200)
        list_layout.addWidget(self.points_table)
        
        # 列表操作按钮
        table_btn_layout = QHBoxLayout()
        table_btn_layout.setSpacing(10)
        
        self.remove_point_btn = self.create_button("删除选中")
        self.remove_point_btn.clicked.connect(self.remove_selected_point)
        table_btn_layout.addWidget(self.remove_point_btn)
        
        self.clear_points_btn = self.create_danger_button("清空所有")
        self.clear_points_btn.clicked.connect(self.clear_all_points)
        table_btn_layout.addWidget(self.clear_points_btn)
        
        table_btn_layout.addStretch()
        list_layout.addLayout(table_btn_layout)
        
        layout.addWidget(list_card)
        
        # 控制卡片
        control_card, control_layout = self.create_card("控制")
        
        # 脚本选择
        auto_script_layout = QHBoxLayout()
        auto_script_layout.setSpacing(10)
        
        auto_script_layout.addWidget(QLabel("执行后回放脚本:"))
        self.auto_script_combo = self.create_combo(["-- 不回放 --"])
        self.auto_script_combo.setMinimumWidth(200)
        auto_script_layout.addWidget(self.auto_script_combo)
        
        self.auto_refresh_script_btn = self.create_button("🔄")
        self.auto_refresh_script_btn.setFixedWidth(40)
        self.auto_refresh_script_btn.clicked.connect(self.refresh_script_list)
        auto_script_layout.addWidget(self.auto_refresh_script_btn)
        
        self.auto_select_script_btn = self.create_button("📁")
        self.auto_select_script_btn.setFixedWidth(40)
        self.auto_select_script_btn.clicked.connect(self.select_script_file)
        auto_script_layout.addWidget(self.auto_select_script_btn)
        
        auto_script_layout.addStretch()
        control_layout.addLayout(auto_script_layout)
        
        # 循环设置
        loop_layout = QHBoxLayout()
        loop_layout.setSpacing(15)
        
        loop_layout.addWidget(QLabel("循环次数:"))
        self.auto_loop_spin = self.create_spinbox(1, 999, 1)
        loop_layout.addWidget(self.auto_loop_spin)
        
        loop_layout.addWidget(QLabel("点之间延迟 (ms):"))
        self.delay_spin = self.create_spinbox(100, 10000, 500, " ms")
        loop_layout.addWidget(self.delay_spin)
        
        loop_layout.addWidget(QLabel("点击和脚本执行延迟 (ms):"))
        self.click_script_delay_spin = self.create_spinbox(0, 10000, 300, " ms")
        loop_layout.addWidget(self.click_script_delay_spin)
        
        loop_layout.addStretch()
        control_layout.addLayout(loop_layout)
        
        # 开始/停止和暂停按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.auto_start_btn = self.create_primary_button("开始执行 (F5)")
        self.auto_start_btn.clicked.connect(self.toggle_auto_click)
        self.auto_start_btn.setMinimumHeight(45)
        btn_layout.addWidget(self.auto_start_btn)
        
        self.auto_pause_btn = self.create_button("暂停 (F1)")
        self.auto_pause_btn.clicked.connect(self.toggle_pause_auto_click)
        self.auto_pause_btn.setMinimumHeight(45)
        self.auto_pause_btn.setEnabled(False)
        btn_layout.addWidget(self.auto_pause_btn)
        
        btn_layout.addStretch()
        control_layout.addLayout(btn_layout)
        
        layout.addWidget(control_card)
        
        # 状态卡片
        status_card, status_layout = self.create_card("状态")
        
        self.auto_status_label = self.create_status_label("状态：未开始")
        status_layout.addWidget(self.auto_status_label)
        
        self.auto_progress_label = self.create_info_label("进度：0/0")
        status_layout.addWidget(self.auto_progress_label)
        
        layout.addWidget(status_card)
        
        # 初始化坐标点列表
        self.coordinate_points = []
        self.is_auto_clicking = False
        self.is_paused = False  # 添加暂停标志位
        self.current_point_index = 0
        self.current_loop = 0
        
        # 添加模式标志
        self.is_adding_mode = False
        self.add_click_type = "单击左键"  # 默认点击类型
        self.is_alt_pressed = False  # 用于追踪 Alt 键是否被按下
        self.last_added_position = None  # 用于避免重复添加相同位置
        layout.addStretch()
        
        # 创建完成后刷新脚本列表
        self.refresh_script_list()
    
    def create_recorder_tab(self):
        """创建录制选项卡 - 现代卡片式布局"""
        self.recorder_tab = QWidget()
        self.recorder_tab.setObjectName("tabContent")
        
        layout = QVBoxLayout(self.recorder_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 录制选项卡片
        options_card, options_layout = self.create_card("录制选项")
        
        self.record_mouse_move = self.create_combo(["录制鼠标移动", "不录制鼠标移动"])
        options_layout.addWidget(self.record_mouse_move)
        
        self.record_mouse_click = self.create_combo(["录制鼠标点击", "不录制鼠标点击"])
        options_layout.addWidget(self.record_mouse_click)
        
        self.record_keyboard = self.create_combo(["录制键盘操作", "不录制键盘操作"])
        options_layout.addWidget(self.record_keyboard)
        
        layout.addWidget(options_card)
        
        # 控制卡片
        control_card, control_layout = self.create_card("控制")
        
        self.record_start_btn = self.create_primary_button("开始录制 (F9)")
        self.record_start_btn.clicked.connect(self.toggle_recording)
        self.record_start_btn.setMinimumHeight(45)
        control_layout.addWidget(self.record_start_btn)
        
        layout.addWidget(control_card)
        
        # 撤销/重做卡片
        undo_card, undo_layout = self.create_card("编辑")
        
        # 第一行：撤销和重做
        undo_redo_layout = QHBoxLayout()
        undo_redo_layout.setSpacing(10)
        
        self.undo_btn = self.create_button("撤销 (Ctrl+Z)")
        self.undo_btn.clicked.connect(self.undo_recording)
        self.undo_btn.setEnabled(False)
        undo_redo_layout.addWidget(self.undo_btn)
        
        self.redo_btn = self.create_button("重做 (Ctrl+Y)")
        self.redo_btn.clicked.connect(self.redo_recording)
        self.redo_btn.setEnabled(False)
        undo_redo_layout.addWidget(self.redo_btn)
        
        undo_layout.addLayout(undo_redo_layout)
        
        # 第二行：删除动作
        delete_layout = QHBoxLayout()
        delete_layout.setSpacing(10)
        
        self.delete_selected_btn = self.create_button("删除选中动作")
        self.delete_selected_btn.clicked.connect(self.delete_selected_action)
        delete_layout.addWidget(self.delete_selected_btn)
        
        self.clear_all_btn = self.create_danger_button("删除所有动作")
        self.clear_all_btn.clicked.connect(self.clear_all_actions)
        delete_layout.addWidget(self.clear_all_btn)
        
        undo_layout.addLayout(delete_layout)
        
        layout.addWidget(undo_card)
        
        # 状态卡片
        status_card, status_layout = self.create_card("状态")
        
        self.record_status_label = self.create_status_label("状态：未录制")
        status_layout.addWidget(self.record_status_label)
        
        self.record_count_label = self.create_info_label("已录制动作：0 个 | 可撤销：0 | 可重做：0")
        status_layout.addWidget(self.record_count_label)
        
        layout.addWidget(status_card)
        
        # 操作列表卡片
        actions_card, actions_layout = self.create_card("录制动作")
        
        self.actions_text = QTextEdit()
        self.actions_text.setReadOnly(True)
        self.actions_text.setObjectName("actionsText")
        self.actions_text.setMinimumHeight(150)
        actions_layout.addWidget(self.actions_text)
        
        layout.addWidget(actions_card)
    
    def create_playback_tab(self):
        """创建回放选项卡 - 现代卡片式布局"""
        self.playback_tab = QWidget()
        self.playback_tab.setObjectName("tabContent")
        
        layout = QVBoxLayout(self.playback_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 回放设置卡片
        settings_card, settings_layout = self.create_card("回放设置")
        
        # 脚本选择
        script_layout = QHBoxLayout()
        script_layout.setSpacing(10)
        
        script_layout.addWidget(self.create_label("选择脚本:"))
        self.script_combo = self.create_combo(["-- 当前录制 --"])
        self.script_combo.setMinimumWidth(200)
        # 不自动加载，只在需要时加载
        # self.script_combo.currentTextChanged.connect(self.load_selected_script)
        script_layout.addWidget(self.script_combo)
        
        # 添加加载按钮
        self.load_script_btn = self.create_button("加载选中脚本")
        self.load_script_btn.clicked.connect(self.load_selected_script)
        script_layout.addWidget(self.load_script_btn)
        
        self.refresh_script_btn = self.create_button("🔄")
        self.refresh_script_btn.setFixedWidth(40)
        self.refresh_script_btn.clicked.connect(self.refresh_script_list)
        script_layout.addWidget(self.refresh_script_btn)
        
        script_layout.addStretch()
        settings_layout.addLayout(script_layout)
        
        # 速度设置
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.create_label("回放速度:"))
        self.playback_speed_spin = self.create_spinbox(1, 500, 100, "%")
        speed_layout.addWidget(self.playback_speed_spin)
        speed_layout.addStretch()
        settings_layout.addLayout(speed_layout)
        
        # 循环次数
        loop_layout = QHBoxLayout()
        loop_layout.addWidget(self.create_label("循环次数:"))
        self.playback_loop_spin = self.create_spinbox(1, 1000, 1)
        loop_layout.addWidget(self.playback_loop_spin)
        loop_layout.addStretch()
        settings_layout.addLayout(loop_layout)
        
        layout.addWidget(settings_card)
        
        # 文件操作卡片
        file_card, file_layout = self.create_card("录制文件")
        
        file_btn_layout = QHBoxLayout()
        file_btn_layout.setSpacing(10)
        
        self.load_file_btn = self.create_button("加载文件")
        self.load_file_btn.clicked.connect(self.load_recording_file)
        file_btn_layout.addWidget(self.load_file_btn)
        
        self.save_file_btn = self.create_button("保存文件")
        self.save_file_btn.clicked.connect(self.save_recording_file)
        file_btn_layout.addWidget(self.save_file_btn)
        
        file_layout.addLayout(file_btn_layout)
        
        self.current_file_label = self.create_info_label("当前文件：无")
        file_layout.addWidget(self.current_file_label)
        
        layout.addWidget(file_card)
        
        # 控制卡片
        control_card, control_layout = self.create_card("控制")
        
        self.playback_start_btn = self.create_primary_button("开始回放 (F11)")
        self.playback_start_btn.clicked.connect(self.toggle_playback)
        self.playback_start_btn.setMinimumHeight(45)
        control_layout.addWidget(self.playback_start_btn)
        
        layout.addWidget(control_card)
        
        # 进度卡片
        progress_card, progress_layout = self.create_card("进度")
        
        self.playback_progress = QProgressBar()
        self.playback_progress.setRange(0, 100)
        self.playback_progress.setValue(0)
        self.playback_progress.setObjectName("progressBar")
        self.playback_progress.setMinimumHeight(25)
        progress_layout.addWidget(self.playback_progress)
        
        layout.addWidget(progress_card)
        
        # 状态卡片
        status_card, status_layout = self.create_card("状态")
        
        self.playback_status_label = self.create_status_label("状态：未播放")
        status_layout.addWidget(self.playback_status_label)
        
        layout.addWidget(status_card)
    
    # ========== 辅助方法 ==========
    
    def create_card(self, title):
        """创建卡片容器"""
        card = QFrame()
        card.setObjectName("card")
        
        # 创建主布局
        main_layout = QVBoxLayout(card)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)
        
        # 卡片标题
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("cardTitle")
            main_layout.addWidget(title_label)
        
        # 内容布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 5, 0, 0)
        content_layout.setSpacing(10)
        main_layout.addLayout(content_layout)
        
        return card, content_layout
    
    def create_label(self, text):
        """创建标签"""
        label = QLabel(text)
        label.setObjectName("formLabel")
        label.setMinimumWidth(80)
        return label
    
    def create_combo(self, items):
        """创建下拉框"""
        combo = QComboBox()
        combo.addItems(items)
        combo.setObjectName("comboBox")
        combo.setMinimumHeight(35)
        return combo
    
    def create_spinbox(self, min_val, max_val, value, suffix="", special_text=None):
        """创建数字输入框"""
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(value)
        if suffix:
            spinbox.setSuffix(suffix)
        if special_text:
            spinbox.setSpecialValueText(special_text)
        spinbox.setObjectName("spinBox")
        spinbox.setMinimumHeight(35)
        return spinbox
    
    def create_button(self, text):
        """创建普通按钮"""
        btn = QPushButton(text)
        btn.setObjectName("normalBtn")
        btn.setMinimumHeight(38)
        return btn
    
    def create_primary_button(self, text):
        """创建主按钮"""
        btn = QPushButton(text)
        btn.setObjectName("primaryBtn")
        btn.setMinimumHeight(38)
        return btn
    
    def create_danger_button(self, text):
        """创建危险按钮"""
        btn = QPushButton(text)
        btn.setObjectName("dangerBtn")
        btn.setMinimumHeight(38)
        return btn
    
    def create_status_label(self, text):
        """创建状态标签"""
        label = QLabel(text)
        label.setObjectName("statusLabel")
        return label
    
    def create_info_label(self, text):
        """创建信息标签"""
        label = QLabel(text)
        label.setObjectName("infoLabel")
        return label
    
    def toggle_recording(self):
        """切换录制状态"""
        if self.recorder.is_recording_active():
            actions = self.recorder.stop_recording()
            self.record_start_btn.setText("开始录制 (F9)")
            self.record_start_btn.setStyleSheet("")
            self.statusBar().showMessage(f'录制已完成 - 共录制{len(actions)}个动作')
            self.update_recording_display()
            
            # 恢复所有全局快捷键监听
            self.global_hotkey.stop()  # 先停止
            self.setup_shortcuts()  # 重新设置所有快捷键
            self.statusBar().showMessage('录制已完成，全局快捷键已恢复', 2000)
        else:
            # 只保留停止录制的快捷键，暂停其他可能冲突的快捷键
            # 这样用户可以在其他界面按F9或F10停止录制
            
            # 先暂停所有快捷键
            self.global_hotkey.stop()
            
            # 重新设置，只保留停止录制和暂停相关的快捷键
            self.global_hotkey.hotkey_map.clear()
            self.global_hotkey.register_hotkey("F9", "toggle_recording")
            self.global_hotkey.register_hotkey("F10", "stop_recording_only")
            self.global_hotkey.register_hotkey("Esc", "emergency_stop")
            self.global_hotkey.register_hotkey("F2", "toggle_pause_auto_click")
            self.global_hotkey.start()
            
            record_mouse_move = "录制" in self.record_mouse_move.currentText()
            record_mouse_click = "录制" in self.record_mouse_click.currentText()
            record_keyboard = "录制" in self.record_keyboard.currentText()
            
            self.recorder.start_recording(
                record_mouse_move, record_mouse_click, record_keyboard
            )
            self.record_start_btn.setText("停止录制")
            self.record_start_btn.setStyleSheet(
                "background-color: #ff6b6b; color: white;"
            )
            self.statusBar().showMessage('录制已开始，只保留停止录制的快捷键')
    
    def toggle_playback(self):
        """切换回放状态"""
        if self.player.is_active():
            self.player.stop_playback()
            self.playback_start_btn.setText("开始回放 (F11)")
            self.playback_start_btn.setStyleSheet("")
            self.statusBar().showMessage('回放已停止')
        else:
            # 获取要回放的脚本
            script_name = self.script_combo.currentText()
            
            if script_name == "-- 当前录制 --":
                # 使用当前录制内容
                actions = self.recorder.get_actions()
            else:
                # 从文件加载脚本
                import os
                script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
                script_path = os.path.join(script_dir, script_name)
                
                if os.path.exists(script_path):
                    # 临时加载脚本
                    temp_recorder = ActionRecorder()
                    if temp_recorder.load_from_file(script_path):
                        actions = temp_recorder.get_actions()
                    else:
                        QMessageBox.critical(self, "错误", "加载脚本失败！")
                        return
                else:
                    QMessageBox.warning(self, "警告", "脚本文件不存在！")
                    return
            
            if not actions:
                QMessageBox.warning(self, "警告", "没有可回放的录制动作！")
                return
            
            speed = self.playback_speed_spin.value() / 100.0
            loop_count = self.playback_loop_spin.value()
            
            # 确保回放时不会录制
            if self.recorder.is_recording_active():
                self.recorder.stop_recording()
            
            self.player.play_actions(actions, speed, loop_count)
            self.playback_start_btn.setText("停止回放")
            self.playback_start_btn.setStyleSheet(
                "background-color: #ff6b6b; color: white;"
            )
            self.statusBar().showMessage(f'回放已开始 - 速度{speed}x, 循环{loop_count}次')
    
    def load_recording_file(self):
        """加载录制文件"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "打开录制文件", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            if self.recorder.load_from_file(filename):
                self.current_file_label.setText(f"当前文件：{filename}")
                self.statusBar().showMessage(f'已加载文件：{filename}')
                self.update_actions_display()
            else:
                QMessageBox.critical(self, "错误", "加载文件失败！")
    
    def save_recording_file(self):
        """保存录制文件"""
        actions = self.recorder.get_actions()
        if not actions:
            QMessageBox.warning(self, "警告", "没有可保存的录制动作！")
            return
        
        import os
        script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存录制文件", os.path.join(script_dir, "recording.json"), "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            if self.recorder.save_to_file(filename):
                self.current_file_label.setText(f"当前文件：{filename}")
                self.statusBar().showMessage(f'已保存到：{filename}')
                # 刷新脚本列表
                self.refresh_script_list()
            else:
                QMessageBox.critical(self, "错误", "保存文件失败！")
    
    def refresh_script_list(self):
        """刷新脚本文件列表"""
        import os
        import glob
        
        # 获取脚本目录（程序所在目录下的 scripts 文件夹）
        script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
        
        # 如果目录不存在，创建它
        if not os.path.exists(script_dir):
            try:
                os.makedirs(script_dir)
            except:
                pass
        
        # 获取所有 JSON 文件
        self.script_files = glob.glob(os.path.join(script_dir, '*.json'))
        
        # 提取文件名（不含路径）
        script_names = [os.path.basename(f) for f in self.script_files]
        
        # 更新回放选项卡的下拉框
        if hasattr(self, 'script_combo'):
            self.script_combo.clear()
            self.script_combo.addItem("-- 当前录制 --")
            self.script_combo.addItems(script_names)
        
        # 更新定点连点选项卡的下拉框
        if hasattr(self, 'auto_script_combo'):
            self.auto_script_combo.clear()
            self.auto_script_combo.addItem("-- 不回放 --")
            self.auto_script_combo.addItems(script_names)
    
    def select_script_file(self):
        """选择脚本文件 - 允许用户从任意位置选择脚本"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择脚本文件", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            import os
            script_name = os.path.basename(filename)
            
            # 检查是否已存在该脚本
            exists = False
            for i in range(self.auto_script_combo.count()):
                if self.auto_script_combo.itemText(i) == script_name:
                    exists = True
                    self.auto_script_combo.setCurrentIndex(i)
                    break
            
            if not exists:
                # 添加到下拉菜单
                self.auto_script_combo.addItem(script_name)
                self.auto_script_combo.setCurrentText(script_name)
            
            # 保存完整路径信息
            if not hasattr(self, 'script_file_paths'):
                self.script_file_paths = {}
            
            self.script_file_paths[script_name] = filename
            
            self.statusBar().showMessage(f'已选择脚本文件: {script_name}')
        
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(f'已刷新脚本列表，共 {len(script_names)} 个脚本')
    
    def load_selected_script(self):
        """加载选中的脚本"""
        script_name = self.script_combo.currentText()
        
        if script_name == "-- 当前录制 --":
            self.current_script_path = None
            self.statusBar().showMessage('使用当前录制内容')
            return
        
        import os
        script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
        script_path = os.path.join(script_dir, script_name)
        
        if os.path.exists(script_path):
            self.current_script_path = script_path
            if self.recorder.load_from_file(script_path):
                self.current_file_label.setText(f"当前文件：{script_path}")
                self.statusBar().showMessage(f'已加载脚本：{script_name}')
                self.update_actions_display()
            else:
                QMessageBox.critical(self, "错误", "加载脚本失败！")
        else:
            self.current_script_path = None
            QMessageBox.warning(self, "警告", "脚本文件不存在！")
    
    def update_actions_display(self):
        """更新动作显示"""
        actions = self.recorder.get_actions()
        if not actions:
            self.actions_text.setText("暂无录制动作")
            self.record_count_label.setText("已录制动作：0 个")
            return
        
        text = f"共录制 {len(actions)} 个动作：\n\n"
        for i, action in enumerate(actions, 1):
            action_type = action.get('type', 'unknown')
            time_val = action.get('time', 0)
            
            if action_type == 'mouse_move':
                text += f"{i}. [{time_val:.2f}s] 鼠标移动到 ({action.get('x', 0)}, {action.get('y', 0)})\n"
            elif action_type == 'mouse_click':
                button = action.get('button', 'unknown')
                pressed = "按下" if action.get('pressed') else "释放"
                text += f"{i}. [{time_val:.2f}s] {pressed}鼠标{button} at ({action.get('x', 0)}, {action.get('y', 0)})\n"
            elif action_type == 'mouse_scroll':
                text += f"{i}. [{time_val:.2f}s] 鼠标滚轮 at ({action.get('x', 0)}, {action.get('y', 0)})\n"
            elif action_type == 'key_press':
                text += f"{i}. [{time_val:.2f}s] 按下按键：{action.get('key', 'unknown')}\n"
            elif action_type == 'key_release':
                text += f"{i}. [{time_val:.2f}s] 释放按键：{action.get('key', 'unknown')}\n"
        
        self.actions_text.setText(text)
        self.record_count_label.setText(f"已录制动作：{len(actions)} 个")
    
    def update_status(self):
        """更新状态显示"""
        if self.recorder.is_recording_active():
            self.record_status_label.setText("状态：录制中...")
            self.record_status_label.setStyleSheet("color: #f44336;")
            self.record_count_label.setText(f"已录制动作：{len(self.recorder.get_actions())} 个")
        else:
            self.record_status_label.setText("状态：未录制")
            self.record_status_label.setStyleSheet("color: #808080;")
            undo_count = self.recorder.get_undo_count()
            redo_count = self.recorder.get_redo_count()
            self.record_count_label.setText(f"已录制动作：{len(self.recorder.get_actions())} 个 | 可撤销：{undo_count} | 可重做：{redo_count}")
        
        if self.player.is_active():
            self.playback_status_label.setText("状态：播放中...")
            self.playback_status_label.setStyleSheet("color: #4caf50;")
            self.playback_progress.setValue(int(self.player.get_progress()))
        else:
            self.playback_status_label.setText("状态：未播放")
            self.playback_status_label.setStyleSheet("color: #808080;")
            self.playback_progress.setValue(0)
    
    def setup_shortcuts(self):
        """设置全局快捷键"""
        # 初始化快捷键配置（使用默认配置）
        if not hasattr(self, 'current_shortcuts'):
            self.current_shortcuts = DEFAULT_SHORTCUTS.copy()
        
        # 清空旧的窗口内快捷键
        if hasattr(self, 'window_shortcuts'):
            for shortcut in self.window_shortcuts:
                shortcut.setEnabled(False)
            self.window_shortcuts.clear()
        
        # 清空旧的全局快捷键映射
        self.global_hotkey.hotkey_map.clear()
        
        # 注册全局快捷键
        for func_name, shortcut in self.current_shortcuts.items():
            if func_name in FUNCTION_METHOD_MAP:
                method_name = FUNCTION_METHOD_MAP[func_name]
                self.global_hotkey.register_hotkey(shortcut, method_name)
        
        # 启动全局快捷键监听
        self.global_hotkey.start()
        
        # 窗口内快捷键（使用QShortcut）
        for func_name, shortcut in self.current_shortcuts.items():
            if func_name in FUNCTION_METHOD_MAP:
                method_name = FUNCTION_METHOD_MAP[func_name]
                method = getattr(self, method_name, None)
                
                if method and shortcut != "Esc":  # Esc键有其他处理
                    try:
                        qt_shortcut = QShortcut(QKeySequence(shortcut), self)
                        qt_shortcut.activated.connect(method)
                        
                        # 保存引用，防止被垃圾回收
                        if not hasattr(self, 'window_shortcuts'):
                            self.window_shortcuts = []
                        self.window_shortcuts.append(qt_shortcut)
                    except Exception:
                        pass
        
    def open_shortcut_editor(self):
        """打开快捷键编辑窗口"""
        if not hasattr(self, 'current_shortcuts'):
            self.current_shortcuts = DEFAULT_SHORTCUTS.copy()
            
        editor = ShortcutEditor(self.current_shortcuts, self)
        editor.shortcutChanged.connect(self.handle_shortcut_changed)
        
        if editor.exec_():
            # 保存新的快捷键配置
            self.current_shortcuts = editor.get_shortcuts()
            self.statusBar().showMessage("快捷键设置已保存")
            
            # 重新设置快捷键
            self.global_hotkey.stop()
            self.setup_shortcuts()
            self.statusBar().showMessage("快捷键已应用")
        else:
            self.statusBar().showMessage("快捷键设置已取消")
            
    def handle_shortcut_changed(self, func_name, new_shortcut):
        """处理快捷键变化"""
        if func_name in FUNCTION_METHOD_MAP:
            method_name = FUNCTION_METHOD_MAP[func_name]
            
            # 更新内部存储
            self.current_shortcuts[func_name] = new_shortcut
            
            # 更新全局快捷键
            old_shortcut = None
            for name, shortcut in self.global_hotkey.hotkey_map.items():
                if shortcut == method_name:
                    old_shortcut = name
                    break
                    
            if old_shortcut and old_shortcut != new_shortcut:
                # 删除旧的快捷键
                if old_shortcut in self.global_hotkey.hotkey_map:
                    del self.global_hotkey.hotkey_map[old_shortcut]
                
                # 添加新的快捷键
                self.global_hotkey.register_hotkey(new_shortcut, method_name)
        
        # Ctrl+S - 保存录制（窗口内）
        shortcut_ctrl_s = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_ctrl_s.activated.connect(self.save_recording_file)
        
        # Ctrl+O - 打开录制文件（窗口内）
        shortcut_ctrl_o = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut_ctrl_o.activated.connect(self.load_recording_file)
        
        # Ctrl+E - 打开脚本编辑器（窗口内）
        shortcut_ctrl_e = QShortcut(QKeySequence("Ctrl+E"), self)
        shortcut_ctrl_e.activated.connect(self.open_script_editor)
        
        # Ctrl+Z - 撤销录制（窗口内）
        shortcut_ctrl_z = QShortcut(QKeySequence("Ctrl+Z"), self)
        shortcut_ctrl_z.activated.connect(self.undo_recording)
        
        # Ctrl+Y - 重做录制（窗口内）
        shortcut_ctrl_y = QShortcut(QKeySequence("Ctrl+Y"), self)
        shortcut_ctrl_y.activated.connect(self.redo_recording)
        
        # Esc - 紧急停止（窗口内）
        shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        shortcut_esc.activated.connect(self.emergency_stop)
        
        # F5 - 定点连点开关（窗口内）
        shortcut_f5 = QShortcut(QKeySequence("F5"), self)
        shortcut_f5.activated.connect(self.toggle_auto_click)
        
        # 注册全局快捷键
        self.global_hotkey.register_hotkey("F5", "toggle_auto_click")
    
    def handle_global_hotkey(self, action_name):
        """处理全局快捷键触发"""
        if hasattr(self, action_name):
            action = getattr(self, action_name)
            if callable(action):
                action()
    
    def stop_all_operations(self):
        """停止所有操作"""
        self.recorder.stop_recording()
        self.player.stop_playback()
        
        # 停止定点连点功能
        if self.is_auto_clicking:
            self.stop_auto_click()
            
        self.statusBar().showMessage('已停止所有操作')
    
    def stop_recording_only(self):
        """仅停止录制"""
        if self.recorder.is_recording_active():
            self.recorder.stop_recording()
            self.statusBar().showMessage('录制已停止')
    
    def stop_playback_only(self):
        """仅停止回放"""
        if self.player.is_active():
            self.player.stop_playback()
            self.statusBar().showMessage('回放已停止')
    
    def undo_recording(self):
        """撤销录制动作"""
        if self.recorder.undo():
            self.update_recording_display()
            self.statusBar().showMessage('已撤销 1 个动作')
        else:
            self.statusBar().showMessage('没有可撤销的动作')
    
    def redo_recording(self):
        """重做录制动作"""
        if self.recorder.redo():
            self.update_recording_display()
            self.statusBar().showMessage('已重做 1 个动作')
        else:
            self.statusBar().showMessage('没有可重做的动作')
    
    def clear_last_actions(self):
        """删除最后 10 个动作"""
        deleted = self.recorder.delete_last_n_actions(10)
        if deleted > 0:
            self.update_recording_display()
            self.statusBar().showMessage(f'已删除最后{deleted}个动作')
        else:
            self.statusBar().showMessage('没有可删除的动作')
    
    def delete_selected_action(self):
        """删除选中的动作"""
        # 获取选中的行
        cursor = self.actions_text.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            # 如果没有选中文字，尝试获取当前行的数字
            cursor.select(QTextCursor.LineUnderCursor)
            selected_text = cursor.selectedText()
        
        # 从行首提取动作编号
        import re
        match = re.match(r'(\d+)\.', selected_text.strip())
        if match:
            index = int(match.group(1)) - 1  # 转换为 0 基索引
            if 0 <= index < len(self.recorder.get_actions()):
                self.recorder.delete_action_at(index)
                self.update_recording_display()
                self.statusBar().showMessage(f'已删除动作 {index + 1}')
            else:
                self.statusBar().showMessage('无效的动作编号')
        else:
            QMessageBox.information(self, "提示", "请先选中要删除的动作行")
    
    def clear_all_actions(self):
        """删除所有动作"""
        if not self.recorder.get_actions():
            self.statusBar().showMessage('没有可删除的动作')
            return
        
        reply = QMessageBox.question(
            self,
            '确认删除',
            '确定要删除所有录制动作吗？此操作不可恢复！',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.recorder.clear_all_actions()
            self.update_recording_display()
            self.statusBar().showMessage('已删除所有动作')
    
    def update_recording_display(self):
        """更新录制显示"""
        actions = self.recorder.get_actions()
        undo_count = self.recorder.get_undo_count()
        redo_count = self.recorder.get_redo_count()
        
        self.record_count_label.setText(f"已录制动作：{len(actions)} 个 | 可撤销：{undo_count} | 可重做：{redo_count}")
        self.undo_btn.setEnabled(undo_count > 0)
        self.redo_btn.setEnabled(redo_count > 0)
        self.update_actions_display()
    
    def emergency_stop(self):
        """紧急停止"""
        if (self.player.is_active()):
            self.stop_all_operations()
            self.statusBar().showMessage('紧急停止！')
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件 (&F)")
        
        editor_action = file_menu.addAction("脚本编辑器 (&E)")
        editor_action.setShortcut("Ctrl+E")
        editor_action.triggered.connect(self.open_script_editor)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("退出 (&X)")
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        
        settings_menu = menubar.addMenu("设置 (&S)")
        
        record_settings_action = settings_menu.addAction("录制设置 (&R)")
        record_settings_action.triggered.connect(self.show_record_settings)
        
        playback_settings_action = settings_menu.addAction("回放设置 (&P)")
        playback_settings_action.triggered.connect(self.show_playback_settings)
        
        shortcut_settings_action = settings_menu.addAction("快捷键设置 (&K)")
        shortcut_settings_action.triggered.connect(self.show_shortcut_settings)
        
        settings_menu.addSeparator()
        
        advanced_settings_action = settings_menu.addAction("高级设置 (&A)")
        advanced_settings_action.triggered.connect(self.show_advanced_settings)
        
        help_menu = menubar.addMenu("帮助 (&H)")
        
        about_action = help_menu.addAction("关于 (&A)")
        about_action.triggered.connect(self.show_about)
    
    def open_script_editor(self):
        """打开脚本编辑器"""
        if self.script_editor is None:
            self.script_editor = ScriptEditor(self.recorder, self)
            self.script_editor.setWindowTitle("脚本编辑器")
            self.script_editor.resize(800, 600)
        
        self.script_editor.show()
        self.script_editor.refresh_table()
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 鼠大师",
            "鼠大师 - 鼠标键盘操控程序\n\n"
            "版本：1.0\n\n"
            "功能特性:\n"
            "- 鼠标连点器\n"
            "- 键盘连点器\n"
            "- 鼠标键盘录制\n"
            "- 动作回放\n"
            "- 脚本编辑器\n\n"
            "© 2026 All Rights Reserved"
        )
    
    def show_record_settings(self):
        """显示录制设置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("录制设置")
        dialog.setMinimumWidth(400)
        dialog.setObjectName("settingsDialog")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addWidget(QLabel("录制选项:"))
        
        self.record_mouse_move_check = QCheckBox("录制鼠标移动")
        self.record_mouse_move_check.setChecked("录制" in self.record_mouse_move.currentText())
        layout.addWidget(self.record_mouse_move_check)
        
        self.record_mouse_click_check = QCheckBox("录制鼠标点击")
        self.record_mouse_click_check.setChecked("录制" in self.record_mouse_click.currentText())
        layout.addWidget(self.record_mouse_click_check)
        
        self.record_keyboard_check = QCheckBox("录制键盘操作")
        self.record_keyboard_check.setChecked("录制" in self.record_keyboard.currentText())
        layout.addWidget(self.record_keyboard_check)
        
        layout.addWidget(QLabel("\n撤销/重做设置:"))
        
        undo_layout = QHBoxLayout()
        undo_layout.addWidget(QLabel("最大撤销步数:"))
        self.max_undo_spin = QSpinBox()
        self.max_undo_spin.setRange(1, 1000)
        self.max_undo_spin.setValue(100)
        undo_layout.addWidget(self.max_undo_spin)
        undo_layout.addStretch()
        layout.addLayout(undo_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(lambda: self.save_record_settings(dialog))
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("normalBtn")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def save_record_settings(self, dialog):
        """保存录制设置"""
        self.record_mouse_move.setCurrentIndex(0 if self.record_mouse_move_check.isChecked() else 1)
        self.record_mouse_click.setCurrentIndex(0 if self.record_mouse_click_check.isChecked() else 1)
        self.record_keyboard.setCurrentIndex(0 if self.record_keyboard_check.isChecked() else 1)
        
        self.statusBar().showMessage('录制设置已保存')
        dialog.close()
    
    def show_playback_settings(self):
        """显示回放设置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("回放设置")
        dialog.setMinimumWidth(400)
        dialog.setObjectName("settingsDialog")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("默认回放速度:"))
        self.playback_speed_setting = QSpinBox()
        self.playback_speed_setting.setRange(1, 500)
        self.playback_speed_setting.setValue(self.playback_speed_spin.value())
        self.playback_speed_setting.setSuffix("%")
        speed_layout.addWidget(self.playback_speed_setting)
        speed_layout.addStretch()
        layout.addLayout(speed_layout)
        
        loop_layout = QHBoxLayout()
        loop_layout.addWidget(QLabel("默认循环次数:"))
        self.playback_loop_setting = QSpinBox()
        self.playback_loop_setting.setRange(1, 1000)
        self.playback_loop_setting.setValue(self.playback_loop_spin.value())
        loop_layout.addWidget(self.playback_loop_setting)
        loop_layout.addStretch()
        layout.addLayout(loop_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(lambda: self.save_playback_settings(dialog))
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("normalBtn")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def save_playback_settings(self, dialog):
        """保存回放设置"""
        self.playback_speed_spin.setValue(self.playback_speed_setting.value())
        self.playback_loop_spin.setValue(self.playback_loop_setting.value())
        
        self.statusBar().showMessage('回放设置已保存')
        dialog.close()
    
    def show_shortcut_settings(self):
        """显示快捷键设置对话框（调用新的快捷键编辑器）"""
        self.open_shortcut_editor()
        

    
    def show_advanced_settings(self):
        """显示高级设置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("高级设置")
        dialog.setMinimumWidth(450)
        dialog.setObjectName("settingsDialog")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addWidget(QLabel("高级选项:"))
        
        global_shortcut_check = QCheckBox("启用全局快捷键（程序后台时也能响应快捷键）")
        global_shortcut_check.setChecked(True)
        global_shortcut_check.setEnabled(False)
        layout.addWidget(global_shortcut_check)
        
        auto_load_check = QCheckBox("启动时自动加载上次使用的录制文件")
        auto_load_check.setChecked(False)
        layout.addWidget(auto_load_check)
        
        tray_check = QCheckBox("最小化到系统托盘")
        tray_check.setChecked(False)
        tray_check.setEnabled(False)
        layout.addWidget(tray_check)
        
        log_check = QCheckBox("启用操作日志记录")
        log_check.setChecked(False)
        layout.addWidget(log_check)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(lambda: self.save_advanced_settings(dialog, auto_load_check.isChecked()))
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("normalBtn")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def save_advanced_settings(self, dialog, auto_load):
        """保存高级设置"""
        self.statusBar().showMessage('高级设置已保存')
        dialog.close()
    
    # ========== 定点连点功能方法 ==========
    
    def toggle_add_mode(self):
        """切换添加模式"""
        if self.is_adding_mode:
            self.stop_add_mode()
        else:
            self.start_add_mode()
    
    def start_add_mode(self):
        """开始添加模式"""
        self.is_adding_mode = True
        self.add_click_type = self.click_type_combo.currentText()
        
        # 更新按钮状态
        self.add_point_btn.setText("添加中...")
        self.add_point_btn.setEnabled(False)
        self.stop_add_btn.setEnabled(True)
        
        # 最小化窗口
        self.showMinimized()
        
        # 启动全局鼠标监听
        self.start_mouse_listener()
        
        self.statusBar().showMessage('添加模式：按住 Ctrl+ 鼠标左键添加点，按 ESC 退出')
    
    def stop_add_mode(self):
        """停止添加模式"""
        if not self.is_adding_mode:
            return
        
        self.is_adding_mode = False
        
        # 停止鼠标监听
        self.stop_mouse_listener()
        
        # 恢复窗口
        self.showNormal()
        self.activateWindow()
        
        # 更新按钮状态
        self.add_point_btn.setText("开始添加 (Ctrl+ 左键)")
        self.add_point_btn.setEnabled(True)
        self.stop_add_btn.setEnabled(False)
        
        self.statusBar().showMessage(f'添加完成！共添加 {len(self.coordinate_points)} 个坐标点')
    
    def start_mouse_listener(self):
        """启动全局鼠标监听"""
        from pynput import mouse, keyboard
        import time
        
        # 记录已经添加过的位置，避免重复
        self.last_added_position = None
        
        def on_press(key):
            try:
                if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    # 按 Ctrl 时获取当前鼠标位置并添加（需要加载脚本）
                    mouse_controller = mouse.Controller()
                    x, y = mouse_controller.position
                    
                    if not self.is_adding_mode:
                        return False
                    
                    # 检查是否和上一个位置相同（避免重复添加）
                    if self.last_added_position != (int(x), int(y)):
                        self.last_added_position = (int(x), int(y))
                        self.add_point_to_list(int(x), int(y), self.add_click_type, need_script=True)
                        # 显示提示
                        self.statusBar().showMessage(f'已添加需加载脚本的点：({int(x)}, {int(y)})', 2000)
                        
                elif key == keyboard.Key.esc:
                    # 按 ESC 退出 - 使用 QTimer 在主线程中执行，避免在监听器线程中停止监听器
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(0, self.stop_add_mode)
                    return False
            except Exception as e:
                pass
                print(f'on_press 错误：{e}')
        
        def on_release(key):
            try:
                pass
            except Exception as e:
                print(f'on_release 错误：{e}')
        
        # 修改键盘监听，添加 Alt 键状态追踪（用于只记录左键点击）
        original_on_press = on_press
        def modified_on_press(key):
            try:
                if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    self.is_alt_pressed = True
                    # 当Alt键被按下时，立即获取当前鼠标位置并记录为左键点击（不需要加载脚本）
                    mouse_controller = mouse.Controller()
                    x, y = mouse_controller.position
                    if self.last_added_position != (int(x), int(y)):
                        self.last_added_position = (int(x), int(y))
                        self.add_point_to_list(int(x), int(y), "单击左键", need_script=False)
                        self.statusBar().showMessage(f'已添加纯左键点击：({int(x)}, {int(y)})', 2000)
                original_on_press(key)
            except Exception as e:
                pass
        
        def modified_on_release(key):
            try:
                if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    self.is_alt_pressed = False
            except Exception as e:
                pass
        
        # 启动键盘监听
        self.keyboard_listener = keyboard.Listener(
            on_press=modified_on_press,
            on_release=modified_on_release
        )
        self.keyboard_listener.start()
        
        # 稍微等待确保监听器启动
        time.sleep(0.2)
    
    def stop_mouse_listener(self):
        """停止鼠标监听"""
        import time
        
        if hasattr(self, 'keyboard_listener') and self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
                # 等待监听器线程停止
                timeout = 1.0  # 1 秒超时
                start_time = time.time()
                while self.keyboard_listener.running and (time.time() - start_time < timeout):
                    time.sleep(0.1)
            except Exception:
                pass
            finally:
                self.keyboard_listener = None
        
        if hasattr(self, 'mouse_listener') and self.mouse_listener:
            try:
                self.mouse_listener.stop()
                # 等待监听器线程停止
                timeout = 1.0  # 1 秒超时
                start_time = time.time()
                while self.mouse_listener.running and (time.time() - start_time < timeout):
                    time.sleep(0.1)
            except Exception:
                pass
            finally:
                self.mouse_listener = None
    
    def add_current_mouse_position(self):
        """添加当前鼠标位置"""
        from pynput.mouse import Controller
        mouse = Controller()
        x, y = mouse.position
        
        click_type = self.click_type_combo.currentText()
        self.add_point_to_list(x, y, click_type)
        self.statusBar().showMessage(f'已添加坐标：({x}, {y}) - {click_type}')
    
    def add_coordinate(self):
        """添加指定坐标"""
        x = self.coord_x_spin.value()
        y = self.coord_y_spin.value()
        click_type = self.click_type_combo.currentText()
        
        self.add_point_to_list(x, y, click_type)
        self.statusBar().showMessage(f'已添加坐标：({x}, {y}) - {click_type}')
    
    def add_point_to_list(self, x, y, click_type, need_script=True):
        """添加坐标点到列表"""
        point = {
            'x': x,
            'y': y,
            'click_type': click_type,
            'need_script': need_script  # 新增字段，标记是否需要加载脚本
        }
        self.coordinate_points.append(point)
        self.update_points_table()
    
    def update_points_table(self):
        """更新坐标点表格"""
        # 清空表格
        self.points_table.setRowCount(0)
        
        # 设置行数
        self.points_table.setRowCount(len(self.coordinate_points))
        
        for i, point in enumerate(self.coordinate_points):
            # 序号
            item_num = QTableWidgetItem(str(i + 1))
            item_num.setFlags(item_num.flags() & ~Qt.ItemIsEditable)
            self.points_table.setItem(i, 0, item_num)
            
            # X 坐标
            item_x = QTableWidgetItem(str(point.get('x', 0)))
            item_x.setFlags(item_x.flags() & ~Qt.ItemIsEditable)
            self.points_table.setItem(i, 1, item_x)
            
            # Y 坐标
            item_y = QTableWidgetItem(str(point.get('y', 0)))
            item_y.setFlags(item_y.flags() & ~Qt.ItemIsEditable)
            self.points_table.setItem(i, 2, item_y)
            
            # 点击类型
            item_type = QTableWidgetItem(point.get('click_type', '单击左键'))
            item_type.setFlags(item_type.flags() & ~Qt.ItemIsEditable)
            self.points_table.setItem(i, 3, item_type)
        
        # 刷新表格
        self.points_table.update()
        
        self.update_progress()
    
    def remove_selected_point(self):
        """删除选中的坐标点"""
        selected_rows = self.points_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选中要删除的坐标点")
            return
        
        # 从后往前删除，避免索引问题
        for index in sorted([row.row() for row in selected_rows], reverse=True):
            if 0 <= index < len(self.coordinate_points):
                self.coordinate_points.pop(index)
        
        self.update_points_table()
        self.statusBar().showMessage('已删除选中的坐标点')
    
    def clear_all_points(self):
        """清空所有坐标点"""
        if not self.coordinate_points:
            self.statusBar().showMessage('没有可删除的坐标点')
            return
        
        reply = QMessageBox.question(
            self,
            '确认清空',
            '确定要清空所有坐标点吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.coordinate_points = []
            self.update_points_table()
            self.statusBar().showMessage('已清空所有坐标点')
    
    def toggle_auto_click(self):
        """切换定点连点"""
        if self.is_auto_clicking:
            self.stop_auto_click()
        else:
            self.start_auto_click()
    
    def start_auto_click(self):
        """开始定点连点"""
        if not self.coordinate_points:
            QMessageBox.warning(self, "警告", "请先添加坐标点！")
            return
        
        self.is_auto_clicking = True
        self.current_point_index = 0
        self.current_loop = 0
        
        self.auto_start_btn.setText("停止执行")
        self.auto_start_btn.setStyleSheet("background-color: #ff6b6b; color: white;")
        self.auto_pause_btn.setEnabled(True)
        self.auto_status_label.setText("状态：执行中...")
        self.auto_status_label.setStyleSheet("color: #4caf50;")
        
        # 在独立线程中执行
        import threading
        thread = threading.Thread(target=self.auto_click_loop, daemon=True)
        thread.start()
        
        self.statusBar().showMessage('开始定点连点')
    
    def toggle_pause_auto_click(self):
        """暂停/继续定点连点"""
        if not self.is_auto_clicking:
            return
            
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.auto_pause_btn.setText("继续 (F1)")
            self.auto_status_label.setText("状态：已暂停")
            self.auto_status_label.setStyleSheet("color: #ffc107;")
            self.statusBar().showMessage('定点连点已暂停')
        else:
            self.auto_pause_btn.setText("暂停 (F1)")
            self.auto_status_label.setText("状态：执行中...")
            self.auto_status_label.setStyleSheet("color: #4caf50;")
            self.statusBar().showMessage('定点连点继续执行')
            
    def stop_auto_click(self):
        """停止定点连点"""
        self.is_auto_clicking = False
        self.is_paused = False
        # 停止正在播放的脚本
        if hasattr(self, 'current_temp_player') and self.current_temp_player.is_active():
            self.current_temp_player.stop_playback()
        self.auto_start_btn.setText("开始执行 (F5)")
        self.auto_start_btn.setStyleSheet("")
        self.auto_pause_btn.setEnabled(False)
        self.auto_pause_btn.setText("暂停 (F1)")
        self.auto_status_label.setText("状态：已停止")
        self.auto_status_label.setStyleSheet("color: #808080;")
        self.statusBar().showMessage('定点连点已停止')
    
    def auto_click_loop(self):
        """定点连点循环"""
        from pynput.mouse import Controller, Button
        import time
        
        mouse = Controller()
        delay = self.delay_spin.value() / 1000.0  # 转换为秒
        max_loops = self.auto_loop_spin.value()
        
        while self.is_auto_clicking and self.current_loop < max_loops:
            # 遍历所有坐标点
            for i, point in enumerate(self.coordinate_points):
                if not self.is_auto_clicking:
                    break
                
                # 检查暂停状态
                while self.is_paused and self.is_auto_clicking:
                    time.sleep(0.1)
                
                if not self.is_auto_clicking:
                    break
                
                self.current_point_index = i
                x, y = point['x'], point['y']
                click_type = point['click_type']
                
                # 更新进度
                total_points = len(self.coordinate_points) * max_loops
                current_progress = self.current_loop * len(self.coordinate_points) + i
                self.update_progress_signal(current_progress, total_points)
                
                # 移动鼠标到坐标
                mouse.position = (x, y)
                time.sleep(0.1)  # 稍微等待，确保鼠标移动到位
                
                # 执行点击
                scroll_amount = point.get('scroll_amount', 0)
                self.perform_click(mouse, click_type, scroll_amount)
                
                # 点击和脚本执行之间的延迟
                click_script_delay = self.click_script_delay_spin.value() / 1000.0  # 转换为秒
                if click_script_delay > 0:
                    time.sleep(click_script_delay)
                    print(f"点击和脚本执行延迟: {click_script_delay:.2f}秒")
                
                # 回放选中的脚本（只对需要加载脚本的坐标点执行）
                need_script = point.get('need_script', True)  # 默认为需要加载脚本
                if need_script:
                    selected_script = self.auto_script_combo.currentText()
                    print(f"当前选中的脚本: '{selected_script}'")
                    
                    if selected_script != "-- 不回放 --":
                        # 获取脚本路径
                        import os
                        script_path = None
                        
                        # 首先检查是否是用户手动选择的脚本（有完整路径）
                        if hasattr(self, 'script_file_paths') and selected_script in self.script_file_paths:
                            script_path = self.script_file_paths[selected_script]
                            print(f"从手动选择的路径加载脚本: {script_path}")
                        else:
                            # 否则检查默认脚本目录
                            script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
                            script_path = os.path.join(script_dir, selected_script)
                            print(f"从默认目录加载脚本: {script_path}")
                        
                        print(f"脚本路径是否存在: {os.path.exists(script_path)}")
                        
                        if script_path and os.path.exists(script_path):
                            # 临时加载脚本
                            temp_recorder = ActionRecorder()
                            if temp_recorder.load_from_file(script_path):
                                actions = temp_recorder.get_actions()
                                print(f"成功加载脚本，动作数量: {len(actions)}")
                                
                                if actions:
                                    # 创建临时播放器回放一次
                                    from playback import ActionPlayer
                                    self.current_temp_player = ActionPlayer()
                                    self.current_temp_player.play_actions(actions, speed=1.0, loop_count=1)
                                    print("开始播放脚本")
                                    # 等待回放完成
                                    while self.current_temp_player.is_active() and self.is_auto_clicking:
                                        time.sleep(0.1)
                                    print("脚本播放完成")
                else:
                    print(f"坐标 ({x}, {y}) 为纯左键点击，无需加载脚本")
                
                # 点之间延迟
                if i < len(self.coordinate_points) - 1:
                    time.sleep(delay)
            
            self.current_loop += 1
        
        # 完成
        self.is_auto_clicking = False
        self.auto_start_btn.setText("开始执行 (F5)")
        self.auto_start_btn.setStyleSheet("")
        self.auto_status_label.setText("状态：已完成")
        self.auto_status_label.setStyleSheet("color: #808080;")
        self.update_progress_signal(0, 0)
    
    def perform_click(self, mouse_controller, click_type, scroll_amount=0):
        """执行点击 - 直接从 main.py 复制"""
        button_map = {
            "单击左键": (Button.left, False),
            "单击右键": (Button.right, False),
            "单击中键": (Button.middle, False),
            "双击左键": (Button.left, True),
            "双击右键": (Button.right, True),
            "双击中键": (Button.middle, True),
        }
        
        button, is_double = button_map.get(click_type, (Button.left, False))
        
        if is_double:
            # 双击
            mouse_controller.press(button)
            mouse_controller.release(button)
            import time
            time.sleep(0.1)
            mouse_controller.press(button)
            mouse_controller.release(button)
        else:
            # 单击
            mouse_controller.press(button)
            mouse_controller.release(button)
    
    def update_progress_signal(self, current, total):
        """更新进度（从线程调用）"""
        # 使用 QTimer 在主线程中更新 UI
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, lambda: self.update_progress(current, total))
    
    def update_progress(self, current=None, total=None):
        """更新进度显示"""
        if current is None or total is None:
            # 从坐标点列表计算
            total = len(self.coordinate_points)
            current = self.current_point_index if hasattr(self, 'current_point_index') else 0
        
        if total > 0:
            self.auto_progress_label.setText(f"进度：{current}/{total}")
        else:
            self.auto_progress_label.setText("进度：0/0")
    
    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        # 停止添加模式
        if self.is_adding_mode:
            self.stop_add_mode()
        
        # 停止全局快捷键
        if hasattr(self, 'global_hotkey'):
            self.global_hotkey.stop()
        
        # 停止所有操作
        self.recorder.stop_recording()
        self.player.stop_playback()
        if self.script_editor:
            self.script_editor.close()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置全局样式
    app.setStyleSheet("""
        /* 主窗口 */
        QMainWindow {
            background-color: rgba(255, 255, 255, 220);
        }
        
        /* 头部 */
        #headerFrame {
            background-color: rgba(66, 133, 244, 200);
            border-bottom: 1px solid rgba(255, 255, 255, 100);
        }
        
        #mainTitle {
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 5px;
        }
        
        #subTitle {
            font-size: 14px;
            color: rgba(255, 255, 255, 200);
            padding: 5px;
            margin-top: 8px;
        }
        
        /* 内容框架 */
        #contentFrame {
            background-color: transparent;
        }
        
        /* 选项卡 */
        #mainTabs {
            background-color: transparent;
        }
        
        #mainTabs::pane {
            border: none;
            background-color: transparent;
        }
        
        #mainTabs QTabBar {
            spacing: 10px;
            padding: 10px;
        }
        
        #mainTabs QTabBar::tab {
            background-color: rgba(255, 255, 255, 180);
            color: #505050;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid rgba(200, 200, 200, 150);
            min-width: 120px;
        }
        
        #mainTabs QTabBar::tab:selected {
            background-color: rgba(66, 133, 244, 200);
            color: white;
        }
        
        #mainTabs QTabBar::tab:hover {
            background-color: rgba(255, 255, 255, 220);
        }
        
        /* 选项卡内容 */
        #tabContent {
            background-color: transparent;
        }
        
        /* 卡片 */
        #card {
            background-color: rgba(255, 255, 255, 220);
            border: 1px solid rgba(200, 200, 200, 150);
            border-radius: 12px;
        }
        
        #cardTitle {
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        
        /* 表单标签 */
        #formLabel {
            color: #505050;
            font-size: 14px;
            font-weight: bold;
        }
        
        /* 下拉框 */
        #comboBox {
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: white;
            font-size: 14px;
        }
        
        #comboBox:hover {
            border-color: #4285f4;
        }
        
        #comboBox::drop-down {
            width: 20px;
        }
        
        /* 数字输入框 */
        #spinBox {
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: white;
            font-size: 14px;
        }
        
        #spinBox:hover {
            border-color: #4285f4;
        }
        
        /* 按钮 */
        #normalBtn {
            background-color: rgba(240, 240, 240, 200);
            color: #303030;
            border: 1px solid #c0c0c0;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
        }
        
        #normalBtn:hover {
            background-color: rgba(220, 220, 220, 200);
        }
        
        #normalBtn:pressed {
            background-color: rgba(200, 200, 200, 200);
        }
        
        #primaryBtn {
            background-color: rgba(66, 133, 244, 200);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
        }
        
        #primaryBtn:hover {
            background-color: rgba(66, 133, 244, 230);
        }
        
        #primaryBtn:pressed {
            background-color: rgba(66, 133, 244, 255);
        }
        
        #dangerBtn {
            background-color: rgba(244, 67, 54, 180);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
        }
        
        #dangerBtn:hover {
            background-color: rgba(244, 67, 54, 200);
        }
        
        #dangerBtn:pressed {
            background-color: rgba(244, 67, 54, 220);
        }
        
        /* 标签 */
        #statusLabel {
            color: #808080;
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
        }
        
        #infoLabel {
            color: #505050;
            font-size: 14px;
            padding: 5px;
        }
        
        /* 进度条 */
        #progressBar {
            border: 1px solid #d0d0d0;
            border-radius: 12px;
            background-color: #f0f0f0;
            text-align: center;
        }
        
        #progressBar::chunk {
            background-color: #4285f4;
            border-radius: 12px;
        }
        
        /* 文本编辑 */
        #actionsText {
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 10px;
            background-color: white;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
        }
        
        /* 状态栏 */
        #statusBar {
            background-color: rgba(255, 255, 255, 200);
            color: #505050;
            font-size: 13px;
            padding: 8px;
            border-top: 1px solid rgba(200, 200, 200, 150);
        }
        
        /* 设置对话框 */
        #settingsDialog {
            background-color: white;
        }
        
        #settingsDialog QLabel {
            color: #404040;
            font-size: 14px;
            padding: 5px;
        }
        
        #settingsDialog QCheckBox {
            color: #404040;
            font-size: 14px;
            padding: 8px;
            spacing: 8px;
        }
        
        #settingsDialog QSpinBox {
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 8px;
            background-color: white;
        }
        
        #settingsDialog QPushButton {
            background-color: #e0e0e0;
            color: #303030;
            border: 1px solid #c0c0c0;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
        }
        
        #settingsDialog QPushButton:hover {
            background-color: #d0d0d0;
        }
    """)
    
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
