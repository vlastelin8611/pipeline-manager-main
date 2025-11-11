import tkinter as tk
from tkinter import messagebox

class Module8(tk.Frame):
    def __init__(self, master, app=None, module7_ref=None, **kwargs):
        """Инициализация модуля 8.
        
        Args:
            master: Родительский виджет
            app: Ссылка на основное приложение
            module7_ref: Прямая ссылка на модуль 7 (альтернативный способ связи)
            **kwargs: Дополнительные аргументы
        """
        super().__init__(master)
        self.master = master
        self.app = app
        
        # Обработка ссылки на модуль 7 - можно передать напрямую или через app
        self.module7_ref = module7_ref
        
        # Если ссылка на модуль 7 не передана, но доступна через app
        if self.module7_ref is None and app is not None and hasattr(app, 'module7'):
            self.module7_ref = app.module7
            print("Module8: Получена ссылка на модуль 7 из app")
            
        print(f"Module8: Инициализация с module7_ref={self.module7_ref}")
            
        self.module3_ref = None  # Ссылка на модуль 3
        self.module9_ref = None  # Ссылка на модуль 9
        
        # Список доступных баз данных (для совместимости с новым кодом)
        self.databases_list = []
        
        # Индекс активной базы данных (начиная с 0)
        self.active_db = tk.IntVar(value=0)  # 0 означает, что база данных не выбрана
        self.prev_active_db = 0  # Для отслеживания изменений
        
        # Настройка интерфейса
        self.setup_ui()
        
        # Привязка к изменению активной БД
        self.active_db.trace_add("write", self.on_active_change)
        
        # Запускаем периодическое обновление
        self.after(1000, self.refresh)
        
        print("Module8: Инициализация завершена")
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Верхняя панель с заголовком и индикатором активной БД
        self.header_frame = tk.Frame(self, height=30)
        self.header_frame.pack(fill="x", pady=5)
        
        tk.Label(self.header_frame, text="Управление активной базой данных", 
               font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        self.active_label = tk.Label(self.header_frame, text="Активная БД: нет", fg="red")
        self.active_label.pack(side="right", padx=5)
        
        # Фрейм для размещения переключателей БД
        self.button_frame = tk.Frame(self, bg="white")
        self.button_frame.pack(expand=True, fill="both", pady=5)
        
        # Индикатор если нет доступных БД
        self.no_db_label = tk.Label(self, text="Нет доступных БД для выбора.\nДобавьте базы данных в модуле 7.",
                                  font=("Arial", 10), fg="gray")
        
        # Нижняя панель с информацией
        self.footer_frame = tk.Frame(self, height=25)
        self.footer_frame.pack(fill="x", side="bottom", pady=5)
        
        self.status_label = tk.Label(self.footer_frame, 
                                   text="Для выбора активной БД нажмите на соответствующую кнопку", 
                                   fg="gray")
        self.status_label.pack(side="left", padx=5)
        
        # Кнопка обновления
        self.refresh_button = tk.Button(self.footer_frame, text="Обновить", 
                                      command=self.refresh)
        self.refresh_button.pack(side="right", padx=5)
        
        # Начальное построение интерфейса
        self.build_ui()
        
    def build_ui(self):
        """Динамическое построение интерфейса на основе доступных БД."""
        # Очищаем фрейм переключателей
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        self.radio_buttons = []

        # Определяем, есть ли хотя бы одна подключённая БД в модуле 7
        connected_exists = False
        if self.module7_ref is not None and hasattr(self.module7_ref, 'squares'):
            connected_exists = any(getattr(square, "connected", False) for square in self.module7_ref.squares)

        if not connected_exists:
            # Если ни одна БД не подключена: скрываем переключатели и показываем надпись
            self.button_frame.pack_forget()
            self.no_db_label.pack(expand=True, fill="both", pady=20)
            self.active_db.set(0)
        else:
            # Если есть хотя бы одна подключённая БД – отображаем фрейм переключателей
            self.button_frame.pack(expand=True, fill="both", pady=5)
            self.no_db_label.pack_forget()
            
            # Определяем количество столбцов для размещения переключателей
            desired_size = 80
            available_width = self.button_frame.winfo_width()
            if available_width <= 0:
                available_width = self.winfo_width()
            num_cols = max(1, available_width // desired_size)

            # Создаем переключатели (радиокнопки) для каждой БД
            for i, square in enumerate(self.module7_ref.squares):
                state = tk.NORMAL if square.connected else tk.DISABLED
                rb = tk.Radiobutton(
                    self.button_frame,
                    text=f"БД {i+1}",
                    variable=self.active_db,
                    value=i+1,
                    state=state,
                    indicatoron=True,
                    bg="white",
                    font=("Arial", 9),
                    width=6,
                    height=3,
                    # Прямая команда при клике на радиокнопку
                    command=lambda idx=i+1: self.db_selected(idx)
                )
                self.radio_buttons.append(rb)
                row = i // num_cols
                col = i % num_cols
                rb.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            for col in range(num_cols):
                self.button_frame.grid_columnconfigure(col, weight=1)
            
            # Выбираем первую доступную БД, если ни одна не выбрана
            if self.active_db.get() == 0:
                self.select_first_available_db()

        self.update_active_label()
        
        # Обновляем список databases_list для совместимости с новым кодом
        self.update_databases_list()
    
    def update_databases_list(self):
        """Обновляет список баз данных для совместимости с новым кодом."""
        self.databases_list = []
        if self.module7_ref and hasattr(self.module7_ref, 'squares'):
            for square in self.module7_ref.squares:
                if square.connected:
                    self.databases_list.append({
                        'connection': square.connection,
                        'path': square.path,
                        'name': square.name
                    })
    
    def select_first_available_db(self):
        """Выбирает первую доступную БД"""
        if self.module7_ref and hasattr(self.module7_ref, 'squares'):
            for idx, square in enumerate(self.module7_ref.squares):
                if square.connected:
                    self.active_db.set(idx+1)
                    break
    
    def db_selected(self, db_index):
        """Вызывается при прямом выборе БД через радиокнопку"""
        if self.module7_ref and db_index > 0 and db_index <= len(self.module7_ref.squares):
            square = self.module7_ref.squares[db_index-1]
            if square.connected:
                # Проверяем, изменилась ли активная БД
                if db_index != self.prev_active_db:
                    # Сохраняем новое значение
                    old_active = self.prev_active_db
                    self.prev_active_db = db_index
                    
                    # Уведомляем о смене БД
                    self.notify_db_change()

    def update_active_label(self):
        """Обновляет текст с информацией об активной БД"""
        active = self.active_db.get()
        if active == 0:
            text = "Активная БД: нет"
            color = "red"
        else:
            text = f"Активная БД: БД {active}"
            color = "green"
        self.active_label.config(text=text, fg=color)

    def on_configure(self, event):
        """Вызывается при изменении размеров окна - перестраиваем интерфейс"""
        self.build_ui()

    def on_active_change(self, *args):
        """Вызывается при изменении переменной active_db"""
        active = self.active_db.get()
        
        if self.module7_ref and hasattr(self.module7_ref, 'squares'):
            squares = self.module7_ref.squares
            # Если ни одна БД не подключена, сбрасываем активное значение
            if not any(square.connected for square in squares):
                self.active_db.set(0)
                self.update_active_label()
                return
        
        # Уведомляем о смене БД
        self.notify_db_change()
        self.update_active_label()
    
    def notify_db_change(self):
        """Уведомляет все заинтересованные модули о смене активной БД"""
        # Получаем информацию об активной БД
        active_db_info = self.get_active_db()
        
        # Уведомление модуля 3
        if self.module3_ref:
            print("Module8: Уведомление модуля 3 о смене активной БД")
            self.module3_ref.on_db_changed()
        
        # Альтернативный способ уведомления модуля 3 через app
        if self.app and hasattr(self.app, 'module3') and self.app.module3:
            print("Module8: Уведомление модуля 3 о смене активной БД через app.module3")
            self.app.module3.on_db_changed()
        
        # Уведомляем модуль 4, если он есть и если active_db_info не None
        app = self.winfo_toplevel()
        if hasattr(app, 'module4') and app.module4 and active_db_info is not None:
            print(f"Module8: Уведомление модуля 4 о смене БД: {active_db_info.get('name', 'Неизвестно')}")
            app.module4.on_db_change(active_db_info)
        elif hasattr(app, 'module4') and app.module4:
            print("Module8: Не удалось уведомить модуль 4 - active_db_info is None")
        
        # Уведомляем основное приложение
        if hasattr(app, 'set_active_database') and active_db_info:
            db_name = active_db_info.get('name', f"БД #{self.active_db.get()}")
            app.set_active_database(db_name)

    def refresh(self):
        """Периодическое обновление состояния модуля"""
        try:
            if self.module7_ref and hasattr(self.module7_ref, 'squares'):
                squares = self.module7_ref.squares
                # Если ни одна БД не подключена, сбрасываем активное значение
                if not any(square.connected for square in squares):
                    self.active_db.set(0)
                
                # Проверяем, существует ли еще выбранная БД
                active = self.active_db.get()
                if active > 0 and active <= len(squares):
                    if not squares[active-1].connected:
                        # Если выбранная БД отключилась, выбираем другую
                        self.active_db.set(0)
                        self.select_first_available_db()
            
            # Обновляем интерфейс
            self.build_ui()
        except Exception as e:
            print(f"Module8: Ошибка обновления: {e}")
        finally:
            # Планируем следующее обновление
            self.after(1000, self.refresh)

    def set_active_database(self, db_number):
        """Устанавливает активную базу данных"""
        app = self.winfo_toplevel()
        if app:
            app.active_db = db_number
            print(f"Активная база данных установлена: {db_number}")

    def get_active_db(self):
        """Возвращает информацию об активной БД и её соединении"""
        try:
            if self.active_db.get() > 0 and self.active_db.get() <= len(self.databases_list):
                db_info = self.databases_list[self.active_db.get() - 1]
                return {
                    'name': db_info.get('name', 'Неизвестная БД'),
                    'path': db_info.get('path'),
                    'connection': db_info.get('connection')
                }
            return None
        except Exception as e:
            print(f"Module8: Ошибка при получении информации об активной БД: {e}")
            return None
            
    def get_connection(self):
        """Возвращает активное соединение с БД"""
        try:
            db_info = self.get_active_db()
            if db_info and db_info.get('connection'):
                return db_info.get('connection')
            return None
        except Exception as e:
            print(f"Module8: Ошибка при получении соединения с БД: {e}")
            return None

    def update_databases(self):
        """Обновляет список баз данных (для совместимости с новым кодом)"""
        # Фактически этот метод просто обновляет интерфейс
        self.build_ui()
        return True

    def on_db_selected(self, event):
        """Обрабатывает выбор базы данных из списка (для совместимости)"""
        # Этот метод нужен для совместимости, но в данном UI не используется
        pass

    def update_interface(self):
        """Обновляет интерфейс (для совместимости)"""
        self.update_active_label()
    
    def set_module3_ref(self, module3):
        """Устанавливает ссылку на модуль 3."""
        print(f"Module8: Установка ссылки на модуль 3: {module3}")
        self.module3_ref = module3

    def set_module9_ref(self, module9):
        """Устанавливает ссылку на модуль 9."""
        print(f"Module8: Установка ссылки на модуль 9: {module9}")
        self.module9_ref = module9
