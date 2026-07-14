import logging
import os
import csv
import json
from datetime import datetime
from core.settings import get_settings

class DailyRotatingHandler(logging.Handler):
    """Кастомный хендлер, который создает новый файл ровно в 00:00 по шаблону"""
    def __init__(self, log_dir, template, date_fmt):
        super().__init__()
        self.log_dir = log_dir
        self.template = template
        self.date_fmt = date_fmt
        self.current_date = None
        self.file_handler = None
        
        os.makedirs(self.log_dir, exist_ok=True)
        self._check_rotation()

    def _get_filename(self):
        date_str = datetime.now().strftime(self.date_fmt)
        return self.template.replace("{date}", date_str)

    def _check_rotation(self):
        today = datetime.now().strftime(self.date_fmt)
        if today != self.current_date:
            if self.file_handler:
                self.file_handler.close()
            
            filepath = os.path.join(self.log_dir, self._get_filename())
            self.file_handler = logging.FileHandler(filepath, encoding='utf-8')
            
            # ИСПРАВЛЕНИЕ: Применяем форматтер только если он уже был установлен
            if self.formatter:
                self.file_handler.setFormatter(self.formatter)
                
            self.current_date = today

    def setFormatter(self, fmt):
        """
        ИСПРАВЛЕНИЕ: Переопределяем setFormatter, чтобы пробросить его 
        во внутренний file_handler и в родительский класс
        """
        super().setFormatter(fmt)
        if self.file_handler:
            self.file_handler.setFormatter(fmt)

    def emit(self, record):
        self._check_rotation()
        self.file_handler.emit(record)

class LogManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        settings = get_settings()
        self.logger = logging.getLogger("FedsfmHybrid")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear() # Очищаем на случай перезапуска
        
        time_fmt = settings.log_time_format
        formatter = logging.Formatter(f'[%(asctime)s] [%(levelname)s] %(message)s', datefmt=time_fmt)

        # 1. Обязательный Plain Text логгер (с ротацией в 00:00)
        txt_handler = DailyRotatingHandler(
            log_dir=settings.log_dir,
            template=settings.log_filename_template,
            date_fmt=settings.log_date_format
        )
        txt_handler.setFormatter(formatter)
        self.logger.addHandler(txt_handler)

        # 2. Консольный вывод (для разработки)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 3. Опциональные папки для CSV и JSON
        if settings.enable_csv_logs:
            self.csv_dir = os.path.join(settings.log_dir, "csv")
            os.makedirs(self.csv_dir, exist_ok=True)
            
        if settings.enable_json_logs:
            self.json_dir = os.path.join(settings.log_dir, "json")
            os.makedirs(self.json_dir, exist_ok=True)

    def log(self, level: str, message: str, extra_data: dict = None):
        """Основной метод для записи лога"""
        settings = get_settings()
        timestamp = datetime.now().strftime(settings.log_time_format)
        
        # Запись в основной plain text (через стандартный logging)
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(message)

        # Запись в CSV (если включено)
        if settings.enable_csv_logs:
            csv_file = os.path.join(self.csv_dir, f"{datetime.now().strftime(settings.log_date_format)}.csv")
            file_exists = os.path.isfile(csv_file)
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Timestamp", "Level", "Message", "Extra"])
                writer.writerow([timestamp, level, message, json.dumps(extra_data, ensure_ascii=False) if extra_data else ""])

        # Запись в JSON (если включено)
        if settings.enable_json_logs:
            json_file = os.path.join(self.json_dir, f"{datetime.now().strftime(settings.log_date_format)}.json")
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                "message": message,
                "extra": extra_data
            }
            with open(json_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                
    def reload(self):
        """Перезагрузка настроек логгера (применяет новые шаблоны и пути)"""
        self._setup()

def get_logger() -> LogManager:
    return LogManager()

