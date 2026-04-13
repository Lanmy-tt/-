#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试定点功能的简单脚本
"""

import sys
import time
import random
import string
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.mouse = Controller()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("定点功能测试")
        self.setGeometry(300, 300, 300, 200)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("准备开始测试")
        layout.addWidget(self.status_label)
        
        self.test_btn = QPushButton("开始测试")
        self.test_btn.clicked.connect(self.start_test)
        layout.addWidget(self.test_btn)
        
        self.setLayout(layout)
        
        # 启动键盘监听器
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()
        
    def on_press(self, key):
        """键盘按键监听"""
        if key == Key.esc:
            self.status_label.setText("测试已取消")
            self.listener.stop()
            return False
            
        if key == Key.f10:
            self.status_label.setText("开始播放")
            self.test_playback()
            
    def start_test(self):
        """开始测试"""
        from pynput.keyboard import Controller as KeyboardController
        self.keyboard = KeyboardController()
        
        # 测试 1: 打开程序（模拟）
        self.status_label.setText("测试中...请打开程序并点击开始添加")
        
    def test_playback(self):
        """测试播放"""
        for i in range(3):
            # 随机位置
            x = random.randint(100, 800)
            y = random.randint(100, 500)
            
            # 移动到位置
            self.mouse.position = (x, y)
            time.sleep(0.1)
            
            # 左键点击
            self.perform_click(self.mouse, "单击左键")
            
            self.status_label.setText(f"已执行点击：({x}, {y})")
            time.sleep(0.5)
            
        self.status_label.setText("播放完成！")
        
    def perform_click(self, mouse_controller, click_type):
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
            time.sleep(0.1)
            mouse_controller.press(button)
            mouse_controller.release(button)
        else:
            # 单击
            mouse_controller.press(button)
            mouse_controller.release(button)
            
    def closeEvent(self, event):
        """窗口关闭时停止监听器"""
        if hasattr(self, 'listener'):
            self.listener.stop()
        event.accept()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
