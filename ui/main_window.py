from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QSystemTrayIcon
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from core.models import AppModel
from ui.pages import DashboardPage, SettingsPage
from ui.tray import TrayManager

class MainWindow(QMainWindow):
    def __init__(self, model: AppModel):
        super().__init__()
        self.model = model
        self.setWindowTitle("FEDSFM Hybrid")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Боковое меню (Sidebar) ---
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(8)

        # Логотип
        logo = QLabel("🛡️ FEDSFM")
        logo.setStyleSheet("font-size: 22px; font-weight: bold; color: #111827; padding: 12px 8px;")
        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(16)

        # Кнопки навигации
        self.btn_dashboard = self._create_nav_button("📊 Обзор", True)
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.btn_dashboard)

        self.btn_settings = self._create_nav_button("⚙️ Настройки", False)
        self.btn_settings.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.btn_settings)

        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        # --- Область контента (Stacked Widget) ---
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #FFFFFF;")
        
        self.dashboard_page = DashboardPage(self.model)
        self.settings_page = SettingsPage(self.model)
        
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.settings_page)
        
        main_layout.addWidget(self.stack, stretch=1)

        # --- Системный трей ---
        self.tray = TrayManager(self)

    def _create_nav_button(self, text, is_active):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        btn.setProperty("active", "true" if is_active else "false")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(44)
        return btn

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        
        # Обновляем стили кнопок
        is_dashboard = (index == 0)
        self.btn_dashboard.setProperty("active", "true" if is_dashboard else "false")
        self.btn_settings.setProperty("active", "false" if is_dashboard else "true")
        
        # Принудительно обновляем стили Qt
        self.btn_dashboard.style().unpolish(self.btn_dashboard)
        self.btn_dashboard.style().polish(self.btn_dashboard)
        self.btn_settings.style().unpolish(self.btn_settings)
        self.btn_settings.style().polish(self.btn_settings)

    def closeEvent(self, event: QCloseEvent):
        """Перехватываем закрытие окна: сворачиваем в трей вместо выхода"""
        event.ignore()
        self.hide()
        self.tray.tray_icon.showMessage(
            "FEDSFM Hybrid",
            "Приложение свернуто в системный трей и продолжает работать в фоне.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def show_from_tray(self):
        """Возврат окна из трея"""
        self.show()
        self.activateWindow()