import sqlite3
import os
import time
import random

def create_test_database(db_path):
    """Создает тестовую базу данных с таблицами raw_data и external_data"""
    
    # Если база уже существует, удаляем ее
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу raw_data
    cursor.execute('''
    CREATE TABLE raw_data (
        id INTEGER PRIMARY KEY,
        temperature REAL,
        pressure REAL,
        flow_rate REAL,
        vibration REAL,
        density REAL,
        timestamp REAL
    )
    ''')
    
    # Создаем таблицу external_data
    cursor.execute('''
    CREATE TABLE external_data (
        id INTEGER PRIMARY KEY,
        outdoor_temperature REAL,
        outdoor_pressure REAL,
        timestamp REAL
    )
    ''')
    
    # Добавляем тестовые данные в raw_data
    current_time = time.time()
    
    for i in range(10):
        # Генерируем случайные значения
        temp = random.uniform(40, 90)
        pressure = random.uniform(5, 15)
        flow = random.uniform(800, 1600)
        vibration = random.uniform(1, 8)
        density = random.uniform(780, 950)
        
        cursor.execute(
            "INSERT INTO raw_data (temperature, pressure, flow_rate, vibration, density, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (temp, pressure, flow, vibration, density, current_time + i)
        )
    
    # Добавляем тестовые данные в external_data
    for i in range(5):
        # Генерируем случайные значения для внешних датчиков
        ext_temp = random.uniform(10, 35)
        ext_pressure = random.uniform(0.9, 1.1)
        
        cursor.execute(
            "INSERT INTO external_data (outdoor_temperature, outdoor_pressure, timestamp) VALUES (?, ?, ?)",
            (ext_temp, ext_pressure, current_time + i)
        )
    
    conn.commit()
    conn.close()
    
    print(f"База данных {db_path} успешно создана с тестовыми данными")

if __name__ == "__main__":
    create_test_database("new_database.db")
    # Проверяем созданную базу данных
    import check_new_database
    check_new_database.check_database("new_database.db") 