from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSizePolicy
from app.util.input_validations import input_contains_regex, input_is_empty
from app.settings_manager import SettingsManager


class AddVideoDialog(QDialog):
    def __init__(self, window):
        super().__init__()
        self.__window = window
        self.__settings_manager = SettingsManager()
        self.__download_formats = self.__settings_manager.get_setting('download_formats')
        self.__special_chars = r'[\\/<>\*\?:|""]'
        self.setWindowTitle("Add Video")
        self.resize(700, 250)
        self.setFixedHeight(250)

        self.dialog_layout = QVBoxLayout()

        self.label_video_url = QLabel('Enter Youtube Video URL:')
        self.line_edit_video_url = QLineEdit()
        self.label_save_name = QLabel('Enter Save Name:')
        self.line_edit_save_name = QLineEdit()
        self.label_line_edit_error = QLabel('Save name must not include:\n/ \\ < > * ? : "" |')
        self.label_line_edit_error.setStyleSheet('color: red;')
        self.label_line_edit_error.hide()

        self.download_format_layout = QHBoxLayout()
        self.label_download_format = QLabel('Download Format:')
        self.label_download_format.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.combo_box_download_format = QComboBox()
        self.combo_box_download_format.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.combo_box_download_format.addItems(self.__download_formats['audio'] + self.__download_formats['video'])
        self.combo_box_download_format.setCurrentIndex(self.__window.combo_box_download_formats.currentIndex())
        self.download_format_layout.addWidget(self.label_download_format)
        self.download_format_layout.addWidget(self.combo_box_download_format)
        self.download_format_layout.addStretch(1)

        self.confimation_layout = QHBoxLayout()
        self.ok_button = QPushButton('Ok')
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        self.confimation_layout.addWidget(self.ok_button)
        self.confimation_layout.addWidget(self.cancel_button)

        self.dialog_layout.addWidget(self.label_video_url)
        self.dialog_layout.addWidget(self.line_edit_video_url)
        self.dialog_layout.addWidget(self.label_save_name)
        self.dialog_layout.addWidget(self.line_edit_save_name)
        self.dialog_layout.addWidget(self.label_line_edit_error)
        self.dialog_layout.addLayout(self.download_format_layout)
        self.dialog_layout.addLayout(self.confimation_layout)

        self.ok_button.setEnabled(False)
        self.line_edit_video_url.textChanged.connect(self.verify_feilds)
        self.line_edit_save_name.textChanged.connect(self.verify_feilds)

        self.setLayout(self.dialog_layout)

    def get_text(self):
        if self.exec() == QDialog.DialogCode.Accepted:
            youtube_url = self.line_edit_video_url.text()
            save_name = self.line_edit_save_name.text()
            download_format = self.combo_box_download_format.currentText()
            return youtube_url, save_name, download_format
        else:
            return None, None, None

    def verify_feilds(self):
        invalid_save_name = input_contains_regex(input_string=self.line_edit_save_name.text(), regex=self.__special_chars)
        missing_input = (input_is_empty(input_string=self.line_edit_video_url.text())
                         or input_is_empty(input_string=self.line_edit_save_name.text()))

        if invalid_save_name:
            self.label_line_edit_error.show()
        else:
            self.label_line_edit_error.hide()

        if missing_input or invalid_save_name:
            self.ok_button.setEnabled(False)
        else:
            self.ok_button.setEnabled(True)