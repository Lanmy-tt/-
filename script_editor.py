"""
脚本编辑器 - 编辑录制的动作脚本
"""
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QTextEdit, QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5.QtWidgets import QMessageBox, QGroupBox, QLabel, QDoubleSpinBox
from PyQt5.QtCore import Qt


class ScriptEditor(QWidget):
    """脚本编辑器窗口类"""
    
    def __init__(self, recorder, parent=None):
        super().__init__(parent)
        self.recorder = recorder
        self.current_file = None
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 文件信息
        info_group = QGroupBox("文件信息")
        info_layout = QVBoxLayout()
        
        self.file_label = QLabel("当前文件：无")
        info_layout.addWidget(self.file_label)
        
        self.action_count_label = QLabel("动作数量：0")
        info_layout.addWidget(self.action_count_label)
        
        self.duration_label = QLabel("总时长：0 秒")
        info_layout.addWidget(self.duration_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 动作表格
        table_group = QGroupBox("动作列表")
        table_layout = QVBoxLayout()
        
        self.action_table = QTableWidget()
        self.action_table.setColumnCount(6)
        self.action_table.setHorizontalHeaderLabels(
            ["序号", "类型", "时间 (秒)", "X", "Y", "详细信息"]
        )
        self.action_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.action_table)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("加载文件")
        self.load_btn.clicked.connect(self.load_file)
        btn_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("保存文件")
        self.save_btn.clicked.connect(self.save_file)
        btn_layout.addWidget(self.save_btn)
        
        self.add_btn = QPushButton("添加动作")
        self.add_btn.clicked.connect(self.add_action)
        btn_layout.addWidget(self.add_btn)
        
        self.delete_btn = QPushButton("删除选中")
        self.delete_btn.clicked.connect(self.delete_action)
        btn_layout.addWidget(self.delete_btn)
        
        self.clear_btn = QPushButton("清空全部")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        
        # 编辑说明
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMaximumHeight(100)
        help_text.setText(
            "使用说明：\n"
            "1. 双击表格单元格可以编辑内容\n"
            "2. 类型支持：mouse_move, mouse_click, key_press, key_release\n"
            "3. 时间单位为秒，从录制开始计算\n"
            "4. 鼠标点击的详细信息格式：button=left,pressed=True\n"
            "5. 键盘操作的详细信息格式：key=a"
        )
        layout.addWidget(help_text)
    
    def load_file(self):
        """加载文件"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "打开录制文件", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.recorder.actions = data.get('actions', [])
                self.current_file = filename
                self.file_label.setText(f"当前文件：{filename}")
                self.refresh_table()
                QMessageBox.information(self, "成功", "文件加载成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载文件失败：{str(e)}")
    
    def save_file(self):
        """保存文件"""
        if not self.recorder.actions:
            QMessageBox.warning(self, "警告", "没有可保存的动作！")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存录制文件", self.current_file or "recording.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            if self.recorder.save_to_file(filename):
                self.current_file = filename
                self.file_label.setText(f"当前文件：{filename}")
                QMessageBox.information(self, "成功", "文件保存成功！")
            else:
                QMessageBox.critical(self, "错误", "保存文件失败！")
    
    def refresh_table(self):
        """刷新表格显示"""
        actions = self.recorder.get_actions()
        self.action_table.setRowCount(len(actions))
        
        for i, action in enumerate(actions):
            # 序号
            self.action_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            
            # 类型
            action_type = action.get('type', 'unknown')
            self.action_table.setItem(i, 1, QTableWidgetItem(action_type))
            
            # 时间
            time_val = action.get('time', 0)
            self.action_table.setItem(i, 2, QTableWidgetItem(f"{time_val:.3f}"))
            
            # X 坐标
            x = action.get('x', '')
            self.action_table.setItem(i, 3, QTableWidgetItem(str(x) if x else ''))
            
            # Y 坐标
            y = action.get('y', '')
            self.action_table.setItem(i, 4, QTableWidgetItem(str(y) if y else ''))
            
            # 详细信息
            detail = self.get_action_detail(action)
            self.action_table.setItem(i, 5, QTableWidgetItem(detail))
        
        # 更新统计信息
        self.action_count_label.setText(f"动作数量：{len(actions)}")
        if actions:
            duration = actions[-1].get('time', 0)
            self.duration_label.setText(f"总时长：{duration:.2f}秒")
    
    def get_action_detail(self, action):
        """获取动作详细信息"""
        action_type = action.get('type', '')
        
        if action_type == 'mouse_click':
            button = action.get('button', '')
            pressed = action.get('pressed', True)
            return f"button={button},pressed={pressed}"
        
        elif action_type in ['key_press', 'key_release']:
            key = action.get('key', '')
            return f"key={key}"
        
        elif action_type == 'mouse_scroll':
            dx = action.get('dx', 0)
            dy = action.get('dy', 0)
            return f"dx={dx},dy={dy}"
        
        return ''
    
    def add_action(self):
        """添加动作"""
        # 添加一个默认的鼠标移动动作
        new_action = {
            'type': 'mouse_move',
            'x': 0,
            'y': 0,
            'time': 0.0
        }
        self.recorder.actions.append(new_action)
        self.refresh_table()
    
    def delete_action(self):
        """删除选中的动作"""
        selected_rows = set()
        for index in self.action_table.selectionModel().selectedRows():
            selected_rows.add(index.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的动作！")
            return
        
        # 从后往前删除，避免索引问题
        actions = self.recorder.get_actions()
        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(actions):
                actions.pop(row)
        
        self.refresh_table()
    
    def clear_all(self):
        """清空所有动作"""
        if self.recorder.get_actions():
            reply = QMessageBox.question(
                self, "确认", "确定要清空所有动作吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.recorder.clear_actions()
                self.refresh_table()
    
    def get_current_actions(self):
        """获取当前编辑的动作"""
        return self.recorder.get_actions()
