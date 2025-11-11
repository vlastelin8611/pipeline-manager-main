import tkinter as tk  # импортирую модуль tkinter для создания графического интерфейса, сокращаю название до tk
from tkinter import ttk, filedialog, scrolledtext  # импортирую дополнительные компоненты tkinter:
# ttk - современные виджеты с улучшенным дизайном
# filedialog - диалоги для работы с файлами (открыть, сохранить)
# scrolledtext - текстовое поле с прокруткой
import sqlite3  # импортирую модуль sqlite3 для работы с базой данных SQLite
import time  # импортирую модуль time для работы со временем (паузы, измерения)
import os  # импортирую модуль os для работы с файлами и папками
import datetime  # импортирую модуль datetime для работы с датой и временем

class Module3(tk.Frame):  # создаю класс Module3, который наследуется от tk.Frame (контейнер для виджетов)
    def __init__(self, parent, app=None):  # конструктор класса, принимает родительский виджет и ссылку на приложение
        """Инициализация модуля 3 - текстовый отчет данных из БД."""  # описание что делает этот класс
        super().__init__(parent, bg="white")  # вызываю конструктор родительского класса с белым фоном
        self.parent = parent  # сохраняю ссылку на родительский виджет
        self.app = app  # сохраняю ссылку на основное приложение
        
        # Размер модуля будет адаптироваться под размер окна
        self.pack(fill="both", expand=True)  # размещаю модуль, заполняя всю доступную область и позволяя расширяться
        
        # Находим ссылку на основное приложение, если не передана
        if self.app is None:  # если ссылка на приложение не была передана
            self.find_app_reference()  # ищу ссылку на основное приложение
        
        # Переменные для работы с БД
        self.update_interval = 60000  # 1 минута (60000 мс)  # устанавливаю интервал обновления 60000 миллисекунд = 1 минута
        self.update_task = None  # переменная для хранения задачи автообновления (пока не назначена)
        self.data_loaded = False  # флаг показывающий загружены ли данные (изначально False)
        self.auto_update = True  # флаг автоматического обновления (изначально включено)
        self.current_db_path = None  # путь к текущей базе данных (пока не задан)
        self.last_report_time = None  # время последнего сохраненного отчета (пока не задано)
        
        # Создаем папку для отчетов в текущей директории программы
        self.reports_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")  # создаю путь к папке reports в директории программы
        # os.path.abspath(__file__) - получаю полный путь к текущему файлу
        # os.path.dirname() - получаю директорию где находится файл
        # os.path.join() - соединяю путь к директории с названием папки "reports"
        if not os.path.exists(self.reports_folder):  # если папка reports не существует
            os.makedirs(self.reports_folder)  # создаю папку reports
        
        # Создание интерфейса
        self.setup_ui()  # вызываю метод для создания пользовательского интерфейса
        
        # Запускаем таймер обновления данных
        self.start_update_timer()  # вызываю метод для запуска автоматического обновления
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Верхняя панель с информацией
        self.info_frame = tk.Frame(self, bg="white", height=18)
        self.info_frame.pack(fill="x", pady=1)
        
        # Заголовок
        self.title_label = tk.Label(self.info_frame, text="Текстовый отчет", 
                                  font=("Arial", 10, "bold"), bg="white")
        self.title_label.pack(side="left", padx=3)
        
        # Убираем кнопку выбора БД - используем только активную БД из блока 8
        
        # Кнопка обновления данных (добавляем на верхнюю панель)
        self.top_refresh_button = tk.Button(self.info_frame, text="🔄 Обновить", 
                                          font=("Arial", 9), width=10, height=1,
                                          bg="lightgreen", activebackground="lightblue",
                                          command=self.force_update_data)
        self.top_refresh_button.pack(side="left", padx=5)
        
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
                                      bg="lightblue", activebackground="skyblue",
                                      command=self.force_update_data)
        self.refresh_button.pack(side="right", padx=1)
    
    def save_report_to_file(self, report_text):
        """Сохраняет отчет в txt файл"""
        try:
            # Генерируем имя файла с текущей датой и временем
            current_time = datetime.datetime.now()
            filename = current_time.strftime("report_%Y-%m-%d_%H-%M-%S.txt")
            filepath = os.path.join(self.reports_folder, filename)
            
            # Сохраняем отчет в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Дата создания отчета: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(report_text)
            
            print(f"Module3: Отчет сохранен в файл: {filename}")
            return True
            
        except Exception as e:
            print(f"Module3: Ошибка при сохранении отчета: {e}")
            return False
    
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
                        report += f"Влажность воздуха: {raw_data[8]:.2f} %\n\n"
                        
                        # Добавляем информацию о состоянии линий и параметрах управления
                        report += self.get_control_and_lines_info()
                        
                        # Обновляем текст отчета
                        self.report_text.delete(1.0, tk.END)
                        self.report_text.update_idletasks()  # Принудительно обновляем виджет
                        self.report_text.insert(1.0, report)
                        self.report_text.update_idletasks()  # Еще раз обновляем после вставки
                        
                        # Автоматически сохраняем отчет в файл каждую минуту
                        current_time = datetime.datetime.now()
                        if (self.last_report_time is None or 
                            (current_time - self.last_report_time).total_seconds() >= 60):
                            self.save_report_to_file(report)
                            self.last_report_time = current_time
                        
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
            # Предотвращаем множественные обновления
            if hasattr(self, '_updating_data') and self._updating_data:
                return
            self._updating_data = True
            
            # Отменяем предыдущий запланированный вызов, если есть
            if self.update_task is not None:
                self.after_cancel(self.update_task)
                self.update_task = None
            
            # Запланируем следующее обновление перед обработкой данных
            # для предотвращения блокировки интерфейса
            if self.auto_update:
                self.update_task = self.after(self.update_interval, self.update_data)
                
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
            
        except Exception as e:
            print(f"Module3: Ошибка при обновлении данных: {e}")
            self.status_indicator.config(bg="red")
            self.status_label.config(text="Ошибка", fg="red")
            
            # Планируем повторную попытку
            if self.auto_update and self.update_task is None:
                self.update_task = self.after(5000, self.update_data)
        finally:
            # Снимаем флаг обновления
            self._updating_data = False
    
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
        """Получает соединение с БД только из основного приложения (блок 8)"""
        try:
            # Используем только соединение из основного приложения (блок 8)
            if self.app and hasattr(self.app, 'get_db_connection'):
                try:
                    conn = self.app.get_db_connection()
                    if conn:
                        print("Module3: Используется соединение из главного приложения")
                        # Проверяем работоспособность соединения
                        conn.execute("SELECT 1")
                        return conn
                except Exception as e:
                    print(f"Module3: Ошибка при использовании app.get_db_connection(): {e}")
            
            # Проверяем app.conn как резерв
            if self.app and hasattr(self.app, 'conn') and self.app.conn is not None:
                try:
                    # Проверяем, работает ли соединение
                    self.app.conn.execute("SELECT 1")
                    print("Module3: Используется app.conn в качестве резерва")
                    return self.app.conn
                except Exception as e:
                    print(f"Module3: Ошибка проверки app.conn: {e}")
            
            print("Module3: Нет активной БД в системе (настройте БД в блоке 8)")
            return None
        except Exception as e:
            print(f"Module3: Общая ошибка при поиске соединения с БД: {e}")
            return None
            
    def get_control_and_lines_info(self):
        """Получает информацию о состоянии линий и параметрах управления из модуля 5."""
        try:
            info = ""
            
            # Получаем информацию о параметрах управления
            if self.app and hasattr(self.app, 'module5') and self.app.module5:
                module5 = self.app.module5
                
                # Параметры управления
                if hasattr(module5, 'get_control_parameters_for_report'):
                    control_params = module5.get_control_parameters_for_report()
                    info += "ПАРАМЕТРЫ УПРАВЛЕНИЯ:\n"
                    info += "-" * 30 + "\n"
                    info += f"Заданное давление: {control_params['pressure_setpoint']:.1f} МПа\n"
                    info += f"Заданная скорость откачки: {control_params['pumping_speed_setpoint']:.1f} м/с\n"
                    info += f"Заданная температура: {control_params['temperature_setpoint']:.1f} °C\n\n"
                
                # Состояние линий
                if hasattr(module5, 'get_line_states_for_report'):
                    line_states = module5.get_line_states_for_report()
                    info += "СОСТОЯНИЕ ЛИНИЙ НЕФТЕПРОВОДА:\n"
                    info += "-" * 30 + "\n"
                    info += f"Линия 1 (ячейки 1-10): {line_states['line_1']}\n"
                    info += f"Линия 2 (ячейки 11-20): {line_states['line_2']}\n"
                    info += f"Линия 3 (ячейки 21-30): {line_states['line_3']}\n"
                    info += f"Линия 4 (ячейки 31-40): {line_states['line_4']}\n"
                    info += f"Активных линий: {line_states['active_lines_count']}/{line_states['total_lines_count']}\n"
                    
                    # Общий статус системы
                    if line_states['active_lines_count'] == line_states['total_lines_count']:
                        system_status = "ШТАТНЫЙ РЕЖИМ"
                    elif line_states['active_lines_count'] > 0:
                        system_status = "ВНИМАНИЕ: НЕКОТОРЫЕ ЛИНИИ ОТКЛЮЧЕНЫ"
                    else:
                        system_status = "КРИТИЧНО: ВСЕ ЛИНИИ ОТКЛЮЧЕНЫ"
                    
                    info += f"Общий статус: {system_status}\n"
            else:
                info += "ПАРАМЕТРЫ УПРАВЛЕНИЯ:\n"
                info += "-" * 30 + "\n"
                info += "Модуль управления недоступен\n\n"
                info += "СОСТОЯНИЕ ЛИНИЙ НЕФТЕПРОВОДА:\n"
                info += "-" * 30 + "\n"
                info += "Информация о линиях недоступна\n"
            
            return info
            
        except Exception as e:
            print(f"Module3: Ошибка получения информации о управлении и линиях: {e}")
            return "ПАРАМЕТРЫ УПРАВЛЕНИЯ И СОСТОЯНИЕ ЛИНИЙ:\nОшибка получения данных\n"