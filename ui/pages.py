from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QTreeWidget, QTreeWidgetItem, QLineEdit, 
                             QCheckBox, QPushButton, QGroupBox, QFormLayout, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from core.models import AppModel
from core.logger import get_logger
from core.settings import get_settings, SettingsManager

class DashboardPage(QWidget):
    def __init__(self, model: AppModel):
        super().__init__()
        self.model = model
        self.init_ui()
        self.model.tasks_changed.connect(self.refresh_table)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        title = QLabel("Обзор системы")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #111827;")
        layout.addWidget(title)

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


class HistoryPage(QWidget):
    """Страница истории для режима программиста"""
    def __init__(self, model: AppModel):
        super().__init__()
        self.model = model
        self.init_ui()
        self.model.history_changed.connect(self.refresh_history)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        title = QLabel("История событий (API Calls)")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #111827;")
        layout.addWidget(title)

        info = QLabel("Наведите курсор на шаг API, чтобы увидеть детали запроса и ответа.")
        info.setStyleSheet("color: #6B7280; font-size: 13px; margin-bottom: 12px;")
        layout.addWidget(info)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Событие / Этап API", "Время", "Статус / URL"])
        self.tree.setColumnWidth(0, 350)
        self.tree.setColumnWidth(1, 180)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: #FFFFFF;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F3F4F6;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #E5E7EB;
                font-weight: 600;
                color: #6B7280;
            }
        """)
        layout.addWidget(self.tree, stretch=1)

        self.refresh_history()

    def refresh_history(self):
        self.tree.clear()
        if not self.model.history_records:
            root = QTreeWidgetItem(["Нет данных о запусках", "", ""])
            self.tree.addTopLevelItem(root)
            return

        for record in self.model.history_records:
            status_icon = "✅" if record.success else "❌"
            top_item = QTreeWidgetItem([
                f"{status_icon} [{record.catalog_type}] Запуск задачи",
                record.start_time,
                "Успешно" if record.success else "Ошибка"
            ])
            
            if not record.success:
                top_item.setForeground(2, QColor("#EF4444"))
                top_item.setToolTip(2, record.error_message or "")
            
            # Добавляем дочерние элементы (шаги API)
            for step in record.steps:
                child_item = QTreeWidgetItem([
                    f"   ↳ {step.stage} ({step.method})",
                    step.timestamp,
                    f"HTTP {step.status_code} | {step.url[:50]}..."
                ])
                
                # Формируем подробный Tooltip с телами запросов
                tooltip = (f"URL: {step.url}\n\n"
                           f"--- Request Body ---\n{step.request_body}\n\n"
                           f"--- Response Body ---\n{step.response_body}")
                child_item.setToolTip(0, tooltip)
                
                if step.status_code >= 400:
                    child_item.setForeground(2, QColor("#EF4444"))
                else:
                    child_item.setForeground(2, QColor("#10B981"))
                    
                top_item.addChild(child_item)
            
            self.tree.addTopLevelItem(top_item)
            top_item.setExpanded(False) # По умолчанию блоки свернуты


class SettingsPage(QWidget):
    """Полноценная страница настроек"""
    def __init__(self, model: AppModel):
        super().__init__()
        self.model = model
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        # ИСПРАВЛЕНИЕ: используем QScrollArea для предотвращения "скашивания"
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        title = QLabel("Настройки системы")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #111827;")
        layout.addWidget(title)

        # --- Группа: Пути и Расписание ---
        group_paths = QGroupBox("Основные параметры")
        form_paths = QFormLayout(group_paths)
        
        self.download_dir_input = QLineEdit()
        form_paths.addRow("Папка для скачивания:", self.download_dir_input)
        
        self.schedule_time_input = QLineEdit()
        self.schedule_time_input.setPlaceholderText("HH:MM (например, 02:00)")
        form_paths.addRow("Время ежедневного запуска:", self.schedule_time_input)
        
        layout.addWidget(group_paths)

        # --- Группа: Логирование ---
        group_logs = QGroupBox("Система логирования")
        form_logs = QFormLayout(group_logs)
        
        self.log_dir_input = QLineEdit()
        form_logs.addRow("Папка для логов:", self.log_dir_input)
        
        self.log_template_input = QLineEdit()
        self.log_template_input.setPlaceholderText("{date}.log")
        form_logs.addRow("Шаблон имени файла:", self.log_template_input)
        
        self.log_date_fmt_input = QLineEdit()
        self.log_date_fmt_input.setPlaceholderText("%d-%m-%Y")
        form_logs.addRow("Формат даты в имени:", self.log_date_fmt_input)

        self.log_time_fmt_input = QLineEdit()
        self.log_time_fmt_input.setPlaceholderText("%Y-%m-%d %H:%M:%S")
        form_logs.addRow("Формат времени в записи:", self.log_time_fmt_input)

        self.csv_check = QCheckBox("Дублировать логи в CSV")
        form_logs.addRow("", self.csv_check)
        
        self.json_check = QCheckBox("Дублировать логи в JSON")
        form_logs.addRow("", self.json_check)
        
        layout.addWidget(group_logs)

        # --- Группа: API ---
        group_api = QGroupBox("Параметры API")
        form_api = QFormLayout(group_api)
        
        self.mock_check = QCheckBox("Использовать Mock API (без реальных запросов)")
        form_api.addRow("", self.mock_check)
        
        self.test_contur_check = QCheckBox("Использовать тестовый контур (test-contur)")
        form_api.addRow("", self.test_contur_check)
        
        layout.addWidget(group_api)

        # --- Кнопки ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Сохранить и применить")
        self.save_btn.setObjectName("PrimaryBtn")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setFixedWidth(220)
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()

        scroll.setWidget(container)
        
        # Основной layout страницы
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def load_settings(self):
        s = get_settings()
        self.download_dir_input.setText(s.download_dir)
        self.schedule_time_input.setText(s.schedule_time)
        self.log_dir_input.setText(s.log_dir)
        self.log_template_input.setText(s.log_filename_template)
        self.log_date_fmt_input.setText(s.log_date_format)
        self.log_time_fmt_input.setText(s.log_time_format)
        self.csv_check.setChecked(s.enable_csv_logs)
        self.json_check.setChecked(s.enable_json_logs)
        self.mock_check.setChecked(s.use_mock_api)
        self.test_contur_check.setChecked(s.is_test_contur)

    def save_settings(self):
        s = get_settings()
        s.download_dir = self.download_dir_input.text()
        s.schedule_time = self.schedule_time_input.text()
        s.log_dir = self.log_dir_input.text()
        s.log_filename_template = self.log_template_input.text()
        s.log_date_format = self.log_date_fmt_input.text()
        s.log_time_format = self.log_time_fmt_input.text()
        s.enable_csv_logs = self.csv_check.isChecked()
        s.enable_json_logs = self.json_check.isChecked()
        s.use_mock_api = self.mock_check.isChecked()
        s.is_test_contur = self.test_contur_check.isChecked()
        
        SettingsManager().save()
        get_logger().reload()
        
        self.model.settings_changed.emit()
        
        QMessageBox.information(self, "Успех", "Настройки сохранены и применены!")