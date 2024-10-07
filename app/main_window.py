import os

from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QStyle, QSizePolicy, QTableView
from app.settings_manager import SettingsManager
from app.components.save_directory.save_directory_controller import SaveDirectoryController


class UIMainWindow(object):
    def setup_ui(self, MainWindow):
        # Settings Manager
        self.settings_manager = SettingsManager()

        # App Name and Size
        MainWindow.setWindowTitle('yt_dlp gui')
        length, height = self.settings_manager.get_setting('window_size')
        MainWindow.resize(length, height)

        # Main layout for the central widget
        self.central_widget = QtWidgets.QWidget(parent=MainWindow)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Config Section
        self.layout_config_section = QtWidgets.QHBoxLayout()

        # Config Section - Download Format Layout
        self.layout_download_format = QtWidgets.QVBoxLayout()
        self.label_download_format = QtWidgets.QLabel('Default Format:')
        self.combo_box_download_formats = QtWidgets.QComboBox()
        self.downlaod_formats = self.settings_manager.get_setting('download_formats')
        self.combo_box_download_formats.addItems(self.downlaod_formats['audio'] + self.downlaod_formats['video'])
        self.combo_box_download_formats.setCurrentIndex(self.combo_box_download_formats.findText(self.settings_manager.get_setting('default_download_format')))
        self.layout_download_format.addWidget(self.label_download_format)
        self.layout_download_format.addWidget(self.combo_box_download_formats)

        # Config Section - Save Directory Layout
        self.layout_save_directory = QtWidgets.QVBoxLayout()
        self.layout_save_directory_header = QtWidgets.QHBoxLayout()
        self.button_directory_selector = QtWidgets.QPushButton()
        self.button_directory_selector.setMaximumSize(QtCore.QSize(20, 20))
        self.button_directory_selector_icon = QApplication.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogOpenButton)
        self.button_directory_selector.setIcon(self.button_directory_selector_icon)
        self.button_directory_selector.setFlat(True)
        self.label_save_directory = QtWidgets.QLabel('Save Directory:')
        self.radio_button_open_save_directory_on_close = QtWidgets.QRadioButton('Open On Close')
        self.radio_button_open_save_directory_on_close.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.radio_button_open_save_directory_on_close.setChecked(self.settings_manager.get_setting('open_save_directory_on_close', bool))
        self.layout_save_directory_header.addWidget(self.button_directory_selector)
        self.layout_save_directory_header.addWidget(self.label_save_directory)
        self.layout_save_directory_header.addWidget(self.radio_button_open_save_directory_on_close)
        self.line_edit_save_directory_display = QtWidgets.QLineEdit()
        self.line_edit_save_directory_display.setReadOnly(True)
        self.line_edit_save_directory_display.setText(self.settings_manager.get_setting('save_directory'))
        self.layout_save_directory.addLayout(self.layout_save_directory_header)
        self.layout_save_directory.addWidget(self.line_edit_save_directory_display)

        # Config Section - Render
        self.layout_config_section.addLayout(self.layout_download_format)
        self.layout_config_section.addLayout(self.layout_save_directory)

        # Video Section
        self.layout_video_section = QtWidgets.QVBoxLayout()

        # Video Section - Buttons
        self.layout_video_section_buttons = QtWidgets.QHBoxLayout()
        self.button_add_video = QtWidgets.QPushButton('Add Video')
        self.button_remove_videos = QtWidgets.QPushButton('Remove Video(s)')
        self.button_download_videos = QtWidgets.QPushButton("Download")
        self.layout_video_section_buttons.addWidget(self.button_add_video)
        self.layout_video_section_buttons.addWidget(self.button_remove_videos)
        self.layout_video_section_buttons.addWidget(self.button_download_videos)

        # Video Section - Video Table Details
        self.table_view_video_details = QtWidgets.QTableView()
        self.table_view_video_details.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table_view_video_details.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view_video_details.horizontalHeader().setSectionsClickable(False)
        self.table_view_video_details.horizontalHeader().setHighlightSections(False)

        # Video Section - Render
        self.layout_video_section.addLayout(self.layout_video_section_buttons)
        self.layout_video_section.addWidget(self.table_view_video_details)

        # Download Status Section
        self.layout_download_status_section = QtWidgets.QVBoxLayout()
        self.label_download_status = QtWidgets.QLabel('Downloading...')
        self.label_download_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar_download_status_percentage = QtWidgets.QProgressBar()
        self.label_download_status.hide()
        self.progress_bar_download_status_percentage.hide()
        self.button_clear_downloads = QtWidgets.QPushButton('Clear Table')
        self.button_clear_downloads.hide()

        # Download Status - Render
        self.layout_download_status_section.addWidget(self.label_download_status)
        self.layout_download_status_section.addWidget(self.progress_bar_download_status_percentage)
        self.layout_download_status_section.addWidget(self.button_clear_downloads)

        # Central Widget - Render
        self.main_layout.addLayout(self.layout_config_section)
        self.main_layout.addLayout(self.layout_video_section)
        self.main_layout.addLayout(self.layout_download_status_section)

        # Components
        self.save_directory_controller = SaveDirectoryController(window=self)

        # Signals and Slots Connections
        self.connect_signals_slots()

        # Tool Tips
        self.set_tool_tips()

        # App Initialization
        MainWindow.setCentralWidget(self.central_widget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # Signals and Slots
    def connect_signals_slots(self):
        self.button_directory_selector.clicked.connect(self.save_directory_controller.save_directory_dialog)

    # Tool Tips
    def set_tool_tips(self):
        self.combo_box_download_formats.setToolTip('Default download format for added videos')
        self.button_directory_selector.setToolTip('Select a directory to store downloaded files')
        self.radio_button_open_save_directory_on_close.setToolTip(
            'Open the save directory of downloaded videos on app closure')
        self.button_add_video.setToolTip('Add video to download, provided a url, save name, and format')
        self.button_remove_videos.setToolTip('Remove currently selected videos')

    # Save App Settings
    def persist_app_settings(self):
        self.settings_manager.set_setting(key='window_size', value=(self.width(), self.height()))
        self.settings_manager.set_setting(key='default_download_format', value=self.combo_box_download_formats.currentText())
        self.settings_manager.set_setting(key='save_directory', value=self.line_edit_save_directory_display.text())
        self.settings_manager.set_setting(key='open_save_directory_on_close', value=self.radio_button_open_save_directory_on_close.isChecked())

    # App Exit
    def open_save_directory_on_app_close(self):
        if self.radio_button_open_save_directory_on_close.isChecked():
            os.startfile(self.line_edit_save_directory_display.text())

    def closeEvent(self, event):
        self.persist_app_settings()
