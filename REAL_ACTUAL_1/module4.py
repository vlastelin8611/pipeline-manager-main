import tkinter as tk
import sqlite3
from tkinter import messagebox

class Module4(tk.Frame):
    def __init__(self, parent, main_app=None):
        """
        Модуль 4 – Авторизация пользователя.
        Проверяет логин и пароль в базе данных.
        
        :param parent: родительский виджет.
        :param main_app: ссылка на основное приложение для разблокировки модулей.
        """
        super().__init__(parent, bg="white")
        self.main_app = main_app  # ссылка на основное приложение
        self.db_connection = None
        self.authenticated = False
        
        # Сохраняем данные авторизованного пользователя
        self.current_login = ""
        self.current_password = ""
        self.current_user_info = {}
        
        # Создаем интерфейс
        self.build_ui()
        
        # Запускаем проверку подключения к БД
        self.check_db_connection()
    
    def build_ui(self):
        """Создает интерфейс модуля авторизации."""
        # Очищаем виджеты
        for widget in self.winfo_children():
            widget.destroy()
        
        # Если пользователь авторизован - показываем его данные
        if self.authenticated:
            self.show_user_info()
        else:
            # Иначе показываем форму авторизации
            self.show_login_form()
    
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
        active_db_name = "Нет активной БД"
        if self.db_connection:
            active_db_name = self.db_connection.get("Название БД", "Неизвестно")
        
        tk.Label(self.login_frame, text="Текущая БД:", bg="white").grid(row=2, column=0, sticky="w", pady=2)
        self.active_db_label = tk.Label(
            self.login_frame,
            text=active_db_name,
            bg="white",
            fg="blue"
        )
        self.active_db_label.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        # Настраиваем веса столбцов
        self.login_frame.grid_columnconfigure(1, weight=1)
        
        # Кнопка входа
        self.login_button = tk.Button(
            self,
            text="Войти",
            command=self.authenticate,
            state="disabled"  # Изначально кнопка отключена
        )
        self.login_button.pack(pady=10)
        
        # Метка статуса
        self.status_label = tk.Label(
            self,
            text="Подключите базу данных для авторизации",
            fg="red",
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
        
        # Блокируем модули 1, 2, 3, 5, 6 после выхода
        if self.main_app:
            self.main_app.lock_modules()
        
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
        # Получаем активную БД из модуля 8
        active_db = self.get_active_db_connection()
        
        # Если активная БД изменилась и пользователь уже авторизован,
        # спрашиваем о перелогинивании
        if active_db and self.db_connection and active_db != self.db_connection and self.authenticated:
            # В этом случае обработкой займется метод on_db_change, вызываемый из модуля 8
            pass
        elif active_db and not self.authenticated:
            # Есть активная БД и пользователь не авторизован
            self.db_connection = active_db
            if hasattr(self, 'active_db_label'):
                self.active_db_label.config(text=active_db.get("Название БД", "Неизвестно"))
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Введите логин и пароль")
            if hasattr(self, 'login_button'):
                self.login_button.config(state="normal")
        elif not active_db and not self.authenticated:
            # Нет активной БД и пользователь не авторизован
            self.db_connection = None
            if hasattr(self, 'active_db_label'):
                self.active_db_label.config(text="Нет активной БД")
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
        
        if not self.db_connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return False
        
        try:
            # Получаем путь к БД из информации о подключении
            db_path = self.db_connection.get("Путь БД", "")
            
            # Подключаемся к БД
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Проверяем существование таблицы operators
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operators'")
            if not cursor.fetchone():
                messagebox.showerror("Ошибка", "В базе данных нет таблицы operators")
                conn.close()
                return False
            
            # Проверяем логин и пароль
            cursor.execute("SELECT id, fio, login, password, high_priority FROM operators WHERE login=? AND password=?", 
                           (login, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # Успешная авторизация
                self.authenticated = True
                self.current_login = login
                self.current_password = password
                
                # Сохраняем информацию о пользователе
                self.current_user_info = {
                    "id": user[0],
                    "fio": user[1],
                    "login": user[2],
                    "password": user[3],
                    "high_priority": user[4]
                }
                
                messagebox.showinfo("Успех", "Авторизация успешна")
                
                # Обновляем интерфейс
                self.build_ui()
                
                # Разблокируем все модули
                if self.main_app:
                    self.main_app.unlock_modules()
                
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