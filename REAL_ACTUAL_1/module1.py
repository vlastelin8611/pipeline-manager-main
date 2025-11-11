import tkinter as tk
import sqlite3
import os
from tkinter import messagebox, Toplevel, simpledialog, StringVar, filedialog

class Module1(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.parent = parent
        
        # Store main application reference
        self.app = None
        self.find_app_reference()
        
        # Local variables
        self.local_conn = None
        self.selected_table = None
        self.current_db_path = None  # Добавляем переменную для хранения полного пути к файлу БД
        
        # Create a main layout frame with two columns
        self.main_layout = tk.Frame(self, bg="white")
        self.main_layout.pack(fill="both", expand=True)
        
        # Left side for cells
        self.left_frame = tk.Frame(self.main_layout, bg="white")
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        # Right side for controls
        self.right_frame = tk.Frame(self.main_layout, bg="white") 
        self.right_frame.pack(side="right", fill="y", padx=5)
        
        # Title at the top
        self.title = tk.Label(self.left_frame, text="Статус ячеек нефтепровода", 
                            font=("Arial", 12, "bold"), bg="white")
        self.title.pack(pady=2)
        
        # Create a frame for cells grid
        self.cells_frame = tk.Frame(self.left_frame, bg="white")
        self.cells_frame.pack(fill="both", expand=True, padx=5, pady=2)
        
        # Create cells grid (8x5 = 40 cells)
        self.cell_indicators = []
        for row in range(8):
            for col in range(5):
                index = row * 5 + col
                cell_frame = tk.Frame(self.cells_frame, bg="white", width=30, height=30)
                cell_frame.grid(row=row, column=col, padx=3, pady=3)
                cell_frame.grid_propagate(False)
                
                # Create cell indicator (square)
                cell = tk.Canvas(cell_frame, width=25, height=25, bg="gray", bd=0, highlightthickness=0)
                cell.pack(padx=1, pady=1)
                
                # Add cell number
                cell.create_text(12, 12, text=str(index+1), fill="white", font=("Arial", 8))
                
                self.cell_indicators.append(cell)
        
        # Status display on right side
        status_frame = tk.Frame(self.right_frame, bg="white")
        status_frame.pack(fill="x", pady=5)
        
        status_label = tk.Label(status_frame, text="Статус:", 
                               bg="white", font=("Arial", 9, "bold"))
        status_label.pack(anchor="w")
        
        self.status_msg = tk.Label(status_frame, text="Ожидание подключения к БД...", 
                               fg="gray", bg="white", font=("Arial", 8))
        self.status_msg.pack(anchor="w", padx=5)
        
        # Database info
        db_frame = tk.Frame(self.right_frame, bg="white")
        db_frame.pack(fill="x", pady=5)
        
        db_title = tk.Label(db_frame, text="База данных:", 
                          bg="white", font=("Arial", 9, "bold"))
        db_title.pack(anchor="w")
        
        self.db_label = tk.Label(db_frame, text="не подключена", 
                              fg="gray", bg="white", font=("Arial", 8, "italic"))
        self.db_label.pack(anchor="w", padx=5)
        
        # Table info
        table_frame = tk.Frame(self.right_frame, bg="white")
        table_frame.pack(fill="x", pady=5)
        
        table_title = tk.Label(table_frame, text="Таблица:", 
                             bg="white", font=("Arial", 9, "bold"))
        table_title.pack(anchor="w")
        
        self.table_label = tk.Label(table_frame, text="не выбрана", 
                                 fg="gray", bg="white", font=("Arial", 8, "italic"))
        self.table_label.pack(anchor="w", padx=5)
        
        # Connection indicator (replace canvas with text label)
        indicator_frame = tk.Frame(self.right_frame, bg="white")
        indicator_frame.pack(fill="x", pady=5)
        
        indicator_title = tk.Label(indicator_frame, text="Статус соединения:", 
                                 bg="white", font=("Arial", 9, "bold"))
        indicator_title.pack(anchor="w")
        
        # Replace canvas indicator with text label
        self.conn_status = tk.Label(indicator_frame, text="Не подключено", 
                                  fg="red", bg="white", font=("Arial", 8))
        self.conn_status.pack(anchor="w", padx=5, pady=2)
        
        # Button frame
        self.button_frame = tk.Frame(self.right_frame, bg="white")
        self.button_frame.pack(fill="x", pady=5)
        
        # Create only the essential buttons (БД выбирается только через блок 8)
        self.table_btn = tk.Button(self.button_frame, text="Выбрать таблицу", 
                                 command=self.select_table)
        self.table_btn.pack(fill="x", pady=2)
        
        self.refresh_btn = tk.Button(self.button_frame, text="Обновить", 
                                  command=self.force_refresh)
        self.refresh_btn.pack(fill="x", pady=2)
        
        # Create auto-update toggle button with indicator
        self.auto_update_frame = tk.Frame(self.button_frame, bg="white")
        self.auto_update_frame.pack(fill="x", pady=2)

        self.auto_update = False  # Default is disabled
        self.auto_indicator = tk.Canvas(self.auto_update_frame, width=15, height=15, 
                                     bg="red", bd=0, highlightthickness=0)
        self.auto_indicator.pack(side="left", padx=5)

        self.auto_btn = tk.Button(self.auto_update_frame, text="Автообновление", 
                               command=self.toggle_auto_update)
        self.auto_btn.pack(fill="x")
        
        # Pack the frame
        self.pack(fill="both", expand=True)
        
        # Register with main application
        if self.app is not None:
            self.app.module1 = self
        
        # Initial update attempt
        self.after(1000, self.update_cells)
        
        # Set up periodic update (every 5 seconds)
        self.after(5000, self.periodic_update)
    
    def connect_to_database(self):
        """Open a dialog to choose a database file and connect to it"""
        # Open file dialog
        cwd = os.getcwd()
        print(f"Module1: Текущая рабочая директория: {cwd}")
        
        file_path = filedialog.askopenfilename(
            initialdir=cwd,
            title="Выберите файл базы данных SQLite",
            filetypes=[("DB files", "*.db"), ("SQLite files", "*.sqlite"), ("All files", "*.*")]
        )
        
        if not file_path:
            print("Module1: Выбор файла БД отменен")
            return False
            
        # Check if file exists
        if not os.path.isfile(file_path):
            self.status_msg.config(text=f"Файл {file_path} не существует", fg="red")
            print(f"Module1: Файл БД {file_path} не существует")
            return False
        
        # Extract database name from path
        file_name = os.path.basename(file_path)
        db_name = os.path.splitext(file_name)[0]
        
        print(f"Module1: Выбран файл БД: {file_path}")
        print(f"Module1: Установлен current_db_path (абсолютный): {file_path}")
        self.current_db_path = file_path  # Сохраняем абсолютный путь
        
        # Если есть основное приложение, используем его метод
        if self.app and hasattr(self.app, 'set_active_database'):
            if self.app.set_active_database(file_path):
                # Обновляем UI
                self.db_label.config(text=f"База данных: {db_name}", fg="green")
                self.status_msg.config(text=f"Подключено к БД {db_name}", fg="green")
                self.conn_status.config(text="Подключено", fg="green")
                
                # Сбрасываем выбранную таблицу
                self.selected_table = None
                self.table_label.config(text="Таблица: не выбрана", fg="gray")
                
                # Очищаем ячейки (устанавливаем серый цвет)
                for cell in self.cell_indicators:
                    cell.config(bg="gray")
                
                # После успешного подключения обновляем данные
                self.update_cells(fresh_query=True)
                
                return True
        
        # Если не удалось через основное приложение, пробуем напрямую
        # Закрываем предыдущее соединение
        if self.local_conn:
            try:
                self.local_conn.close()
                print("Module1: Закрыто предыдущее соединение")
            except Exception as e:
                print(f"Module1: Ошибка при закрытии соединения: {e}")
        
        # Получаем соединение через общий метод
        self.local_conn = self.get_connection(force_new=True)
        
        if not self.local_conn:
            self.status_msg.config(text=f"Ошибка подключения к {db_name}", fg="red")
            self.conn_status.config(text="Ошибка подключения", fg="red")
            return False
            
        # Обновляем UI
        self.db_label.config(text=f"База данных: {db_name}", fg="green")
        self.status_msg.config(text=f"Подключено к БД {db_name}", fg="green")
        self.conn_status.config(text="Подключено", fg="green")
        
        # Сбрасываем выбранную таблицу
        self.selected_table = None
        self.table_label.config(text="Таблица: не выбрана", fg="gray")
        
        # Очищаем ячейки (устанавливаем серый цвет)
        for cell in self.cell_indicators:
            cell.config(bg="gray")
            
        # После успешного подключения обновляем данные
        self.update_cells(fresh_query=True)
        
        print(f"Module1: Успешное подключение к БД {file_path}")
        return True
    
    def connect_to_specific_db(self, db_name, file_path=None):
        """Connect to a specific database"""
        try:
            # Update application database connection if possible
            if self.app:
                if self.app.set_active_database(db_name):
                    self.db_label.config(text=f"База данных: {db_name}", fg="green")
                    self.status_msg.config(text=f"Подключено к БД {db_name}", fg="green")
                    self.conn_status.config(text="Подключено", fg="green")
                    return True
            
            # Otherwise, create a local connection
            if file_path:
                db_file = file_path
                print(f"Module1: Используется указанный путь: {db_file}")
            else:
                # Формируем путь к файлу без префикса nefteprovod_
                db_file = f"{db_name}.db"
                print(f"Module1: Сформирован путь из имени: {db_file}")
            
            # Сохраняем путь к файлу БД для последующих обновлений
            self.current_db_path = db_file
            print(f"Module1: Установлен current_db_path: {self.current_db_path}")
            
            # Check if file exists
            if not os.path.exists(db_file):
                self.status_msg.config(text=f"Файл БД {db_file} не существует", fg="red")
                self.conn_status.config(text="Ошибка подключения", fg="red")
                return False
            
            # Close any existing connection
            if self.local_conn:
                try:
                    self.local_conn.close()
                    print(f"Module1: Закрыто предыдущее соединение")
                except Exception as e:
                    print(f"Module1: Ошибка закрытия соединения: {e}")
                self.local_conn = None
                
            # Connect to database with direct file access
            self.local_conn = sqlite3.connect(db_file, isolation_level=None)
            
            # Отключаем кэширование для обеспечения актуальности данных
            self.local_conn.execute("PRAGMA cache_size = 0")
            self.local_conn.execute("PRAGMA synchronous = OFF")
            self.local_conn.execute("PRAGMA journal_mode = OFF")
            
            print(f"Module1: Прямое подключение к БД {db_file} успешно")
            
            # Update UI
            self.db_label.config(text=f"База данных: {db_name}", fg="green")
            self.status_msg.config(text=f"Подключено к БД {db_name}", fg="green")
            self.conn_status.config(text="Подключено", fg="green")
            
            # Reset selected table
            self.selected_table = None
            self.table_label.config(text="Таблица: не выбрана", fg="gray")
            
            # Clear cells (set to gray)
            for cell in self.cell_indicators:
                cell.config(bg="gray")
                
            return True
        except Exception as e:
            self.status_msg.config(text=f"Ошибка подключения к БД: {e}", fg="red")
            self.conn_status.config(text="Ошибка подключения", fg="red")
            print(f"Module1: Ошибка подключения к БД {db_name}: {e}")
            return False
    
    def find_app_reference(self):
        """Find the main Application instance"""
        try:
            # Navigate up the widget hierarchy to find the main application
            widget = self.parent
            while widget:
                # Check if this is the root window (Application)
                if isinstance(widget, tk.Tk) and hasattr(widget, 'db_connected'):
                    self.app = widget
                    print("Module1: Найдено главное приложение")
                    return
                
                # Alternative: if parent widget has a reference to the main app
                if hasattr(widget, 'master') and hasattr(widget.master, 'master'):
                    if hasattr(widget.master.master, 'db_connected'):
                        self.app = widget.master.master
                        print("Module1: Найдено главное приложение (через master.master)")
                        return
                
                # Move up one level in the hierarchy
                if hasattr(widget, 'master'):
                    widget = widget.master
                else:
                    break
            
            print("Module1: Не найдено главное приложение")
        except Exception as e:
            print(f"Module1: Ошибка при поиске главного приложения: {e}")
    
    def is_line_disabled(self, line_number):
        """Проверяет, отключена ли указанная линия в модуле 5."""
        try:
            if self.app and hasattr(self.app, 'module5') and self.app.module5:
                # Получаем состояние линии из модуля 5
                if hasattr(self.app.module5, 'line_states'):
                    return not self.app.module5.line_states.get(line_number, True)
            return False  # По умолчанию линия включена
        except Exception as e:
            print(f"Module1: Ошибка проверки состояния линии {line_number}: {e}")
            return False
    
    def debug_connection(self):
        """Show debug information about database connection"""
        debug_info = []
        
        # Check main app reference
        if self.app:
            debug_info.append(f"Найдено главное приложение: {self.app}")
            
            # Check connection attributes
            if hasattr(self.app, 'db_connected'):
                debug_info.append(f"db_connected: {self.app.db_connected}")
            else:
                debug_info.append("Атрибут db_connected не найден")
                
            if hasattr(self.app, 'active_db'):
                debug_info.append(f"active_db: {self.app.active_db}")
            else:
                debug_info.append("Атрибут active_db не найден")
                
            if hasattr(self.app, 'conn'):
                debug_info.append(f"conn: {self.app.conn}")
                
                # Test connection
                try:
                    cursor = self.app.conn.cursor()
                    cursor.execute("SELECT sqlite_version()")
                    version = cursor.fetchone()
                    debug_info.append(f"SQLite версия: {version[0]}")
                    
                    # List tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    if tables:
                        table_list = ", ".join([t[0] for t in tables])
                        debug_info.append(f"Таблицы: {table_list}")
                    else:
                        debug_info.append("Таблиц не найдено")
                except Exception as e:
                    debug_info.append(f"Ошибка доступа к БД: {e}")
            else:
                debug_info.append("Атрибут conn не найден")
        else:
            debug_info.append("Главное приложение не найдено")
            
        # Show debug information
        messagebox.showinfo("Диагностика подключения к БД", "\n".join(debug_info))
    
    def get_connection(self, force_new=False):
        """Получить соединение с БД только из основного приложения (блок 8)"""
        # Используем только соединение из основного приложения (блок 8)
        if self.app and hasattr(self.app, 'get_db_connection'):
            try:
                conn = self.app.get_db_connection()
                if conn:
                    print("Module1: Используем соединение из основного приложения")
                    # Проверяем работоспособность соединения
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    return conn
            except Exception as e:
                print(f"Module1: Ошибка получения соединения из приложения: {e}")
        
        # Проверяем app.conn как резерв
        if self.app and hasattr(self.app, 'conn') and self.app.conn:
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("SELECT 1")
                print("Module1: Используем app.conn в качестве резерва")
                return self.app.conn
            except Exception as e:
                print(f"Module1: Ошибка при использовании app.conn: {e}")
        
        print("Module1: Нет активной БД в системе (настройте БД в блоке 8)")
        self.status_msg.config(text="Нет активной БД (настройте в блоке 8)", fg="red")
        return None
    
    def get_active_database(self):
        """Найти имя активной базы данных"""
        if self.app and hasattr(self.app, 'active_db') and self.app.active_db:
            return self.app.active_db
        
        # Default database name if nothing else is found
        return "data"
    
    def get_database_tables(self):
        """Получить список таблиц в текущей БД"""
        try:
            # Пробуем использовать соединение из основного приложения
            conn = None
            should_close = False
            
            if self.app and hasattr(self.app, 'conn') and self.app.conn:
                try:
                    # Проверяем работоспособность соединения
                    cursor = self.app.conn.cursor()
                    cursor.execute("SELECT 1")
                    conn = self.app.conn
                    print("Module1: Используем соединение приложения для получения таблиц")
                except Exception as e:
                    print(f"Module1: Ошибка соединения приложения: {e}")
            
            # Если соединения из приложения нет, ищем файл БД
            if not conn:
                db_file = self.find_db_file()
                if not db_file:
                    print("Module1: Файл БД не найден для получения таблиц")
                    self.status_msg.config(text="Файл БД не найден", fg="red")
                    return []
                
                # Создаем временное соединение для чтения
                conn = sqlite3.connect(db_file, timeout=30.0)
                conn.execute("PRAGMA busy_timeout = 30000")
                should_close = True
            
            cursor = conn.cursor()
            
            # Запрашиваем список таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Закрываем временное соединение
            if should_close:
                cursor.close()
                conn.close()
            
            print(f"Module1: Найдено {len(tables)} таблиц в БД: {tables}")
            return tables
            
        except sqlite3.Error as e:
            print(f"Module1: Ошибка получения списка таблиц: {e}")
            self.status_msg.config(text=f"Ошибка получения таблиц: {e}", fg="red")
            return []
    
    def select_table(self):
        """Открыть диалог для выбора таблицы из БД"""
        # Статус: пытаемся получить таблицы из БД
        self.status_msg.config(text="Получение списка таблиц из БД...", fg="blue")
        
        # Получаем список таблиц
        tables = self.get_database_tables()
        
        if not tables:
            messagebox.showinfo("Нет доступных таблиц", 
                               "В текущей базе данных не найдено таблиц. Проверьте подключение к БД.")
            return
            
        # Создаем диалог выбора таблицы
        table_dialog = Toplevel(self)
        table_dialog.title("Выбор таблицы")
        table_dialog.geometry("300x350")
        table_dialog.transient(self)
        table_dialog.grab_set()
        table_dialog.focus_set()
        
        # Создаем фрейм для инструкций
        instruction_frame = tk.Frame(table_dialog, bg="white", padx=10, pady=5)
        instruction_frame.pack(fill="x", side="top")
        
        # Инструкции
        tk.Label(instruction_frame, text="Выберите таблицу с данными о ячейках:",
                bg="white", anchor="w").pack(fill="x")
        
        # Создаем фрейм для списка
        list_frame = tk.Frame(table_dialog, padx=10, pady=5)
        list_frame.pack(fill="both", expand=True)
        
        # Создаем полосу прокрутки
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Создаем список с таблицами
        listbox = tk.Listbox(list_frame, selectmode="single", 
                           yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Добавляем таблицы в список
        for table in tables:
            listbox.insert(tk.END, table)
        
        # Предварительно выбираем текущую таблицу, если она существует
        if self.selected_table and self.selected_table in tables:
            idx = tables.index(self.selected_table)
            listbox.select_set(idx)
            listbox.see(idx)
            
        # Создаем фрейм для деталей
        details_frame = tk.Frame(table_dialog, bg="white", padx=10, pady=5)
        details_frame.pack(fill="x", side="top")
        
        details_label = tk.Label(details_frame, text="", bg="white")
        details_label.pack(fill="x")
        
        # Функция для отображения информации о столбцах выбранной таблицы
        def show_table_details(*args):
            if not listbox.curselection():
                return
                
            selected_idx = listbox.curselection()[0]
            table_name = tables[selected_idx]
            
            try:
                # Находим файл БД
                db_file = self.find_db_file()
                if not db_file:
                    details_label.config(text="Файл БД не найден")
                    return
                    
                # Создаем соединение
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Получаем информацию о столбцах
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                # Показываем столбцы
                details_label.config(text=f"Столбцы: {', '.join(column_names)}")
                
                # Закрываем соединение
                cursor.close()
                conn.close()
                
            except Exception as e:
                details_label.config(text=f"Ошибка: {e}")
        
        # Привязываем событие выбора
        listbox.bind('<<ListboxSelect>>', show_table_details)
        
        # Фрейм для кнопок
        button_frame = tk.Frame(table_dialog, padx=10, pady=10)
        button_frame.pack(fill="x", side="bottom")
        
        # Кнопка отмены
        cancel_btn = tk.Button(button_frame, text="Отмена", 
                             command=table_dialog.destroy)
        cancel_btn.pack(side="left", padx=5)
        
        # Функция выбора таблицы
        def on_select():
            if not listbox.curselection():
                messagebox.showwarning("Выбор таблицы", "Пожалуйста, выберите таблицу")
                return
                
            selected_idx = listbox.curselection()[0]
            table_name = tables[selected_idx]
            
            # Устанавливаем выбранную таблицу
            self.selected_table = table_name
            self.table_label.config(text=f"Таблица: {table_name}", fg="green")
            
            # Закрываем диалог
            table_dialog.destroy()
            
            # Обновляем ячейки
            self.update_cells(fresh_query=True)
        
        # Кнопка выбора
        select_btn = tk.Button(button_frame, text="Выбрать", command=on_select)
        select_btn.pack(side="right", padx=5)
        
        # Ждем закрытия диалога
        self.wait_window(table_dialog)
    
    def update_cells(self, fresh_query=False):
        """Обновить ячейки на основе актуальных данных из БД"""
        # Проверка выбора таблицы
        if not self.selected_table:
            self.status_msg.config(text="Таблица не выбрана", fg="blue")
            return False
            
        try:
            # ИСПОЛЬЗУЕМ ЕДИНОЕ СОЕДИНЕНИЕ ИЗ ОСНОВНОГО ПРИЛОЖЕНИЯ
            conn = None
            if self.app and hasattr(self.app, 'conn') and self.app.conn:
                try:
                    # Проверяем работоспособность соединения
                    cursor = self.app.conn.cursor()
                    cursor.execute("SELECT 1")
                    conn = self.app.conn
                    print("Module1: Используем соединение из основного приложения")
                except Exception as e:
                    print(f"Module1: Ошибка соединения из приложения: {e}")
            
            # Если соединения из приложения нет, ищем файл БД
            if not conn:
                db_file = self.find_db_file()
                if not db_file:
                    self.status_msg.config(text="Файл БД не найден", fg="red")
                    return False
                
                # Создаем временное соединение ТОЛЬКО для чтения
                conn = sqlite3.connect(db_file, timeout=30.0)
                conn.execute("PRAGMA busy_timeout = 30000")  # 30 секунд timeout
                should_close = True
            else:
                should_close = False
            
            cursor = conn.cursor()
            
            # Получаем информацию о столбцах таблицы
            cursor.execute(f"PRAGMA table_info({self.selected_table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Находим подходящие столбцы для ID и статуса
            id_column = next((col for col in ['cell_id', 'id'] if col in columns), None)
            status_column = next((col for col in ['working_status', 'status'] if col in columns), None)
            
            if not id_column or not status_column:
                self.status_msg.config(text=f"Не найдены нужные столбцы в таблице", fg="red")
                if should_close:
                    cursor.close()
                    conn.close()
                return False
            
            # Выполняем запрос
            query = f"SELECT {id_column}, {status_column} FROM {self.selected_table}"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Отладочная информация
            print(f"Module1: Прочитано {len(rows)} строк из таблицы {self.selected_table}")
            
            # Обрабатываем полученные данные
            cell_statuses = {}
            for row in rows:
                try:
                    cell_id = int(row[0])
                    status = 1 if row[1] == 1 or str(row[1]).strip() == '1' else 0
                    cell_statuses[cell_id] = status
                except Exception as e:
                    print(f"Module1: Ошибка обработки строки {row}: {e}")
            
            # Обновляем каждую ячейку
            for i, cell in enumerate(self.cell_indicators):
                cell_id = i + 1  # ID ячеек начинаются с 1
                
                # Проверяем состояние линии (приоритет выше других цветов)
                line_number = (i // 10) + 1  # Определяем номер линии (1-4)
                is_line_disabled = self.is_line_disabled(line_number)
                
                if is_line_disabled:
                    # Линия отключена - оранжевый цвет (высший приоритет)
                    cell.config(bg="orange")
                    cell.itemconfig(1, fill="black")  # Текст черный на оранжевом фоне
                elif cell_id in cell_statuses:
                    # Устанавливаем цвет на основе статуса
                    if cell_statuses[cell_id] == 1:
                        cell.config(bg="green")
                        cell.itemconfig(1, fill="black")  # Текст черный на зеленом фоне
                    else:
                        cell.config(bg="red")
                        cell.itemconfig(1, fill="white")  # Текст белый на красном фоне
                else:
                    # Ячейка не найдена в БД
                    cell.config(bg="gray")
                    cell.itemconfig(1, fill="white")  # Текст белый на сером фоне
                    
            # Обновляем статус
            if self.app and hasattr(self.app, 'active_db'):
                db_name = self.app.active_db or "БД"
            else:
                db_name = "БД"
            self.status_msg.config(text=f"Данные обновлены из {db_name}", fg="green")
            
            # Закрываем временное соединение если создавали его
            if should_close:
                cursor.close()
                conn.close()
            
            return True
            
        except Exception as e:
            self.status_msg.config(text=f"Ошибка обновления: {e}", fg="red")
            print(f"Module1: Ошибка обновления ячеек: {e}")
            return False
    
    def periodic_update(self):
        """Периодическое обновление данных из БД"""
        try:
            if self.auto_update:
                # Выполняем полное переподключение к БД для обновления данных
                self.force_refresh()
                print("Module1: Выполнено автоматическое обновление данных")
        except Exception as e:
            print(f"Module1: Ошибка автоматического обновления: {e}")
        finally:
            # Планируем следующее обновление через 5 секунд
            self.after(5000, self.periodic_update)
    
    def show_data_dialog(self):
        """Display a dialog with the current data from the selected table"""
        # Implementation code would go here
        pass

    def simulate_working_cells(self):
        """Update all cells to working status (for testing)"""
        conn = self.get_connection()
        if not conn or not self.selected_table:
            return
            
        try:
            cursor = conn.cursor()
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({self.selected_table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Find status column
            status_column = None
            for col in ['working_status', 'status', 'статус', 'работает', 'working']:
                if col in columns:
                    status_column = col
                    break
            
            if not status_column:
                messagebox.showinfo("Ошибка", "Не найден столбец статуса")
                return
                
            # Update all cells to working status (1)
            cursor.execute(f"UPDATE {self.selected_table} SET {status_column} = 1")
            conn.commit()
            
            # Update the display
            self.update_cells()
            
            messagebox.showinfo("Готово", "Все ячейки установлены как рабочие (зелёные)")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")

    def simulate_random_cells(self):
        """Randomize cell statuses (for testing)"""
        import random
        
        conn = self.get_connection()
        if not conn or not self.selected_table:
            return
            
        try:
            cursor = conn.cursor()
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({self.selected_table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Find ID and status columns
            status_column = None
            id_column = None
            
            for col in ['working_status', 'status', 'статус', 'работает', 'working']:
                if col in columns:
                    status_column = col
                    break
                    
            for col in ['cell_id', 'id', 'cell', 'ячейка', 'номер']:
                if col in columns:
                    id_column = col
                    break
            
            if not status_column or not id_column:
                messagebox.showinfo("Ошибка", "Не найдены нужные столбцы")
                return
                
            # Get all cell IDs
            cursor.execute(f"SELECT {id_column} FROM {self.selected_table}")
            cell_ids = [row[0] for row in cursor.fetchall()]
            
            # Update each cell with random status (0 or 1)
            for cell_id in cell_ids:
                status = random.randint(0, 1)
                cursor.execute(f"UPDATE {self.selected_table} SET {status_column} = ? WHERE {id_column} = ?", 
                            (status, cell_id))
            
            conn.commit()
            
            # Update the display
            self.update_cells()
            
            messagebox.showinfo("Готово", "Случайные статусы установлены для всех ячеек")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")

    def debug_cell_values(self):
        """Debug the cell values being used for coloring"""
        if not self.selected_table or not self.get_connection():
            messagebox.showinfo("Debug", "No table selected or no connection")
            return
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({self.selected_table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Find status column
            status_column = None
            id_column = None
            
            for col in ['working_status', 'status', 'статус', 'работает', 'working']:
                if col in columns:
                    status_column = col
                    break
                    
            for col in ['cell_id', 'id', 'cell', 'ячейка', 'номер']:
                if col in columns:
                    id_column = col
                    break
            
            if not status_column or not id_column:
                messagebox.showinfo("Debug", "Could not find status or id column")
                return
            
            # Get all values
            cursor.execute(f"SELECT {id_column}, {status_column} FROM {self.selected_table}")
            rows = cursor.fetchall()
            
            debug_info = ["Debug Cell Values:"]
            for row in rows[:20]:  # Show first 20 rows
                cell_id, status = row
                debug_info.append(f"Cell {cell_id}: {status} (type: {type(status).__name__})")
                
            messagebox.showinfo("Cell Values Debug", "\n".join(debug_info))
            
        except Exception as e:
            messagebox.showerror("Debug Error", f"Error: {e}")

    def debug_cell_colors(self):
        """Debug detailed cell coloring logic"""
        if not self.selected_table or not self.get_connection():
            messagebox.showinfo("Debug", "No table selected or no connection")
            return
            
        try:
            # Implementation code here
            pass
        except Exception as e:
            print(f"Debug error: {e}")

    def fix_cell_colors(self):
        """Apply a fixed version of the cell coloring logic"""
        if not self.selected_table or not self.get_connection():
            return
            
        try:
            # Implementation code here
            pass
        except Exception as e:
            print(f"Error fixing colors: {e}")

    def force_refresh(self):
        """Полное переподключение к БД и обновление данных"""
        try:
            # Показываем статус обновления
            self.status_msg.config(text="Обновление данных из БД...", fg="blue")
            
            # Проверяем соединение с основным приложением
            if self.app and hasattr(self.app, 'conn') and self.app.conn:
                try:
                    # Проверяем работоспособность соединения
                    cursor = self.app.conn.cursor()
                    cursor.execute("SELECT 1")
                    
                    # Получаем имя БД из основного приложения
                    if hasattr(self.app, 'active_db') and self.app.active_db:
                        db_name = self.app.active_db
                    else:
                        db_name = "БД"
                    
                    # Обновляем UI для состояния подключения
                    self.db_label.config(text=f"База данных: {db_name}", fg="green")
                    self.status_msg.config(text=f"Используем соединение к {db_name}", fg="green")
                    self.conn_status.config(text="Подключено", fg="green")
                    
                    # Обновляем данные ячеек
                    self.update_cells(fresh_query=True)
                    
                    print(f"Module1: Использовано соединение из основного приложения")
                    return True
                    
                except Exception as e:
                    print(f"Module1: Ошибка использования соединения приложения: {e}")
            
            # Если соединения из приложения нет, ищем файл БД
            db_file = self.find_db_file()
            
            if not db_file:
                self.status_msg.config(text="Файл БД не найден", fg="red")
                return False
                
            # Получаем имя БД из имени файла
            file_name = os.path.basename(db_file)
            db_name = file_name.replace('.db', '')  # Просто удаляем расширение
            
            # Закрываем текущее локальное соединение если есть
            if self.local_conn:
                try:
                    self.local_conn.close()
                    print(f"Module1: Закрыто локальное соединение")
                except Exception as e:
                    print(f"Module1: Ошибка закрытия соединения: {e}")
                self.local_conn = None
            
            # Обновляем UI для состояния подключения
            self.status_msg.config(text=f"Подключение к БД {db_name}...", fg="blue")
            self.conn_status.config(text="Подключение...", fg="blue")
            
            # Уведомляем основное приложение об изменении БД
            if self.app and hasattr(self.app, 'set_active_database'):
                if self.app.set_active_database(db_file):
                    # Обновляем UI
                    self.db_label.config(text=f"База данных: {db_name}", fg="green")
                    self.status_msg.config(text=f"Подключено к БД {db_name}", fg="green")
                    self.conn_status.config(text="Подключено", fg="green")
                    
                    # Обновляем данные ячеек
                    self.update_cells(fresh_query=True)
                    
                    print(f"Module1: Успешное подключение к БД {db_file} через основное приложение")
                    return True
                else:
                    self.status_msg.config(text=f"Ошибка подключения к {db_name}", fg="red")
                    self.conn_status.config(text="Ошибка подключения", fg="red")
                    return False
            else:
                # Если нет основного приложения, обновляем напрямую
                self.db_label.config(text=f"База данных: {db_name}", fg="green")
                self.status_msg.config(text=f"Найдена БД {db_name}", fg="green")
                self.conn_status.config(text="Файл найден", fg="green")
                
                # Обновляем данные ячеек
                self.update_cells(fresh_query=True)
                
                return True
                
        except Exception as e:
            print(f"Module1: Ошибка полного обновления: {e}")
            self.status_msg.config(text=f"Ошибка обновления: {e}", fg="red")
            return False

    def verify_db_values(self):
        """Directly check DB values by reopening connection"""
        try:
            # Implementation code here
            pass
        except Exception as e:
            messagebox.showerror("Ошибка проверки", f"Не удалось проверить значения: {e}")

            # If we get here, check we have both columns needed
            if not id_column or not status_column:
                print(f"Missing required columns in {self.selected_table}")
                return
                
            # Execute query
            query = f"SELECT {id_column}, {status_column} FROM {self.selected_table}"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Create properly formatted dictionary
            cell_statuses = {}
            for row in rows:
                try:
                    cell_id = int(row[0])
                    status = int(row[1]) if row[1] is not None else 0
                    cell_statuses[cell_id] = status
                except (ValueError, TypeError) as e:
                    print(f"Error converting row {row}: {e}")
            
            # Update UI with success message
            db_name = self.get_active_database()

    # Add this new method to toggle auto update
    def toggle_auto_update(self):
        """Включение/отключение автоматического обновления данных"""
        self.auto_update = not self.auto_update
        
        if self.auto_update:
            self.auto_indicator.config(bg="green")
            self.status_msg.config(text="Автообновление включено", fg="green")
            print("Module1: Автообновление включено")
            # Выполняем немедленное обновление при включении
            self.force_refresh()
        else:
            self.auto_indicator.config(bg="red")
            self.status_msg.config(text="Автообновление отключено", fg="gray")
            print("Module1: Автообновление отключено")

    def find_db_file(self):
        """Ищет файл БД в рабочей директории и возвращает абсолютный путь"""
        # Текущая рабочая директория
        current_dir = os.path.abspath(os.getcwd())
        print(f"Module1: Текущая рабочая директория: {current_dir}")
        
        # Если путь уже установлен, проверяем его
        if hasattr(self, 'current_db_path') and self.current_db_path:
            if os.path.exists(self.current_db_path):
                print(f"Module1: Используем текущий файл БД: {self.current_db_path}")
                return self.current_db_path
            else:
                print(f"Module1: Файл {self.current_db_path} не найден")
        
        # Ищем все файлы БД в текущей директории
        db_files = [f for f in os.listdir(current_dir) if f.endswith('.db')]
        
        if not db_files:
            print(f"Module1: В директории {current_dir} не найдены файлы БД")
            self.status_msg.config(text="Файлы БД не найдены в рабочей директории", fg="red")
            return None
            
        # Берем первый найденный файл
        db_file = os.path.join(current_dir, db_files[0])
        print(f"Module1: Выбран файл БД: {db_file}")
        
        # Сохраняем абсолютный путь
        self.current_db_path = os.path.abspath(db_file)
        print(f"Module1: Установлен current_db_path (абсолютный): {self.current_db_path}")
        
        return self.current_db_path

# Save as test_syntax.py in the same folder
import sys
import os

def check_syntax(filename):
    """Check Python file for syntax errors"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, filename, 'exec')
        print(f"No syntax errors in {filename}")
    except SyntaxError as e:
        print(f"Syntax error in {filename} at line {e.lineno}, column {e.offset}")
        print(f"Details: {e.text}")
        print(f"Error message: {e}")

if __name__ == "__main__":
    check_syntax("module1.py")