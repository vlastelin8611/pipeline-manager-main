import tkinter as tk  # импортирую модуль tkinter для создания графического интерфейса, сокращаю название до tk
from tkinter import messagebox  # импортирую messagebox для показа всплывающих сообщений пользователю
import sqlite3  # импортирую модуль sqlite3 для работы с базой данных SQLite
import os  # импортирую модуль os для работы с файлами и папками

class DBConnectionSquare(tk.Frame):  # создаю класс DBConnectionSquare, который наследуется от tk.Frame (контейнер для виджетов)
    def __init__(self, parent, index, *args, **kwargs):  # конструктор класса, принимает родительский виджет, номер квадрата и дополнительные параметры
        """
        Квадрат для отображения информации об одном подключении к БД.
        :param parent: родительский виджет.
        :param index: номер квадрата (от 1 до 6).
        """  # многострочный комментарий, объясняющий назначение класса и его параметры
        super().__init__(parent, *args, **kwargs)  # вызываю конструктор родительского класса
        self.index = index  # сохраняю номер квадрата (от 1 до 6)
        self.connected = False  # флаг подключения к БД (изначально False - не подключен)
        self.connection_info = None  # переменная для хранения информации о подключении (пока не задана)
        self.connection = None  # Добавляем атрибут для совместимости с новой логикой  # переменная для хранения объекта соединения с БД
        self.path = None  # Добавляем атрибут для совместимости с новой логикой  # переменная для хранения пути к файлу БД
        self.name = f"БД {index}"  # Добавляем атрибут для совместимости с новой логикой  # создаю название БД используя номер квадрата
        self.configure(borderwidth=1, relief="solid", bg="white")  # настраиваю внешний вид квадрата: рамка 1 пиксель, сплошная линия, белый фон
        self.create_initial_ui()  # вызываю метод для создания начального интерфейса

    def create_initial_ui(self):  # определяю метод для создания начального состояния интерфейса
        """Изначальное состояние: вывод надписи, что БД не подключена."""  # описание что делает этот метод
        for widget in self.winfo_children():  # прохожусь по всем дочерним виджетам в квадрате
            widget.destroy()  # удаляю каждый виджет
        self.title_label = tk.Label(  # создаю метку с заголовком
            self,
            text=f"БД {self.index}: Не подключена",  # текст показывающий номер БД и статус "Не подключена"
            font=("Arial", 8, "bold"),  # шрифт Arial, размер 8, жирный
            bg="white"  # белый фон
        )
        self.title_label.pack(side="top", fill="x", pady=2)  # размещаю метку вверху, растягивая по горизонтали с вертикальным отступом 2 пикселя
        self.connected = False  # устанавливаю флаг подключения в False (не подключен)
        self.connection_info = None  # сбрасываю информацию о подключении
        self.connection = None  # Сбрасываем соединение  # сбрасываю объект соединения
        self.path = None  # Сбрасываем путь  # сбрасываю путь к файлу БД
        self.name = f"БД {self.index}"  # Устанавливаем имя по умолчанию  # восстанавливаю название по умолчанию

    def set_connection(self, connection_info):
        """
        Обновляет квадрат, заполняя его данными о подключении.
        :param connection_info: словарь с ключами:
            "Название БД", "Путь БД", "Тип БД", "Статус", "Пинг"
        """
        self.connected = True
        self.connection_info = connection_info
        
        # Обновляем атрибуты для совместимости с новой логикой
        self.name = connection_info.get("Название БД", f"БД {self.index}")
        self.path = connection_info.get("Путь БД")
        
        # Если есть соединение в информации, сохраняем его
        if "connection" in connection_info:
            self.connection = connection_info["connection"]
            
        for widget in self.winfo_children():
            widget.destroy()

        # Заголовок с номером квадрата
        self.title_label = tk.Label(
            self,
            text=f"БД {self.index}",
            font=("Arial", 8, "bold"),
            bg="white"
        )
        self.title_label.pack(side="top", fill="x", pady=2)

        # Фрейм для отображения деталей подключения
        details_frame = tk.Frame(self, bg="white")
        details_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Перечисляем нужные поля
        fields = ["Название БД", "Путь БД", "Тип БД", "Статус", "Пинг"]
        for field in fields:
            row = tk.Frame(details_frame, bg="white")
            row.pack(fill="x", pady=1)
            lbl = tk.Label(
                row,
                text=f"{field}:",
                font=("Arial", 7),
                bg="white",
                anchor="w",
                width=12
            )
            lbl.pack(side="left")
            # Используем Entry с состоянием readonly для возможности копирования текста
            entry_var = tk.StringVar(value=connection_info.get(field, ""))
            entry = tk.Entry(row, textvariable=entry_var, font=("Arial", 7), state="readonly")
            entry.configure(readonlybackground="white")
            entry.pack(side="left", fill="x", expand=True)

        # Кнопка для отключения
        self.disconnect_button = tk.Button(
            self,
            text="Отключ.",
            font=("Arial", 7),
            command=self.confirm_disconnect
        )
        self.disconnect_button.pack(side="bottom", fill="x", padx=2, pady=2)

    def confirm_disconnect(self):
        """Отображает модальное окно с подтверждением отключения."""
        confirm_window = tk.Toplevel(self)
        confirm_window.title("Подтверждение отключения")
        confirm_window.grab_set()  # Делаем окно модальным
        lbl = tk.Label(confirm_window, text="Вы действительно хотите отключиться?", font=("Arial", 8))
        lbl.pack(padx=10, pady=10)
        btn_frame = tk.Frame(confirm_window)
        btn_frame.pack(pady=5)
        btn_disconnect = tk.Button(
            btn_frame,
            text="Отключ.",
            font=("Arial", 8),
            command=lambda: self.disconnect(confirm_window)
        )
        btn_cancel = tk.Button(
            btn_frame,
            text="Отмена",
            font=("Arial", 8),
            command=confirm_window.destroy
        )
        btn_disconnect.pack(side="left", padx=5)
        btn_cancel.pack(side="left", padx=5)

    def disconnect(self, confirm_window):
        """Отключает текущее подключение и возвращает квадрат в исходное состояние."""
        confirm_window.destroy()
        
        # Закрываем соединение с БД
        if self.connection:
            try:
                self.connection.close()
                print(f"DBConnectionSquare: Закрыто соединение с БД {self.name}")
            except Exception as e:
                print(f"DBConnectionSquare: Ошибка при закрытии соединения: {e}")
                
        self.create_initial_ui()


class Module7(tk.Frame):
    def __init__(self, master, app=None):
        """Инициализация модуля 7."""
        super().__init__(master)
        self.master = master
        self.app = app
        self.module8_ref = None  # Ссылка на модуль 8
        
        # Список объектов для отображения подключений БД (квадраты)
        self.squares = []
        
        # Путь к директории с базами данных (сохраняем для совместимости с новой логикой)
        self.db_directory = tk.StringVar(value="./databases")
        
        # Настройка интерфейса
        self.setup_ui()
        
        print("Module7: Инициализация завершена")
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Верхняя панель с заголовком
        self.header_frame = tk.Frame(self)
        self.header_frame.pack(fill="x")
        
        tk.Label(self.header_frame, text="Мониторинг подключенных баз данных",
                font=("Arial", 10, "bold")).pack(side="left", padx=5, pady=5)
        
        # Кнопка подключения новой БД
        self.add_button = tk.Button(self.header_frame, text="+ Добавить БД", command=self.open_add_dialog)
        self.add_button.pack(side="right", padx=5, pady=5)
        
        # Фрейм для размещения квадратов
        self.squares_frame = tk.Frame(self)
        self.squares_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Настраиваем сетку для размещения квадратов 3x2
        for i in range(3):
            self.squares_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.squares_frame.grid_rowconfigure(i, weight=1)
        
        # Создаем 6 квадратов для размещения информации о подключениях
        for i in range(6):
            row = i // 3
            col = i % 3
            square = DBConnectionSquare(self.squares_frame, i+1)
            square.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.squares.append(square)
            
    def open_add_dialog(self):
        """Открывает диалог для добавления нового подключения."""
        # Если уже 6 подключений, выводим сообщение
        if all(square.connected for square in self.squares):
            messagebox.showwarning("Максимум подключений", 
                                "Достигнуто максимальное количество подключений (6).\n"
                                "Отключите одно из существующих для добавления нового.")
            return
        
        # Обходим модули и ищем модуль 9 (подключения)
        app = self.winfo_toplevel()
        if hasattr(app, 'module9') and app.module9:
            module9 = app.module9
            # Если у модуля 9 есть метод show_connection_options, вызываем его
            if hasattr(module9, 'show_connection_options'):
                module9.show_connection_options()
            else:
                messagebox.showinfo("Информация", 
                                  "Модуль подключения (9) не найден или не имеет необходимых методов.")
        else:
            messagebox.showinfo("Информация", 
                              "Модуль подключения (9) не найден. Используйте его для добавления новой БД.")
        
    def add_connection(self, connection_info):
        """
        Добавляет информацию о подключении в первый свободный квадрат.
        Если все квадраты заняты, отображается сообщение об ошибке.
        :param connection_info: словарь с данными подключения.
        :return: True, если подключение добавлено, иначе False.
        """
        for square in self.squares:
            if not square.connected:
                square.set_connection(connection_info)
                # Уведомляем модуль 8 об изменении списка баз данных
                if self.module8_ref:
                    self.module8_ref.refresh()
                return True
        messagebox.showerror(
            "Ошибка",
            "Подключено максимальное количество БД, новое подключение невозможно."
        )
        return False

    def select_directory(self):
        """Открывает диалог выбора директории с базами данных."""
        from tkinter import filedialog
        dir_path = filedialog.askdirectory(title="Выберите директорию с базами данных")
        if dir_path:
            self.db_directory.set(dir_path)
            print(f"Module7: Выбрана директория: {dir_path}")
            
    def scan_databases(self):
        """Сканирует директорию на наличие баз данных и подключается к ним."""
        # Очищаем текущие подключения
        self.close_all_connections()
        
        db_dir = self.db_directory.get() if hasattr(self.db_directory, 'get') else self.db_directory
        print(f"Module7: Сканирование директории: {db_dir}")
        
        if not db_dir or not os.path.exists(db_dir):
            print(f"Module7: Директория {db_dir} не существует")
            return
            
        # Ищем файлы .db и .sqlite
        db_files = []
        for file in os.listdir(db_dir):
            if file.endswith(('.db', '.sqlite')):
                db_path = os.path.join(db_dir, file)
                db_files.append(db_path)
                
        print(f"Module7: Найдено баз данных: {len(db_files)}")
        
        # Подключаемся к каждой базе данных
        for i, db_path in enumerate(db_files):
            if i >= 6:  # Максимум 6 подключений
                break
                
            try:
                # Создаем соединение
                connection = sqlite3.connect(db_path, isolation_level=None)
                
                # Получаем имя файла из пути
                db_name = os.path.basename(db_path)
                
                # Создаем информацию о подключении
                connection_info = {
                    "Название БД": db_name,
                    "Путь БД": db_path,
                    "Тип БД": "SQLite",
                    "Статус": "Подключена",
                    "Пинг": "-",
                    "connection": connection  # Добавляем соединение в информацию
                }
                
                # Обновляем соответствующий квадрат
                self.squares[i].set_connection(connection_info)
                print(f"Module7: Подключено к БД {db_name}")
                
            except Exception as e:
                print(f"Module7: Ошибка подключения к БД {db_path}: {e}")
            
        # Уведомляем модуль 8 об изменении списка баз данных
        if self.module8_ref:
            self.module8_ref.refresh()
            
    def close_all_connections(self):
        """Закрывает все открытые соединения с базами данных."""
        for square in self.squares:
            if square.connected:
                square.disconnect(None)  # None вместо окна подтверждения
                
    def set_module8_ref(self, module8):
        """Устанавливает ссылку на модуль 8."""
        print(f"Module7: Установка ссылки на модуль 8: {module8}")
        self.module8_ref = module8
