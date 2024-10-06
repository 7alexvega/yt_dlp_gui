from PyQt6.QtCore import QRunnable


class YTDLPDetailsTask(QRunnable):
    def __init__(self, worker, youtube_url: str, save_name: str, download_format: str):
        super().__init__()
        self.__worker = worker
        self.__youtube_url = youtube_url
        self.__save_name = save_name
        self.__download_format = download_format

    def run(self):
        self.__worker.get_video_details(youtube_url=self.__youtube_url,
                                      download_format=self.__download_format,
                                      save_name=self.__save_name)