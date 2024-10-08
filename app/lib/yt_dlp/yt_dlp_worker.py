import os
import re
import sys
import yt_dlp
from datetime import timedelta
from PyQt6.QtCore import QObject, pyqtSignal
from app.settings_manager import SettingsManager


class YTDLPWorker(QObject):
    download_progress = pyqtSignal(int)
    video_download_response = pyqtSignal(str, int)
    video_details_response = pyqtSignal(int, tuple)

    def __init__(self):
        super().__init__()
        self.__settings_manager = SettingsManager()
        self.__download_formats = self.__settings_manager.get_setting('download_formats')

        # ffmpeg path in pyinstaller build
        self.__bundle_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        self.__ffmpeg_path = os.path.join(self.__bundle_path, 'ffmpeg.exe')

    def get_video_details(self, youtube_url: str, save_name: str, download_format: str):
        yt_dlp_options = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(yt_dlp_options) as yt:
            try:
                info = yt.extract_info(youtube_url, download=False)
                title = info.get('title')
                channel = info.get('channel')
                duration = str(timedelta(seconds=info.get('duration')))
                self.video_details_response.emit(0, (title, channel, duration, save_name, download_format, youtube_url))

            except Exception as e:
                self.video_details_response.emit(-1, (youtube_url, e))

    def __download_progress_hook(self, yt_dlp_process):
        percent = 0
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        if yt_dlp_process['status'] == 'downloading':
            raw_percent = yt_dlp_process.get('_percent_str', '0').strip('%')
            cleaned_percent = ansi_escape.sub('', raw_percent)
            numeric_percent = cleaned_percent.rstrip('%').strip()
            percent = int(float(numeric_percent))
        elif yt_dlp_process['status'] == 'finished':
            percent = 100,

        self.download_progress.emit(percent)

    def download_video(self, youtube_url: str, download_format: str, save_name: str, save_path: str, video_index: int):
        yt_dlp_options = {
            'quiet': True,
            'outtmpl': os.path.join(save_path, f'{save_name}.%(ext)s'),
            'ffmpeg_location': self.__ffmpeg_path,
            'progress_hooks': [self.__download_progress_hook],
        }

        if download_format in self.__download_formats['video']:
            if download_format == 'best video':
                format_value = 'bestvideo+bestaudio/best'
            else:
                format_value = f'bestvideo[ext={download_format}]+bestaudio[ext=m4a]/best[ext={download_format}]/best'
            yt_dlp_options['format'] = format_value
        else:
            yt_dlp_options['format'] = 'bestaudio/best'
            yt_dlp_options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': download_format,
            }]

        try:
            with yt_dlp.YoutubeDL(yt_dlp_options) as yt:
                yt.download([youtube_url])

            self.video_download_response.emit('Downloaded', video_index)

        except yt_dlp.DownloadError as e:
            self.video_download_response.emit('Error', video_index)
