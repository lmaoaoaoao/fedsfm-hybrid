from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

class TrayManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tray_icon = QSystemTrayIcon(self._create_icon(), main_window)
        self.tray_icon.setToolTip("FEDSFM Hybrid (Работает в фоне)")

        # Контекстное меню (правый клик)
        menu = QMenu()
        
        show_action = menu.addAction("📂 Показать окно")
        show_action.triggered.connect(self.main_window.show_from_tray)
        
        menu.addSeparator()
        
        exit_action = menu.addAction("❌ Полный выход")
        exit_action.triggered.connect(self.quit_app)

        self.tray_icon.setContextMenu(menu)
        
        # Двойной клик по иконке тоже открывает окно
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def _create_icon(self):
        """Генерируем простую минималистичную иконку программно"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Синий скругленный квадрат
        painter.setBrush(QColor("#2563EB"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 16, 16)
        
        # Белый внутренний элемент (имитация щита/документа)
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawRoundedRect(22, 22, 20, 20, 4, 4)
        
        painter.end()
        return QIcon(pixmap)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.main_window.show_from_tray()

    def quit_app(self):
        """Полное завершение приложения"""
        from PyQt6.QtWidgets import QApplication
        self.tray_icon.hide()
        QApplication.quit()