import os
from PyQt6.QtCore import QSettings


class SettingsManager:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(SettingsManager, cls).__new__(cls)

        return cls.__instance

    def __init__(self):
        self.__settings = QSettings('yt_dlp_guiv1.0.1', 'yt_dlp_gui')
        self.__app_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.__default_settings = {
            'window_size': (1000, 600),
            'download_formats': {
                'audio': [
                    'flac',
                    'm4a',
                    'mp3',
                    'opus',
                    'vorbis',
                    'wav'
                ],
                'video': [
                    'mp4',
                    'best video'
                ]
            },
            'default_download_format': 'wav',
            'save_directory': os.path.join(self.__app_directory, 'downloads'),
            'open_save_directory_on_close': False
        }
        self.verify_save_directory()

    def get_setting(self, key: str, value_type=None):
        if value_type:
            return self.__settings.value(key, self.__default_settings[key], type=value_type)
        return self.__settings.value(key, self.__default_settings[key])

    def set_setting(self, key: str, value):
        self.__settings.setValue(key, value)

    def verify_save_directory(self):
        save_directory = self.__settings.value('save_directory')

        if not save_directory:
            self.__set_default_save_directory()
            return

        if not os.path.isdir(save_directory):
            self.__set_default_save_directory()
            return

    def __set_default_save_directory(self):
        if not os.path.isdir(self.__default_settings['save_directory']):
            print('creating default save directory')
            os.makedirs(self.__default_settings['save_directory'])
            self.__settings.setValue('save_directory', self.__default_settings['save_directory'])

# settings_manager = SettingsManager()
# settings_manager.set_setting(key='window_size', value=(1000, 600))