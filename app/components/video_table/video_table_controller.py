from collections import deque
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QHeaderView, QMessageBox
from app.components.video_table.add_video_dialog import AddVideoDialog
from app.lib.yt_dlp.yt_dlp_thread_manager import YTDLPThreadManager


class VideoTableController:
    def __init__(self, window):
        self.__window = window

        # Video Table
        self.__video_table_model = self.__window.video_table_model
        self.__table_selection_model = self.__window.table_view_video_details.selectionModel()
        self.__video_table_model.video_table_buttons_state.connect(self.video_buttons_state)

        # Widgets
        self.__save_directory_line_edit = self.__window.line_edit_save_directory_display
        self.__download_format_combo_box = self.__window.combo_box_download_formats
        self.__add_video_button = self.__window.button_add_video
        self.__download_button = self.__window.button_download_videos
        self.__remove_button = self.__window.button_remove_videos
        self.__clear_downloads_button = self.__window.button_clear_downloads
        self.__progress_bar_download_percentage = self.__window.progress_bar_download_status_percentage
        self.__label_download_progress = self.__window.label_download_status
        self.__overlay = self.__window.loading_overlay

        self.__download_queue = deque()
        self.__processing_download_queue = False
        self.__total_videos = 0
        self.__yt_dlp_client = YTDLPThreadManager()
        self.__yt_dlp_client.video_download_response.connect(self.update_video_table_status)
        self.__yt_dlp_client.video_details_response.connect(self.add_video_thread_completion)
        self.__yt_dlp_client.download_progress.connect(self.update_progress_bar_download)

    def setup_table_headers_layout(self, table_view):
        header = table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        table_view.setColumnHidden(0, True)

    def video_buttons_state(self):
        empty = self.__video_table_model.video_table_is_empty()
        self.__download_button.setEnabled(not empty)
        self.__remove_button.setEnabled(not empty)

    def remove_selected_video_entries(self):
        selected_indices = self.__table_selection_model.selectedRows()
        selected_rows = [index.row() for index in selected_indices]
        self.__video_table_model.remove_video_entries(selected_rows)

    def open_add_video_dialog(self):
        add_video_dialog = AddVideoDialog(window=self.__window)
        add_video_dialog.move(self.__window.x() + (self.__window.width() - add_video_dialog.width()) // 2,
                              self.__window.y() + (self.__window.height() - add_video_dialog.height()) // 2)
        youtube_url, save_name, download_format = add_video_dialog.get_text()

        if youtube_url and save_name:
            self.add_video_to_table(video_url=youtube_url,
                                    save_name=save_name,
                                    download_format=download_format)

    def add_video_to_table(self, video_url: str, save_name: str, download_format: str):
        if self.add_video_to_table_pre_validation(video_url=video_url,
                                                  save_name=save_name,
                                                  download_format=download_format):
            return

        self.__overlay.resize(self.__window.size())
        self.__overlay.show()

        QTimer.singleShot(0, lambda: self.__start_video_details_thread(video_url, save_name, download_format))

    def __start_video_details_thread(self, video_url: str, save_name: str, download_format: str):
        self.__yt_dlp_client.start_get_details_thread(youtube_url=video_url,
                                                      save_name=save_name,
                                                      download_format=download_format)

    def add_video_thread_completion(self, response_code, video_details):
        self.__overlay.hide()

        # Invalid youtube url
        if response_code == -1:
            youtube_url, error = video_details
            QMessageBox.warning(self.__window, 'Invalid URL', f'The url `{youtube_url}` is invalid.\n\n{error}')

        # Add video to table
        else:
            video_title, channel_name, video_length, save_name, download_format, youtube_url = video_details
            self.__video_table_model.insert_video_entry(youtube_url=youtube_url,
                                                        video_title=video_title,
                                                        channel_name=channel_name,
                                                        save_name=save_name,
                                                        video_length=video_length,
                                                        download_format=download_format)

    def add_video_to_table_pre_validation(self, video_url: str, save_name: str, download_format: str):
        # Duplicate save name and download format
        if self.__video_table_model.duplicate_savename_and_download_format(save_name=save_name, download_format=download_format):
            QMessageBox.warning(self.__window, 'Duplicate Entry', f'An entry with the save name: `{save_name}` and format: `{download_format}` already exists.')
            return True

        url_exists_in_table, video_index = self.__video_table_model.url_exists(youtube_url=video_url)

        # Url exists bypass api data retrieval
        if url_exists_in_table:

            # Duplicate url and download format
            if self.__video_table_model.duplicate_download_format(row_index=video_index, download_format=download_format):
                QMessageBox.warning(self.__window, 'Duplicate Entry', f'The entry: `{video_url}`, `{download_format}` already exists.')
                return True

            # Duplicate url different download format
            else:
                video_title, channel_name, video_length = self.__video_table_model.get_video_details(video_index=video_index)
                self.__video_table_model.insert_video_entry(youtube_url=video_url,
                                                            video_title=video_title,
                                                            channel_name=channel_name,
                                                            save_name=save_name,
                                                            video_length=video_length,
                                                            download_format=download_format)
                return True

        return False

    def download_videos(self):
        self.__download_queue = deque(enumerate(self.__video_table_model.get_videos()))
        self.__total_videos = len(self.__download_queue)
        self.__label_download_progress.setText(f'Queued {self.__total_videos} videos')
        self.__label_download_progress.show()

        if not self.__processing_download_queue:
            self.__progress_bar_download_percentage.show()
            QTimer.singleShot(0, self.__process_download_queue)

    def __process_download_queue(self):
        if not self.__download_queue:
            self.__processing_download_queue = False
            self.__label_download_progress.setText('Downloads Finished')
            self.__progress_bar_download_percentage.hide()
            self.downloads_complete()
            return

        self.__processing_download_queue = True
        video_number, video = self.__download_queue.popleft()
        self.__video_table_model.update_video_entry_status(video_number, 'Downloading')
        self.__label_download_progress.setText(f'Downloading {video_number + 1} of {self.__total_videos}')
        url,save_name, download_format = video[0], video[3], video[5]

        self.__yt_dlp_client.start_download_thread(youtube_url=url,
                                                   save_name=save_name,
                                                   download_format=download_format,
                                                   save_path=self.__save_directory_line_edit.text(),
                                                   video_index=video_number)

    def update_progress_bar_download(self, percent):
        self.__progress_bar_download_percentage.setValue(percent)

    def update_video_table_status(self, response_status, video_index):
        self.__video_table_model.update_video_entry_status(video_index=video_index,
                                                           status=response_status)
        QTimer.singleShot(0, self.__process_download_queue)

    def downloads_complete(self):
        self.__clear_downloads_button.show()
        self.__download_button.setEnabled(False)
        self.__remove_button.setEnabled(False)
        self.__add_video_button.setEnabled(False)

    def table_cleared(self):
        self.__add_video_button.setEnabled(True)
        self.__label_download_progress.hide()
        self.__clear_downloads_button.hide()
        self.__video_table_model.clear_table()