import sys             # для системных параметров
import os              # для работы с файловой системой
import sqlite3         # для работы с sqlite базами
import time            # для измерения времени
import random          # для генерации случайных значений

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QTextEdit, QDialog, QMessageBox,
    QFileDialog, QFormLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QTabWidget, QCheckBox, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

# глобальный список для хранения открытых окон (чтобы они не удалялись сборщиком мусора)
activeDialogs = []

def show_instruction_dialog(title, instruction_text):
    # функция для показа диалогового окна с инструкцией
    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.setWindowModality(Qt.NonModal)
    layout = QVBoxLayout(dialog)
    text_edit = QTextEdit()
    text_edit.setReadOnly(True)
    text_edit.setText(instruction_text)
    text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
    layout.addWidget(text_edit)
    ok_button = QPushButton("ok")
    ok_button.clicked.connect(dialog.close)
    layout.addWidget(ok_button)
    dialog.setAttribute(Qt.WA_DeleteOnClose, True)
    activeDialogs.append(dialog)
    dialog.finished.connect(lambda _: activeDialogs.remove(dialog))
    dialog.show()

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
    
    # Удаляем старые данные из таблиц
    client_cur.execute("DELETE FROM operators;")
    client_cur.execute("DELETE FROM cells;")
    client_cur.execute("DELETE FROM external_data;")
    client_cur.execute("DELETE FROM reports;")
    
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
        working_status INTEGER,
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
    print("Таблица cells создана или уже существует.")  # Отладочное сообщение
    
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
            client_cur.execute("""INSERT INTO operators (fio, login, password, high_priority, logs)
                                  VALUES (?, ?, ?, ?, ?)""",
                               (op.get("operator_fio"), op.get("operator_login"), op.get("operator_password"), op.get("operator_high_priority"), op.get("operator_logs")))
        
        # Переносим уникальные ячейки в таблицу cells
        cells = {}
        for row in raw_rows:
            row_dict = dict(zip(col_names, row))
            key = row_dict.get("cell_id")
            if key and key not in cells:
                cells[key] = row_dict
        for cell in cells.values():
            working_status = 1 if cell.get("cell_working_status") == "работает" else 0
            client_cur.execute("""INSERT INTO cells (cell_id, working_status, pressure, temperature, pumping_speed, vibrations, tilt_angle)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)""",
                               (cell.get("cell_id"), working_status, cell.get("cell_pressure"), cell.get("cell_temperature"), cell.get("cell_pumping_speed"), cell.get("cell_vibrations"), cell.get("cell_tilt_angle")))
            print(f"Добавлена ячейка: {cell.get('cell_id')} с статусом {working_status}")  # Отладочное сообщение
        
        # Переносим данные в таблицу external_data
        external = {}
        for row in raw_rows:
            row_dict = dict(zip(col_names, row))
            key = row_dict.get("timestamp")
            if key and key not in external:
                external[key] = row_dict
        for ext in external.values():
            client_cur.execute("""INSERT INTO external_data (outdoor_temperature, outdoor_pressure, wind, humidity, timestamp)
                                  VALUES (?, ?, ?, ?, ?)""",
                               (ext.get("outdoor_temperature"), ext.get("outdoor_pressure"), ext.get("outdoor_wind"), ext.get("outdoor_humidity"), ext.get("timestamp")))
        
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
            
            client_cur.execute("""INSERT INTO reports (report_time, avg_pressure, avg_temperature, avg_pumping_speed, avg_vibrations, avg_tilt_angle)
                                  VALUES (?, ?, ?, ?, ?, ?)""",
                               (minute, avg_pressure, avg_temperature, avg_pumping_speed, avg_vibrations, avg_tilt_angle))
    else:
        # Если выбран стандартный формат, вставляем примерные данные, если таблицы пустые
        client_cur.execute("SELECT COUNT(*) FROM operators;")
        if client_cur.fetchone()[0] == 0:
            client_cur.execute("INSERT INTO operators (fio, login, password, high_priority, logs) VALUES (?, ?, ?, ?, ?)",
                               ("Иванов Иван Иванович", "ivanov", "pass123", 1, "лог действий"))
        client_cur.execute("SELECT COUNT(*) FROM cells;")
        if client_cur.fetchone()[0] == 0:
            # Устанавливаем working_status как 1 (True)
            client_cur.execute("INSERT INTO cells (cell_id, working_status, pressure, temperature, pumping_speed, vibrations, tilt_angle) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (1, 1, 50.0, 20.0, 5.0, 0.1, 10.0))  # Изменено на working_status = 1
            # Добавьте остальные ячейки аналогично
            for i in range(2, 41):  # Пример для 40 ячеек
                client_cur.execute("INSERT INTO cells (cell_id, working_status, pressure, temperature, pumping_speed, vibrations, tilt_angle) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (i, 1, 50.0, 20.0, 5.0, 0.1, 10.0))  # Все ячейки работают
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
    # Добавляем сигнал для передачи пути к БД
    db_selected = pyqtSignal(str)
    # Добавляем сигнал об обновлении данных
    data_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("управление данными бд")
        self.setFixedSize(600, 220)
        self.db_conn = None
        self.db_path = None
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
            self.db_path = file_path
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
            
            # Испускаем сигнал о выбранной БД
            self.db_selected.emit(file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"не удалось открыть базу: {str(e)}")
            if self.db_conn:
                self.db_conn.close()
                self.db_conn = None
            self.db_path = None

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
            cursor = self.db_conn.cursor()
            
            # Получаем все ячейки
            cursor.execute("SELECT cell_id FROM cells")
            cells = cursor.fetchall()
            
            if not cells:
                print("Нет ячеек для обновления")
                return
                
            # Обновляем каждую ячейку
            for cell_id in cells:
                cell_id = cell_id[0]
                
                # Генерируем новые значения
                pressure = random.uniform(40.0, 60.0)
                temperature = random.uniform(15.0, 25.0)
                pumping_speed = random.uniform(3.0, 7.0)
                vibrations = random.uniform(0.01, 0.2)
                tilt_angle = random.uniform(8.0, 12.0)
                
                # Обновляем таблицу cells
                cursor.execute("""
                    UPDATE cells 
                    SET pressure = ?, temperature = ?, pumping_speed = ?, vibrations = ?, tilt_angle = ?
                    WHERE cell_id = ?
                """, (pressure, temperature, pumping_speed, vibrations, tilt_angle, cell_id))
                
                # Добавляем запись в raw_data
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO raw_data (
                        operator_fio, operator_login, operator_password, operator_high_priority, operator_logs,
                        cell_id, cell_working_status, cell_pressure, cell_temperature, cell_pumping_speed,
                        cell_vibrations, cell_tilt_angle, outdoor_temperature, outdoor_pressure,
                        outdoor_wind, outdoor_humidity, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "Иванов Иван Иванович", "ivanov", "pass123", 1, "лог действий",
                    cell_id, "работает", pressure, temperature, pumping_speed,
                    vibrations, tilt_angle, 15.0, 101.3, 3.0, 60.0, timestamp
                ))
            
            self.db_conn.commit()
            
            # Обновление отображения
            self.update_cells_display()
            
            # Отправляем сигнал об обновлении данных
            self.data_updated.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"ошибка генерации данных ячеек: {str(e)}")
            if "cells" in self.timers:
                self.timers["cells"].stop()
                self.cells_start_btn.setText("запуск генерации ячеек")

    def generate_env_data(self):
        """Генерирует и записывает случайные данные для окружающей среды"""
        if not self.db_conn:
            return
            
        try:
            # Генерируем новые значения
            outdoor_temperature = random.uniform(-5.0, 35.0)
            outdoor_pressure = random.uniform(99.0, 103.0)
            wind = random.uniform(0.0, 10.0)
            humidity = random.uniform(30.0, 90.0)
            
            # Обновление базы данных
            cursor = self.db_conn.cursor()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Добавляем запись в external_data
            cursor.execute("""
                INSERT INTO external_data (outdoor_temperature, outdoor_pressure, wind, humidity, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (outdoor_temperature, outdoor_pressure, wind, humidity, timestamp))
            
            # Добавляем запись в raw_data
            cursor.execute("""
                INSERT INTO raw_data (
                    operator_fio, operator_login, operator_password, operator_high_priority, operator_logs,
                    cell_id, cell_working_status, cell_pressure, cell_temperature, cell_pumping_speed,
                    cell_vibrations, cell_tilt_angle, outdoor_temperature, outdoor_pressure,
                    outdoor_wind, outdoor_humidity, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "Иванов Иван Иванович", "ivanov", "pass123", 1, "лог действий",
                1, "работает", 50.0, 20.0, 5.0, 0.1, 10.0,
                outdoor_temperature, outdoor_pressure, wind, humidity, timestamp
            ))
            
            self.db_conn.commit()
            
            # Обновление отображения
            self.update_env_display()
            
            # Отправляем сигнал об обновлении данных
            self.data_updated.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"ошибка генерации данных окружающей среды: {str(e)}")
            if "env" in self.timers:
                self.timers["env"].stop()
                self.env_start_btn.setText("запуск генерации окружающей среды")

    def change_random_cell(self):
        """Изменяет состояние случайной ячейки"""
        if not self.db_conn:
            QMessageBox.warning(self, "внимание", "сначала выберите БД")
            return
        
        try:
            cursor = self.db_conn.cursor()
            
            # Получаем все доступные cell_id из таблицы с более подробной информацией
            cursor.execute("SELECT cell_id, working_status FROM cells")
            all_cells = cursor.fetchall()
            
            if not all_cells:
                QMessageBox.warning(self, "внимание", "в таблице нет ячеек")
                return
            
            # Ограничиваем список первыми 40 ячейками (если их больше)
            cells_to_use = all_cells[:40] if len(all_cells) > 40 else all_cells
            
            # Выбираем случайную ячейку из списка
            random_cell = random.choice(cells_to_use)
            random_cell_id = random_cell[0]
            old_status = random_cell[1]
            
            # Меняем статус ячейки на 0 (не работает) или 1 (работает)
            new_status = 0 if old_status == 1 else 1
            cursor.execute("""UPDATE cells 
                              SET working_status = ?
                              WHERE cell_id = ?""", (new_status, random_cell_id))
            
            self.db_conn.commit()
            
            status_text = "не работает" if new_status == 0 else "работает"
            QMessageBox.information(self, "успех", f"ячейка {random_cell_id} теперь: {status_text}")
            
            # Обновляем отображение ячеек
            self.update_cells_display()
            
            # Отправляем сигнал об обновлении данных
            self.data_updated.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"ошибка изменения состояния ячейки: {str(e)}")
            import traceback
            traceback.print_exc()

    def update_cells_display(self):
        """Обновляет отображение текущих значений ячеек"""
        values = self.current_values["cells"]
        working_cells = self.get_working_cells_count()
        text = (f"давление: {values['pressure']:.2f}\n"
                f"температура: {values['temperature']:.2f} °C\n"
                f"скорость откачки: {values['pumping_speed']:.2f}\n"
                f"вибрации: {values['vibrations']:.2f}\n"
                f"угол наклона: {values['tilt_angle']:.2f}°\n"
                f"работает: {working_cells['работает']} | не работает: {working_cells['не работает']}")
        self.cells_status.setText(text)
        
    def get_working_cells_count(self):
        """Получает количество работающих и неработающих ячеек"""
        working_count = 0
        non_working_count = 0
        
        if self.db_conn:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("SELECT working_status, COUNT(*) FROM cells GROUP BY working_status")
                statuses = cursor.fetchall()
                
                for status, count in statuses:
                    if status == 1:
                        working_count = count
                    else:
                        non_working_count = count
            except Exception:
                pass
                
        return {
            "работает": working_count,
            "не работает": non_working_count
        }

    def update_env_display(self):
        """Обновляет отображение текущих значений окружающей среды"""
        values = self.current_values["external"]
        text = (f"уличная температура: {values['outdoor_temperature']:.2f} °C\n"
                f"атмосферное давление: {values['outdoor_pressure']:.2f} кПа\n"
                f"скорость ветра: {values['wind']:.2f} м/с\n"
                f"влажность: {values['humidity']:.2f}%")
        self.env_status.setText(text)

    def create_cells(self):
        """Создает ячейки в базе данных (до 40 штук)"""
        if not self.db_conn:
            QMessageBox.warning(self, "внимание", "сначала выберите БД")
            return
        
        try:
            cursor = self.db_conn.cursor()
            
            # Проверяем наличие таблицы cells
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cells'")
            if not cursor.fetchone():
                # Создаем таблицу, если ее нет
                cursor.execute('''
                    CREATE TABLE cells (
                        cell_id INTEGER PRIMARY KEY,
                        working_status INTEGER,
                        pressure REAL,
                        temperature REAL,
                        pumping_speed REAL,
                        vibrations REAL,
                        tilt_angle REAL
                    )
                ''')
                self.db_conn.commit()
            
            # Получаем текущее количество ячеек
            cursor.execute("SELECT COUNT(*) FROM cells")
            current_count = cursor.fetchone()[0]
            
            # Сколько ячеек нужно создать
            cells_to_create = 40 - current_count
            
            if cells_to_create <= 0:
                QMessageBox.information(self, "инфо", "в БД уже есть 40 ячеек")
                return
            
            # Начальный ID для новых ячеек
            start_id = current_count + 1
            
            # Создаем новые ячейки
            for i in range(start_id, start_id + cells_to_create):
                # Генерируем случайные значения для полей
                status = 1  # Устанавливаем статус по умолчанию на 1
                pressure = round(random.uniform(0.5, 10.0), 2)
                temperature = round(random.uniform(20.0, 80.0), 2)
                pumping_speed = round(random.uniform(1.0, 15.0), 2)
                vibrations = round(random.uniform(0.1, 5.0), 2)
                tilt_angle = round(random.uniform(0.0, 10.0), 2)
                
                # Добавляем ячейку в базу
                cursor.execute('''INSERT INTO cells (cell_id, working_status, pressure, temperature, 
                                              pumping_speed, vibrations, tilt_angle)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                               (i, status, pressure, temperature, pumping_speed, vibrations, tilt_angle))
            
            self.db_conn.commit()
            QMessageBox.information(self, "успех", f"создано {cells_to_create} новых ячеек")
            
            # Обновляем отображение
            self.update_cells_display()
            
            # Отправляем сигнал об обновлении данных
            self.data_updated.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "ошибка", f"ошибка создания ячеек: {str(e)}")
            import traceback
            traceback.print_exc()

# окно для просмотра базы данных с выбором таблицы
class DBViewerWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("просмотр данных бд")
        self.setFixedSize(600, 200)
        self.db_path = None
        self.current_table = "raw_data"  # Таблица по умолчанию
        self.initUI()
        
        # Таймер обновления данных
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateMeters)
        self.timer.start(200)  # Обновляем 5 раз в секунду
        
        # Словарь для хранения последних значений
        self.last_values = {}
        
        print("DBViewerWidget инициализирован")
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Верхняя панель с кнопками
        top_layout = QHBoxLayout()
        
        # Кнопка выбора БД
        self.select_db_btn = QPushButton("выбрать бд")
        self.select_db_btn.clicked.connect(self.selectDB)
        top_layout.addWidget(self.select_db_btn)
        
        # Кнопка для таблицы raw_data
        self.raw_data_btn = QPushButton("raw_data")
        self.raw_data_btn.clicked.connect(lambda: self.setTable("raw_data"))
        top_layout.addWidget(self.raw_data_btn)
        
        # Кнопка для таблицы external_data
        self.external_data_btn = QPushButton("external_data")
        self.external_data_btn.clicked.connect(lambda: self.setTable("external_data"))
        top_layout.addWidget(self.external_data_btn)
        
        # Статус
        self.status_label = QLabel("статус: не подключено")
        top_layout.addWidget(self.status_label, 1)
        
        layout.addLayout(top_layout)
        
        # Область для отображения числовых показателей
        self.meters_layout = QGridLayout()
        self.meters_group = QGroupBox("показатели")
        self.meters_group.setLayout(self.meters_layout)
        layout.addWidget(self.meters_group)
        
        # Словарь для хранения числовых индикаторов
        self.meters = {}
        
        self.setLayout(layout)
    
    def setTable(self, table_name):
        """Переключение между таблицами"""
        self.current_table = table_name
        # Выделяем активную кнопку
        self.raw_data_btn.setStyleSheet("" if table_name != "raw_data" else "background-color: #ddf;")
        self.external_data_btn.setStyleSheet("" if table_name != "external_data" else "background-color: #ddf;")
        
        # Обновляем показатели
        self.clearMeters()
        if self.db_path:
            self.createMeters()
            self.updateMeters()
    
    def selectDB(self):
        """Выбор файла базы данных"""
        file_path, _ = QFileDialog.getOpenFileName(self, "выберите файл базы данных", "", "SQLite DB (*.db)")
        if file_path:
            self.db_path = file_path
            self.status_label.setText(f"подключено: {os.path.basename(file_path)}")
            
            # Сбрасываем индикаторы и создаем новые
            self.clearMeters()
            self.createMeters()
            self.updateMeters()
    
    def clearMeters(self):
        """Очистка всех индикаторов"""
        # Удаляем все виджеты из сетки
        for i in reversed(range(self.meters_layout.count())):
            widget = self.meters_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Очищаем словарь индикаторов
        self.meters.clear()
    
    def createMeters(self):
        """Создание индикаторов для выбранной таблицы"""
        if not self.db_path:
            return
            
        try:
            # Подключаемся к БД
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем информацию о столбцах таблицы
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = cursor.fetchall()
            
            # Фильтруем, исключая id
            columns = [col for col in columns if col[1].lower() != 'id']
            
            # Создаем индикаторы для каждого столбца
            for i, col in enumerate(columns):
                col_name = col[1]
                row = i // 3  # 3 столбца в сетке
                col = i % 3
                
                # Создаем метку и индикатор
                label = QLabel(f"{col_name}:")
                value = QLabel("0.0")
                value.setStyleSheet("font-weight: bold; color: blue;")
                
                # Добавляем в сетку
                self.meters_layout.addWidget(label, row, col*2)
                self.meters_layout.addWidget(value, row, col*2+1)
                
                # Сохраняем ссылку на индикатор
                self.meters[col_name] = value
            
            conn.close()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"ошибка при создании индикаторов: {str(e)}")
    
    def updateMeters(self):
        """Обновление значений индикаторов"""
        if not self.db_path or not self.meters:
            return
            
        try:
            # Подключаемся к БД
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Проверяем существование таблицы
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.current_table}'")
            if not cursor.fetchone():
                self.status_label.setText(f"таблица {self.current_table} не найдена")
                conn.close()
                return
            
            # Получаем последнюю запись из таблицы
            try:
                cursor.execute(f"SELECT * FROM {self.current_table} ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
            except sqlite3.OperationalError:
                # Если нет столбца id, просто берем любую запись
                cursor.execute(f"SELECT * FROM {self.current_table} LIMIT 1")
                row = cursor.fetchone()
            
            if not row:
                self.status_label.setText(f"нет данных в {self.current_table}")
                conn.close()
                return
            
            # Получаем имена столбцов
            column_names = [desc[0] for desc in cursor.description]
            
            # Обновляем значения индикаторов
            for i, name in enumerate(column_names):
                if name.lower() == 'id':
                    continue
                    
                if name in self.meters:
                    value = row[i]
                    # Попытка преобразовать в число
                    try:
                        if value is not None:
                            float_value = float(value)
                            formatted_value = f"{float_value:.2f}"
                            
                            # Если значение изменилось, подсвечиваем его
                            if name not in self.last_values or self.last_values[name] != formatted_value:
                                self.meters[name].setStyleSheet("font-weight: bold; color: red;")
                                QTimer.singleShot(300, lambda m=self.meters[name]: m.setStyleSheet("font-weight: bold; color: blue;"))
                                self.last_values[name] = formatted_value
                            
                            self.meters[name].setText(formatted_value)
                        else:
                            self.meters[name].setText("N/A")
                    except (ValueError, TypeError):
                        self.meters[name].setText(str(value))
            
            conn.close()
            self.status_label.setText(f"данные из {self.current_table} обновлены")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"ошибка: {str(e)}")
    
    def set_db_from_manage(self, db_path):
        """Получает путь к БД от другого модуля"""
        if not os.path.exists(db_path):
            self.status_label.setText("ошибка: файл не существует")
            return
            
        self.db_path = db_path
        self.status_label.setText(f"подключено: {os.path.basename(db_path)}")
        
        # Сбрасываем индикаторы и создаем новые
        self.clearMeters()
        self.createMeters()
        self.updateMeters()
        
        print(f"DBViewerWidget: подключен к БД {db_path}")

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
        file_path = os.path.join(dir_path, "new_database.db")
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
        
        # Связываем сигнал выбора БД с методом обновления в DBViewerWidget
        self.manage_group.db_selected.connect(self.viewer_group.set_db_from_manage)
        
        # Связываем сигнал обновления данных с методом обновления таблицы
        self.manage_group.data_updated.connect(self.viewer_group.updateMeters)
        
        # Добавляем экспериментальный блок с кнопками
        self.experimental_group = QGroupBox("экспериментальные функции")
        experimental_layout = QVBoxLayout()
        
        # Кнопка для управления пользователями
        self.user_management_button = QPushButton("управление пользователями")
        self.user_management_button.clicked.connect(self.open_user_management_dialog)
        experimental_layout.addWidget(self.user_management_button)
        
        # Кнопка для создания ячеек
        self.create_cells_button = QPushButton("создать ячейки (до 40)")
        self.create_cells_button.clicked.connect(self.manage_group.create_cells)
        experimental_layout.addWidget(self.create_cells_button)
        
        self.experimental_group.setLayout(experimental_layout)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.manage_group)
        bottom_layout.addWidget(self.viewer_group)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.status_group)
        main_layout.addWidget(self.experimental_group)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def get_connected_db_info(self):
        info_list = []
        for widget in self.db_status_widgets:
            if widget.is_connected():
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
    
    def open_user_management_dialog(self):
        # Диалог для управления пользователями (операторами)
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление пользователями")
        dialog.setMinimumWidth(450)
        layout = QVBoxLayout(dialog)

        # Верхняя часть с пояснениями
        info_label = QLabel(
            "Этот модуль позволяет добавлять пользователей (операторов) в базу данных. "
            "Пользователи используются для авторизации в системе мониторинга нефтепроводов."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Форма для ввода данных пользователя
        form_layout = QFormLayout()
        
        fio_input = QLineEdit()
        form_layout.addRow("ФИО оператора:", fio_input)
        fio_hint = QLabel("Введите полное имя оператора (Фамилия И.О.)")
        fio_hint.setStyleSheet("color: gray; font-size: 8pt;")
        form_layout.addRow("", fio_hint)
        
        login_input = QLineEdit()
        form_layout.addRow("Логин:", login_input)
        login_hint = QLabel("Логин для входа в систему (только латинские буквы и цифры)")
        login_hint.setStyleSheet("color: gray; font-size: 8pt;")
        form_layout.addRow("", login_hint)
        
        password_input = QLineEdit()
        form_layout.addRow("Пароль:", password_input)
        password_hint = QLabel("Пароль для входа в систему (минимум 4 символа)")
        password_hint.setStyleSheet("color: gray; font-size: 8pt;")
        form_layout.addRow("", password_hint)
        
        # Выбор уровня доступа
        priority_combo = QComboBox()
        priority_combo.addItem("Базовый доступ (0)", 0)
        priority_combo.addItem("Продвинутый доступ (1)", 1)
        form_layout.addRow("Уровень доступа:", priority_combo)
        priority_hint = QLabel("Базовый - только просмотр, Продвинутый - полный доступ")
        priority_hint.setStyleSheet("color: gray; font-size: 8pt;")
        form_layout.addRow("", priority_hint)
        
        layout.addLayout(form_layout)
        
        # Выбор базы данных
        db_label = QLabel("Выберите базу данных для добавления пользователя:")
        layout.addWidget(db_label)
        
        db_combo = QComboBox()
        connected_dbs = self.get_connected_db_info()
        for i, db_info in enumerate(connected_dbs):
            db_combo.addItem(f"{db_info['name']} ({db_info['property']})", db_info)
        
        layout.addWidget(db_combo)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Добавить пользователя")
        cancel_button = QPushButton("Отмена")
        
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        # Обработчики событий
        def on_add_button_clicked():
            fio = fio_input.text().strip()
            login = login_input.text().strip()
            password = password_input.text().strip()
            high_priority = priority_combo.currentData()
            
            # Проверка заполнения данных
            if not fio:
                QMessageBox.warning(dialog, "Ошибка", "Введите ФИО оператора")
                return
            
            if not login:
                QMessageBox.warning(dialog, "Ошибка", "Введите логин")
                return
            
            if not password or len(password) < 4:
                QMessageBox.warning(dialog, "Ошибка", "Введите пароль (минимум 4 символа)")
                return
            
            # Проверка, что база данных выбрана
            if db_combo.count() == 0:
                QMessageBox.warning(dialog, "Ошибка", "Нет подключенных баз данных")
                return
            
            selected_db = db_combo.currentData()
            
            try:
                # Подключение к выбранной БД
                conn = sqlite3.connect(selected_db['property'])
                cursor = conn.cursor()
                
                # Проверка существования таблицы operators
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operators'")
                if not cursor.fetchone():
                    # Создаем таблицу, если она не существует
                    cursor.execute('''
                    CREATE TABLE operators (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fio TEXT NOT NULL,
                        login TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        high_priority INTEGER DEFAULT 0
                    )
                    ''')
                    conn.commit()
                
                # Проверка на уникальность логина
                cursor.execute("SELECT COUNT(*) FROM operators WHERE login=?", (login,))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(dialog, "Ошибка", f"Пользователь с логином '{login}' уже существует")
                    conn.close()
                    return
                
                # Добавление нового пользователя
                cursor.execute(
                    "INSERT INTO operators (fio, login, password, high_priority) VALUES (?, ?, ?, ?)",
                    (fio, login, password, high_priority)
                )
                conn.commit()
                conn.close()
                
                QMessageBox.information(
                    dialog, 
                    "Успех", 
                    f"Пользователь '{fio}' с логином '{login}' успешно добавлен в базу данных"
                )
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка при добавлении пользователя: {str(e)}")
        
        def on_cancel_button_clicked():
            dialog.reject()
        
        add_button.clicked.connect(on_add_button_clicked)
        cancel_button.clicked.connect(on_cancel_button_clicked)
        
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())


