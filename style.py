"""
样式表 - 银灰动漫少女主题
基于动漫头像配色的界面风格
配色灵感：银灰色长发、淡蓝眼睛、白皙肤色、深色服装
"""

# 主窗口样式
MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #f5f5f7;
}
"""

# 选项卡样式
TAB_STYLE = """
QTabWidget::pane {
    border: 2px solid #d0d0d5;
    border-radius: 12px;
    background-color: #ffffff;
}
QTabBar::tab {
    background-color: #e8e8ed;
    color: #5a6c7d;
    padding: 12px 25px;
    margin: 3px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 14px;
    border: 2px solid #c0c0c8;
}
QTabBar::tab:selected {
    background-color: #7a8fa3;
    color: #ffffff;
    border: 2px solid #7a8fa3;
}
QTabBar::tab:hover {
    background-color: #8fa3b8;
    border: 2px solid #8fa3b8;
}
"""

# 通用组件样式
COMMON_STYLE = """
QGroupBox {
    font-weight: bold;
    font-size: 16px;
    color: #5a6c7d;
    border: 2px solid #d0d0d5;
    border-radius: 12px;
    margin-top: 15px;
    padding-top: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 8px 20px;
    background-color: #7a8fa3;
    color: #ffffff;
    border-radius: 8px;
    font-weight: bold;
}
QLabel {
    color: #5a6c7d;
    font-size: 14px;
    font-weight: bold;
}
QComboBox {
    border: 2px solid #d0d0d5;
    border-radius: 8px;
    padding: 10px;
    background-color: #ffffff;
    color: #5a6c7d;
    font-weight: bold;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QSpinBox {
    border: 2px solid #d0d0d5;
    border-radius: 8px;
    padding: 10px;
    background-color: #ffffff;
    color: #5a6c7d;
    font-weight: bold;
}
QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7a8fa3, stop:1 #5a6c7d);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 18px;
    font-size: 18px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #8fa3b8, stop:1 #6d7f91);
}
QPushButton:pressed {
    background-color: #5a6c7d;
}
QPushButton:disabled {
    background-color: #d0d0d5;
    color: #a0a0a8;
}
"""

# 状态栏样式
STATUS_BAR_STYLE = """
QStatusBar {
    background-color: #7a8fa3;
    color: #ffffff;
    font-weight: bold;
    font-size: 13px;
    padding: 8px;
}
"""

# 标题栏样式
TITLE_BAR_STYLE = """
QFrame {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #a8b8c8, stop:0.5 #7a8fa3, stop:1 #a8b8c8);
    border-radius: 15px;
    padding: 15px;
}
QLabel#titleLabel {
    color: #ffffff;
    font-size: 28px;
    font-weight: bold;
    padding: 10px;
}
"""

# 进度条样式
PROGRESS_BAR_STYLE = """
QProgressBar {
    border: 2px solid #d0d0d5;
    border-radius: 10px;
    background-color: #e8e8ed;
    color: #5a6c7d;
    font-weight: bold;
    text-align: center;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7a8fa3, stop:1 #8fa3b8);
    border-radius: 8px;
}
"""

# 文本编辑框样式
TEXT_EDIT_STYLE = """
QTextEdit {
    border: 2px solid #d0d0d5;
    border-radius: 10px;
    background-color: #fafafc;
    color: #5a6c7d;
    font-size: 13px;
    padding: 10px;
}
QTextEdit:focus {
    border: 2px solid #7a8fa3;
}
"""

# 状态标签样式 (运行中)
STATUS_RUNNING_STYLE = """
QLabel {
    background-color: #e8f0f5;
    color: #4a9f6f;
    font-size: 15px;
    font-weight: bold;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #c0d0d8;
}
"""

# 状态标签样式 (已停止)
STATUS_STOPPED_STYLE = """
QLabel {
    background-color: #f0f0f5;
    color: #888890;
    font-size: 15px;
    font-weight: bold;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #d0d0d8;
}
"""

# 状态标签样式 (普通信息)
STATUS_INFO_STYLE = """
QLabel {
    background-color: #e8f0f5;
    color: #5a6c7d;
    font-size: 15px;
    font-weight: bold;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #c0d0d8;
}
"""

# 提示标签样式
TIP_LABEL_STYLE = """
QLabel {
    background-color: #f5f8fc;
    color: #6d7f91;
    font-size: 13px;
    font-weight: bold;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #d0d8e0;
}
"""

# 配色说明
"""
银灰动漫少女主题配色方案:

主色调:
├─ 背景色：#f5f5f7 (浅灰白) - 白皙肤色
├─ 组件色：#ffffff / #fafafc (白色/浅灰白) - 纯洁感
├─ 边框色：#d0d0d5 / #c0c0c8 (浅灰色) - 银灰发色
├─ 主色调：#7a8fa3 (灰蓝色) - 眼睛颜色
├─ 辅助色：#5a6c7d (深灰蓝) - 深色服装
├─ 强调色：#8fa3b8 / #a8b8c8 (浅蓝灰) - 头发高光
└─ 文字色：#5a6c7d (深灰蓝) - 柔和对比

特点:
- 柔和的灰蓝色调
- 低饱和度配色
- 清新优雅
- 二次元少女风格
- 视觉舒适不刺眼
"""
