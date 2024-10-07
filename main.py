import sys
from app.main_window import UIMainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QStyleFactory


class MainWindow(QMainWindow, UIMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setup_ui(self)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    app.aboutToQuit.connect(window.open_save_directory_on_app_close)
    app.exec()