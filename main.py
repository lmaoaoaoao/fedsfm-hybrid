import sys
from core.settings import get_settings, SettingsManager
from core.logger import get_logger

def main():
    # 1. Инициализация настроек
    settings = get_settings()
    print(f"✅ Настройки загружены. Папка логов: {settings.log_dir}")
    
    # 2. Инициализация логгера
    logger = get_logger()
    
    # 3. Тестовые записи
    logger.log("INFO", "Приложение FEDSFM Hybrid запущено.")
    logger.log("INFO", f"Используется тестовый контур: {settings.is_test_contur}")
    logger.log("WARN", "Это тестовое предупреждение для проверки цветов и ротации.")
    
    # Тестовая запись с доп. данными (для CSV/JSON)
    logger.log("INFO", "Получен ID каталога TE21", extra_data={"idXml": "123e4567-e89b-12d3-a456-426614174000", "size": "4.2MB"})
    
    print("✅ Тестовые логи записаны. Проверьте папку 'logs'.")
    print("🚀 Готово к Шагу 2. Нажмите Enter для выхода...")
    input()

if __name__ == "__main__":
    main()