import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sqlite3

class Module9(tk.Frame):
    def __init__(self, parent, connection_callback=None, *args, **kwargs):
        """
        :param parent: Родительский виджет.
        :param connection_callback: Функция, которая вызывается при успешном подключении.
                                    Должна принимать один аргумент — словарь с информацией о подключении.
                                    Например, это будет метод add_connection модуля 7.
        """
        super().__init__(parent, *args, **kwargs)
        self.connection_callback = connection_callback
        self.module8_ref = None  # Ссылка на модуль 8
        self.configure(bg="white")
        self.create_initial_ui()

    def create_initial_ui(self):
        """Исходное состояние модуля: одна кнопка 'Подключиться к БД'."""
        self.clear_frame()
        
        # Заголовок модуля
        header_label = tk.Label(self, text="Модуль подключения к базам данных", 
                               font=("Arial", 10, "bold"), bg="white")
        header_label.pack(pady=10)
        
        # Инструкция
        instruction_label = tk.Label(self, text="Используйте данный модуль для подключения к локальным\n"
                                           "или удалённым базам данных", 
                                   bg="white", justify="center")
        instruction_label.pack(pady=5)
        
        # Кнопка подключения
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(expand=True, pady=20)
        
        self.connect_button = tk.Button(button_frame, text="Подключиться к БД", 
                                      font=("Arial", 10), 
                                      width=20, height=2,
                                      command=self.show_connection_options)
        self.connect_button.pack()

    def show_connection_options(self):
        """Отображает три кнопки: локальное подключение, удалённое подключение, Назад."""
        self.clear_frame()
        
        # Заголовок
        tk.Label(self, text="Выберите тип подключения", 
               font=("Arial", 10, "bold"), bg="white").pack(pady=10)
        
        # Фрейм для кнопок с отступами
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(expand=True)

        self.btn_local = tk.Button(button_frame, text="Подключиться к локальной БД (SQLite)", 
                                   width=30, height=2,
                                   command=self.connect_local)
        self.btn_remote = tk.Button(button_frame, text="Подключиться к удалённой БД (PostgreSQL)", 
                                    width=30, height=2,
                                    command=self.connect_remote)
        self.btn_back = tk.Button(button_frame, text="Назад", 
                                 width=30,
                                 command=self.create_initial_ui)

        self.btn_local.pack(fill='x', padx=10, pady=5)
        self.btn_remote.pack(fill='x', padx=10, pady=5)
        self.btn_back.pack(fill='x', padx=10, pady=15)

    def connect_local(self):
        """Открывает диалог выбора файла для подключения к локальной БД (SQLite)."""
        file_path = filedialog.askopenfilename(
            title="Выберите файл БД SQLite",
            filetypes=[("SQLite DB", "*.sqlite *.db"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                # Сначала проверяем, существует ли файл
                if not os.path.exists(file_path):
                    messagebox.showerror("Ошибка", f"Файл базы данных не существует: {file_path}")
                    return
                
                # Используем абсолютный путь к файлу
                abs_path = os.path.abspath(file_path)
                
                # Проверяем возможность подключения к базе данных
                try:
                    # Создаем тестовое соединение с БД
                    connection = sqlite3.connect(abs_path, check_same_thread=False)
                    
                    # Тестируем соединение
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    
                    # Проверяем наличие нужных таблиц (raw_data и external_data)
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='raw_data' OR name='external_data')")
                    tables = cursor.fetchall()
                    tables = [t[0] for t in tables]
                    
                    if not ("raw_data" in tables or "external_data" in tables):
                        result = messagebox.askquestion("Предупреждение", 
                                         "В выбранной БД не найдены таблицы raw_data или external_data.\n"
                                         "Для корректной работы системы мониторинга необходимо наличие этих таблиц.\n"
                                         "Создать таблицы автоматически?")
                        if result == "yes":
                            # Создаем необходимые таблицы
                            cursor.execute("""
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
                            """)
                            
                            cursor.execute("""
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
                            """)
                            
                            # Добавляем тестовые данные
                            cursor.execute("""
                                INSERT INTO raw_data (
                                    cell_pressure, cell_temperature, cell_pumping_speed, 
                                    cell_vibrations, cell_tilt_angle, outdoor_temperature,
                                    outdoor_pressure, outdoor_wind, outdoor_humidity
                                ) VALUES (52.3, 20.5, 5.0, 0.1, 10.0, 25.0, 101.3, 5.0, 65.0)
                            """)
                            
                            cursor.execute("""
                                INSERT INTO external_data (
                                    sensor1_value, sensor2_value, sensor3_value, sensor4_value,
                                    flow_rate, temperature_external, pressure_atmospheric
                                ) VALUES (1.2, 4.5, 7.8, 10.1, 25.0, 22.0, 100.5)
                            """)
                            
                            connection.commit()
                            print(f"Module9: Созданы необходимые таблицы и тестовые данные")
                    
                    # Если соединение работает, создаем информацию о подключении
                    connection_info = {
                        "Название БД": os.path.basename(abs_path),
                        "Путь БД": abs_path,
                        "Тип БД": "SQLite Local",
                        "Статус": "Подключена",
                        "Пинг": "-",  # Для локальной БД пинг не применяется
                        "connection": connection  # Добавляем соединение в информацию
                    }
                    
                    print(f"Module9: Успешное подключение к БД {abs_path}")
                    
                    # Закрываем тестовое соединение - оно будет создано через основное приложение
                    connection.close()
                    
                    # Вызываем callback для обновления модуля 7
                    if self.connection_callback:
                        result = self.connection_callback(connection_info)
                        if not result:
                            # Если callback вернул False, сообщаем об ошибке
                            messagebox.showwarning("Информация", "Не удалось добавить подключение. Возможно, достигнуто максимальное количество подключений.")
                            return
                        
                        # Устанавливаем активную БД в основном приложении
                        app = self.winfo_toplevel()
                        if hasattr(app, 'set_active_database'):
                            app.set_active_database(abs_path)  # Используем полный путь к файлу
                        
                        # Разблокируем модули
                        if hasattr(app, 'unlock_modules'):
                            app.unlock_modules()
                        
                    # Уведомляем модуль 8 об изменении списка БД
                    self.notify_module8()
                    
                    # Показываем уведомление
                    messagebox.showinfo("Подключение", f"Успешно подключено к БД {os.path.basename(abs_path)}")
                    
                    # Возвращаемся к исходному интерфейсу
                    self.create_initial_ui()
                    
                except sqlite3.Error as e:
                    print(f"Module9: Ошибка SQLite при тестировании: {e}")
                    messagebox.showerror("Ошибка SQLite", f"Ошибка при тестировании подключения: {e}")
                    
            except Exception as e:
                print(f"Module9: Ошибка подключения к БД {file_path}: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных:\n{e}")

    def connect_remote(self):
        """Диалог подключения к удалённой БД (PostgreSQL)."""
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self)
        dialog.title("Подключение к удалённой БД")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        dialog.grab_set()  # Делаем окно модальным
        
        # Фрейм для формы
        form_frame = tk.Frame(dialog, padx=10, pady=10)
        form_frame.pack(fill="both", expand=True)
        
        # Поля ввода
        tk.Label(form_frame, text="Сервер:").grid(row=0, column=0, sticky="w", pady=5)
        server_entry = tk.Entry(form_frame, width=30)
        server_entry.grid(row=0, column=1, pady=5)
        server_entry.insert(0, "localhost")
        
        tk.Label(form_frame, text="Порт:").grid(row=1, column=0, sticky="w", pady=5)
        port_entry = tk.Entry(form_frame, width=30)
        port_entry.grid(row=1, column=1, pady=5)
        port_entry.insert(0, "5432")
        
        tk.Label(form_frame, text="База данных:").grid(row=2, column=0, sticky="w", pady=5)
        db_entry = tk.Entry(form_frame, width=30)
        db_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(form_frame, text="Пользователь:").grid(row=3, column=0, sticky="w", pady=5)
        user_entry = tk.Entry(form_frame, width=30)
        user_entry.grid(row=3, column=1, pady=5)
        user_entry.insert(0, "postgres")
        
        tk.Label(form_frame, text="Пароль:").grid(row=4, column=0, sticky="w", pady=5)
        pass_entry = tk.Entry(form_frame, width=30, show="*")
        pass_entry.grid(row=4, column=1, pady=5)
        
        # Кнопки
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", pady=10)
        
        # Функция для демонстрационного подключения
        def demo_connect():
            server = server_entry.get()
            port = port_entry.get()
            db_name = db_entry.get()
            
            if not db_name:
                messagebox.showwarning("Предупреждение", "Введите название базы данных")
                return
                
            # Симулируем успешное подключение для демонстрационной версии
            connection_info = {
                "Название БД": db_name,
                "Путь БД": f"{server}:{port}/{db_name}",
                "Тип БД": "PostgreSQL Remote",
                "Статус": "Подключена",
                "Пинг": "50 ms",
                "connection": None  # В демо-версии нет реального соединения
            }
            
            # Закрываем окно
            dialog.destroy()
            
            # Вызываем callback для обновления модуля 7
            if self.connection_callback:
                result = self.connection_callback(connection_info)
                if result:
                    messagebox.showinfo("Подключение", f"Демонстрационное подключение к БД {db_name} на {server}")
                    
                    # Устанавливаем активную БД в основном приложении
                    app = self.winfo_toplevel()
                    if hasattr(app, 'set_active_database'):
                        # Используем специальный формат для удаленных БД
                        app.set_active_database(f"remote:{server}:{port}/{db_name}")
                    
                    # Разблокируем модули
                    if hasattr(app, 'unlock_modules'):
                        app.unlock_modules()
            
            # Уведомляем модуль 8 об изменении списка БД
            self.notify_module8()
            
            # Возвращаемся к исходному интерфейсу
            self.create_initial_ui()
        
        tk.Button(button_frame, text="Подключиться", 
                command=demo_connect).pack(side="right", padx=5)
        tk.Button(button_frame, text="Отмена", 
                command=dialog.destroy).pack(side="right", padx=5)

    def notify_module8(self):
        """Уведомляет модуль 8 об изменении списка баз данных."""
        # Метод 1: Через прямую ссылку
        if self.module8_ref:
            if hasattr(self.module8_ref, 'refresh'):
                self.module8_ref.refresh()
            elif hasattr(self.module8_ref, 'update_databases'):
                self.module8_ref.update_databases()
            print("Module9: Уведомлен модуль 8 через прямую ссылку")
            return
            
        # Метод 2: Через основное приложение
        app = self.winfo_toplevel()
        if hasattr(app, 'module8') and app.module8:
            module8 = app.module8
            if hasattr(module8, 'refresh'):
                module8.refresh()
            elif hasattr(module8, 'update_databases'):
                module8.update_databases()
            print("Module9: Уведомлен модуль 8 через app.module8")
            return
            
        print("Module9: Не удалось уведомить модуль 8 - не найдена ссылка")

    def connect_to_database(self, db_path):
        """Подключение к базе данных по пути (для прямого вызова)"""
        try:
            # Проверяем существование файла
            if not os.path.exists(db_path):
                print(f"Module9: Файл БД {db_path} не существует")
                messagebox.showerror("Ошибка подключения", f"Файл базы данных не существует:\n{db_path}")
                return False
                
            # Используем абсолютный путь
            abs_path = os.path.abspath(db_path)
            
            # Создаем тестовое соединение
            conn = sqlite3.connect(abs_path, check_same_thread=False)
            
            # Тестируем соединение
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            
            # Получаем имя файла
            db_file = os.path.basename(abs_path)
            
            # Создаем информацию о подключении
            connection_info = {
                "Название БД": db_file,
                "Путь БД": abs_path,
                "Тип БД": "SQLite",
                "Статус": "Подключена",
                "Пинг": "-",
                "connection": conn
            }
            
            # Вызываем callback для обновления модуля 7
            if self.connection_callback:
                result = self.connection_callback(connection_info)
                if not result:
                    # Если callback вернул False, закрываем соединение и сообщаем об ошибке
                    conn.close()
                    messagebox.showwarning("Информация", "Не удалось добавить подключение. Возможно, достигнуто максимальное количество подключений.")
                    return False
                else:
                    print(f"Module9: БД {db_file} успешно подключена")
                    
                    # Устанавливаем активную БД в основном приложении
                    app = self.winfo_toplevel()
                    if hasattr(app, 'set_active_database'):
                        app.set_active_database(abs_path)
                    
                    # Разблокируем модули
                    if hasattr(app, 'unlock_modules'):
                        app.unlock_modules()
                        
                    # Уведомляем модуль 8 об изменении списка БД
                    self.notify_module8()
                    
                    # Закрываем тестовое соединение - оно будет создано через основное приложение
                    conn.close()
                    
                    return True
            else:
                # Если нет callback, просто устанавливаем активную БД
                app = self.winfo_toplevel()
                if hasattr(app, 'set_active_database'):
                    app.set_active_database(abs_path)
                
                # Разблокируем модули
                if hasattr(app, 'unlock_modules'):
                    app.unlock_modules()
                
                # Уведомляем модуль 8 об изменении списка БД
                self.notify_module8()
            
                # Закрываем тестовое соединение - оно будет создано через основное приложение
                conn.close()
            
                return True
            
        except Exception as e:
            print(f"Module9: Ошибка при подключении к БД {db_path}: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных:\n{e}")
            return False

    def unlock_module3(self):
        """Разблокирует модуль 3 (если есть)."""
        app = self.winfo_toplevel()
        
        # Разблокируем через основное приложение (если есть метод)
        if hasattr(app, 'unlock_modules'):
            app.unlock_modules()
        
        # Альтернативный способ: ищем модуль 3 и вызываем его метод
        module3 = None
        
        # Способ 1: Через основное приложение
        if hasattr(app, 'module3') and app.module3:
            module3 = app.module3
            
        if module3 and hasattr(module3, 'unlock'):
            module3.unlock()
            print("Module9: Модуль 3 разблокирован через метод unlock")
            return True
            
        # Способ 2: Ищем в tiles основного приложения
        if hasattr(app, 'tiles') and app.tiles:
            try:
                # В app.tiles[0][2] должен быть модуль 3
                module3_tile = app.tiles[0][2]
                if hasattr(module3_tile, 'set_locked'):
                    module3_tile.set_locked(False)
                    print("Module9: Модуль 3 разблокирован через set_locked")
                    return True
            except:
                pass
                
        return False

    def clear_frame(self):
        """Очищает все виджеты во фрейме."""
        for widget in self.winfo_children():
            widget.destroy()

    def set_module8_ref(self, module8):
        """Устанавливает прямую ссылку на модуль 8."""
        self.module8_ref = module8
        print("Module9: Установлена прямая ссылка на модуль 8")
