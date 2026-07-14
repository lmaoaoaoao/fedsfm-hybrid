import json
import os
from dataclasses import dataclass, asdict

CONFIG_FILE = "config.json"

@dataclass
class AppSettings:
    # Настройки скачивания
    download_dir: str = "downloads"
    schedule_time: str = "02:00"
    
    # Настройки логирования
    log_dir: str = "logs"
    log_filename_template: str = "{date}.log"  # Шаблон имени
    log_date_format: str = "%d-%m-%Y"          # Формат даты в имени файла
    log_time_format: str = "%Y-%m-%d %H:%M:%S" # Формат времени в самой записи
    enable_csv_logs: bool = False
    enable_json_logs: bool = False
    
    # Настройки API
    use_mock_api: bool = True
    fedsfm_base_url: str = "https://portal.fedsfm.ru:8081/Services/fedsfm-service"
    is_test_contur: bool = True

class SettingsManager:
    _instance = None
    _settings: AppSettings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._settings = AppSettings(**data)
            except Exception:
                self._settings = AppSettings()
        else:
            self._settings = AppSettings()
            self.save()

    def save(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(asdict(self._settings), f, indent=4, ensure_ascii=False)

    def get(self) -> AppSettings:
        return self._settings

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self._settings, k):
                setattr(self._settings, k, v)
        self.save()

def get_settings() -> AppSettings:
    return SettingsManager().get()