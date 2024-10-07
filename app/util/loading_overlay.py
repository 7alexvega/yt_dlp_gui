from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter


class LoadingOverlay(QWidget):
    def __init__(self, window=None):
        super().__init__(window)
        self.setParent(window)

        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 127);
            color: white;
            font-size: 30px;
            font-weight: bold;
        """)

        self.loading_label = QLabel("Gathering Video Information...", self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.loading_label)

        self.hide()

    def showEvent(self, event):
        self.setGeometry(self.parent().rect())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 127))