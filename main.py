import sys
import time
from core.settings import get_settings, SettingsManager
from core.logger import get_logger
from core.models import AppModel
from services.scheduler import TaskScheduler

def main():
    settings = get_settings()
    logger = get_logger()
    
    logger.log("INFO", "=== Инициализация ядра FEDSFM Hybrid ===")
    
    # 1. Создаем модель
    model = AppModel()
    
    # 2. Инициализируем планировщик (он автоматически подхватит настройки и создаст API клиент)
    scheduler = TaskScheduler(model)
    
    logger.log("INFO", "Запуск тестового выполнения задач (Mock режим)...")
    
    # 3. Запускаем задачи вручную для проверки
    scheduler.run_now()
    
    # 4. Даем время на завершение асинхронных операций (в реальном приложении это делает UI/Event Loop)
    time.sleep(3)
    
    # 5. Выводим результаты
    logger.log("INFO", "=== Результаты выполнения ===")
    for task in model.tasks:
        status = "✅ Успех" if task.last_history_record.success else f"❌ Ошибка: {task.last_history_record.error_message}"
        logger.log("INFO", f"Задача {task.catalog_type}: {status}")
        
        # Демонстрация истории шагов
        if task.last_history_record.steps:
            logger.log("INFO", f"  -> Цепочка вызовов ({len(task.last_history_record.steps)} шагов):")
            for step in task.last_history_record.steps:
                logger.log("INFO", f"     [{step.stage}] {step.method} {step.url} -> {step.status_code}")

    logger.log("INFO", "Тест завершен. Проверьте папку 'logs' и 'downloads'.")
    print("\nНажмите Enter для выхода...")
    input()

if __name__ == "__main__":
    main()