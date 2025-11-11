import tkinter as tk
from module9 import Module9
import sqlite3
import os

# Проверка наличия тестовой БД и создание, если не существует
def ensure_test_db():
    test_db_path = "test_debug.db"
    if not os.path.exists(test_db_path):
        print(f"Создаю тестовую БД: {test_db_path}")
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
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
                timestamp TEXT
            )
        ''')
        # Добавляем тестовые данные
        cursor.execute('''
            INSERT INTO raw_data (
                cell_pressure, cell_temperature, cell_pumping_speed, 
                cell_vibrations, cell_tilt_angle, outdoor_temperature, 
                outdoor_pressure, outdoor_wind, outdoor_humidity, timestamp)
            VALUES (52.5, 20.3, 4.7, 0.12, 10.1, 25.8, 101.3, 5.2, 60.5, 
                    datetime('now'))
        ''')
        conn.commit()
        conn.close()
        print(f"Тестовая БД создана: {test_db_path}")
    else:
        print(f"Тестовая БД уже существует: {test_db_path}")
    return os.path.abspath(test_db_path)

# Функция-заглушка для connection_callback
def mock_connection_callback(connection_info):
    print("\nПолучена информация о подключении:")
    for key, value in connection_info.items():
        if key != "connection":  # Не выводим объект соединения
            print(f"  {key}: {value}")
    return True

# Класс приложения для тестирования
class TestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Тест модуля 9")
        self.geometry("600x400")
        
        self.db_connected = False
        self.conn = None
        
        # Добавляем модуль 9
        self.frame = tk.Frame(self, padx=10, pady=10)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем кнопку для прямого подключения к тестовой БД
        self.btn_direct_connect = tk.Button(
            self.frame, text="Прямое подключение к тестовой БД",
            command=self.direct_connect
        )
        self.btn_direct_connect.pack(pady=10)
        
        # Создаем модуль 9
        self.module9 = Module9(self.frame, connection_callback=mock_connection_callback)
        self.module9.pack(fill=tk.BOTH, expand=True)
        
        # Для хранения ссылки на тестовую БД
        self.test_db_path = ensure_test_db()
        
    def direct_connect(self):
        print(f"\nПрямое подключение к тестовой БД: {self.test_db_path}")
        self.module9.connect_to_database(self.test_db_path)
        
    def set_active_database(self, db_name):
        print(f"\nУстановка активной БД: {db_name}")
        self.active_db = db_name
        self.db_connected = True
        
        # Если есть соединение, закрываем его
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
        
        # Создаем новое соединение
        try:
            # Ищем файл БД
            db_path = None
            if os.path.exists(db_name):
                db_path = db_name
            else:
                # Полный путь к текущему каталогу
                current_dir = os.path.abspath(".")
                possible_path = os.path.join(current_dir, db_name)
                if os.path.exists(possible_path):
                    db_path = possible_path
            
            if db_path:
                self.conn = sqlite3.connect(db_path)
                print(f"Соединение создано: {db_path}")
                return True
            else:
                print(f"Файл БД не найден: {db_name}")
                return False
        except Exception as e:
            print(f"Ошибка при установке активной БД: {e}")
            return False
        
    def unlock_modules(self):
        print("\nРазблокировка модулей")
        return True

if __name__ == "__main__":
    app = TestApp()
    app.mainloop() 