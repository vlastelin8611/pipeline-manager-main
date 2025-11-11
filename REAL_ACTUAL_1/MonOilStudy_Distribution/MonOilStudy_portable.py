import tkinter as tk  # импорт tkinter для работы с графическим интерфейсом
import os
import sqlite3
from module1 import Module1  # Импортируем модуль 1
from tkinter import messagebox
from module3 import Module3


import sys

def get_application_path():
    """Получает путь к директории приложения (exe или скрипт)"""
    if getattr(sys, 'frozen', False):
        # Если запущено как exe
        application_path = os.path.dirname(sys.executable)
    else:
        # Если запущено как скрипт
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path

class ModuleTile(tk.Frame):  # класс moduletile, наследуется от tk.frame
    def __init__(self, parent, module_id, *args, **kwargs):  # инициализатор, принимает родителя, номер модуля и доп. параметры
        super().__init__(parent, *args, **kwargs)  # вызываем конструктор родительского класса
        self.module_id = module_id  # сохраняем номер модуля в атрибуте
        self.configure(borderwidth=2, relief="solid", bg="white")  # задаем рамку 2px, сплошной стиль и белый фон
        
        # Минимальный размер для лучшей видимости контента
        self.config(width=350, height=220)
        # Позволяем модулю расширяться при увеличении окна
        self.pack_propagate(True)
        
        # Устанавливаем минимальные размеры, но позволяем расширение
        self.grid_propagate(True)
        
        # Получаем ссылку на основное приложение
        app = self.master.master
        
        # Переменная для хранения состояния блокировки
        # Блокируем все модули кроме 4, 7, 8, 9
        # Но если БД уже подключена, разблокируем все модули
        if hasattr(app, 'db_connected') and app.db_connected:
            self.locked = False
        else:
            self.locked = module_id not in [4, 7, 8, 9]

        # установка заголовка модуля, расположенного сверху
        if self.module_id == 7:  # если модуль 7
            title_text = "мониторинг состояния бд"  # название модуля 7
        elif self.module_id == 9:  # если модуль 9
            title_text = "модуль подключения к бд"  # название модуля 9
        elif self.module_id == 4:  # если модуль 4
            title_text = "авторизация пользователя"  # название модуля 4
        else:  # для остальных модулей
            title_text = f"модуль {module_id}"  # название будет 'модуль' и номер

        self.title_label = tk.Label(self, text=title_text, anchor='w',
                                    font=("Arial", 10, "bold"), bg="white")  # создаем метку с заголовком
        self.title_label.pack(side="top", fill="x", padx=2, pady=2)  # размещаем метку сверху, растягивая по горизонтали

        # создаем контейнер для будущего содержимого модуля с поддержкой прокрутки
        self.scroll_container = tk.Frame(self, bg="white")
        self.scroll_container.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        
        # Создаем canvas для прокрутки
        self.canvas = tk.Canvas(self.scroll_container, bg="white", highlightthickness=0)
        
        # Создаем scrollbar для вертикальной прокрутки
        self.v_scrollbar = tk.Scrollbar(self.scroll_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
        
        # Создаем scrollbar для горизонтальной прокрутки
        self.h_scrollbar = tk.Scrollbar(self.scroll_container, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set)
        
        # Размещаем canvas и scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Настраиваем grid веса
        self.scroll_container.grid_rowconfigure(0, weight=1)
        self.scroll_container.grid_columnconfigure(0, weight=1)
        
        # Создаем фрейм внутри canvas для содержимого модуля
        self.content_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Привязываем события для обновления размеров прокрутки
        self.content_frame.bind('<Configure>', self.update_scroll_region)
        self.canvas.bind('<Configure>', self.configure_scroll_region)
        
        # Привязываем прокрутку колесом мыши
        self.bind_mousewheel()

        # Обновляем состояние блокировки
        self.update_lock_state()

        # Вместо немедленной инициализации используем отложенную
        # Сохраняем ссылку на модуль для последующей инициализации
        self.module_obj = None
        self._scroll_update_pending = False  # флаг для предотвращения множественных обновлений
    
    def update_scroll_region(self, event=None):
        """Обновляет область прокрутки при изменении размера содержимого"""
        # Предотвращаем множественные обновления
        if self._scroll_update_pending:
            return
        self._scroll_update_pending = True
        
        # Добавляем небольшую задержку для группировки обновлений
        if hasattr(self, '_scroll_update_timer'):
            self.after_cancel(self._scroll_update_timer)
        
        self._scroll_update_timer = self.after(50, self._update_scroll_region)
        
    def _update_scroll_region(self):
        """Внутренний метод для обновления области прокрутки"""
        try:
            # Обновляем геометрию content_frame
            self.content_frame.update_idletasks()
            
            # Получаем размеры содержимого
            bbox = self.canvas.bbox("all")
            if bbox:
                # Убеждаемся, что bbox корректный
                x1, y1, x2, y2 = bbox
                if x2 > x1 and y2 > y1:
                    self.canvas.configure(scrollregion=bbox)
                else:
                    # Fallback к размерам content_frame
                    width = self.content_frame.winfo_reqwidth()
                    height = self.content_frame.winfo_reqheight()
                    if width > 0 and height > 0:
                        self.canvas.configure(scrollregion=(0, 0, width, height))
            else:
                # Если bbox пустой, используем размеры content_frame
                width = self.content_frame.winfo_reqwidth()
                height = self.content_frame.winfo_reqheight()
                if width > 0 and height > 0:
                    self.canvas.configure(scrollregion=(0, 0, width, height))
        except Exception as e:
            # Логируем ошибки для отладки
            if hasattr(self, 'module_id'):
                print(f"ModuleTile {self.module_id}: Ошибка обновления scrollregion: {e}")
            pass
        finally:
            # Сбрасываем флаг обновления
            self._scroll_update_pending = False
        
    def configure_scroll_region(self, event):
        """Настраивает размер content_frame при изменении размера canvas"""
        canvas_width = event.width
        canvas_height = event.height
        
        # Устанавливаем ширину content_frame равной ширине canvas
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        # Обновляем область прокрутки
        self.update_scroll_region()
    
    def bind_mousewheel(self):
        """Привязывает прокрутку колесом мыши"""
        import sys
        
        def on_mousewheel(event):
            # Проверяем, что canvas имеет прокрутку по вертикали
            if self.canvas.cget("yscrollcommand"):
                # Разные платформы имеют разные значения delta
                if sys.platform == "win32":
                    delta = int(-1 * (event.delta / 120))
                elif sys.platform == "darwin":  # macOS
                    delta = int(-1 * event.delta)
                else:  # Linux
                    delta = -1 if event.num == 4 else 1
                self.canvas.yview_scroll(delta, "units")
        
        def on_shift_mousewheel(event):
            # Проверяем, что canvas имеет прокрутку по горизонтали
            if self.canvas.cget("xscrollcommand"):
                if sys.platform == "win32":
                    delta = int(-1 * (event.delta / 120))
                elif sys.platform == "darwin":  # macOS
                    delta = int(-1 * event.delta)
                else:  # Linux
                    delta = -1 if event.num == 4 else 1
                self.canvas.xview_scroll(delta, "units")
        
        def bind_wheel_to_widget(widget):
            """Рекурсивно привязывает прокрутку ко всем дочерним виджетам"""
            try:
                # Windows и macOS
                widget.bind("<MouseWheel>", on_mousewheel)
                widget.bind("<Shift-MouseWheel>", on_shift_mousewheel)
                
                # Linux
                widget.bind("<Button-4>", on_mousewheel)
                widget.bind("<Button-5>", on_mousewheel)
                widget.bind("<Shift-Button-4>", on_shift_mousewheel)
                widget.bind("<Shift-Button-5>", on_shift_mousewheel)
                
                # Фокус для активации прокрутки
                widget.bind("<Enter>", lambda e: widget.focus_set())
                
                # Рекурсивно привязываем к дочерним виджетам
                for child in widget.winfo_children():
                    bind_wheel_to_widget(child)
            except:
                pass  # Игнорируем ошибки привязки
        
        # Привязываем к canvas
        bind_wheel_to_widget(self.canvas)
        
        # Привязываем к самому модулю
        bind_wheel_to_widget(self)
        
        # Обновляем привязки при добавлении новых виджетов
        self.after(100, lambda: bind_wheel_to_widget(self.content_frame))
        
        # Дополнительное обновление привязок через некоторое время
        self.after(500, lambda: bind_wheel_to_widget(self))
    
    def force_scroll_update(self):
        """Принудительно обновляет скроллы - вызывается после инициализации модуля"""
        # Сбрасываем флаг чтобы разрешить обновление
        self._scroll_update_pending = False
        self.update_scroll_region()
        # Только одно дополнительное обновление с большей задержкой
        self.after(200, lambda: (setattr(self, '_scroll_update_pending', False), self.update_scroll_region()))
            
    def set_locked(self, locked):
        """Изменяет состояние блокировки модуля"""
        self.locked = locked
        self.update_lock_state()
        
    def update_lock_state(self):
        """Обновляет внешний вид модуля в зависимости от состояния блокировки"""
        if self.locked:
            # Блокированное состояние - полупрозрачный модуль с оверлеем
            self.configure(bg="#f0f0f0")  # Более светлый фон
            self.title_label.configure(bg="#f0f0f0")
            if hasattr(self, 'scroll_container'):
                self.scroll_container.configure(bg="#f0f0f0")
                self.canvas.configure(bg="#f0f0f0")
            self.content_frame.configure(bg="#f0f0f0")
            
            # Создаем оверлей для блокировки
            if not hasattr(self, 'lock_overlay'):
                self.lock_overlay = tk.Frame(self, bg="#f0f0f0", bd=0)
                self.lock_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
                
                # Добавляем замок или текст о блокировке
                lock_label = tk.Label(self.lock_overlay, text="🔒 Заблокирован",
                                      bg="#f0f0f0", fg="gray")
                lock_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # Разблокированное состояние
            self.configure(bg="white")
            self.title_label.configure(bg="white")
            if hasattr(self, 'scroll_container'):
                self.scroll_container.configure(bg="white")
                self.canvas.configure(bg="white")
            self.content_frame.configure(bg="white")
            
            # Удаляем оверлей, если он есть
            if hasattr(self, 'lock_overlay'):
                self.lock_overlay.destroy()
                delattr(self, 'lock_overlay')

class Application(tk.Tk):  # класс приложения, наследуется от tk.tk
    def __init__(self):  # инициализатор приложения
        super().__init__()  # вызываем конструктор родительского класса
        self.module7 = None  # создаем атрибут для хранения экземпляра модуля 7
        self.module4 = None  # создаем атрибут для модуля 4 (авторизация)
        self.db_connected = False
        self.conn = None
        self.active_db = None  # Убедитесь, что это правильно инициализировано
        self.initialization_complete = False

        # Настройки окна приложения
        self.title("Мониторинг нефтепровода")  # задаем заголовок окна
        self.geometry("1200x800")  # задаем начальный размер окна (увеличено для лучшей видимости)
        self.minsize(1000, 600)  # минимальный размер окна
        
        self.configure(bg="#1E3A5F")  # устанавливаем глубокий синий фон для окна

        # создаем основной фрейм, который занимает всё окно
        self.main_frame = tk.Frame(self, bg="#1E3A5F")  # создаем фрейм с таким же фоном
        self.main_frame.pack(fill="both", expand=True)  # размещаем фрейм, чтобы он занимал всё окно

        self.tiles = []  # создаем список для хранения плиток модулей
        
        # Создаем плитки с минимальной настройкой
        self.create_tiles()

        # Инициализация других компонентов приложения
        self.module1 = None
        self.module2 = None
        self.module3 = None
        self.module8 = None
        self.module9 = None

        # Вместо инициализации модулей сразу, планируем её через 100 мс
        self.after(100, self.initialize_modules)

    def create_tiles(self):  # метод для создания плиток модулей
        # Оптимизированный метод создания плиток без динамического изменения размеров
        
        # Предварительная настройка весов для строк и столбцов (один раз)
        for i in range(3):
            self.main_frame.grid_rowconfigure(i, weight=1)
            self.main_frame.grid_columnconfigure(i, weight=1)
        
        for i in range(3):  # проходим по 3 строкам
            row = []  # создаем список для плиток текущей строки
            for j in range(3):  # проходим по 3 столбцам
                module_id = i * 3 + j + 1  # вычисляем номер модуля от 1 до 9
                tile = ModuleTile(self.main_frame, module_id=module_id)  # создаем плитку модуля
                
                # Размещаем плитку с фиксированными отступами
                tile.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                
                row.append(tile)  # добавляем плитку в список текущей строки
            self.tiles.append(row)  # добавляем строку плиток в общий список

    def initialize_modules(self):
        """Отложенная инициализация модулей с постепенной загрузкой"""
        try:
            # Изначально блокируем модули 1, 2, 3, 5, 6 (разблокируются после авторизации)
            self.lock_modules()
            
            # Запускаем инициализацию модулей с интервалами
            # Порядок важен: сначала инициализируем модуль 7 (мониторинг БД)
            self.after(100, self.initialize_module_7)  # Сначала модуль 7
            
            # Затем инициализируем модуль 8 (управление БД)
            self.after(300, self.initialize_module_8)
            
            # Затем инициализируем модуль 9 (подключение к БД)
            self.after(500, self.initialize_module_9)
            
            # Инициализируем модуль 4 в последнюю очередь
            self.after(700, self.initialize_module_4)
            
            # Остальные модули будут инициализированы после авторизации
            
            self.initialization_complete = True
            print("Инициализация модулей запланирована")
        except Exception as e:
            print(f"Ошибка при планировании инициализации модулей: {e}")

    def initialize_module_1(self):
        """Инициализация модуля 1"""
        try:
            # Находим тайл модуля 1
            tile = self.tiles[0][0]
            
            # Проверяем, что модуль еще не инициализирован
            if tile.module_obj is not None or hasattr(tile, '_initializing'):
                return
            
            tile._initializing = True
            
            # Очищаем содержимое перед созданием нового модуля
            for widget in tile.content_frame.winfo_children():
                widget.destroy()
            
            # Создаем экземпляр модуля 1
            from module1 import Module1
            module1_instance = Module1(tile.content_frame)
            tile.module_obj = module1_instance
            self.module1 = module1_instance
            # Обновляем скроллы после инициализации
            tile.force_scroll_update()
            tile._initializing = False
            print("Модуль 1 успешно инициализирован")
        except Exception as e:
            print(f"Ошибка инициализации модуля 1: {e}")
            if hasattr(self.tiles[0][0], '_initializing'):
                delattr(self.tiles[0][0], '_initializing')

    def initialize_module_2(self):
        """Инициализация модуля 2"""
        try:
            # Находим тайл модуля 2
            tile = self.tiles[0][1]
            
            # Проверяем, что модуль еще не инициализирован
            if tile.module_obj is not None or hasattr(tile, '_initializing'):
                return
            
            tile._initializing = True
            
            # Очищаем содержимое перед созданием нового модуля
            for widget in tile.content_frame.winfo_children():
                widget.destroy()
            
            try:
                from module2 import Module2
                module2_instance = Module2(tile.content_frame, app=self)
                module2_instance.pack(fill="both", expand=True)
                tile.module_obj = module2_instance
                self.module2 = module2_instance
                # Обновляем скроллы после инициализации
                tile.force_scroll_update()
                tile._initializing = False
                print("Модуль 2 успешно инициализирован")
            except Exception as e:
                print(f"Ошибка инициализации модуля 2: {e}")
                placeholder = tk.Label(tile.content_frame, text="(модуль 2: ошибка инициализации)", 
                                     bg="white", wraplength=150)
                placeholder.pack(fill="both", expand=True)
                tile._initializing = False
        except Exception as e:
            print(f"Общая ошибка инициализации модуля 2: {e}")
            if hasattr(self.tiles[0][1], '_initializing'):
                delattr(self.tiles[0][1], '_initializing')

    def initialize_module_3(self):
        """Инициализация модуля 3"""
        try:
            # Находим тайл модуля 3
            tile = self.tiles[0][2]
            
            # Проверяем, что модуль еще не инициализирован
            if tile.module_obj is not None or hasattr(tile, '_initializing'):
                return
            
            tile._initializing = True
            
            # Очищаем содержимое перед созданием нового модуля
            for widget in tile.content_frame.winfo_children():
                widget.destroy()
            
            try:
                from module3 import Module3
                module3_instance = Module3(tile.content_frame, app=self)
                module3_instance.pack(fill="both", expand=True)
                tile.module_obj = module3_instance
                self.module3 = module3_instance
                # Обновляем скроллы после инициализации
                tile.force_scroll_update()
                tile._initializing = False
                print("Модуль 3 успешно инициализирован")
            except Exception as e:
                print(f"Ошибка инициализации модуля 3: {e}")
                placeholder = tk.Label(tile.content_frame, text="(модуль 3: ошибка инициализации)", 
                                     bg="white", wraplength=150)
                placeholder.pack(fill="both", expand=True)
                tile._initializing = False
        except Exception as e:
            print(f"Общая ошибка инициализации модуля 3: {e}")
            if hasattr(self.tiles[0][2], '_initializing'):
                delattr(self.tiles[0][2], '_initializing')

    def initialize_module_4(self):
        """Инициализация модуля 4"""
        try:
            tile = None
            for row in self.tiles:
                for t in row:
                    if t.module_id == 4:
                        tile = t
                        break
                if tile:
                    break
            
            if tile:
                # Проверяем, что модуль еще не инициализирован
                if tile.module_obj is not None or hasattr(tile, '_initializing'):
                    return
                
                tile._initializing = True
                
                # Очищаем содержимое перед созданием нового модуля
                for widget in tile.content_frame.winfo_children():
                    widget.destroy()
                
                # Импортируем и создаем модуль 4
                from module4 import Module4
                module4_instance = Module4(tile.content_frame, main_app=self)
                module4_instance.pack(fill="both", expand=True)  # ВАЖНО: pack для отображения
                
                # Сохраняем ссылку на модуль
                tile.module_obj = module4_instance
                self.module4 = module4_instance
                
                tile._initializing = False
                print("Модуль 4 успешно инициализирован")
            else:
                print("Тайл для модуля 4 не найден")
        except Exception as e:
            print(f"Ошибка инициализации модуля 4: {e}")
            import traceback
            traceback.print_exc()
            if tile:
                if hasattr(tile, '_initializing'):
                    delattr(tile, '_initializing')
                placeholder = tk.Label(tile.content_frame, text="(модуль 4: ошибка инициализации)", 
                                     bg="white", wraplength=150)
                placeholder.pack(fill="both", expand=True)

    def initialize_module_5(self):
        """Инициализация модуля 5 - панель управления нефтепроводом"""
        try:
            tile = None
            for row in self.tiles:
                for t in row:
                    if t.module_id == 5:
                        tile = t
                        break
                if tile:
                    break
            
            if tile:
                # Проверяем, что модуль еще не инициализирован
                if tile.module_obj is not None or hasattr(tile, '_initializing'):
                    return
                
                tile._initializing = True
                
                # Очищаем содержимое перед созданием нового модуля
                for widget in tile.content_frame.winfo_children():
                    widget.destroy()
                
                # Импортируем и создаем модуль 5
                from module5 import Module5
                module5_instance = Module5(tile.content_frame, app=self)
                module5_instance.pack(fill="both", expand=True)  # ВАЖНО: pack для отображения
                
                # Сохраняем ссылку на модуль
                tile.module_obj = module5_instance
                self.module5 = module5_instance  # Важная ссылка для других модулей
                
                # Обновляем скроллы после инициализации
                tile.force_scroll_update()
                tile._initializing = False
                print("Модуль 5 (панель управления) успешно инициализирован")
            else:
                print("Тайл для модуля 5 не найден")
        except Exception as e:
            print(f"Ошибка инициализации модуля 5: {e}")
            import traceback
            traceback.print_exc()
            if tile:
                if hasattr(tile, '_initializing'):
                    delattr(tile, '_initializing')
                placeholder = tk.Label(tile.content_frame, text="(модуль 5: ошибка инициализации)", 
                                     bg="white", wraplength=150)
                placeholder.pack(fill="both", expand=True)

    def initialize_module_6(self):
        """Инициализация модуля 6 - архив отчетов"""
        try:
            tile = None
            for row in self.tiles:
                for t in row:
                    if t.module_id == 6:
                        tile = t
                        break
                if tile:
                    break
            
            if tile:
                # Проверяем, что модуль еще не инициализирован
                if tile.module_obj is not None or hasattr(tile, '_initializing'):
                    return
                
                tile._initializing = True
                
                # Очищаем содержимое перед созданием нового модуля
                for widget in tile.content_frame.winfo_children():
                    widget.destroy()
                
                # Импортируем и создаем модуль 6
                from module6 import Module6
                module6_instance = Module6(tile.content_frame, app=self)
                module6_instance.pack(fill="both", expand=True)  # ВАЖНО: pack для отображения
                
                # Сохраняем ссылку на модуль
                tile.module_obj = module6_instance
                self.module6 = module6_instance
                
                # Обновляем скроллы после инициализации
                tile.force_scroll_update()
                tile._initializing = False
                print("Модуль 6 успешно инициализирован")
            else:
                print("Тайл для модуля 6 не найден")
        except Exception as e:
            print(f"Ошибка инициализации модуля 6: {e}")
            if tile:
                if hasattr(tile, '_initializing'):
                    delattr(tile, '_initializing')
                placeholder = tk.Label(tile.content_frame, text="(модуль 6: ошибка инициализации)", 
                                     bg="white", wraplength=150)
                placeholder.pack(fill="both", expand=True)

    def initialize_module_7(self):
        """Инициализация модуля 7"""
        try:
            # Находим тайл модуля 7
            tile = self.tiles[2][0]
            
            try:
                from module7 import Module7
                module7_instance = Module7(tile.content_frame)
                module7_instance.pack(fill="both", expand=True)
                tile.module_obj = module7_instance
                self.module7 = module7_instance
                print("Модуль 7 успешно инициализирован")
            except Exception as e:
                print(f"Ошибка инициализации модуля 7: {e}")
                placeholder = tk.Label(tile.content_frame, text="(модуль 7: ошибка инициализации)", 
                                     bg="white", wraplength=150)
                placeholder.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Общая ошибка инициализации модуля 7: {e}")

    def initialize_module_8(self):
        """Инициализация модуля 8"""
        try:
            # Находим тайл модуля 8
            tile = self.tiles[2][1]
            
            try:
                from module8 import Module8
                
                # Проверяем, создан ли модуль 7
                if not hasattr(self, 'module7') or self.module7 is None:
                    module8_instance = Module8(tile.content_frame)
                else:
                    module8_instance = Module8(tile.content_frame, module7_ref=self.module7)
                
                module8_instance.pack(fill="both", expand=True)
                tile.module_obj = module8_instance
                self.module8 = module8_instance
                print("Модуль 8 успешно инициализирован")
            except Exception as e:
                print(f"Ошибка инициализации модуля 8: {e}")
                placeholder = tk.Label(tile.content_frame, text="(модуль 8: ошибка инициализации)", 
                                     bg="white", wraplength=150)
                placeholder.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Общая ошибка инициализации модуля 8: {e}")

    def initialize_module_9(self):
        """Инициализация модуля 9"""
        try:
            # Находим тайл модуля 9
            tile = self.tiles[2][2]
            
            # Отладка - проверяем инициализацию модуля 7
            print("DEBUG: Перед инициализацией модуля 9:")
            print(f"DEBUG: module7 существует: {hasattr(self, 'module7')}")
            if hasattr(self, 'module7'):
                print(f"DEBUG: module7 не None: {self.module7 is not None}")
                print(f"DEBUG: module7 имеет метод add_connection: {hasattr(self.module7, 'add_connection')}")
            
            try:
                from module9 import Module9
                callback = None
                if hasattr(self, 'module7') and self.module7 is not None:
                    callback = self.module7.add_connection
                    print(f"DEBUG: Получен callback из модуля 7: {callback}")
                else:
                    print("DEBUG: Не удалось получить callback из модуля 7")
                
                module9_instance = Module9(tile.content_frame, connection_callback=callback)
                module9_instance.pack(fill="both", expand=True)
                tile.module_obj = module9_instance
                self.module9 = module9_instance
                
                # Настройка связей между модулями
                if hasattr(self, 'module8') and self.module8:
                    print("DEBUG: Устанавливаем связь между модулями 8 и 9")
                    if hasattr(module9_instance, 'set_module8_ref'):
                        module9_instance.set_module8_ref(self.module8)
                
                print("Модуль 9 успешно инициализирован")
            except Exception as e:
                print(f"Ошибка инициализации модуля 9: {e}")
                import traceback
                traceback.print_exc()
                placeholder = tk.Label(tile.content_frame, text="(модуль 9: ошибка инициализации)", 
                                     bg="white", wraplength=150)
                placeholder.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Общая ошибка инициализации модуля 9: {e}")
            import traceback
            traceback.print_exc()

    def unlock_modules(self):
        """Разблокирует все модули после успешной авторизации."""
        print("Разблокировка модулей после успешной авторизации")
        for row in self.tiles:
            for tile in row:
                # Разблокируем только модули 1, 2, 3, 5, 6
                # Модули 4, 7, 8, 9 остаются всегда доступными
                if tile.module_id in [1, 2, 3, 5, 6]:
                    tile.set_locked(False)
                    print(f"Модуль {tile.module_id} разблокирован")
        
        # Инициализируем остальные модули после авторизации
        self.after(100, self.initialize_unlocked_modules)
    
    def lock_modules(self):
        """Блокирует модули после выхода из системы или смены БД."""
        print("Блокировка модулей")
        for row in self.tiles:
            for tile in row:
                # Блокируем модули 1, 2, 3, 5, 6
                # Модули 4, 7, 8, 9 остаются всегда доступными
                if tile.module_id in [1, 2, 3, 5, 6]:
                    tile.set_locked(True)
                    print(f"Модуль {tile.module_id} заблокирован")

    def initialize_unlocked_modules(self):
        """Инициализация разблокированных модулей с интервалами"""
        # Инициализируем модули 1, 2 и 3, которые требуют подключения к БД, с задержкой
        self.after(100, self.initialize_module_1)
        self.after(300, self.initialize_module_2)
        self.after(500, self.initialize_module_3)
        self.after(600, self.initialize_module_5)  # Модуль 5 - панель управления
        self.after(700, self.initialize_module_6)  # Модуль 6 - архив отчетов
        
        # Другие модули при необходимости

    def set_active_database(self, db_name):
        """Set active database and establish connection"""
        print(f"DEBUG: set_active_database вызван с db_name={db_name}")
        
        if db_name != self.active_db or not self.db_connected:
            try:
                # Close existing connection if any
                if self.conn:
                    try:
                        self.conn.close()
                        print(f"DEBUG: Закрыто предыдущее соединение с БД")
                    except Exception as e:
                        print(f"DEBUG: Ошибка при закрытии предыдущего соединения: {e}")
                    
                # Проверяем, существует ли файл базы данных
                db_path = None
                
                # Если это прямой путь к файлу и файл существует
                if os.path.isfile(db_name):
                    db_path = db_name
                    print(f"DEBUG: Указан прямой путь к существующему файлу БД: {db_path}")
                    
                # Проверяем, может быть это просто имя файла в текущем каталоге
                elif os.path.exists(os.path.join(".", db_name)):
                    db_path = os.path.join(".", db_name)
                    print(f"DEBUG: Файл БД найден в текущем каталоге: {db_path}")
                    
                # Если это имя файла без пути, попробуем найти в текущем каталоге и подкаталогах
                else:
                    print(f"DEBUG: Поиск файла БД '{db_name}' в текущем каталоге и подкаталогах")
                    for root, dirs, files in os.walk(".", topdown=False):
                        for file in files:
                            if file == db_name:
                                db_path = os.path.join(root, file)
                                print(f"DEBUG: Файл БД найден: {db_path}")
                                break
                        if db_path:
                            break
                    
                # Если файл не найден - пробуем последний вариант - просто подключиться к указанному пути
                if not db_path:
                    db_path = db_name
                    print(f"DEBUG: Пробуем подключиться напрямую к указанному пути: {db_path}")
                
                # Connect to database - используем check_same_thread=False для предотвращения блокировок
                print(f"DEBUG: Создаем соединение с БД {db_path}")
                self.conn = sqlite3.connect(db_path, check_same_thread=False)
                
                # Включаем поддержку внешних ключей и устанавливаем timeout
                self.conn.execute("PRAGMA foreign_keys = ON")
                self.conn.execute("PRAGMA busy_timeout = 5000")
                
                # Проверяем структуру БД
                if not self.validate_db_structure():
                    messagebox.showwarning("Неполная БД", 
                        "Подключенная база данных не содержит всех необходимых таблиц.\n"
                        "Система будет работать с ограниченной функциональностью.")
                
                self.active_db = db_path  # Сохраняем полный путь к файлу
                self.db_connected = True
                print(f"Подключение к БД {db_path} успешно")
                
                # Уведомляем модуль 4 о смене БД
                self.notify_module4_db_change()
                
                # НЕ разблокируем модули автоматически - только через авторизацию в модуле 4
                # НЕ ВЫЗЫВАЕМ unlock_modules() здесь!
                    
                return True
            except Exception as e:
                print(f"Ошибка подключения к БД: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Ошибка базы данных", f"Ошибка подключения: {e}")
                self.db_connected = False
                return False
        return True



    def validate_db_structure(self):
        """Проверяет, что БД содержит все необходимые таблицы"""
        if not self.conn:
            return False
        
        required_tables = ['operators', 'cells', 'external_data', 'reports', 'raw_data']
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                print(f"Отсутствующие таблицы в БД: {missing_tables}")
                return False
            
            print("Структура БД корректна - все необходимые таблицы найдены")
            return True
            
        except Exception as e:
            print(f"Ошибка при проверке структуры БД: {e}")
            return False
    
    def notify_module4_db_change(self):
        """Уведомляет модуль 4 о смене активной БД"""
        try:
            # Находим модуль 4
            module4 = None
            for row in self.tiles:
                for tile in row:
                    if tile.module_id == 4:
                        # Ищем экземпляр Module4 в дочерних виджетах
                        for child in tile.content_frame.winfo_children():
                            if hasattr(child, 'on_db_change'):
                                module4 = child
                                break
                        break
                if module4:
                    break
            
            if module4:
                # Формируем информацию о новой БД
                db_info = {
                    "Название БД": os.path.basename(self.active_db),
                    "Путь БД": self.active_db,
                    "Статус": "Подключена"
                }
                
                # Уведомляем модуль 4
                module4.on_db_change(db_info)
                print(f"Уведомили модуль 4 о смене БД на {db_info['Название БД']}")
            else:
                print("Модуль 4 не найден для уведомления о смене БД")
                
        except Exception as e:
            print(f"Ошибка при уведомлении модуля 4 о смене БД: {e}")

    def get_db_connection(self):
        """Возвращает текущее соединение с БД"""
        return self.conn if self.db_connected else None

if __name__ == "__main__":  # если запускаем этот файл как основную программу
    app = Application()  # создаем экземпляр приложения
    app.mainloop()  # запускаем главный цикл приложения
