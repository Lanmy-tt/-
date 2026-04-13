"""
快捷键编辑器 - 允许用户自定义快捷键配置
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence


class ShortcutEditor(QDialog):
    """快捷键编辑窗口"""
    
    shortcutChanged = pyqtSignal(str, str)  # 信号：功能名称，新快捷键
    
    def __init__(self, current_shortcuts, parent=None):
        super().__init__(parent)
        self.current_shortcuts = current_shortcuts.copy()
        self.setWindowTitle("快捷键设置")
        self.setGeometry(200, 200, 600, 400)
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("自定义快捷键设置")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 说明文字
        info_label = QLabel(
            "点击\"编辑\"按钮后，按您想要的快捷键组合。\n"
            "支持的修饰键：Ctrl, Alt, Shift。\n"
            "支持的功能键：F1-F12, Enter, Space, Esc等。"
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        # 快捷键表格
        self.shortcuts_table = QTableWidget()
        self.shortcuts_table.setColumnCount(3)
        self.shortcuts_table.setHorizontalHeaderLabels(["功能名称", "当前快捷键", "操作"])
        self.shortcuts_table.horizontalHeader().setStretchLastSection(True)
        self.shortcuts_table.setAlternatingRowColors(True)
        self.shortcuts_table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.shortcuts_table)
        
        # 加载快捷键数据
        self.load_shortcuts()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("恢复默认")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.setMinimumWidth(100)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #333;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003d80;
            }
            QPushButton#reset_btn {
                background-color: #ffc107;
                color: #000;
            }
            QPushButton#reset_btn:hover {
                background-color: #ffb300;
            }
        """)
        
    def load_shortcuts(self):
        """加载快捷键数据到表格"""
        self.shortcuts_table.setRowCount(len(self.current_shortcuts))
        
        for i, (func_name, shortcut) in enumerate(self.current_shortcuts.items()):
            # 功能名称
            func_item = QTableWidgetItem(func_name)
            func_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.shortcuts_table.setItem(i, 0, func_item)
            
            # 当前快捷键
            shortcut_item = QTableWidgetItem(shortcut)
            shortcut_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.shortcuts_table.setItem(i, 1, shortcut_item)
            
            # 编辑按钮
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_shortcut(idx))
            self.shortcuts_table.setCellWidget(i, 2, edit_btn)
            
        # 调整列宽
        self.shortcuts_table.resizeColumnsToContents()
        self.shortcuts_table.setColumnWidth(0, 200)
        self.shortcuts_table.setColumnWidth(1, 150)
        self.shortcuts_table.setColumnWidth(2, 80)
        
    def edit_shortcut(self, index):
        """编辑快捷键"""
        func_name = self.shortcuts_table.item(index, 0).text()
        
        # 创建输入对话框
        input_dialog = ShortcutInputDialog(func_name, self)
        if input_dialog.exec_():
            new_shortcut = input_dialog.get_shortcut()
            
            # 检查是否与其他功能冲突
            if self.is_shortcut_conflict(new_shortcut, func_name):
                QMessageBox.warning(
                    self, "警告",
                    f"快捷键 {new_shortcut} 已被其他功能使用！"
                )
                return
                
            # 更新表格
            self.shortcuts_table.setItem(index, 1, QTableWidgetItem(new_shortcut))
            
            # 更新内部数据
            self.current_shortcuts[func_name] = new_shortcut
            
            # 发送信号
            self.shortcutChanged.emit(func_name, new_shortcut)
            
    def is_shortcut_conflict(self, shortcut, exclude_func):
        """检查快捷键是否冲突"""
        for func_name, sc in self.current_shortcuts.items():
            if func_name != exclude_func and sc == shortcut:
                return True
        return False
        
    def reset_to_defaults(self):
        """恢复默认快捷键"""
        reply = QMessageBox.question(
            self, "确认", "确定要恢复所有快捷键到默认值吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 恢复默认快捷键
            from main import DEFAULT_SHORTCUTS
            self.current_shortcuts = DEFAULT_SHORTCUTS.copy()
            self.load_shortcuts()
            
            # 发送所有快捷键重置的信号
            for func_name, shortcut in self.current_shortcuts.items():
                self.shortcutChanged.emit(func_name, shortcut)
                
    def get_shortcuts(self):
        """获取最终的快捷键配置"""
        return self.current_shortcuts.copy()
        
        
class ShortcutInputDialog(QDialog):
    """快捷键输入对话框"""
    
    def __init__(self, func_name, parent=None):
        super().__init__(parent)
        self.func_name = func_name
        self.captured_keys = []
        self.is_capturing = False
        self.setWindowTitle("录制快捷键")
        self.setGeometry(300, 300, 400, 200)
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        
        # 功能说明
        func_label = QLabel(f"为功能 \"{self.func_name}\" 设置快捷键")
        func_label.setFont(QFont("Microsoft YaHei", 11))
        main_layout.addWidget(func_label)
        
        # 输入区域
        input_layout = QVBoxLayout()
        
        self.input_label = QLabel("请按下快捷键组合...")
        self.input_label.setAlignment(Qt.AlignCenter)
        self.input_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.input_label.setStyleSheet("color: #666;")
        input_layout.addWidget(self.input_label)
        
        self.shortcut_label = QLabel("")
        self.shortcut_label.setAlignment(Qt.AlignCenter)
        self.shortcut_label.setFont(QFont("Consolas", 14, QFont.Bold))
        self.shortcut_label.setStyleSheet("color: #007bff; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        input_layout.addWidget(self.shortcut_label)
        
        main_layout.addLayout(input_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("清除")
        self.clear_btn.clicked.connect(self.clear_capture)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        self.confirm_btn = QPushButton("确定")
        self.confirm_btn.clicked.connect(self.accept)
        self.confirm_btn.setEnabled(False)
        button_layout.addWidget(self.confirm_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # 开始捕获快捷键
        self.start_capture()
        
    def start_capture(self):
        """开始捕获键盘输入"""
        self.is_capturing = True
        self.captured_keys = []
        self.input_label.setText("正在录制...")
        
    def keyPressEvent(self, event):
        """处理键盘按键事件"""
        if not self.is_capturing:
            return
            
        key = event.key()
        
        # 过滤特殊键
        if key == Qt.Key_unknown:
            return
            
        # 处理修饰键
        modifiers = []
        if event.modifiers() & Qt.ControlModifier:
            modifiers.append("Ctrl")
        if event.modifiers() & Qt.AltModifier:
            modifiers.append("Alt")
        if event.modifiers() & Qt.ShiftModifier:
            modifiers.append("Shift")
            
        # 处理普通按键
        key_text = self.key_to_text(key)
        
        if key_text:
            modifiers.append(key_text)
            
        # 构建快捷键字符串
        shortcut = "+".join(modifiers)
        
        # 更新显示
        self.shortcut_label.setText(shortcut)
        
        # 启用确认按钮
        if shortcut:
            self.confirm_btn.setEnabled(True)
            
    def key_to_text(self, key):
        """将Qt按键转换为文本"""
        key_map = {
            Qt.Key_F1: "F1", Qt.Key_F2: "F2", Qt.Key_F3: "F3",
            Qt.Key_F4: "F4", Qt.Key_F5: "F5", Qt.Key_F6: "F6",
            Qt.Key_F7: "F7", Qt.Key_F8: "F8", Qt.Key_F9: "F9",
            Qt.Key_F10: "F10", Qt.Key_F11: "F11", Qt.Key_F12: "F12",
            Qt.Key_Enter: "Enter", Qt.Key_Return: "Enter",
            Qt.Key_Space: "Space", Qt.Key_Escape: "Esc",
            Qt.Key_Tab: "Tab", Qt.Key_Backspace: "Backspace",
            Qt.Key_Delete: "Delete", Qt.Key_Home: "Home",
            Qt.Key_End: "End", Qt.Key_PageUp: "PageUp",
            Qt.Key_PageDown: "PageDown", Qt.Key_Up: "Up",
            Qt.Key_Down: "Down", Qt.Key_Left: "Left",
            Qt.Key_Right: "Right"
        }
        
        if key in key_map:
            return key_map[key]
        elif 0x20 <= key <= 0xFF:
            char = chr(key)
            return char.upper()
        else:
            return ""
            
    def clear_capture(self):
        """清除捕获"""
        self.captured_keys = []
        self.shortcut_label.setText("")
        self.confirm_btn.setEnabled(False)
        self.start_capture()
        
    def get_shortcut(self):
        """获取录制的快捷键"""
        return self.shortcut_label.text()
