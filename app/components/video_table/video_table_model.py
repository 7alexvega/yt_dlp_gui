from PyQt6.QtCore import Qt, QModelIndex, QAbstractTableModel, pyqtSignal
from PyQt6.QtGui import QColor
from app.util.input_validations import input_contains_regex, input_is_empty


class VideoTableModel(QAbstractTableModel):
    video_table_buttons_state = pyqtSignal(bool)

    def __init__(self, data: list[any], headers: list[str]):
        super().__init__()
        self.__data = data
        self.__headers = headers
        self.__status_index = self.__headers.index('Status')
        self.__save_name_index = self.__headers.index('Save Name')
        self.__download_format_index = self.__headers.index('Format')
        self.__special_chars = r'[\\/<>\*\?:|""]'
        self.__video_status_colors = {"Pending": QColor(90, 90, 90),
                                      "Downloading": QColor(150, 150, 120),
                                      "Downloaded": QColor(0, 100, 0),
                                      "Error": QColor(105, 0, 0)}

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.__headers[section]
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self.__data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.__headers)

    def data (self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            return self.__data[row][column]

        elif role == Qt.ItemDataRole.BackgroundRole:
            status = self.__data[row][self.__status_index]
            return self.__video_status_colors[status]

        return None

    def get_videos(self):
        return self.__data

    def get_video_details(self, video_index: int):
        video_title = self.__data[video_index][self.__headers.index('Title')]
        channel_name = self.__data[video_index][self.__headers.index('Channel')]
        video_length = self.__data[video_index][self.__headers.index('Length')]
        return video_title, channel_name, video_length

    # Check for an existing entry with the attempted save name and download format
    def duplicate_savename_and_download_format(self, save_name: str, download_format: str):
        for row in range(len(self.__data)):
            existing_save_name = self.__data[row][self.__save_name_index]
            existing_download_format = self.__data[row][self.__download_format_index]
            if existing_save_name == save_name and existing_download_format == download_format:
                return True

        return False

    # Check for when adding existing youtube url with the same download format
    def duplicate_download_format(self, download_format: str, row_index: int):
        return self.__data[row_index][self.__download_format_index] == download_format

    # Check for an existing entry with the attempted youtube url
    # - used with get_video_details to bypass api data retrieval
    def url_exists(self, youtube_url: str):
        for row in range(len(self.__data)):
            existing_url = self.__data[row][0]
            if existing_url == youtube_url:
                return True, row

        return False, 0

    def video_table_is_empty(self):
        return len(self.__data) == 0

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            row = index.row()
            column = index.column()

            if column == self.__save_name_index:
                valid_save_name = not input_contains_regex(input_string=value, regex=self.__special_chars)
                empty_save_name = input_is_empty(input_string=value)

                if (self.__data[row][column] != value
                    and valid_save_name
                    and not empty_save_name
                    and not self.duplicate_savename_and_download_format(save_name=value, download_format=self.__data[row][-2])):

                    self.__data[row][column] = value
                    self.dataChanged.emit(index, index, [role])
                    return True
                else:
                    return False

        return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        column = index.column()
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        if column in [self.__save_name_index]:
            return flags | Qt.ItemFlag.ItemIsEditable

        return flags

    def insert_video_entry(self, youtube_url: str, video_title: str, channel_name: str, save_name: str, video_length: str, download_format: str):
        self.beginInsertRows(QModelIndex(), len(self.__data), len(self.__data))
        self.__data.append([youtube_url, video_title, channel_name, save_name, video_length, download_format, 'Pending'])
        self.endInsertRows()
        self.video_table_buttons_state.emit(self.video_table_is_empty())

    def remove_video_entries(self, selected_rows):
        for row_index in sorted(selected_rows, reverse=True):
            self.beginRemoveRows(QModelIndex(), row_index, row_index)
            self.__data.pop(row_index)
            self.endRemoveRows()

        self.video_table_buttons_state.emit(self.video_table_is_empty())

    def update_video_entry_status(self, video_index: int, status: str):
        self.__data[video_index][self.__status_index] = status
        first_column_index = self.index(video_index, 0)
        last_column_index = self.index(video_index, self.columnCount() - 1)
        self.dataChanged.emit(first_column_index, last_column_index)

    def clear_table(self):
        self.remove_video_entries(range(len(self.__data)))