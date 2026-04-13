#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试定点功能修复后的脚本来验证程序是否正常工作
"""

import sys
import time
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.mouse = Controller()
        self.test_points = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("定点功能修复测试")
        self.setGeometry(300, 300, 400, 200)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("程序已准备好，现在可以打开主程序测试定点功能")
        layout.addWidget(self.status_label)
        
        self.instructions_label = QLabel("使用说明：\n1. 点击开始添加\n2. 按 Ctrl 键添加需加载脚本的点\n3. 按 Alt 键添加纯左键点击的点\n4. 点击开始执行，观察是否循环执行所有点")
        self.instructions_label.setWordWrap(True)
        layout.addWidget(self.instructions_label)
        
        self.test_btn = QPushButton("开始测试操作")
        self.test_btn.clicked.connect(self.perform_test_operations)
        layout.addWidget(self.test_btn)
        
        self.setLayout(layout)
        
    def perform_test_operations(self):
        """执行一些常见的鼠标操作来准备测试场景"""
        from pynput.keyboard import Controller as KeyboardController
        self.keyboard = KeyboardController()
        
        self.status_label.setText("正在执行一些鼠标操作来准备测试场景...")
        
        # 模拟用户可能的操作
        positions = [
            (random.randint(100, 300), random.randint(100, 300)),  #