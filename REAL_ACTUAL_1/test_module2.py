import tkinter as tk
import sqlite3
import os
import time
import threading
from module2 import Module2

# Создаем тестовую БД
def create_test_db():
    # Пути к БД
    db_path = "test_module2.db"
    
    # Проверяем, существует ли уже БД
    db_exists = os.path.exists(db_path)
    
    # Создаем соединение
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу raw_data, если не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cell_pressure REAL,
            cell_temperature REAL,
            cell_pumping_speed REAL,
            cell_vibrations REAL,
            cell_tilt_angle REAL,
            outdoor_temperature REAL,
            outdoor_pressure REAL,
            outdoor_wind REAL,
            outdoor_humidity REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создаем таблицу external_data, если не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS external_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor1_value REAL,
            sensor2_value REAL,
            sensor3_value REAL,
            sensor4_value REAL,
            flow_rate REAL,
            temperature_external REAL,
            pressure_atmospheric REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Если БД не существовала ранее, добавляем несколько записей
    if not db_exists:
        # Добавляем записи в raw_data
        cursor.execute('''
            INSERT INTO raw_data (
                cell_pressure, cell_temperature, cell_pumping_speed, cell_vibrations, 
                cell_tilt_angle, outdoor_temperature, outdoor_pressure, outdoor_wind, outdoor_humidity
            ) VALUES (52.3, 20.5, 5.0, 0.1, 10.0, 25.0, 101.3, 5.0, 65.0)
        ''')
        
        cursor.execute('''
            INSERT INTO raw_data (
                cell_pressure, cell_temperature, cell_pumping_speed, cell_vibrations, 
                cell_tilt_angle, outdoor_temperature, outdoor_pressure, outdoor_wind, outdoor_humidity
            ) VALUES (52.5, 20.7, 5.2, 0.12, 10.2, 25.5, 101.5, 4.8, 66.0)
        ''')
        
        # Добавляем записи в external_data
        cursor.execute('''
            INSERT INTO external_data (
                sensor1_value, sensor2_value, sensor3_value, sensor4_value, 
                flow_rate, temperature_external, pressure_atmospheric
            ) VALUES (1.23, 4.56, 7.89, 10.11, 25.5, 22.0, 100.5)
        ''')
        
        cursor.execute('''
            INSERT INTO external_data (
                sensor1_value, sensor2_value, sensor3_value, sensor4_value, 
                flow_rate, temperature_external, pressure_atmospheric
            ) VALUES (1.25, 4.60, 7.90, 10.15, 26.0, 22.5, 100.7)
        ''')
        
    conn.commit()
    
    print(f"База данных создана/обновлена: {os.path.abspath(db_path)}")
    return conn, os.path.abspath(db_path)

# Имитация обновления БД
def db_update_thread(db_path):
    try:
        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        counter = 0
        while True:
            counter += 1
            
            # Обновляем raw_data каждые 2 секунды
            if counter % 2 == 0:
                # Добавляем случайные значения с небольшим изменением
                import random
                
                cell_pressure = 52.0 + random.uniform(-1, 1)
                cell_temperature = 20.0 + random.uniform(-0.5, 0.5)
                cell_pumping_speed = 5.0 + random.uniform(-0.3, 0.3)
                cell_vibrations = 0.1 + random.uniform(-0.02, 0.02)
                cell_tilt_angle = 10.0 + random.uniform(-0.2, 0.2)
                outdoor_temperature = 25.0 + random.uniform(-1, 1)
                outdoor_pressure = 101.3 + random.uniform(-0.2, 0.2)
                outdoor_wind = 5.0 + random.uniform(-0.5, 0.5)
                outdoor_humidity = 65.0 + random.uniform(-2, 2)
                
                cursor.execute('''
                    INSERT INTO raw_data (
                        cell_pressure, cell_temperature, cell_pumping_speed, cell_vibrations, 
                        cell_tilt_angle, outdoor_temperature, outdoor_pressure, outdoor_wind, outdoor_humidity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cell_pressure, cell_temperature, cell_pumping_speed, cell_vibrations, 
                    cell_tilt_angle, outdoor_temperature, outdoor_pressure, outdoor_wind, outdoor_humidity
                ))
                
                conn.commit()
                print(f"Добавлена новая запись в raw_data (#{counter})")
            
            # Обновляем external_data каждые 3 секунды
            if counter % 3 == 0:
                import random
                
                sensor1_value = 1.2 + random.uniform(-0.1, 0.1)
                sensor2_value = 4.5 + random.uniform(-0.2, 0.2)
                sensor3_value = 7.8 + random.uniform(-0.1, 0.1)
                sensor4_value = 10.1 + random.uniform(-0.05, 0.05)
                flow_rate = 25.0 + random.uniform(-0.5, 0.5)
                temperature_external = 22.0 + random.uniform(-0.3, 0.3)
                pressure_atmospheric = 100.5 + random.uniform(-0.1, 0.1)
                
                cursor.execute('''
                    INSERT INTO external_data (
                        sensor1_value, sensor2_value, sensor3_value, sensor4_value, 
                        flow_rate, temperature_external, pressure_atmospheric
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sensor1_value, sensor2_value, sensor3_value, sensor4_value, 
                    flow_rate, temperature_external, pressure_atmospheric
                ))
                
                conn.commit()
                print(f"Добавлена новая запись в external_data (#{counter})")
            
            # Пауза
            time.sleep(1)
            
    except Exception as e:
        print(f"Ошибка в потоке обновления БД: {e}")
    finally:
        if conn:
            conn.close()

# Основной класс приложения
class TestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Тест модуля 2")
        self.geometry("600x400")
        
        # Создаем тестовую БД
        self.conn, self.db_path = create_test_db()
        self.active_db = self.db_path
        
        # Запускаем поток обновления БД
        self.update_thread = threading.Thread(target=db_update_thread, args=(self.db_path,))
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Создаем модуль 2
        self.module2 = Module2(self)
        self.module2.pack(fill="both", expand=True)
        
        # Обработчик закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        print(f"Приложение запущено, тестовая БД: {self.db_path}")
        
    def on_close(self):
        if hasattr(self.module2, 'on_close'):
            self.module2.on_close()
            
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
                
        self.destroy()

if __name__ == "__main__":
    app = TestApp()
    app.mainloop() 