import tkinter as tk
from tkinter import ttk
import sqlite3
import time
import os
from datetime import datetime

class Module2(tk.Frame):
    def __init__(self, parent, app=None):
        """Инициализация модуля 2 - визуализации данных из БД."""
        super().__init__(parent, bg="white")
        self.parent = parent
        self.app = app
        
        # Размер модуля будет адаптироваться под размер окна
        self.pack(fill="both", expand=True)
        
        # Находим ссылку на основное приложение, если не передана
        if self.app is None:
            self.find_app_reference()
        
        # Переменные для работы с БД
        self.update_interval = 200  # 5 раз в секунду
        self.update_task = None
        self.data_loaded = False
        self.last_values = {}  # Словарь для хранения последних значений
        self.current_values = {}  # Словарь для хранения текущих значений
        self.auto_update = True
        self.active_table = "raw_data"  # По умолчанию используем таблицу raw_data
        self.conn = None  # Соединение с БД
        self.highlighted_indicators = set()  # Множество для отслеживания выделенных индикаторов
        
        # Словарь русских названий для полей базы данных
        self.field_translations = {
            # Поля raw_data - основные датчики нефтепровода
            'cell_pressure': 'Давление в трубе (МПа)',
            'cell_temperature': 'Температура нефти (°C)',
            'cell_pumping_speed': 'Скорость перекачки (м/с)',
            'cell_vibrations': 'Вибрации трубы (мм/с)',
            'cell_tilt_angle': 'Угол наклона (град)',
            'outdoor_temperature': 'Температура воздуха (°C)',
            'outdoor_pressure': 'Атмосферное давление (кПа)',
            'outdoor_wind': 'Скорость ветра (м/с)',
            'outdoor_humidity': 'Влажность воздуха (%)',
            'timestamp': 'Время измерения',
            
            # Поля cells - данные ячеек
            'pressure': 'Давление (МПа)',
            'temperature': 'Температура (°C)',
            'pumping_speed': 'Скорость насоса (м/с)',
            'vibrations': 'Уровень вибраций (мм/с)',
            'tilt_angle': 'Угол наклона (град)',
            
            # Поля external_data - внешние датчики
            'env_temperature': 'Температура среды (°C)',
            'env_pressure': 'Давление среды (кПа)',
            'env_wind': 'Ветер (м/с)',
            'env_humidity': 'Влажность (%)',
            
            # Общие поля
            'id': 'ID записи',
            'operator_id': 'ID оператора',
            'created_at': 'Время создания',
            'updated_at': 'Время обновления'
        }
        
        # Создание интерфейса
        self.setup_ui()
        
        # Запускаем таймер обновления данных
        self.start_update_timer()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Верхняя панель с информацией
        self.info_frame = tk.Frame(self, bg="white", height=18)
        self.info_frame.pack(fill="x", pady=1)
        
        # Заголовок
        self.title_label = tk.Label(self.info_frame, text="Мониторинг данных", 
                                  font=("Arial", 10, "bold"), bg="white")
        self.title_label.pack(side="left", padx=3)
        
        # Кнопки для выбора таблиц
        self.tables_frame = tk.Frame(self.info_frame, bg="white")
        self.tables_frame.pack(side="left", padx=10)
        
        self.raw_data_button = tk.Button(self.tables_frame, text="Основные датчики", 
                                       font=("Arial", 8), 
                                       bg="lightblue" if self.active_table == "raw_data" else "lightgray",
                                       command=lambda: self.switch_table("raw_data"))
        self.raw_data_button.pack(side="left", padx=2)
        
        self.external_data_button = tk.Button(self.tables_frame, text="Внешние датчики", 
                                           font=("Arial", 8), 
                                           bg="lightgray",
                                           command=lambda: self.switch_table("external_data"))
        self.external_data_button.pack(side="left", padx=2)
        
        # Индикатор статуса подключения
        self.status_frame = tk.Frame(self.info_frame, bg="white")
        self.status_frame.pack(side="right", padx=3)
        
        self.status_indicator = tk.Canvas(self.status_frame, width=8, height=8, 
                                       bg="orange", bd=0, highlightthickness=0)
        self.status_indicator.pack(side="left", padx=2)
        
        self.status_label = tk.Label(self.status_frame, text="Ожидание", 
                                   fg="orange", bg="white", font=("Arial", 9))
        self.status_label.pack(side="left")
        
        # Создаем фрейм для индикаторов данных
        self.indicators_frame = tk.Frame(self, bg="white")
        self.indicators_frame.pack(fill="both", expand=True, padx=3, pady=2)
        
        # Словари для хранения виджетов индикаторов
        self.indicators = {}
        
        # Нижняя панель с кнопками
        self.bottom_frame = tk.Frame(self, bg="white", height=18)
        self.bottom_frame.pack(fill="x", side="bottom", pady=1)
            
        # Метка для времени последнего обновления
        self.update_time_label = tk.Label(self.bottom_frame, text="Ожидание данных", 
                                      font=("Arial", 9), bg="white", fg="gray")
        self.update_time_label.pack(side="left", padx=3)
        
        # Кнопки управления
        self.buttons_frame = tk.Frame(self.bottom_frame, bg="white")
        self.buttons_frame.pack(side="right", padx=3)
        
        # Кнопка автообновления
        self.auto_update_button = tk.Button(self.buttons_frame, text="Авто", 
                                          font=("Arial", 9), width=5, height=1,
                                          bg="light green" if self.auto_update else "light grey",
                                          command=self.toggle_auto_update)
        self.auto_update_button.pack(side="right", padx=2)
        
        # Кнопка обновления
        self.refresh_button = tk.Button(self.buttons_frame, text="🔄 Обновить", 
                                      font=("Arial", 9), width=10, height=1,
                                      bg="lightblue", activebackground="skyblue",
                                      command=self.force_update_data)
        self.refresh_button.pack(side="right", padx=2)
        
    def switch_table(self, table_name):
        """Переключает отображение на указанную таблицу"""
        if self.active_table == table_name:
            return
            
        self.active_table = table_name
        
        # Обновляем стиль кнопок
        self.raw_data_button.configure(
            bg="lightblue" if table_name == "raw_data" else "lightgray")
        self.external_data_button.configure(
            bg="lightblue" if table_name == "external_data" else "lightgray")
        
        # Очищаем текущие индикаторы и обновляем данные
        self.clear_indicators()
        self.force_update_data()
        
    def clear_indicators(self):
        """Очищает все индикаторы"""
        for widget in self.indicators_frame.winfo_children():
            widget.destroy()
        self.indicators = {}
        # Принудительно обновляем отображение после очистки
        self.indicators_frame.update_idletasks()
        
    def create_indicator(self, field_name, field_value):
        """Создает индикатор для поля"""
        # Создаем фрейм для индикатора
        indicator = tk.Frame(self.indicators_frame, bg="white", bd=1, relief="solid")
        indicator.pack(fill="x", padx=5, pady=2)
        
        # Получаем русское название поля
        display_name = self.field_translations.get(field_name, field_name)
        
        # Метка с названием поля
        name_label = tk.Label(indicator, text=display_name, font=("Arial", 9, "bold"), 
                             bg="white", anchor="w", width=30)
        name_label.pack(side="left", padx=5, pady=2)
        
        # Форматируем значение
        formatted_value = self.format_field_value(field_name, field_value)
        
        # Метка со значением
        value_label = tk.Label(indicator, text=formatted_value, font=("Arial", 10), 
                              bg="white", fg="blue")
        value_label.pack(side="left", padx=5, pady=2)
        
        # Сохраняем виджеты в словарь индикаторов
        self.indicators[field_name] = {
            'frame': indicator,
            'name_label': name_label,
            'value_label': value_label,
            'last_value': field_value
        }
    
    def format_field_value(self, field_name, value):
        """Форматирует значение поля для отображения"""
        if value is None:
            return "Нет данных"
        
        # Форматирование для разных типов полей
        if field_name in ['timestamp', 'created_at', 'updated_at']:
            return str(value)
        elif field_name in ['id', 'operator_id']:
            return str(int(value)) if isinstance(value, (int, float)) else str(value)
        elif isinstance(value, (int, float)):
            # Для числовых значений показываем 2 знака после запятой
            return f"{float(value):.2f}"
        else:
            return str(value)
        
    def update_indicator(self, field_name, new_value):
        """Обновляет значение индикатора"""
        if field_name not in self.indicators:
            # Создаем новый индикатор, если его нет
            self.create_indicator(field_name, new_value)
            return
            
        # Получаем текущий индикатор
        indicator = self.indicators[field_name]
        last_value = indicator['last_value']
        
        # Форматируем и обновляем значение
        formatted_value = self.format_field_value(field_name, new_value)
        indicator['value_label'].config(text=formatted_value)
        
        # Выделяем цветом, если значение изменилось
        if last_value != new_value:
            indicator['value_label'].config(fg="red")
            self.highlighted_indicators.add(field_name)
            # Планируем сброс цвета через 1 секунду
            self.after(1000, lambda: self.reset_color(field_name))
        
        # Запоминаем новое значение
        indicator['last_value'] = new_value
        
        # Принудительно обновляем отображение родительского фрейма
        self.indicators_frame.update_idletasks()
        
    def reset_color(self, field_name):
        """Сбрасывает цвет индикатора на синий"""
        if field_name in self.indicators and field_name in self.highlighted_indicators:
            self.indicators[field_name]['value_label'].config(fg="blue")
            self.highlighted_indicators.remove(field_name)
        
    def find_db_connection(self):
        """Получает соединение с БД только из основного приложения (блок 8)"""
        connection = None
        
        # Используем только соединение из основного приложения (блок 8)
        if self.app and hasattr(self.app, 'get_db_connection'):
            try:
                connection = self.app.get_db_connection()
                if connection:
                    print(f"Module2: Соединение получено через app.get_db_connection()")
                    # Проверяем работоспособность соединения
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                else:
                    print(f"Module2: Нет активного соединения через app.get_db_connection()")
            except Exception as e:
                print(f"Module2: Ошибка при использовании app.get_db_connection(): {e}")
                connection = None
        
        # Проверяем app.conn как резерв
        if connection is None and self.app and hasattr(self.app, 'conn') and self.app.conn:
            try:
                # Проверяем, работает ли соединение
                cursor = self.app.conn.cursor()
                cursor.execute("SELECT 1")
                connection = self.app.conn
                print(f"Module2: Соединение получено через app.conn в качестве резерва")
            except Exception as e:
                print(f"Module2: Ошибка при использовании app.conn: {e}")
        
        # Обновляем индикатор статуса
        if connection:
            self.status_indicator.config(bg="green")
            self.status_label.config(text="Подключено", fg="green")
        else:
            self.status_indicator.config(bg="red")
            self.status_label.config(text="Нет активной БД (блок 8)", fg="red")
            print("Module2: Нет активной БД в системе (настройте БД в блоке 8)")
        
        return connection
        
    def start_update_timer(self):
        """Запускает таймер обновления данных"""
        if self.auto_update:
            self.update_data()
            
        # Отменяем предыдущую задачу, если она существует
        if self.update_task is not None:
            self.after_cancel(self.update_task)
            
        # Планируем следующее обновление
        self.update_task = self.after(self.update_interval, self.start_update_timer)
    
    def toggle_auto_update(self):
        """Включает/выключает автообновление"""
        self.auto_update = not self.auto_update
        self.auto_update_button.config(
            bg="light green" if self.auto_update else "light grey")
        
        # Если автообновление включено, запускаем обновление данных
        if self.auto_update:
            self.force_update_data()
                
    def force_update_data(self):
        """Принудительно обновляет данные из БД"""
        self.update_data()
    
    def update_data(self):
        """Обновляет данные из БД"""
        try:
            # Предотвращаем множественные обновления
            if hasattr(self, '_updating_data') and self._updating_data:
                return
            self._updating_data = True
            
            # Проверяем соединение с БД или создаем новое
            if self.conn is None:
                self.conn = self.find_db_connection()
                
            # Если соединения нет, пробуем обновить через некоторое время
            if self.conn is None:
                self.update_time_label.config(text="⚠ Нет подключения к базе данных")
                self._updating_data = False
                return
                
            # Получаем числовые поля из таблицы
            cursor = self.conn.cursor()
                
            # Проверяем существование таблицы
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.active_table}'")
            if not cursor.fetchone():
                self.clear_indicators()
                table_name = "основных датчиков" if self.active_table == "raw_data" else "внешних датчиков"
                self.update_time_label.config(text=f"⚠ Таблица {table_name} не найдена")
                return
            
            # Получаем информацию о столбцах таблицы
            cursor.execute(f"PRAGMA table_info({self.active_table})")
            columns_info = cursor.fetchall()
            
            # Выбираем числовые столбцы (тип INTEGER или REAL), кроме id
            numeric_columns = []
            for col_info in columns_info:
                col_name = col_info[1]
                col_type = col_info[2].upper()
                if col_name.lower() != "id" and ("INT" in col_type or "REAL" in col_type or "NUM" in col_type or "FLOAT" in col_type):
                    numeric_columns.append(col_name)
            
            if not numeric_columns:
                self.clear_indicators()
                table_name = "основных датчиков" if self.active_table == "raw_data" else "внешних датчиков"
                self.update_time_label.config(text=f"⚠ В таблице {table_name} нет данных для отображения")
                return
            
            # Получаем последнюю запись из таблицы
            sql = f"SELECT {', '.join(numeric_columns)} FROM {self.active_table} ORDER BY id DESC LIMIT 1"
            cursor.execute(sql)
            row = cursor.fetchone()
            
            if not row:
                self.clear_indicators()
                table_name = "основных датчиков" if self.active_table == "raw_data" else "внешних датчиков"
                self.update_time_label.config(text=f"⚠ В таблице {table_name} пока нет измерений")
                return
                
            # Обновляем индикаторы
            for i, col_name in enumerate(numeric_columns):
                self.update_indicator(col_name, row[i])
                
            # Обновляем время последнего обновления
            current_time = datetime.now().strftime("%H:%M:%S")
            table_name = "основных датчиков" if self.active_table == "raw_data" else "внешних датчиков"
            self.update_time_label.config(text=f"✓ Данные {table_name} обновлены в {current_time}")
            self.data_loaded = True
                
        except sqlite3.Error as e:
            print(f"Module2: Ошибка SQLite: {e}")
            self.conn = None  # Сбрасываем соединение, чтобы попытаться установить его заново
            self.status_indicator.config(bg="red")
            self.status_label.config(text="Ошибка БД", fg="red")
            self.update_time_label.config(text=f"❌ Ошибка базы данных: {e}")
        except Exception as e:
            print(f"Module2: Общая ошибка: {e}")
            self.status_indicator.config(bg="red")
            self.status_label.config(text="Ошибка", fg="red")
            self.update_time_label.config(text=f"❌ Системная ошибка: {e}")
        finally:
            # Снимаем флаг обновления
            self._updating_data = False

    def find_app_reference(self):
        """Ищет ссылку на основное приложение"""
        widget = self.parent
        depth = 0
        max_depth = 10  # Максимальная глубина поиска
        
        while widget and depth < max_depth:
            if hasattr(widget, 'module7') or hasattr(widget, 'module8'):
                self.app = widget
                print("Module2: Найдена ссылка на основное приложение")
                break
            widget = widget.master
            depth += 1
        
        if not self.app:
            print("Module2: Не найдена ссылка на основное приложение")
    
    def on_close(self):
        """Вызывается при закрытии модуля"""
        # Останавливаем таймер обновления
        if self.update_task is not None:
            self.after_cancel(self.update_task)
        # Закрываем соединение с БД, если оно наше
        if self.conn and not self.app:
            try:
                self.conn.close()
            except:
                pass 