from app.lib.yt_dlp.yt_dlp_worker import YTDLPWorker
from app.lib.yt_dlp.yt_dlp_download_task import YTDLPDownloadTask
from app.lib.yt_dlp.yt_dlp_details_task import YTDLPDetailsTask
from PyQt6.QtCore import QThreadPool


class YTDLPThreadManager:
    def __init__(self):
        self.__yt_dlp_worker = YTDLPWorker()
        self.__thread_pool = QThreadPool()
        self.download_progress = self.__yt_dlp_worker.download_progress
        self.video_download_response = self.__yt_dlp_worker.video_download_response
        self.video_details_response = self.__yt_dlp_worker.video_details_response

    def start_download_thread(self, youtube_url: str, save_name: str, download_format: str, save_path: str, video_index: int):
        self.__thread_pool.start(YTDLPDownloadTask(self.__yt_dlp_worker,
                                                   youtube_url,
                                                   save_name,
                                                   save_path,
                                                   download_format,
                                                   video_index))

    def start_get_details_thread(self, youtube_url: str, save_name: str, download_format: str):
        self.__thread_pool.start(YTDLPDetailsTask(self.__yt_dlp_worker,
                                                  youtube_url,
                                                  save_name,
                                                  download_format))