import tkinter as tk  # импортирую модуль tkinter для создания графического интерфейса, сокращаю название до tk
import sqlite3  # импортирую модуль sqlite3 для работы с базой данных SQLite
from tkinter import messagebox  # импортирую messagebox для показа всплывающих сообщений пользователю

class Module4(tk.Frame):  # создаю класс Module4, который наследуется от tk.Frame (контейнер для виджетов)
    def __init__(self, parent, main_app=None):  # конструктор класса, принимает родительский виджет и ссылку на главное приложение
        """
        Модуль 4 – Авторизация пользователя.
        Проверяет логин и пароль в базе данных.
        
        :param parent: родительский виджет.
        :param main_app: ссылка на основное приложение для разблокировки модулей.
        """  # многострочный комментарий, объясняющий назначение класса и его параметры
        super().__init__(parent, bg="white")  # вызываю конструктор родительского класса с белым фоном
        self.main_app = main_app  # ссылка на основное приложение  # сохраняю ссылку на главное приложение для взаимодействия с ним
        self.db_connection = None  # переменная для хранения соединения с базой данных (пока не установлено)
        self.authenticated = False  # флаг авторизации пользователя (изначально False - не авторизован)
        
        # Сохраняем данные авторизованного пользователя
        self.current_login = ""  # строка для хранения логина текущего пользователя (пока пустая)
        self.current_password = ""  # строка для хранения пароля текущего пользователя (пока пустая)
        self.current_user_info = {}  # словарь для хранения дополнительной информации о пользователе (пока пустой)
        
        # Создаем интерфейс
        self.build_ui()  # вызываю метод для построения пользовательского интерфейса
        
        # НЕ запускаем автоматическую проверку подключения к БД
        # Модуль будет активироваться только при подключении через модуль 9
    
    def build_ui(self):  # определяю метод для создания пользовательского интерфейса
        """Создает интерфейс модуля авторизации."""  # описание что делает этот метод
        # Очищаем виджеты
        for widget in self.winfo_children():  # прохожусь по всем дочерним виджетам в текущем контейнере
            widget.destroy()  # удаляю каждый виджет
        
        # Если пользователь авторизован - показываем его данные
        if self.authenticated:  # если пользователь успешно прошел авторизацию
            self.show_user_info()  # показываю информацию о пользователе
        else:  # иначе (если пользователь не авторизован)
            # Иначе показываем форму авторизации
            self.show_login_form()  # показываю форму для ввода логина и пароля
    
    def show_login_form(self):
        """Показывает форму для ввода логина и пароля"""
        # Заголовок
        self.title_label = tk.Label(
            self,
            text="Авторизация пользователя",
            font=("Arial", 10, "bold"),
            bg="white"
        )
        self.title_label.pack(pady=(5, 10))
        
        # Фрейм для полей ввода
        self.login_frame = tk.Frame(self, bg="white")
        self.login_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле для логина
        tk.Label(self.login_frame, text="Логин:", bg="white").grid(row=0, column=0, sticky="w", pady=2)
        self.login_entry = tk.Entry(self.login_frame)
        self.login_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Поле для пароля
        tk.Label(self.login_frame, text="Пароль:", bg="white").grid(row=1, column=0, sticky="w", pady=2)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Добавляем информацию об активной БД
        # По умолчанию показываем, что нет активной БД
        active_db_name = "Нет активной БД"
        
        # Проверяем подключение к БД через главное приложение
        if self.main_app and self.main_app.get_db_connection():
            db_path = self.main_app.get_active_database_path()
            if db_path:
                import os
                active_db_name = os.path.basename(db_path)
        
        tk.Label(self.login_frame, text="Текущая БД:", bg="white").grid(row=2, column=0, sticky="w", pady=2)
        self.active_db_label = tk.Label(
            self.login_frame,
            text=active_db_name,
            bg="white",
            fg="blue" if active_db_name != "Нет активной БД" else "red"
        )
        self.active_db_label.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        # Настраиваем веса столбцов
        self.login_frame.grid_columnconfigure(1, weight=1)
        
        # Кнопка входа
        has_db = self.main_app and self.main_app.get_db_connection()
        self.login_button = tk.Button(
            self,
            text="Войти",
            command=self.authenticate,
            state="normal" if has_db else "disabled"
        )
        self.login_button.pack(pady=10)
        
        # Метка статуса
        status_text = "Введите логин и пароль" if has_db else "Подключите базу данных для авторизации"
        status_color = "black" if has_db else "red"
        
        self.status_label = tk.Label(
            self,
            text=status_text,
            fg=status_color,
            bg="white",
            wraplength=150
        )
        self.status_label.pack(pady=5)
    
    def show_user_info(self):
        """Отображает информацию об авторизованном пользователе"""
        # Заголовок
        self.title_label = tk.Label(
            self,
            text="Информация о пользователе",
            font=("Arial", 10, "bold"),
            bg="white"
        )
        self.title_label.pack(pady=(5, 10))
        
        # Создаем фрейм для информации
        info_frame = tk.Frame(self, bg="white")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Отображаем ФИО пользователя, если оно есть
        if "fio" in self.current_user_info and self.current_user_info["fio"]:
            fio_label = tk.Label(
                info_frame,
                text=f"ФИО: {self.current_user_info['fio']}",
                bg="white",
                anchor="w",
                font=("Arial", 9)
            )
            fio_label.pack(fill="x", pady=2)
        
        # Отображаем логин
        login_label = tk.Label(
            info_frame,
            text=f"Логин: {self.current_login}",
            bg="white",
            anchor="w",
            font=("Arial", 9)
        )
        login_label.pack(fill="x", pady=2)
        
        # Отображаем уровень доступа
        high_priority = self.current_user_info.get("high_priority", 0)
        access_level = "Продвинутый" if high_priority == 1 else "Базовый"
        access_label = tk.Label(
            info_frame,
            text=f"Уровень доступа: {access_level}",
            bg="white",
            anchor="w",
            font=("Arial", 9)
        )
        access_label.pack(fill="x", pady=2)
        
        # Отображаем метку о БД
        if self.db_connection:
            db_name = self.db_connection.get("Название БД", "Неизвестно")
            db_label = tk.Label(
                info_frame,
                text=f"База данных: {db_name}",
                bg="white",
                anchor="w",
                font=("Arial", 9)
            )
            db_label.pack(fill="x", pady=2)
        
        # Кнопка выхода
        logout_button = tk.Button(
            self,
            text="Выйти",
            command=self.logout
        )
        logout_button.pack(pady=10)
        
        # Статус авторизации
        status_label = tk.Label(
            self,
            text="Авторизован",
            fg="green",
            bg="white"
        )
        status_label.pack(pady=5)
    
    def logout(self):
        """Выход из системы"""
        self.authenticated = False
        self.current_login = ""
        self.current_password = ""
        self.current_user_info = {}
        
        # Выход из системы через главное приложение
        if self.main_app:
            self.main_app.logout_user()
        
        # Обновляем интерфейс
        self.build_ui()
    
    def get_active_db_connection(self):
        """Получает информацию об активной БД из модуля 8"""
        if not hasattr(self.main_app, 'module7') or not self.main_app.module7:
            return None
        
        # Получаем ссылку на модуль 8
        module8 = None
        for row in self.main_app.tiles:
            for tile in row:
                if tile.module_id == 8:
                    # Находим модуль 8 в дочерних виджетах содержимого плитки
                    for child in tile.content_frame.winfo_children():
                        if isinstance(child, tk.Frame) and hasattr(child, 'module7_ref'):
                            module8 = child
                            break
                    if module8:
                        break
            if module8:
                break
        
        if not module8:
            # Если не нашли модуль 8, возвращаем первую подключенную БД
            for square in self.main_app.module7.squares:
                if square.connected:
                    return square.connection_info
            return None
        
        # Получаем активную БД из модуля 8
        active_db_idx = module8.active_db.get()
        if active_db_idx > 0 and active_db_idx <= len(module8.module7_ref.squares):
            square = module8.module7_ref.squares[active_db_idx-1]
            if square.connected:
                return square.connection_info
        
        # Если активная БД не выбрана, возвращаем первую подключенную БД
        for square in self.main_app.module7.squares:
            if square.connected:
                return square.connection_info
        
        return None
    
    def check_db_connection(self):
        """Проверяет наличие активной БД и обновляет интерфейс."""
        # Проверяем подключение к БД через главное приложение
        has_db_connection = False
        db_name = "Нет активной БД"
        
        if self.main_app:
            db_connection = self.main_app.get_db_connection()
            if db_connection:
                has_db_connection = True
                db_path = self.main_app.get_active_database_path()
                if db_path:
                    import os
                    db_name = os.path.basename(db_path)
        
        # Обновляем интерфейс в зависимости от состояния БД
        if has_db_connection and not self.authenticated:
            # Есть активная БД и пользователь не авторизован
            if hasattr(self, 'active_db_label'):
                self.active_db_label.config(text=db_name)
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Введите логин и пароль", fg="black")
            if hasattr(self, 'login_button'):
                self.login_button.config(state="normal")
        elif not has_db_connection and not self.authenticated:
            # Нет активной БД и пользователь не авторизован
            if hasattr(self, 'active_db_label'):
                self.active_db_label.config(text=db_name)
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Подключите базу данных для авторизации", fg="red")
            if hasattr(self, 'login_button'):
                self.login_button.config(state="disabled")
        
        # Повторно запланировать проверку через 1 секунду
        self.after(1000, self.check_db_connection)
    
    def authenticate(self, login=None, password=None):
        """
        Проверяет логин и пароль по базе данных.
        
        :param login: Логин (если None, берется из поля ввода)
        :param password: Пароль (если None, берется из поля ввода)
        :return: True, если авторизация успешна, иначе False
        """
        # Если логин и пароль не переданы, берем из полей ввода
        if login is None:
            login = self.login_entry.get().strip()
        
        if password is None:
            password = self.password_entry.get().strip()
        
        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return False
        
        # Получаем подключение к БД из главного приложения
        if not self.main_app or not self.main_app.get_db_connection():
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return False
        
        try:
            # Используем централизованное подключение к БД
            result = self.main_app.authenticate_user(login, password)
            
            if result:
                # Успешная авторизация
                self.authenticated = True
                self.current_login = login
                self.current_password = password
                
                # Получаем информацию о пользователе из главного приложения
                user_info = self.main_app.get_authenticated_user()
                if user_info:
                    self.current_user_info = {
                        "id": user_info.get('id', ''),
                        "fio": user_info.get('name', ''),
                        "login": user_info.get('login', ''),
                        "password": password,
                        "high_priority": 0  # По умолчанию базовый уровень
                    }
                
                messagebox.showinfo("Успех", "Авторизация успешна")
                
                # Обновляем интерфейс
                self.build_ui()
                
                return True
            else:
                # Неудачная авторизация
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="Неверный логин или пароль", fg="red")
                return False
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при проверке данных: {str(e)}")
            return False
    
    def on_db_change(self, new_db_info):
        """
        Вызывается при изменении активной БД в модуле 8.
        
        :param new_db_info: Информация о новой активной БД
        """
        # Для отладки - выводим сообщение в консоль
        print(f"Модуль 4: Получено уведомление о смене БД на {new_db_info.get('Название БД', 'Неизвестно')}")
        
        # При любой смене БД пользователь должен перелогиниться
        # Это обеспечивает безопасность системы
        
        if self.authenticated:
            # Если пользователь был авторизован - разлогиниваем его
            print("Модуль 4: Смена БД - требуется повторная авторизация")
            messagebox.showinfo(
                "Смена БД", 
                f"Подключена новая база данных '{new_db_info.get('Название БД', 'Неизвестно')}'\n"
                "Необходимо войти в систему заново."
            )
            self.logout()
        
        # Обновляем ссылку на новую БД
        self.db_connection = new_db_info
        
        # Обновляем интерфейс для новой БД
        if hasattr(self, 'active_db_label'):
            self.active_db_label.config(text=new_db_info.get("Название БД", "Неизвестно"))
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Введите логин и пароль для новой БД", fg="blue")
        
        if hasattr(self, 'login_button'):
            self.login_button.config(state="normal")

    def on_database_changed(self, db_name):
        """
        Альтернативное название метода для совместимости с рефакторнутой версией.
        
        :param db_name: Название новой БД
        """
        print(f"Модуль 4: Получено уведомление о смене БД на {db_name}")
        
        # Обновляем интерфейс при смене БД
        if hasattr(self, 'active_db_label') and self.active_db_label:
            self.active_db_label.config(text=db_name, fg="blue")
        
        if hasattr(self, 'status_label') and self.status_label:
            if self.authenticated:
                # Если пользователь был авторизован - требуется повторная авторизация
                self.logout()
                self.status_label.config(text="Смена БД - войдите заново", fg="orange")
            else:
                self.status_label.config(text="Введите логин и пароль", fg="black")
        
        if hasattr(self, 'login_button') and self.login_button:
            self.login_button.config(state="normal") 