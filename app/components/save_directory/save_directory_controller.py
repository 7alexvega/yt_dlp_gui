import os
from PyQt6.QtWidgets import QFileDialog


class SaveDirectoryController:
    def __init__(self, window):
        self.__window = window
        self.__line_edit_save_directory_display = self.__window.line_edit_save_directory_display

    # noinspection PyTypeChecker
    def save_directory_dialog(self):
        save_dir = QFileDialog.getExistingDirectory(self.__window,
                                                    'Select save directory',
                                                    self.__line_edit_save_directory_display.text(),
                                                    QFileDialog.Option.ShowDirsOnly |
                                                    QFileDialog.Option.DontResolveSymlinks)
        if save_dir:
            save_dir = os.path.normpath(save_dir)
            self.__line_edit_save_directory_display.setText(save_dir)
