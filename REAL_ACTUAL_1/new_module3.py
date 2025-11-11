import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import sqlite3
import time
import os
import datetime

class Module3(tk.Frame):
    def __init__(self, parent, app=None):
        """Инициализация модуля 3 - текстовый отчет данных из БД."""
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
        self.auto_update = True
        self.current_db_path = None
        
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
        self.title_label = tk.Label(self.info_frame, text="Текстовый отчет", 
                                  font=("Arial", 10, "bold"), bg="white")
        self.title_label.pack(side="left", padx=3)
        
        # Кнопка выбора БД
        self.select_db_button = tk.Button(self.info_frame, text="Выбрать БД", 
                                       font=("Arial", 9), width=10, height=1,
                                       command=self.select_database)
        self.select_db_button.pack(side="left", padx=5)
        
        # Индикатор статуса подключения
        self.status_frame = tk.Frame(self.info_frame, bg="white")
        self.status_frame.pack(side="right", padx=3)
        
        self.status_indicator = tk.Canvas(self.status_frame, width=8, height=8, 
                                       bg="orange", bd=0, highlightthickness=0)
        self.status_indicator.pack(side="left", padx=2)
        
        self.status_label = tk.Label(self.status_frame, text="Ожидание", 
                                   fg="orange", bg="white", font=("Arial", 9))
        self.status_label.pack(side="left")
        
        # Создаем текстовое поле для отчета
        self.report_frame = tk.Frame(self, bg="white")
        self.report_frame.pack(fill="both", expand=True, padx=3, pady=2)
        
        # Создаем текстовое поле с прокруткой
        self.text_scroll = tk.Scrollbar(self.report_frame)
        self.text_scroll.pack(side="right", fill="y")
        
        self.report_text = tk.Text(self.report_frame, wrap="word", 
                                 yscrollcommand=self.text_scroll.set,
                                 font=("Arial", 10), bg="white")
        self.report_text.pack(side="left", fill="both", expand=True)
        
        self.text_scroll.config(command=self.report_text.yview)
        
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
                                          font=("Arial", 9), width=4, height=1,
                                          bg="light green" if self.auto_update else "light grey",
                                          command=self.toggle_auto_update)
        self.auto_update_button.pack(side="right", padx=1)
        
        # Кнопка обновления
        self.refresh_button = tk.Button(self.buttons_frame, text="Обновить", 
                                      font=("Arial", 9), width=8, height=1,
                                      command=self.force_update_data)
        self.refresh_button.pack(side="right", padx=1)
    
    def get_data_from_db(self):
        """Получает данные из БД"""
        try:
            # Ищем соединение с БД
            conn = self.find_db_connection()
            
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    # Получаем последние данные из raw_data
                    cursor.execute("""
                        SELECT 
                            cell_pressure as "Давление нефтепровода",
                            cell_temperature as "Температура нефтепровода",
                            cell_pumping_speed as "Скорость откачки",
                            cell_vibrations as "Вибрации",
                            cell_tilt_angle as "Угол наклона",
                            outdoor_temperature as "Температура окружающей среды",
                            outdoor_pressure as "Давление окружающей среды",
                            outdoor_wind as "Скорость ветра",
                            outdoor_humidity as "Влажность воздуха",
                            timestamp as "Время измерения"
                        FROM raw_data
                        ORDER BY id DESC LIMIT 1
                    """)
                    raw_data = cursor.fetchone()
                    
                    if raw_data:
                        # Формируем отчет
                        report = "ОТЧЕТ О СОСТОЯНИИ НЕФТЕПРОВОДА\n"
                        report += "=" * 40 + "\n\n"
                        
                        # Добавляем данные
                        report += f"Время измерения: {raw_data[9]}\n\n"
                        
                        report += "ПАРАМЕТРЫ НЕФТЕПРОВОДА:\n"
                        report += "-" * 30 + "\n"
                        report += f"Давление: {raw_data[0]:.2f} МПа\n"
                        report += f"Температура: {raw_data[1]:.2f} °C\n"
                        report += f"Скорость откачки: {raw_data[2]:.2f} м/с\n"
                        report += f"Вибрации: {raw_data[3]:.2f} мм/с\n"
                        report += f"Угол наклона: {raw_data[4]:.2f} градусов\n\n"
                        
                        report += "ПАРАМЕТРЫ ОКРУЖАЮЩЕЙ СРЕДЫ:\n"
                        report += "-" * 30 + "\n"
                        report += f"Температура: {raw_data[5]:.2f} °C\n"
                        report += f"Давление: {raw_data[6]:.2f} кПа\n"
                        report += f"Скорость ветра: {raw_data[7]:.2f} м/с\n"
                        report += f"Влажность воздуха: {raw_data[8]:.2f} %\n"
                        
                        # Обновляем текст отчета
                        self.report_text.delete(1.0, tk.END)
                        self.report_text.insert(1.0, report)
                        
                        self.data_loaded = True
                        return True
                    
                except sqlite3.Error as e:
                    print(f"Module3: Ошибка при получении данных: {e}")
                    
        except Exception as e:
            print(f"Module3: Ошибка при работе с БД: {e}")
            
        return False
    
    def start_update_timer(self):
        """Запускает таймер обновления данных"""
        if self.update_task is not None:
            self.after_cancel(self.update_task)
        # Запускаем первое обновление сразу
        self.update_data()
        
    def find_app_reference(self):
        """Поиск ссылки на главное приложение."""
        try:
            # Навигация вверх по иерархии виджетов для поиска главного приложения
            widget = self.parent
            while widget:
                # Проверяем является ли виджет корневым окном
                if isinstance(widget, tk.Tk):
                    self.app = widget
                    return True
                # Пробуем получить родительский виджет
                if hasattr(widget, 'master'):
                    widget = widget.master
                else:
                    break
            
            return False
        except Exception as e:
            print(f"Module3: Ошибка при поиске главного приложения: {e}")
            return False
    
    def toggle_auto_update(self):
        """Включает/выключает автоматическое обновление данных."""
        self.auto_update = not self.auto_update
        
        # Обновляем внешний вид кнопки
        if self.auto_update:
            self.auto_update_button.config(bg="light green")
            # Запускаем обновление данных
            self.force_update_data()
        else:
            self.auto_update_button.config(bg="light grey")
            # Отменяем запланированные обновления
            if self.update_task is not None:
                self.after_cancel(self.update_task)
                self.update_task = None
                
    def force_update_data(self):
        """Принудительное обновление данных."""
        self.update_data()
    
    def update_data(self):
        """Обновляет данные и отображает их."""
        try:
            # Отменяем предыдущий запланированный вызов, если есть
            if self.update_task is not None:
                self.after_cancel(self.update_task)
                self.update_task = None
            
            # Получаем данные из БД
            if self.get_data_from_db():
                self.status_indicator.config(bg="green")
                self.status_label.config(text="Подключено", fg="green")
                # Обновляем время последнего обновления
                current_time = time.strftime("%H:%M:%S")
                self.update_time_label.config(text=f"Обновлено: {current_time}")
            else:
                self.status_indicator.config(bg="red")
                self.status_label.config(text="Нет данных", fg="red")
            
            # Если автообновление включено, планируем следующее обновление
            if self.auto_update:
                self.update_task = self.after(self.update_interval, self.update_data)
            
        except Exception as e:
            print(f"Module3: Ошибка при обновлении данных: {e}")
            self.status_indicator.config(bg="red")
            self.status_label.config(text="Ошибка", fg="red")
            
            # Планируем повторную попытку
            if self.auto_update:
                self.update_task = self.after(5000, self.update_data)
    
    def on_close(self):
        """Вызывается при закрытии модуля."""
        # Останавливаем периодическое обновление
        if self.update_task is not None:
            self.after_cancel(self.update_task)
            self.update_task = None

    def select_database(self):
        """Открывает диалог выбора БД"""
        from tkinter import filedialog
        
        # Открываем диалог выбора файла
        file_path = filedialog.askopenfilename(
            title="Выберите файл базы данных",
            filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        # Преобразуем в абсолютный путь
        file_path = os.path.abspath(file_path)
        
        # Сохраняем путь к БД
        self.current_db_path = file_path
        
        # Обновляем статус
        self.status_indicator.config(bg="blue")
        self.status_label.config(text="Подключение...", fg="blue")
        
        # Запускаем обновление данных
        self.force_update_data()

    def find_db_connection(self):
        """Ищет соединение с БД"""
        try:
            # Проверяем, есть ли активное соединение в главном приложении
            if self.app and hasattr(self.app, 'conn') and self.app.conn is not None:
                try:
                    # Проверяем, работает ли соединение
                    self.app.conn.execute("SELECT 1")
                    print("Module3: Используется соединение из главного приложения")
                    return self.app.conn
                except Exception as e:
                    print(f"Module3: Ошибка проверки соединения из главного приложения: {e}")
            
            # Если нет активного соединения в главном приложении, используем локальное
            if hasattr(self, 'current_db_path') and self.current_db_path:
                try:
                    # Создаем новое соединение
                    conn = sqlite3.connect(self.current_db_path)
                    # Включаем поддержку внешних ключей
                    conn.execute("PRAGMA foreign_keys = ON")
                    return conn
                except Exception as e:
                    print(f"Module3: Ошибка при подключении к БД: {e}")
            
            return None
            
        except Exception as e:
            print(f"Module3: Ошибка при поиске соединения с БД: {e}")
            return None 