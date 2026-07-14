from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from core.settings import get_settings
from core.logger import get_logger
from services.api_client import FedsfmApiClient

class TaskScheduler:
    def __init__(self, app_model):
        self.model = app_model
        self.settings = get_settings()
        self.logger = get_logger()
        self.scheduler = BackgroundScheduler()
        self.api_client = FedsfmApiClient()
        
        self._setup_initial_schedule()

    def _setup_initial_schedule(self):
        """Настраивает расписание на основе настроек при запуске"""
        self.scheduler.remove_all_jobs()
        time_str = self.settings.schedule_time # например, "02:00"
        try:
            hour, minute = map(int, time_str.split(':'))
            self.scheduler.add_job(
                func=self._run_all_tasks,
                trigger=CronTrigger(hour=hour, minute=minute),
                id='daily_fedsfm_download',
                name='Ежедневная загрузка перечней ФСФМ',
                replace_existing=True
            )
            self.logger.log("INFO", f"Планировщик настроен на ежедневный запуск в {time_str}")
        except Exception as e:
            self.logger.log("ERROR", f"Ошибка настройки планировщика: {str(e)}")

    def update_schedule(self, new_time_str: str):
        """Обновляет время расписания на лету"""
        self.settings.update(schedule_time=new_time_str)
        self._setup_initial_schedule()
        self.logger.log("INFO", f"Расписание обновлено на {new_time_str}")

    def run_now(self):
        """Немедленный запуск всех задач (по кнопке из UI)"""
        self.logger.log("INFO", "Запуск задач по требованию пользователя...")
        self._run_all_tasks()

    def _run_all_tasks(self):
        """Внутренний метод выполнения всех задач"""
        self.logger.log("INFO", "Начало цикла загрузки каталогов...")
        
        for task in self.model.tasks:
            # Обновляем статус в UI
            task.status = "Загрузка" # Используем строку или TaskStatus.DOWNLOADING, зависит от вашей модели
            task.progress = 0
            self.model.tasks_changed.emit()

            # Выполняем задачу через API клиент
            history_record = self.api_client.execute_catalog_task(
                task_id=task.id,
                catalog_type=task.catalog_type,
                endpoint_catalog=task.endpoint_catalog,
                endpoint_file=task.endpoint_file,
                filename=task.filename
            )

            # Сохраняем историю и обновляем статус
            task.last_history_record = history_record
            task.status = "Завершено" if history_record.success else "Ошибка"
            task.progress = 100
            
            # Добавляем в общую историю (храним последние 7 дней, упрощенно - последние 50 записей)
            self.model.history_records.insert(0, history_record)
            if len(self.model.history_records) > 50:
                self.model.history_records.pop()
                
            self.model.tasks_changed.emit()
            self.model.history_changed.emit() # Новый сигнал для обновления UI истории

        self.logger.log("INFO", "Цикл загрузки каталогов завершен.")

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.log("INFO", "Планировщик запущен.")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.logger.log("WARN", "Планировщик остановлен.")