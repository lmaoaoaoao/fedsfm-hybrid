from PyQt6.QtCore import QObject, pyqtSignal
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime
from core.logger import get_logger

class TaskStatus(Enum):
    QUEUED = "В очереди"
    DOWNLOADING = "Загрузка"
    COMPLETED = "Завершено"
    ERROR = "Ошибка"

@dataclass
class ApiCallStep:
    """Детальное описание одного шага API-вызова"""
    stage: str          # "Auth", "GetCatalogID", "DownloadFile"
    url: str
    method: str         # "POST", "GET"
    status_code: int
    request_body: str   # JSON строка или "Binary data"
    response_body: str  # JSON строка или "Binary data (X bytes)"
    timestamp: str

@dataclass
class TaskHistoryRecord:
    """Полная запись об одном запуске задачи (для истории за 7 дней)"""
    task_id: str
    catalog_type: str   # "TE21", "MVK", "UN_RU", "UN_EN"
    start_time: str
    end_time: str
    success: bool
    error_message: Optional[str] = None
    steps: List[ApiCallStep] = field(default_factory=list)

@dataclass
class CatalogTask:
    """Текущая активная задача"""
    id: str
    catalog_type: str
    endpoint_catalog: str
    endpoint_file: str
    filename: str
    status: TaskStatus
    progress: int
    schedule: str
    last_history_record: Optional[TaskHistoryRecord] = None


class AppModel(QObject):
    """Центральная модель данных, связывающая UI, Настройки и Планировщик"""
    
    # Сигналы для обновления UI
    tasks_changed = pyqtSignal()
    history_changed = pyqtSignal()
    log_added = pyqtSignal(str, str)
    mode_changed = pyqtSignal(bool)
    settings_changed = pyqtSignal()  # <--- ИСПРАВЛЕНИЕ 1: Сигнал для настроек

    def __init__(self):
        super().__init__()
        self.is_advanced_mode = False
        self.history_records: List[TaskHistoryRecord] = []
        self.logger = get_logger()
        
        # Инициализация тестовых задач
        self.tasks: List[CatalogTask] = [
            CatalogTask("1", "TE21", "suspect-catalogs/current-te21-catalog", "suspect-catalogs/current-te21-file", "te21_catalog.zip", TaskStatus.QUEUED, 0, "Ежедневно"),
            CatalogTask("2", "MVK", "suspect-catalogs/current-mvk-catalog", "suspect-catalogs/current-mvk-file-zip", "mvk_list.zip", TaskStatus.QUEUED, 0, "Ежедневно"),
            CatalogTask("3", "UN_RU", "suspect-catalogs/current-un-catalog-rus", "suspect-catalogs/current-un-file", "un_catalog_rus.xml", TaskStatus.QUEUED, 0, "Ежедневно"),
            CatalogTask("4", "UN_EN", "suspect-catalogs/current-un-catalog", "suspect-catalogs/current-un-file", "un_catalog.xml", TaskStatus.QUEUED, 0, "Ежедневно"),
        ]

    def toggle_mode(self):
        self.is_advanced_mode = not self.is_advanced_mode
        self.mode_changed.emit(self.is_advanced_mode)

    # <--- ИСПРАВЛЕНИЕ 2: Добавляем недостающий метод add_log
    def add_log(self, message: str, level: str = "INFO"):
        """Записывает лог в файл и отправляет сигнал в UI"""
        self.logger.log(level, message)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_added.emit(f"[{timestamp}] {message}", level)