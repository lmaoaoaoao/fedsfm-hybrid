import sys
from PyQt6.QtWidgets import QApplication
from core.models import AppModel
from services.scheduler import TaskScheduler
from ui.main_window import MainWindow
from ui.styles import GLOBAL_QSS

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_QSS)
    app.setQuitOnLastWindowClosed(False)

    model = AppModel()
    scheduler = TaskScheduler(model)
    scheduler.start()

    window = MainWindow(model)
    window.show()

    # Обработка изменения настроек (перезапуск планировщика)
    def on_settings_changed():
        from core.settings import get_settings
        new_time = get_settings().schedule_time
        scheduler.update_schedule(new_time)
        model.add_log(f"Планировщик обновлен. Новое время запуска: {new_time}", "INFO")
        
    model.settings_changed.connect(on_settings_changed)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()