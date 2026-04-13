#!/usr/bin/env python3
"""
简单测试程序，检查滚动操作是否正常
"""

import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from pynput.mouse import Controller

class SimpleScrollTest(QWidget):
    def __init__(self):
        super().__init__()
        self.mouse = Controller()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("滚动操作简单测试")
        self.setGeometry(300, 300, 300, 100)
        
        layout = QVBoxLayout()
        
        self.result_label = QLabel("测试滚动操作")
        layout.addWidget(self.result_label)
        
        self.btn_up = QPushButton("向上滚动")
        self.btn_up.clicked.connect(self.test_scroll_up)
        layout.addWidget(self.btn_up)
        
        self.btn_down = QPushButton("向下滚动")
        self.btn_down.clicked.connect(self.test_scroll_down)
        layout.addWidget(self.btn_down)
        
        self.setLayout(layout)
        
    def test_scroll_up(self):
        """测试向上滚动"""
        try:
            print("测试向上滚动...")
            pos = self.mouse.position
            print(f"当前位置: {pos}")
            
            self.mouse.scroll(0, 1)
            time.sleep(0.5)
            
            self.result_label.setText(f"向上滚动成功\n位置: {self.mouse.position}")
            print(f"向上滚动后的位置: {self.mouse.position}")
            
        except Exception as e:
            self.result_label.setText(f"向上滚动失败: {e}")
            print(f"向上滚动失败: {e}")
            
    def test_scroll_down(self):
        """测试向下滚动"""
        try:
            print("测试向下滚动...")
            pos = self.mouse.position
            print(f"当前位置: {pos}")
            
            self.mouse.scroll(0, -1)
            time.sleep(0.5)
            
            self.result_label.setText(f"向下滚动成功\n位置: {self.mouse.position}")
            print(f"向下滚动后的位置: {self.mouse.position}")
            
        except Exception as e:
            self.result_label.setText(f"向下滚动失败: {e}")
            print(f"向下滚动失败: {e}")
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleScrollTest()
    window.show()
    
    print("测试窗口创建完成")
    print("请点击按钮测试滚动操作")
    
    sys.exit(app.exec_())
