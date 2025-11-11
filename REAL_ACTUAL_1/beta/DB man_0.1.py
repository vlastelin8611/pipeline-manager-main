import sys             # для системных параметров  # импортирую модуль sys для работы с системными функциями и параметрами Python
import os              # для работы с файловой системой  # импортирую модуль os для работы с файлами, папками и путями
import sqlite3         # для работы с sqlite базами  # импортирую модуль sqlite3 для работы с базой данных SQLite
import time            # для измерения времени  # импортирую модуль time для работы со временем (паузы, измерения)
import random          # для генерации случайных значений  # импортирую модуль random для генерации случайных чисел и значений

from PyQt5.QtWidgets import (  # импортирую виджеты из PyQt5 для создания графического интерфейса:
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,  # основные виджеты и компоновщики
    QGroupBox, QLabel, QLineEdit, QTextEdit, QDialog, QMessageBox,  # группы, метки, поля ввода, диалоги
    QFileDialog, QFormLayout, QComboBox, QTableWidget, QTableWidgetItem,  # диалоги файлов, формы, выпадающие списки, таблицы
    QTabWidget  # виджет вкладок
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer  # импортирую основные классы PyQt5:
# Qt - базовые константы и перечисления
# pyqtSignal - для создания сигналов (событий)
# QTimer - для работы с таймерами

# глобальный список для хранения открытых окон (чтобы они не удалялись сборщиком мусора)
activeDialogs = []  # создаю пустой список для хранения ссылок на активные диалоговые окна, чтобы Python не удалил их из памяти

def show_instruction_dialog(title, instruction_text):  # определяю функцию для показа инструкций пользователю
    # функция для показа диалогового окна с инструкцией
    dialog = QDialog()  # создаю новое диалоговое окно
    dialog.setWindowTitle(title)  # устанавливаю заголовок окна из параметра title
    dialog.setWindowModality(Qt.NonModal)  # делаю окно немодальным (можно работать с другими окнами)
    layout = QVBoxLayout(dialog)  # создаю вертикальную компоновку для размещения элементов в диалоге
    text_edit = QTextEdit()  # создаю текстовое поле для отображения инструкции
    text_edit.setReadOnly(True)  # делаю текстовое поле только для чтения (нельзя редактировать)
    text_edit.setText(instruction_text)  # заполняю текстовое поле текстом инструкции
    text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)  # разрешаю выделение текста мышью и переход по ссылкам
    layout.addWidget(text_edit)  # добавляю текстовое поле в компоновку
    ok_button = QPushButton("ok")  # создаю кнопку "ok" для закрытия диалога
    ok_button.clicked.connect(dialog.close)  # привязываю закрытие диалога к нажатию кнопки
    layout.addWidget(ok_button)  # добавляю кнопку в компоновку
    dialog.setAttribute(Qt.WA_DeleteOnClose, True)  # устанавливаю автоматическое удаление диалога при закрытии
    activeDialogs.append(dialog)  # добавляю диалог в список активных окон
    dialog.finished.connect(lambda _: activeDialogs.remove(dialog))  # при закрытии диалога удаляю его из списка активных
    dialog.show()  # показываю диалог пользователю

def get_standard_data():
    # возвращает стандартные данные для нормализации
    standard_instructions = (
        "стандартный формат базы данных включает:\n"
        "таблица operators: фио, логин, пароль, доступ высшего приоритета (bool), логи действий;\n"
        "таблица cells: 40 ячеек с данными: работоспособность, давление, температура, скорость откачки, вибрации, угол наклона;\n"
        "таблица external_data: данные об улице: температура, давление, ветер, влажность;\n"
        "таблица reports: периодические отчеты (среднее арифметическое за последнюю минуту).\n"
    )
    return {
        "name": "стандарт",
        "type": "стандартный формат",
        "property": "стандартный формат",
        "ping": "",
        "status": "готов",
        "remote_instructions": standard_instructions
    }

def normalize_database(server_db_path, client_db_path, use_standard=False):
    """
    Функция нормализации базы данных.
    Если таблица raw_data отсутствует в серверной базе, она создаётся с примером данных.
    Затем данные из raw_data переносятся в таблицы:
      operators, cells, external_data и reports.
    Если выбран стандартный формат, то в клиентской базе вставляются примерные данные, если таблицы пустые.
    """
    client_conn = sqlite3.connect(client_db_path)
    client_cur = client_conn.cursor()
    # Создаем стандартные таблицы в клиентской базе
    client_cur.execute("""CREATE TABLE IF NOT EXISTS operators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fio TEXT,
        login TEXT,
        password TEXT,
        high_priority INTEGER,
        logs TEXT
    );""")
    client_cur.execute("""CREATE TABLE IF NOT EXISTS cells (
        cell_id INTEGER PRIMARY KEY,
        working_status TEXT,
        pressure REAL,
        temperature REAL,
        pumping_speed REAL,
        vibrations REAL,
        tilt_angle REAL
    );""")
    client_cur.execute("""CREATE TABLE IF NOT EXISTS external_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        outdoor_temperature REAL,
        outdoor_pressure REAL,
        wind REAL,
        humidity REAL,
        timestamp TEXT
    );""")
    client_cur.execute("""CREATE TABLE IF NOT EXISTS reports (
        report_time TEXT PRIMARY KEY,
        avg_pressure REAL,
        avg_temperature REAL,
        avg_pumping_speed REAL,
        avg_vibrations REAL,
        avg_tilt_angle REAL
    );""")
    client_conn.commit()
    if not use_standard:
        # Проверяем наличие таблицы raw_data в серверной базе
        server_conn = sqlite3.connect(server_db_path)
        server_cur = server_conn.cursor()
        server_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='raw_data';")
        if not server_cur.fetchone():
            # Если таблицы raw_data нет, создаем её и вставляем примерную строку
            server_cur.execute("""CREATE TABLE IF NOT EXISTS raw_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator_fio TEXT,
                operator_login TEXT,
                operator_password TEXT,
                operator_high_priority INTEGER,
                operator_logs TEXT,
                cell_id INTEGER,
                cell_working_status TEXT,
                cell_pressure REAL,
                cell_temperature REAL,
                cell_pumping_speed REAL,
                cell_vibrations REAL,
                cell_tilt_angle REAL,
                outdoor_temperature REAL,
                outdoor_pressure REAL,
                outdoor_wind REAL,
                outdoor_humidity REAL,
                timestamp TEXT
            );""")
            server_cur.execute("""INSERT INTO raw_data 
                (operator_fio, operator_login, operator_password, operator_high_priority, operator_logs,
                 cell_id, cell_working_status, cell_pressure, cell_temperature, cell_pumping_speed, cell_vibrations, cell_tilt_angle,
                 outdoor_temperature, outdoor_pressure, outdoor_wind, outdoor_humidity, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("Иванов Иван Иванович", "ivanov", "pass123", 1, "лог действий",
                 1, "работает", 50.0, 20.0, 5.0, 0.1, 10.0,
                 15.0, 101.3, 3.0, 60.0, "2023-01-01 12:00:00"))
            server_conn.commit()
        # Переносим данные из raw_data
        server_cur.execute("SELECT * FROM raw_data;")
        raw_rows = server_cur.fetchall()
        col_names = [desc[0] for desc in server_cur.description]
        server_conn.close()
        # Переносим уникальных операторов в таблицу operators
        operators = {}
        for row in raw_rows:
            row_dict = dict(zip(col_names, row))
            key = row_dict.get("operator_login")
            if key and key not in operators:
                operators[key] = row_dict
        for op in operators.values():
            client_cur.execute("""
                INSERT INTO operators (fio, login, password, high_priority, logs)
                VALUES (?, ?, ?, ?, ?)
            """, (op.get("operator_fio"), op.get("operator_login"), op.get("operator_password"), op.get("operator_high_priority"), op.get("operator_logs")))
        # Переносим уникальные ячейки в таблицу cells
        cells = {}
        for row in raw_rows:
            row_dict = dict(zip(col_names, row))
            key = row_dict.get("cell_id")
            if key and key not in cells:
                cells[key] = row_dict
        for cell in cells.values():
            client_cur.execute("""
                INSERT INTO cells (cell_id, working_status, pressure, temperature, pumping_speed, vibrations, tilt_angle)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cell.get("cell_id"), cell.get("cell_working_status"), cell.get("cell_pressure"), cell.get("cell_temperature"), cell.get("cell_pumping_speed"), cell.get("cell_vibrations"), cell.get("cell_tilt_angle")))
        # Переносим данные в таблицу external_data
        external = {}
        for row in raw_rows:
            row_dict = dict(zip(col_names, row))
            key = row_dict.get("timestamp")
            if key and key not in external:
                external[key] = row_dict
        for ext in external.values():
            client_cur.execute("""
                INSERT INTO external_data (outdoor_temperature, outdoor_pressure, wind, humidity, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (ext.get("outdoor_temperature"), ext.get("outdoor_pressure"), ext.get("outdoor_wind"), ext.get("outdoor_humidity"), ext.get("timestamp")))
        # Формируем отчеты, группируя данные по минутам (средние значения)
        reports = {}
        for row in raw_rows:
            row_dict = dict(zip(col_names, row))
            minute = row_dict.get("timestamp", "")[:16]
            if minute:
                if minute not in reports:
                    reports[minute] = {"pressure": [], "temperature": [], "pumping_speed": [], "vibrations": [], "tilt_angle": []}
                reports[minute]["pressure"].append(row_dict.get("cell_pressure", 0))
                reports[minute]["temperature"].append(row_dict.get("cell_temperature", 0))
                reports[minute]["pumping_speed"].append(row_dict.get("cell_pumping_speed", 0))
                reports[minute]["vibrations"].append(row_dict.get("cell_vibrations", 0))
                reports[minute]["tilt_angle"].append(row_dict.get("cell_tilt_angle", 0))
        for minute, vals in reports.items():
            avg_pressure = sum(vals["pressure"]) / len(vals["pressure"]) if vals["pressure"] else None
            avg_temperature = sum(vals["temperature"]) / len(vals["temperature"]) if vals["temperature"] else None
            avg_pumping_speed = sum(vals["pumping_speed"]) / len(vals["pumping_speed"]) if vals["pumping_speed"] else None
            avg_vibrations = sum(vals["vibrations"]) / len(vals["vibrations"]) if vals["vibrations"] else None
            avg_tilt_angle = sum(vals["tilt_angle"]) / len(vals["tilt_angle"]) if vals["tilt_angle"] else None
            client_cur.execute("""
                INSERT INTO reports (report_time, avg_pressure, avg_temperature, avg_pumping_speed, avg_vibrations, avg_tilt_angle)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (minute, avg_pressure, avg_temperature, avg_pumping_speed, avg_vibrations, avg_tilt_angle))
    else:
        # Если выбран стандартный формат, вставляем примерные данные, если таблицы пустые
        client_cur.execute("SELECT COUNT(*) FROM operators;")
        if client_cur.fetchone()[0] == 0:
            client_cur.execute("INSERT INTO operators (fio, login, password, high_priority, logs) VALUES (?, ?, ?, ?, ?)",
                               ("Иванов Иван Иванович", "ivanov", "pass123", 1, "лог действий"))
        client_cur.execute("SELECT COUNT(*) FROM cells;")
        if client_cur.fetchone()[0] == 0:
            client_cur.execute("INSERT INTO cells (cell_id, working_status, pressure, temperature, pumping_speed, vibrations, tilt_angle) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (1, "работает", 50.0, 20.0, 5.0, 0.1, 10.0))
        client_cur.execute("SELECT COUNT(*) FROM external_data;")
        if client_cur.fetchone()[0] == 0:
            client_cur.execute("INSERT INTO external_data (outdoor_temperature, outdoor_pressure, wind, humidity, timestamp) VALUES (?, ?, ?, ?, ?)",
                               (15.0, 101.3, 3.0, 60.0, "2023-01-01 12:00:00"))
        client_cur.execute("SELECT COUNT(*) FROM reports;")
        if client_cur.fetchone()[0] == 0:
            client_cur.execute("INSERT INTO reports (report_time, avg_pressure, avg_temperature, avg_pumping_speed, avg_vibrations, avg_tilt_angle) VALUES (?, ?, ?, ?, ?, ?)",
                               ("2023-01-01 12:00", 50.0, 20.0, 5.0, 0.1, 10.0))
    client_conn.commit()
    client_conn.close()
    
# конец Part 1
# класс виджета для отображения состояния подключенной базы
class DBStatusWidget(QGroupBox):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.db_info = None
        self.connected = False
        self.initUI()
    def initUI(self):
        self.setTitle(f"бд {self.index + 1}")
        self.setFixedSize(220, 220)
        self.layout = QVBoxLayout()
        self.name_label = QLabel("имя: ")
        self.type_label = QLabel("тип: ")
        self.property_label = QLabel("свойство: ")
        self.status_label = QLabel("статус: ")
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.type_label)
        self.layout.addWidget(self.property_label)
        self.layout.addWidget(self.status_label)
        btn_layout = QHBoxLayout()
        self.disconnect_btn = QPushButton("отключиться")
        self.instruction_btn = QPushButton("инструкция")
        btn_layout.addWidget(self.disconnect_btn)
        btn_layout.addWidget(self.instruction_btn)
        self.layout.addLayout(btn_layout)
        self.disconnect_btn.clicked.connect(self.disconnect_db)
        self.instruction_btn.clicked.connect(self.show_instructions)
        self.setLayout(self.layout)
    def update_info(self, db_info):
        self.db_info = db_info
        self.connected = True
        self.name_label.setText(f"имя: {db_info.get('name', '')}")
        self.type_label.setText(f"тип: {db_info.get('type', '')}")
        self.property_label.setText(f"свойство: {db_info.get('property', '')}")
        self.status_label.setText(f"статус: {db_info.get('status', '')}")
    def is_connected(self):
        return self.connected
    def disconnect_db(self):
        if self.connected:
            reply = QMessageBox.question(self, "отключиться", "вы уверены, что хотите отключиться от этой бд?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db_info = None
                self.connected = False
                self.name_label.setText("имя: ")
                self.type_label.setText("тип: ")
                self.property_label.setText("свойство: ")
                self.status_label.setText("статус: отключено")
    def show_instructions(self):
        if self.db_info and "remote_instructions" in self.db_info:
            show_instruction_dialog("инструкция для подключения", self.db_info["remote_instructions"])
        else:
            show_instruction_dialog("инструкция", "информация отсутствует")

# окно для управления экспериментальными функциями
class ManageWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("управление данными бд")
        self.setFixedSize(600, 220)
        self.db_conn = None
        self.timers = {}
        self.current_values = {
            "cells": {
                "pressure": 50.0,
                "temperature": 20.0,
                "pumping_speed": 5.0,
                "vibrations": 0.1,
                "tilt_angle": 10.0
            },
            "external": {
                "outdoor_temperature": 15.0,
                "outdoor_pressure": 101.3,
                "wind": 3.0,
                "humidity": 60.0
            }
        }
        self.cell_statuses = ["работает", "не работает", "требует обслуживания"]
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Верхняя панель с выбором БД
        top_layout = QHBoxLayout()
        self.db_select_btn = QPushButton("выбрать бд")
        self.db_select_btn.clicked.connect(self.select_db)
        self.db_path_label = QLabel("бд не выбрана")
        top_layout.addWidget(self.db_select_btn)
        top_layout.addWidget(self.db_path_label, 1)
        layout.addLayout(top_layout)
        
        # Создаем вкладки для разных таблиц
        self.tabs = QTabWidget()
        
        # Вкладка для ячеек (cells)
        cells_tab = QWidget()
        cells_layout = QVBoxLayout(cells_tab)
        cells_btn_layout = QHBoxLayout()
        
        self.cells_start_btn = QPushButton("запуск генерации ячеек")
        self.cells_start_btn.clicked.connect(lambda: self.toggle_timer("cells"))
        cells_btn_layout.addWidget(self.cells_start_btn)
        
        self.change_random_cell_btn = QPushButton("изменить случайную ячейку")
        self.change_random_cell_btn.clicked.connect(self.change_random_cell)
        cells_btn_layout.addWidget(self.change_random_cell_btn)
        
        cells_layout.addLayout(cells_btn_layout)
        self.cells_status = QTextEdit()
        self.cells_status.setReadOnly(True)
        self.cells_status.setMaximumHeight(80)
        cells_layout.addWidget(self.cells_status)
        
        # Вкладка для окружающей среды (external_data)
        env_tab = QWidget()
        env_layout = QVBoxLayout(env_tab)
        self.env_start_btn = QPushButton("запуск генерации окружающей среды")
        self.env_start_btn.clicked.connect(lambda: self.toggle_timer("env"))
        env_layout.addWidget(self.env_start_btn)
        self.env_status = QTextEdit()
        self.env_status.setReadOnly(True)
        self.env_status.setMaximumHeight(80)
        env_layout.addWidget(self.env_status)
        
        # Добавляем вкладки
        self.tabs.addTab(cells_tab, "ячейки")
        self.tabs.addTab(env_tab, "окружающая среда")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Обновление отображения текущих значений
        self.update_cells_display()
        self.update_env_display()

    def select_db(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "выберите файл базы данных", "", "sqlite db files (*.db)")
        if not file_path:
            return
            
        try:
            # Закрываем предыдущее соединение, если было
            if self.db_conn:
                self.db_conn.close()
                
            # Открываем новое соединение
            self.db_conn = sqlite3.connect(file_path)
            self.db_path_label.setText(f"Выбрана БД: {os.path.basename(file_path)}")
            
            # Проверяем наличие необходимых таблиц
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='cells' OR name='external_data')")
            tables = cursor.fetchall()
            tables = [t[0] for t in tables]
            
            if 'cells' not in tables or 'external_data' not in tables:
                QMessageBox.warning(self, "внимание", "В выбранной БД нет таблиц cells или external_data.\n"
                                   "Пожалуйста, сначала нормализуйте базу.")
            
            # Загружаем последние значения
            self.load_current_values()
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"не удалось открыть базу: {str(e)}")
            if self.db_conn:
                self.db_conn.close()
                self.db_conn = None

    def load_current_values(self):
        """Загружаем последние значения из БД"""
        if not self.db_conn:
            return
            
        try:
            cursor = self.db_conn.cursor()
            
            # Загружаем значения ячеек
            cursor.execute("SELECT pressure, temperature, pumping_speed, vibrations, tilt_angle FROM cells LIMIT 1")
            row = cursor.fetchone()
            if row:
                self.current_values["cells"]["pressure"] = row[0] or 50.0
                self.current_values["cells"]["temperature"] = row[1] or 20.0
                self.current_values["cells"]["pumping_speed"] = row[2] or 5.0
                self.current_values["cells"]["vibrations"] = row[3] or 0.1
                self.current_values["cells"]["tilt_angle"] = row[4] or 10.0
                
            # Загружаем значения окружающей среды
            cursor.execute("SELECT outdoor_temperature, outdoor_pressure, wind, humidity FROM external_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                self.current_values["external"]["outdoor_temperature"] = row[0] or 15.0
                self.current_values["external"]["outdoor_pressure"] = row[1] or 101.3
                self.current_values["external"]["wind"] = row[2] or 3.0
                self.current_values["external"]["humidity"] = row[3] or 60.0
                
            # Обновляем отображение
            self.update_cells_display()
            self.update_env_display()
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"не удалось загрузить данные: {str(e)}")

    def toggle_timer(self, timer_type):
        """Запускает или останавливает таймер для генерации данных"""
        if timer_type in self.timers and self.timers[timer_type].isActive():
            self.timers[timer_type].stop()
            if timer_type == "cells":
                self.cells_start_btn.setText("запуск генерации ячеек")
            else:
                self.env_start_btn.setText("запуск генерации окружающей среды")
        else:
            if not self.db_conn:
                QMessageBox.warning(self, "внимание", "сначала выберите БД")
                return
                
            # Создаем и запускаем таймер
            timer = QTimer(self)
            if timer_type == "cells":
                timer.timeout.connect(self.generate_cells_data)
                self.cells_start_btn.setText("остановить генерацию ячеек")
            else:
                timer.timeout.connect(self.generate_env_data)
                self.env_start_btn.setText("остановить генерацию окружающей среды")
                
            timer.start(1000)  # 1 секунда
            self.timers[timer_type] = timer

    def generate_cells_data(self):
        """Генерирует и записывает случайные данные для ячеек"""
        if not self.db_conn:
            return
            
        try:
            # Логичные небольшие изменения значений
            self.current_values["cells"]["pressure"] += random.uniform(-0.3, 0.3)
            self.current_values["cells"]["temperature"] += random.uniform(-0.1, 0.1)
            self.current_values["cells"]["pumping_speed"] += random.uniform(-0.1, 0.1)
            self.current_values["cells"]["vibrations"] += random.uniform(-0.01, 0.01)
            self.current_values["cells"]["tilt_angle"] += random.uniform(-0.05, 0.05)
            
            # Ограничения значений в разумных пределах
            self.current_values["cells"]["pressure"] = max(40.0, min(60.0, self.current_values["cells"]["pressure"]))
            self.current_values["cells"]["temperature"] = max(15.0, min(25.0, self.current_values["cells"]["temperature"]))
            self.current_values["cells"]["pumping_speed"] = max(3.0, min(7.0, self.current_values["cells"]["pumping_speed"]))
            self.current_values["cells"]["vibrations"] = max(0.01, min(0.2, self.current_values["cells"]["vibrations"]))
            self.current_values["cells"]["tilt_angle"] = max(8.0, min(12.0, self.current_values["cells"]["tilt_angle"]))
            
            # Обновление базы данных
            cursor = self.db_conn.cursor()
            
            # Обновляем таблицу cells
            cursor.execute("""
                UPDATE cells 
                SET pressure = ?, temperature = ?, pumping_speed = ?, vibrations = ?, tilt_angle = ?
                WHERE cell_id = 1
            """, (
                self.current_values["cells"]["pressure"],
                self.current_values["cells"]["temperature"],
                self.current_values["cells"]["pumping_speed"],
                self.current_values["cells"]["vibrations"],
                self.current_values["cells"]["tilt_angle"]
            ))
            
            # ВАЖНО: Также обновляем таблицу raw_data для синхронизации с модулями 2 и 3
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Проверяем существование таблицы raw_data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='raw_data'")
            if cursor.fetchone():
                # Если таблица существует, обновляем последнюю запись или вставляем новую
                cursor.execute("SELECT COUNT(*) FROM raw_data")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Обновляем последнюю запись
                    cursor.execute("""
                        UPDATE raw_data 
                        SET cell_pressure = ?, 
                            cell_temperature = ?, 
                            cell_pumping_speed = ?, 
                            cell_vibrations = ?, 
                            cell_tilt_angle = ?,
                            timestamp = ?
                        WHERE id = (SELECT MAX(id) FROM raw_data)
                    """, (
                        self.current_values["cells"]["pressure"],
                        self.current_values["cells"]["temperature"],
                        self.current_values["cells"]["pumping_speed"],
                        self.current_values["cells"]["vibrations"],
                        self.current_values["cells"]["tilt_angle"],
                        timestamp
                    ))
                else:
                    # Вставляем новую запись с текущими значениями окружающей среды
                    cursor.execute("""
                        INSERT INTO raw_data 
                        (cell_pressure, cell_temperature, cell_pumping_speed, cell_vibrations, cell_tilt_angle,
                         outdoor_temperature, outdoor_pressure, outdoor_wind, outdoor_humidity, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        self.current_values["cells"]["pressure"],
                        self.current_values["cells"]["temperature"],
                        self.current_values["cells"]["pumping_speed"],
                        self.current_values["cells"]["vibrations"],
                        self.current_values["cells"]["tilt_angle"],
                        self.current_values["external"]["outdoor_temperature"],
                        self.current_values["external"]["outdoor_pressure"],
                        self.current_values["external"]["wind"],
                        self.current_values["external"]["humidity"],
                        timestamp
                    ))
            
            self.db_conn.commit()
            print(f"Обновлены данные ячеек: давление={self.current_values['cells']['pressure']:.2f}, температура={self.current_values['cells']['temperature']:.2f}")
            
            # Обновление отображения
            self.update_cells_display()
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"ошибка генерации данных ячеек: {str(e)}")
            print(f"Ошибка в generate_cells_data: {e}")
            # Исправляем ошибку с неопределенной переменной timer_type
            if hasattr(self, 'timers') and "cells" in self.timers:
                self.timers["cells"].stop()
                if hasattr(self, 'cells_start_btn'):
                    self.cells_start_btn.setText("запуск генерации ячеек")

    def generate_env_data(self):
        """Генерирует и записывает случайные данные для окружающей среды"""
        if not self.db_conn:
            return
            
        try:
            # Логичные небольшие изменения значений
            self.current_values["external"]["outdoor_temperature"] += random.uniform(-0.2, 0.2)
            self.current_values["external"]["outdoor_pressure"] += random.uniform(-0.05, 0.05)
            self.current_values["external"]["wind"] += random.uniform(-0.2, 0.2)
            self.current_values["external"]["humidity"] += random.uniform(-0.5, 0.5)
            
            # Ограничения значений в разумных пределах
            self.current_values["external"]["outdoor_temperature"] = max(-5.0, min(35.0, self.current_values["external"]["outdoor_temperature"]))
            self.current_values["external"]["outdoor_pressure"] = max(99.0, min(103.0, self.current_values["external"]["outdoor_pressure"]))
            self.current_values["external"]["wind"] = max(0.0, min(10.0, self.current_values["external"]["wind"]))
            self.current_values["external"]["humidity"] = max(30.0, min(90.0, self.current_values["external"]["humidity"]))
            
            # Обновление базы данных
            cursor = self.db_conn.cursor()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Обновляем таблицу external_data
            cursor.execute("""
                INSERT INTO external_data (outdoor_temperature, outdoor_pressure, wind, humidity, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.current_values["external"]["outdoor_temperature"],
                self.current_values["external"]["outdoor_pressure"],
                self.current_values["external"]["wind"],
                self.current_values["external"]["humidity"],
                timestamp
            ))
            
            # ВАЖНО: Также обновляем таблицу raw_data для синхронизации с модулями 2 и 3
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='raw_data'")
            if cursor.fetchone():
                # Если таблица существует, обновляем последнюю запись
                cursor.execute("SELECT COUNT(*) FROM raw_data")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Обновляем данные окружающей среды в последней записи
                    cursor.execute("""
                        UPDATE raw_data 
                        SET outdoor_temperature = ?, 
                            outdoor_pressure = ?, 
                            outdoor_wind = ?, 
                            outdoor_humidity = ?,
                            timestamp = ?
                        WHERE id = (SELECT MAX(id) FROM raw_data)
                    """, (
                        self.current_values["external"]["outdoor_temperature"],
                        self.current_values["external"]["outdoor_pressure"],
                        self.current_values["external"]["wind"],
                        self.current_values["external"]["humidity"],
                        timestamp
                    ))
                else:
                    # Вставляем новую запись
                    cursor.execute("""
                        INSERT INTO raw_data 
                        (cell_pressure, cell_temperature, cell_pumping_speed, cell_vibrations, cell_tilt_angle,
                         outdoor_temperature, outdoor_pressure, outdoor_wind, outdoor_humidity, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        self.current_values["cells"]["pressure"],
                        self.current_values["cells"]["temperature"],
                        self.current_values["cells"]["pumping_speed"],
                        self.current_values["cells"]["vibrations"],
                        self.current_values["cells"]["tilt_angle"],
                        self.current_values["external"]["outdoor_temperature"],
                        self.current_values["external"]["outdoor_pressure"],
                        self.current_values["external"]["wind"],
                        self.current_values["external"]["humidity"],
                        timestamp
                    ))
            
            self.db_conn.commit()
            print(f"Обновлены данные окружающей среды: температура={self.current_values['external']['outdoor_temperature']:.2f}, давление={self.current_values['external']['outdoor_pressure']:.2f}")
            
            # Обновление отображения
            self.update_env_display()
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"ошибка генерации данных окружающей среды: {str(e)}")
            print(f"Ошибка в generate_env_data: {e}")
            if hasattr(self, 'timers') and "env" in self.timers:
                self.timers["env"].stop()
                if hasattr(self, 'env_start_btn'):
                    self.env_start_btn.setText("запуск генерации окружающей среды")

    def change_random_cell(self):
        """Изменяет состояние случайной ячейки"""
        if not self.db_conn:
            QMessageBox.warning(self, "внимание", "сначала выберите БД")
            return
            
        try:
            cursor = self.db_conn.cursor()
            
            # Получаем количество ячеек
            cursor.execute("SELECT COUNT(*) FROM cells")
            count = cursor.fetchone()[0]
            
            if count == 0:
                QMessageBox.warning(self, "внимание", "в таблице нет ячеек")
                return
                
            # Выбираем случайную ячейку
            random_cell_id = random.randint(1, count)
            random_status = random.choice(self.cell_statuses)
            
            # Меняем статус ячейки
            cursor.execute("""
                UPDATE cells 
                SET working_status = ?
                WHERE cell_id = ?
            """, (random_status, random_cell_id))
            self.db_conn.commit()
            
            QMessageBox.information(self, "успех", f"ячейка {random_cell_id} теперь: {random_status}")
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"ошибка изменения состояния ячейки: {str(e)}")

    def update_cells_display(self):
        """Обновляет отображение текущих значений ячеек"""
        values = self.current_values["cells"]
        text = (f"давление: {values['pressure']:.2f}\n"
                f"температура: {values['temperature']:.2f} °C\n"
                f"скорость откачки: {values['pumping_speed']:.2f}\n"
                f"вибрации: {values['vibrations']:.2f}\n"
                f"угол наклона: {values['tilt_angle']:.2f}°")
        self.cells_status.setText(text)

    def update_env_display(self):
        """Обновляет отображение текущих значений окружающей среды"""
        values = self.current_values["external"]
        text = (f"уличная температура: {values['outdoor_temperature']:.2f} °C\n"
                f"атмосферное давление: {values['outdoor_pressure']:.2f} кПа\n"
                f"скорость ветра: {values['wind']:.2f} м/с\n"
                f"влажность: {values['humidity']:.2f}%")
        self.env_status.setText(text)

# окно для просмотра базы данных с выбором таблицы
class DBViewerWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("просмотр бд")
        self.setFixedSize(600, 200)
        self.initUI()
    def initUI(self):
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.select_btn = QPushButton("выбрать бд")
        self.select_btn.clicked.connect(self.select_db)
        self.table_combo = QComboBox()   # комбобокс для выбора таблицы
        top_layout.addWidget(self.select_btn)
        top_layout.addWidget(self.table_combo)
        layout.addLayout(top_layout)
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)
    def select_db(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "выберите файл базы данных", "", "sqlite db files (*.db)")
        if not file_path:
            return
        try:
            conn = sqlite3.connect(file_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()
            if not tables:
                QMessageBox.information(self, "информация", "в этой базе нет таблиц")
                conn.close()
                return
            self.table_combo.clear()
            for t in tables:
                self.table_combo.addItem(t[0])
            self.load_table(self.table_combo.currentText(), conn)
            self.table_combo.currentIndexChanged.connect(lambda: self.load_table(self.table_combo.currentText(), conn))
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"не удалось открыть базу: {str(e)}")
    def load_table(self, table_name, conn):
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            col_names = [desc[0] for desc in cur.description]
            self.populate_table(col_names, rows)
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"не удалось загрузить данные: {str(e)}")
    def populate_table(self, col_names, rows):
        self.table_widget.clear()
        self.table_widget.setColumnCount(len(col_names))
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setHorizontalHeaderLabels(col_names)
        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                item = QTableWidgetItem(str(cell))
                self.table_widget.setItem(row_idx, col_idx, item)

# диалог нормализации БД
class NormalizeDialog(QDialog):
    def __init__(self, connected_dbs, parent=None):
        super().__init__(parent)
        self.connected_dbs = connected_dbs
        self.server_db = None
        self.client_db = None
        self.use_standard = False
        self.setWindowTitle("нормализовать бд")
        self.setWindowModality(Qt.NonModal)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Всегда создаем два комбобокса независимо от количества подключенных БД
        self.server_combo = QComboBox()
        self.client_combo = QComboBox()
        
        # Наполняем списки БД
        for db in self.connected_dbs:
            self.server_combo.addItem(f"{db['name']} ({db['type']})", db)
            self.client_combo.addItem(f"{db['name']} ({db['type']})", db)
            
        self.server_combo.currentIndexChanged.connect(self.update_client_combo)
        
        layout.addWidget(QLabel("выберите бд-сервер:"))
        layout.addWidget(self.server_combo)
        layout.addWidget(QLabel("выберите бд-клиент:"))
        layout.addWidget(self.client_combo)
        
        self.standard_btn = QPushButton("стандартный формат")
        self.standard_btn.clicked.connect(self.use_standard_format)
        layout.addWidget(self.standard_btn)
        
        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("подтвердить")
        self.close_btn = QPushButton("закрыть")
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Единый обработчик для кнопки подтверждения
        self.confirm_btn.clicked.connect(self.on_confirm)
        self.close_btn.clicked.connect(self.close)
        
        # Инициализация данных, если списки не пусты
        if self.server_combo.count() > 0:
            self.server_db = self.server_combo.currentData()
            
    def update_client_combo(self):
        if self.server_combo.count() == 0:
            return
            
        selected_server = self.server_combo.currentData()
        self.server_db = selected_server
        
        current_client = self.client_combo.currentData()
        self.client_combo.clear()
        
        # Наполняем список клиентских БД, исключая выбранную серверную
        for db in self.connected_dbs:
            if db == selected_server:
                continue
            self.client_combo.addItem(f"{db['name']} ({db['type']})", db)
            
        # Если то же самое БД используется как сервер и клиент
        if len(self.connected_dbs) == 1:
            self.client_combo.addItem(f"{selected_server['name']} ({selected_server['type']})", selected_server)
            
    def use_standard_format(self):
        self.use_standard = True
        self.server_combo.setEnabled(False)
        self.server_combo.setStyleSheet("background-color: lightgray;")
        self.server_db = get_standard_data()
        
    def on_confirm(self):
        # Проверяем наличие клиентской БД
        if self.client_combo.count() == 0 and not self.use_standard:
            QMessageBox.warning(self, "ошибка", "нет доступной бд-клиента")
            return
            
        # Если есть выбранная клиентская БД, получаем её
        if self.client_combo.count() > 0:
            self.client_db = self.client_combo.currentData()
        elif len(self.connected_dbs) == 1:
            # Если одна БД, используем её как клиент
            self.client_db = self.connected_dbs[0]
        else:
            QMessageBox.warning(self, "ошибка", "выберите бд-клиента")
            return
            
        # Подтверждение нормализации
        reply = QMessageBox.question(self, "подтверждение нормализации",
                                    ("данные из бд-сервера будут перенесены в бд-клиент и пройдут нормализацию до 3-х уровней.\nвы подтверждаете?"),
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                normalize_database(self.server_db["property"], self.client_db["property"], self.use_standard)
            except Exception as e:
                QMessageBox.critical(self, "ошибка нормализации", f"нормализация не выполнена:\n{str(e)}")
                return
            self.show_success_message()
            
    def show_success_message(self):
        def show_msg():
            QMessageBox.information(self, "успех", "нормализация бд успешно выполнена")
            self.close()
        QTimer.singleShot(0, show_msg)

# диалог создания базы данных
class CreateDBDialog(QDialog):
    dbCreated = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.db_info = {}
        self.setWindowTitle("создание бд")
        self.setWindowModality(Qt.NonModal)
        self.initUI()
    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel("создать sqlite бд:")
        layout.addWidget(label)
        self.sqlite_btn = QPushButton("sqlite")
        layout.addWidget(self.sqlite_btn)
        self.back_btn = QPushButton("назад")
        layout.addWidget(self.back_btn, alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.sqlite_btn.clicked.connect(self.create_sqlite_db)
        self.back_btn.clicked.connect(self.close)
    def create_sqlite_db(self):
        dir_path = QFileDialog.getExistingDirectory(self, "выберите папку для создания бд")
        if not dir_path:
            return
        # Запрашиваем имя файла БД у пользователя
        from PyQt5.QtWidgets import QInputDialog
        db_name, ok = QInputDialog.getText(self, 'Имя базы данных', 
                                          'Введите имя файла базы данных (без расширения):',
                                          text='new_database')
        if not ok or not db_name.strip():
            return
        
        # Добавляем расширение .db если его нет
        if not db_name.endswith('.db'):
            db_name += '.db'
        
        file_path = os.path.join(dir_path, db_name)
        if os.path.exists(file_path):
            reply = QMessageBox.question(self, "файл существует",
                                         f"файл {file_path} уже существует. перезаписать?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        try:
            conn = sqlite3.connect(file_path)
            # Создаем таблицу raw_data, если ее нет, и вставляем примерную строку
            conn.execute("""CREATE TABLE IF NOT EXISTS raw_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator_fio TEXT,
                operator_login TEXT,
                operator_password TEXT,
                operator_high_priority INTEGER,
                operator_logs TEXT,
                cell_id INTEGER,
                cell_working_status TEXT,
                cell_pressure REAL,
                cell_temperature REAL,
                cell_pumping_speed REAL,
                cell_vibrations REAL,
                cell_tilt_angle REAL,
                outdoor_temperature REAL,
                outdoor_pressure REAL,
                outdoor_wind REAL,
                outdoor_humidity REAL,
                timestamp TEXT
            );""")
            conn.execute("""INSERT INTO raw_data 
                (operator_fio, operator_login, operator_password, operator_high_priority, operator_logs,
                 cell_id, cell_working_status, cell_pressure, cell_temperature, cell_pumping_speed, cell_vibrations, cell_tilt_angle,
                 outdoor_temperature, outdoor_pressure, outdoor_wind, outdoor_humidity, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("Иванов Иван Иванович", "ivanov", "pass123", 1, "лог действий",
                 1, "работает", 50.0, 20.0, 5.0, 0.1, 10.0,
                 15.0, 101.3, 3.0, 60.0, "2023-01-01 12:00:00"))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "успех", f"sqlite бд создана по пути:\n{file_path}")
            remote_instructions = (
                "для подключения к этой базе удаленно используйте следующие данные:\n"
                "ip: <ip>\n"
                "порт: <порт>\n"
                f"имя бд: {os.path.basename(file_path)}\n"
                "пользователь: admin\n"
                "пароль: admin"
            )
            instr_file = os.path.join(dir_path, "db_instructions.txt")
            try:
                with open(instr_file, "w", encoding="utf-8") as f:
                    f.write(remote_instructions)
            except Exception as e:
                QMessageBox.warning(self, "ошибка записи", f"не удалось записать инструкцию в файл:\n{str(e)}")
            show_instruction_dialog("подключение", 
                "для подключения к созданной бд используйте:\n"
                " - локальное подключение: выберите 'подключиться к бд' -> 'локальная бд'\n"
                " - удаленное подключение: выберите 'подключиться к бд' -> 'удаленная бд'\n\n" +
                remote_instructions)
            self.db_info = {
                "name": os.path.basename(file_path),
                "type": "sqlite (local)",
                "property": file_path,
                "ping": "",
                "status": "создана",
                "remote_instructions": remote_instructions
            }
            self.dbCreated.emit(self.db_info)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"не удалось создать sqlite бд:\n{str(e)}")

# диалог подключения к базе данных (только для SQLite)
class ConnectDBDialog(QDialog):
    dbConnected = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.db_info = {}
        self.setWindowTitle("подключение к бд")
        self.setWindowModality(Qt.NonModal)
        self.initUI()
    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel("выберите тип подключения к бд (только локально):")
        layout.addWidget(label)
        self.local_btn = QPushButton("локальная бд")
        layout.addWidget(self.local_btn)
        self.back_btn = QPushButton("назад")
        layout.addWidget(self.back_btn, alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.local_btn.clicked.connect(self.connect_local)
        self.back_btn.clicked.connect(self.close)
    def connect_local(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "выберите файл sqlite бд для подключения", "", "sqlite db files (*.db)")
        if not file_path:
            return
        if os.path.exists(file_path):
            QMessageBox.information(self, "успех", f"подключение к локальной бд успешно выполнено:\n{file_path}")
            remote_instructions = (
                "для подключения к этой базе удаленно используйте следующие данные:\n"
                "ip: <ip>\n"
                "порт: <порт>\n"
                f"имя бд: {os.path.basename(file_path)}\n"
                "пользователь: admin\n"
                "пароль: admin"
            )
            self.db_info = {
                "name": os.path.basename(file_path),
                "type": "локальная",
                "property": file_path,
                "ping": "",
                "status": "подключена",
                "remote_instructions": remote_instructions
            }
            self.dbConnected.emit(self.db_info)
            self.close()
        else:
            QMessageBox.critical(self, "ошибка", "выбранный файл не существует.")

# конец Part 2
# класс виджета для отображения информации о подключенной базе
class DBStatusWidget(QGroupBox):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.db_info = None
        self.connected = False
        self.initUI()
    def initUI(self):
        self.setTitle(f"бд {self.index + 1}")
        self.setFixedSize(220, 220)
        self.layout = QVBoxLayout()
        self.name_label = QLabel("имя: ")
        self.type_label = QLabel("тип: ")
        self.property_label = QLabel("свойство: ")
        self.status_label = QLabel("статус: ")
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.type_label)
        self.layout.addWidget(self.property_label)
        self.layout.addWidget(self.status_label)
        btn_layout = QHBoxLayout()
        self.disconnect_btn = QPushButton("отключиться")
        self.instruction_btn = QPushButton("инструкция")
        btn_layout.addWidget(self.disconnect_btn)
        btn_layout.addWidget(self.instruction_btn)
        self.layout.addLayout(btn_layout)
        self.disconnect_btn.clicked.connect(self.disconnect_db)
        self.instruction_btn.clicked.connect(self.show_instructions)
        self.setLayout(self.layout)
    def update_info(self, db_info):
        self.db_info = db_info
        self.connected = True
        self.name_label.setText(f"имя: {db_info.get('name', '')}")
        self.type_label.setText(f"тип: {db_info.get('type', '')}")
        self.property_label.setText(f"свойство: {db_info.get('property', '')}")
        self.status_label.setText(f"статус: {db_info.get('status', '')}")
    def is_connected(self):
        return self.connected
    def disconnect_db(self):
        if self.connected:
            reply = QMessageBox.question(self, "отключиться", "вы уверены, что хотите отключиться от этой бд?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db_info = None
                self.connected = False
                self.name_label.setText("имя: ")
                self.type_label.setText("тип: ")
                self.property_label.setText("свойство: ")
                self.status_label.setText("статус: отключено")
    def show_instructions(self):
        if self.db_info and "remote_instructions" in self.db_info:
            show_instruction_dialog("инструкция для подключения", self.db_info["remote_instructions"])
        else:
            show_instruction_dialog("инструкция", "информация отсутствует")

# главное окно приложения
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.max_db = 5
        self.db_status_widgets = []
        self.create_db_dialog = None
        self.connect_db_dialog = None
        self.normalize_db_dialog = None
        self.initUI()
    def initUI(self):
        self.setWindowTitle("db manager")
        self.create_db_btn = QPushButton("создать бд")
        self.create_db_btn.setFixedSize(150, 50)
        self.connect_db_btn = QPushButton("подключиться к бд")
        self.connect_db_btn.setFixedSize(150, 50)
        self.normalize_db_btn = QPushButton("нормализовать бд")
        self.normalize_db_btn.setFixedSize(150, 50)
        self.create_db_btn.clicked.connect(self.open_create_db_dialog)
        self.connect_db_btn.clicked.connect(self.open_connect_db_dialog)
        self.normalize_db_btn.clicked.connect(self.open_normalize_db_dialog)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.create_db_btn)
        btn_layout.addWidget(self.connect_db_btn)
        btn_layout.addWidget(self.normalize_db_btn)
        self.status_group = QGroupBox("статус подключенных бд")
        status_layout = QHBoxLayout()
        for i in range(self.max_db):
            widget = DBStatusWidget(i)
            self.db_status_widgets.append(widget)
            status_layout.addWidget(widget)
        self.status_group.setLayout(status_layout)
        self.manage_group = ManageWidget()  # окно управления БД
        self.viewer_group = DBViewerWidget()  # окно просмотра базы
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.manage_group)
        bottom_layout.addWidget(self.viewer_group)
        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.status_group)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
    def get_connected_db_info(self):
        info_list = []
        for widget in self.db_status_widgets:
            if widget.is_connected() and widget.db_info is not None:
                info_list.append(widget.db_info)
        return info_list
    def add_db_status(self, db_info):
        for widget in self.db_status_widgets:
            if not widget.is_connected():
                widget.update_info(db_info)
                return
        QMessageBox.warning(self, "максимум бд", "достигнуто максимальное количество подключенных бд.")
    def open_create_db_dialog(self):
        try:
            dialog = CreateDBDialog()
            dialog.dbCreated.connect(self.add_db_status)
            dialog.finished.connect(lambda: setattr(self, 'create_db_dialog', None))
            self.create_db_dialog = dialog
            dialog.show()
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"при открытии диалога создания бд произошла ошибка:\n{str(e)}")
    def open_connect_db_dialog(self):
        try:
            dialog = ConnectDBDialog()
            dialog.dbConnected.connect(self.add_db_status)
            dialog.finished.connect(lambda: setattr(self, 'connect_db_dialog', None))
            self.connect_db_dialog = dialog
            dialog.show()
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"при открытии диалога подключения к бд произошла ошибка:\n{str(e)}")
    def open_normalize_db_dialog(self):
        connected = self.get_connected_db_info()
        # Всегда открываем диалог нормализации, даже если список пуст
        dialog = NormalizeDialog(connected, self)
        self.normalize_db_dialog = dialog
        dialog.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())


