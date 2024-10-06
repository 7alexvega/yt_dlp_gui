from PyQt6.QtCore import QRunnable


class YTDLPDownloadTask(QRunnable):
    def __init__(self, worker, youtube_url: str, save_name: str, save_path: str, download_format: str, video_index: int):
        super().__init__()
        self.__worker = worker
        self.__youtube_url = youtube_url
        self.__save_name = save_name
        self.__save_path = save_path
        self.__download_format = download_format
        self.__video_index = video_index

    def run(self):
        self.__worker.download_video(youtube_url=self.__youtube_url,
                                   download_format=self.__download_format,
                                   save_name=self.__save_name,
                                   save_path=self.__save_path,
                                   video_index=self.__video_index)