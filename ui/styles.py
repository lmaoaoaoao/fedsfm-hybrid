GLOBAL_QSS = """
/* Базовые цвета и шрифты */
QMainWindow, QWidget {
    background-color: #FFFFFF;
    color: #111827;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    font-size: 14px;
}

/* Боковое меню (Sidebar) */
#Sidebar {
    background-color: #F9FAFB;
    border-right: 1px solid #E5E7EB;
}
#Sidebar QPushButton {
    text-align: left;
    padding: 12px 20px;
    border: none;
    border-radius: 6px;
    color: #374151;
    font-weight: 500;
    background: transparent;
}
#Sidebar QPushButton:hover {
    background-color: #F3F4F6;
}
/* Активная кнопка в меню */
#Sidebar QPushButton[active="true"] {
    background-color: #EFF6FF;
    color: #2563EB;
    font-weight: 600;
}

/* Карточки и группы */
QGroupBox {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    margin-top: 16px;
    padding: 20px 16px 16px 16px;
    font-weight: bold;
    color: #111827;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 6px;
}

/* Поля ввода */
QLineEdit, QComboBox {
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 8px 12px;
    background: #FFFFFF;
}
QLineEdit:focus {
    border-color: #2563EB;
}

/* Кнопки */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 8px 16px;
    color: #374151;
}
QPushButton:hover {
    background-color: #F9FAFB;
    border-color: #9CA3AF;
}
QPushButton#PrimaryBtn {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
}
QPushButton#PrimaryBtn:hover {
    background-color: #1D4ED8;
}

/* Таблицы */
QTableWidget {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    gridline-color: #F3F4F6;
    background-color: #FFFFFF;
}
QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #F3F4F6;
}
QHeaderView::section {
    background-color: #F9FAFB;
    padding: 12px;
    border: none;
    border-bottom: 1px solid #E5E7EB;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    font-size: 12px;
}
"""