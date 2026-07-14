from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                             QStackedWidget, QSystemTrayIcon, QComboBox, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from core.models import AppModel
from ui.pages import DashboardPage, SettingsPage, HistoryPage
from ui.tray import TrayManager

class MainWindow(QMainWindow):
    def __init__(self, model: AppModel):
        super().__init__()
        self.model = model
        self.setWindowTitle("FEDSFM Hybrid")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

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

        logo = QLabel("🛡️ FEDSFM")
        logo.setStyleSheet("font-size: 22px; font-weight: bold; color: #111827; padding: 12px 8px;")
        sidebar_layout.addWidget(logo)
        
        # Переключатель режимов
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["👤 Обычный режим", "⚙️ Режим программиста"])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background: #FFFFFF;
                font-weight: 500;
            }
            QComboBox:hover { border-color: #9CA3AF; }
        """)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        sidebar_layout.addWidget(self.mode_combo)
        
        sidebar_layout.addSpacing(16)

        # Кнопки навигации
        self.btn_dashboard = self._create_nav_button("📊 Обзор", True)
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.btn_dashboard)

        self.btn_history = self._create_nav_button("📜 История", False)
        self.btn_history.clicked.connect(lambda: self.switch_page(1))
        self.btn_history.setVisible(False) # Скрыто для обычного пользователя
        sidebar_layout.addWidget(self.btn_history)

        sidebar_layout.addStretch()

        self.btn_settings = self._create_nav_button("⚙️ Настройки", False)
        self.btn_settings.clicked.connect(lambda: self.switch_page(2))
        sidebar_layout.addWidget(self.btn_settings)

        main_layout.addWidget(self.sidebar)

        # --- Область контента ---
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #FFFFFF;")
        
        self.dashboard_page = DashboardPage(self.model)
        self.history_page = HistoryPage(self.model)
        self.settings_page = SettingsPage(self.model)
        
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.history_page)
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
        
        # Сбрасываем стили всех кнопок
        for btn in [self.btn_dashboard, self.btn_history, self.btn_settings]:
            btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        # Активируем нужную кнопку
        active_btn = [self.btn_dashboard, self.btn_history, self.btn_settings][index]
        active_btn.setProperty("active", "true")
        active_btn.style().unpolish(active_btn)
        active_btn.style().polish(active_btn)

    def on_mode_changed(self, index):
        is_dev = (index == 1)
        self.btn_history.setVisible(is_dev)
        
        # Если скрыли кнопку истории и мы сейчас на ней, переключаем на дашборд
        if not is_dev and self.stack.currentIndex() == 1:
            self.switch_page(0)
            
        mode_name = "Программиста" if is_dev else "Обычный"
        self.model.add_log(f"Режим интерфейса изменен на: {mode_name}", "INFO")

    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()
        self.tray.tray_icon.showMessage(
            "FEDSFM Hybrid",
            "Приложение свернуто в системный трей и продолжает работать в фоне.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def show_from_tray(self):
        self.show()
        self.activateWindow()