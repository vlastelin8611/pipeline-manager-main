import tkinter as tk  # импорт tkinter для работы с графическим интерфейсом

class ModuleTile(tk.Frame):  # класс moduletile, наследуется от tk.frame
    def __init__(self, parent, module_id, *args, **kwargs):  # инициализатор, принимает родителя, номер модуля и доп. параметры
        super().__init__(parent, *args, **kwargs)  # вызываем конструктор родительского класса
        self.module_id = module_id  # сохраняем номер модуля в атрибуте
        self.configure(borderwidth=2, relief="solid", bg="white")  # задаем рамку 2px, сплошной стиль и белый фон
        self.grid_propagate(False)  # отключаем автоизменение размера плитки в зависимости от содержимого

        # установка заголовка модуля, расположенного сверху
        if self.module_id == 7:  # если модуль 7
            title_text = "мониторинг состояния бд"  # название модуля 7
        elif self.module_id == 9:  # если модуль 9
            title_text = "модуль подключения к бд"  # название модуля 9
        else:  # для остальных модулей
            title_text = f"модуль {module_id}"  # название будет 'модуль' и номер

        self.title_label = tk.Label(self, text=title_text, anchor='w',
                                    font=("Arial", 10, "bold"), bg="white")  # создаем метку с заголовком
        self.title_label.pack(side="top", fill="x", padx=2, pady=2)  # размещаем метку сверху, растягивая по горизонтали

        # создаем контейнер для будущего содержимого модуля
        self.content_frame = tk.Frame(self, bg="white")  # создаем фрейм для контента с белым фоном
        self.content_frame.pack(side="top", fill="both", expand=True, padx=2, pady=2)  # размещаем фрейм, чтобы он занимал всё доступное место

        # ниже идут шлюзы для вставки кода каждого модуля (плейсхолдеры)
        if self.module_id == 1:  # если модуль 1
            # шлюз для модуля 1: графика трубопровода
            placeholder = tk.Label(self.content_frame, text="(модуль 1: графика трубопровода)", 
                                   bg="white", wraplength=150)  # создаем метку с текстом и ограничением переноса
            placeholder.pack(fill="both", expand=True)  # размещаем метку
        elif self.module_id == 2:  # если модуль 2
            # шлюз для модуля 2: динамические шкалы с показателями
            placeholder = tk.Label(self.content_frame, text="(модуль 2: динамические шкалы)", 
                                   bg="white", wraplength=150)  # создаем метку с текстом
            placeholder.pack(fill="both", expand=True)  # размещаем метку
        elif self.module_id == 3:  # если модуль 3
            # шлюз для модуля 3: отчет о трубопроводе
            placeholder = tk.Label(self.content_frame, text="(модуль 3: отчет о трубопроводе)", 
                                   bg="white", wraplength=150)  # создаем метку с текстом
            placeholder.pack(fill="both", expand=True)  # размещаем метку
        elif self.module_id == 4:  # если модуль 4
            # шлюз для модуля 4: данные об операторе
            placeholder = tk.Label(self.content_frame, text="(модуль 4: данные об операторе)", 
                                   bg="white", wraplength=150)  # создаем метку с текстом
            placeholder.pack(fill="both", expand=True)  # размещаем метку
        elif self.module_id == 5:  # если модуль 5
            # шлюз для модуля 5: панель управления
            placeholder = tk.Label(self.content_frame, text="(модуль 5: панель управления)", 
                                   bg="white", wraplength=150)  # создаем метку с текстом
            placeholder.pack(fill="both", expand=True)  # размещаем метку
        elif self.module_id == 6:  # если модуль 6
            # шлюз для модуля 6: архив отчетов
            placeholder = tk.Label(self.content_frame, text="(модуль 6: архив отчетов)", 
                                   bg="white", wraplength=150)  # создаем метку с текстом
            placeholder.pack(fill="both", expand=True)  # размещаем метку
        elif self.module_id == 7:  # если модуль 7
            # импортируем модуль 7 (мониторинг состояния бд) из отдельного файла module7.py
            from module7 import Module7  # импорт модуля 7
            module7_instance = Module7(self.content_frame)  # создаем экземпляр модуля 7
            module7_instance.pack(fill="both", expand=True)  # размещаем его в фрейме контента
            # сохраняем ссылку на модуль 7 в основном приложении для последующей работы
            self.master.master.module7 = module7_instance  # сохраняем в атрибуте module7 главного окна
        elif self.module_id == 8:  # если модуль 8
            # импортируем модуль 8 (управление бд) из файла module8.py
            from module8 import Module8  # импорт модуля 8
            # передаем ссылку на модуль 7, чтобы знать, какие базы подключены
            module8_instance = Module8(self.content_frame, module7_ref=self.master.master.module7)  
            module8_instance.pack(fill="both", expand=True)  # размещаем экземпляр модуля 8
        elif self.module_id == 9:  # если модуль 9
            # импортируем модуль 9 (подключение к бд) из файла module9.py
            from module9 import Module9  # импорт модуля 9
            # устанавливаем callback: если модуль 7 создан, берем его метод add_connection, иначе callback = none
            callback = None  # начальное значение callback
            if hasattr(self.master.master, 'module7') and self.master.master.module7 is not None:
                callback = self.master.master.module7.add_connection  # получаем callback из модуля 7
            module9_instance = Module9(self.content_frame, connection_callback=callback)  # создаем экземпляр модуля 9
            module9_instance.pack(fill="both", expand=True)  # размещаем его
        else:  # если модуль с таким номером не реализован
            placeholder = tk.Label(self.content_frame, text=f"(модуль {self.module_id}: шлюз не реализован)", 
                                   bg="white", wraplength=150)  # создаем метку с текстом
            placeholder.pack(fill="both", expand=True)  # размещаем метку

class Application(tk.Tk):  # класс приложения, наследуется от tk.tk
    def __init__(self):  # инициализатор приложения
        super().__init__()  # вызываем конструктор родительского класса
        self.module7 = None  # создаем атрибут для хранения экземпляра модуля 7

        self.title("модульная система 3x3")  # задаем заголовок окна
        self.geometry("600x600")  # задаем размер окна 600 на 600
        self.configure(bg="#1E3A5F")  # устанавливаем глубокий синий фон для окна

        # создаем основной фрейм, который занимает всё окно
        self.main_frame = tk.Frame(self, bg="#1E3A5F")  # создаем фрейм с таким же фоном
        self.main_frame.pack(fill="both", expand=True)  # размещаем фрейм, чтобы он занимал всё окно

        self.tiles = []  # создаем список для хранения плиток модулей
        self.create_tiles()  # вызываем метод для создания плиток

    def create_tiles(self):  # метод для создания плиток модулей
        for i in range(3):  # проходим по 3 строкам
            row = []  # создаем список для плиток текущей строки
            for j in range(3):  # проходим по 3 столбцам
                module_id = i * 3 + j + 1  # вычисляем номер модуля от 1 до 9
                tile = ModuleTile(self.main_frame, module_id=module_id)  # создаем плитку модуля с заданным номером
                tile.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")  # размещаем плитку в сетке с отступами
                row.append(tile)  # добавляем плитку в список текущей строки
            self.tiles.append(row)  # добавляем строку плиток в общий список

        # равномерно распределяем пространство по строкам и столбцам
        for i in range(3):  # для каждой строки и столбца
            self.main_frame.grid_rowconfigure(i, weight=1)  # задаем вес строки, чтобы пространство распределялось равномерно
            self.main_frame.grid_columnconfigure(i, weight=1)  # задаем вес столбца

if __name__ == "__main__":  # если запускаем этот файл как основную программу
    app = Application()  # создаем экземпляр приложения
    app.mainloop()  # запускаем главный цикл приложения
