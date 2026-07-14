from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from core.models import AppModel

class DashboardPage(QWidget):
    def __init__(self, model: AppModel):
        super().__init__()
        self.model = model
        self.init_ui()
        # Подписываемся на обновления модели
        self.model.tasks_changed.connect(self.refresh_table)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        title = QLabel("Обзор системы")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #111827;")
        layout.addWidget(title)

        # Карточка статуса
        status_card = QWidget()
        status_card.setStyleSheet("background: #F9FAFB; border-radius: 8px; padding: 16px;")
        status_layout = QVBoxLayout(status_card)
        
        self.status_label = QLabel("🟢 Статус: Служба активна")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #10B981;")
        status_layout.addWidget(self.status_label)
        
        self.next_run_label = QLabel("Следующий запуск: По расписанию")
        self.next_run_label.setStyleSheet("color: #6B7280;")
        status_layout.addWidget(self.next_run_label)
        
        layout.addWidget(status_card)

        # Таблица перечней
        table_title = QLabel("Актуальность перечней")
        table_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827;")
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Каталог", "Дата обновления", "Размер", "Статус"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table, stretch=1)

        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.model.tasks))
        for row, task in enumerate(self.model.tasks):
            self.table.setItem(row, 0, QTableWidgetItem(task.catalog_type))
            
            if task.last_history_record:
                date = task.last_history_record.end_time or "Ошибка"
                status = "✅ Успешно" if task.last_history_record.success else "❌ Ошибка"
            else:
                date = "Нет данных"
                status = "⏳ Ожидание"
                
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem("-")) 
            self.table.setItem(row, 3, QTableWidgetItem(status))


class SettingsPage(QWidget):
    def __init__(self, model: AppModel):
        super().__init__()
        self.model = model
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        title = QLabel("Настройки")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #111827;")
        layout.addWidget(title)

        info = QLabel("Здесь будут настройки подключения, сертификатов и расписания.\n(Добавим в Шаге 4)")
        info.setStyleSheet("color: #6B7280; font-size: 16px;")
        layout.addWidget(info)
        
        layout.addStretch()