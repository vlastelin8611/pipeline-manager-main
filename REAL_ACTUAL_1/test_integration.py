import os
import sqlite3
import threading
import time
import random
import sys

"""
Скрипт для проверки интеграции модуля 2 с основной программой.
Запускается перед запуском основной программы для гарантии того, что БД существует,
имеет правильную структуру и содержит тестовые данные.
"""

def ensure_database_exists():
    """Проверяет наличие базы данных и при необходимости создает ее"""
    if not os.path.exists("new_database.db"):
        print("БД new_database.db не существует. Создаем...")
        create_test_database("new_database.db")
    else:
        print("БД new_database.db уже существует")
        
    # Проверяем структуру таблиц
    check_and_fix_database("new_database.db")

def create_test_database(db_path):
    """Создает тестовую базу данных со всеми необходимыми таблицами"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу raw_data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS raw_data (
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
    )''')
    
    # Создаем таблицу external_data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS external_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        outdoor_temperature REAL,
        outdoor_pressure REAL,
        wind REAL,
        humidity REAL,
        timestamp TEXT
    )''')
    
    # Создаем таблицу cells
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cells (
        cell_id INTEGER PRIMARY KEY,
        working_status INTEGER,
        pressure REAL,
        temperature REAL,
        pumping_speed REAL,
        vibrations REAL,
        tilt_angle REAL
    )''')
    
    # Создаем таблицу operators
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS operators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fio TEXT,
        login TEXT,
        password TEXT,
        high_priority INTEGER,
        logs TEXT
    )''')
    
    # Создаем таблицу reports
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        report_time TEXT PRIMARY KEY,
        avg_pressure REAL,
        avg_temperature REAL,
        avg_pumping_speed REAL,
        avg_vibrations REAL,
        avg_tilt_angle REAL
    )''')
    
    conn.commit()
    conn.close()
    
    # Добавляем тестовые данные
    add_test_data(db_path)
    
def add_test_data(db_path):
    """Добавляет тестовые данные в базу"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем, есть ли операторы
    cursor.execute("SELECT COUNT(*) FROM operators")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO operators (fio, login, password, high_priority, logs) VALUES (?, ?, ?, ?, ?)",
            ("Иванов Иван Иванович", "ivanov", "pass123", 1, "лог действий")
        )
    
    # Проверяем, есть ли ячейки
    cursor.execute("SELECT COUNT(*) FROM cells")
    if cursor.fetchone()[0] == 0:
        for i in range(1, 41):
            cursor.execute(
                "INSERT INTO cells (cell_id, working_status, pressure, temperature, pumping_speed, vibrations, tilt_angle) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (i, 1, random.uniform(40, 60), random.uniform(15, 25), random.uniform(4, 7), random.uniform(0.1, 0.5), random.uniform(8, 12))
            )
    
    # Проверяем, есть ли записи external_data
    cursor.execute("SELECT COUNT(*) FROM external_data")
    if cursor.fetchone()[0] == 0:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO external_data (outdoor_temperature, outdoor_pressure, wind, humidity, timestamp) VALUES (?, ?, ?, ?, ?)",
            (random.uniform(5, 30), random.uniform(95, 105), random.uniform(0, 10), random.uniform(30, 90), current_time)
        )
    
    # Проверяем, есть ли записи raw_data
    cursor.execute("SELECT COUNT(*) FROM raw_data")
    if cursor.fetchone()[0] == 0:
        # Получаем данные оператора
        cursor.execute("SELECT * FROM operators LIMIT 1")
        operator = cursor.fetchone()
        
        # Получаем данные ячейки
        cursor.execute("SELECT * FROM cells WHERE cell_id = 1")
        cell = cursor.fetchone()
        
        # Получаем данные внешней среды
        cursor.execute("SELECT * FROM external_data ORDER BY id DESC LIMIT 1")
        external = cursor.fetchone()
        
        if operator and cell and external:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """INSERT INTO raw_data (
                    operator_fio, operator_login, operator_password, 
                    operator_high_priority, operator_logs, 
                    cell_id, cell_working_status, cell_pressure, 
                    cell_temperature, cell_pumping_speed, cell_vibrations, 
                    cell_tilt_angle, outdoor_temperature, outdoor_pressure, 
                    outdoor_wind, outdoor_humidity, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    operator[1], operator[2], operator[3], operator[4], operator[5],
                    cell[0], cell[1], cell[2], cell[3], cell[4], cell[5], cell[6],
                    external[1], external[2], external[3], external[4], current_time
                )
            )
    
    # Проверяем, есть ли отчеты
    cursor.execute("SELECT COUNT(*) FROM reports")
    if cursor.fetchone()[0] == 0:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")[:16]
        cursor.execute(
            "INSERT INTO reports (report_time, avg_pressure, avg_temperature, avg_pumping_speed, avg_vibrations, avg_tilt_angle) VALUES (?, ?, ?, ?, ?, ?)",
            (current_time, 50.0, 20.0, 5.0, 0.1, 10.0)
        )
    
    conn.commit()
    conn.close()
    print("Тестовые данные добавлены в БД")

def check_and_fix_database(db_path):
    """Проверяет структуру БД и исправляет при необходимости"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем таблицы
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    
    # Список необходимых таблиц
    required_tables = ['raw_data', 'external_data', 'cells', 'operators', 'reports']
    
    # Проверяем наличие всех необходимых таблиц
    missing_tables = [table for table in required_tables if table not in tables]
    
    if missing_tables:
        print(f"Отсутствуют таблицы: {', '.join(missing_tables)}")
        # Пересоздаем БД полностью
        conn.close()
        os.remove(db_path)
        create_test_database(db_path)
    else:
        conn.close()
        print("Структура БД соответствует требованиям")

def start_data_updater():
    """Запускает процесс периодического обновления данных в БД"""
    def update_db_data():
        while True:
            try:
                conn = sqlite3.connect("new_database.db")
                cursor = conn.cursor()
                
                # Текущее время
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Обновляем external_data
                cursor.execute(
                    "INSERT INTO external_data (outdoor_temperature, outdoor_pressure, wind, humidity, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (random.uniform(5, 30), random.uniform(95, 105), random.uniform(0, 10), random.uniform(30, 90), current_time)
                )
                
                # Получаем данные оператора
                cursor.execute("SELECT * FROM operators LIMIT 1")
                operator = cursor.fetchone()
                
                # Получаем данные ячейки
                cursor.execute("SELECT * FROM cells WHERE cell_id = 1")
                cell = cursor.fetchone()
                
                # Получаем данные внешних датчиков
                cursor.execute("SELECT * FROM external_data ORDER BY id DESC LIMIT 1")
                external = cursor.fetchone()
                
                if operator and cell and external:
                    # Создаем запись в raw_data
                    cursor.execute(
                        """INSERT INTO raw_data (
                            operator_fio, operator_login, operator_password, 
                            operator_high_priority, operator_logs, 
                            cell_id, cell_working_status, cell_pressure, 
                            cell_temperature, cell_pumping_speed, cell_vibrations, 
                            cell_tilt_angle, outdoor_temperature, outdoor_pressure, 
                            outdoor_wind, outdoor_humidity, timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            operator[1], operator[2], operator[3], operator[4], operator[5],
                            cell[0], cell[1], random.uniform(40, 60), 
                            random.uniform(15, 25), random.uniform(4, 7), random.uniform(0.1, 0.5),
                            random.uniform(8, 12), external[1], external[2], 
                            external[3], external[4], current_time
                        )
                    )
                
                conn.commit()
                conn.close()
                
                # Периодически меняем статус случайной ячейки
                if random.random() < 0.1:  # 10% шанс при каждом обновлении
                    conn = sqlite3.connect("new_database.db")
                    cursor = conn.cursor()
                    
                    # Выбираем случайную ячейку
                    cell_id = random.randint(1, 40)
                    cursor.execute("SELECT working_status FROM cells WHERE cell_id = ?", (cell_id,))
                    status = cursor.fetchone()[0]
                    
                    # Меняем статус
                    new_status = 0 if status == 1 else 1
                    cursor.execute("UPDATE cells SET working_status = ? WHERE cell_id = ?", (new_status, cell_id))
                    
                    conn.commit()
                    conn.close()
                    print(f"Изменен статус ячейки {cell_id} на {new_status}")
                
                print(f"Данные обновлены в {current_time}")
                
            except Exception as e:
                print(f"Ошибка при обновлении данных: {e}")
            
            # Ждем 2 секунды
            time.sleep(2)
    
    # Запускаем обновления в отдельном потоке
    update_thread = threading.Thread(target=update_db_data, daemon=True)
    update_thread.start()
    print("Запущен процесс обновления данных в БД")
    return update_thread

if __name__ == "__main__":
    # Проверяем и обновляем БД
    ensure_database_exists()
    
    # Запускаем процесс обновления данных
    updater_thread = start_data_updater()
    
    # Запускаем MonOilStudy
    print("\nНажмите Ctrl+C для завершения обновления данных\n")
    print("Запускаем MonOilStudy test.py...\n")
    
    # Выполняем команду запуска MonOilStudy
    os.system('python "MonOilStudy test.py"') 