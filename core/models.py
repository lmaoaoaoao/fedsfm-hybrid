from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

class TaskStatus(Enum):
    QUEUED = "В очереди"
    DOWNLOADING = "Загрузка"
    COMPLETED = "Завершено"
    ERROR = "Ошибка"

@dataclass
class ApiCallStep:
    """Детальное описание одного шага API (например, только авторизация или только скачивание)"""
    stage: str          # "Auth", "GetCatalogID", "DownloadFile"
    url: str
    method: str         # "POST", "GET"
    status_code: int
    request_body: str   # JSON или форма
    response_body: str  # Текст ответа или "Binary data (X bytes)"
    timestamp: str

@dataclass
class TaskHistoryRecord:
    """Полная запись об одном запуске задачи (хранится для истории за 7 дней)"""
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
    status: TaskStatus
    progress: int
    schedule: str
    last_history_record: Optional[TaskHistoryRecord] = None