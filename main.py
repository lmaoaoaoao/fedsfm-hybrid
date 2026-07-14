import sys
from PyQt6.QtWidgets import QApplication
from core.models import AppModel
from services.scheduler import TaskScheduler
from ui.main_window import MainWindow
from ui.styles import GLOBAL_QSS

def main():
    # 1. Инициализация Qt приложения
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Базовая тема
    app.setStyleSheet(GLOBAL_QSS) # Наш минималистичный стиль
    
    # Критически важно: не закрывать приложение при скрытии главного окна
    app.setQuitOnLastWindowClosed(False)

    # 2. Инициализация Ядра и Сервисов
    model = AppModel()
    scheduler = TaskScheduler(model)
    scheduler.start() # Запускаем фоновый планировщик

    # 3. Инициализация UI
    window = MainWindow(model)
    window.show()

    # 4. Запуск event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()