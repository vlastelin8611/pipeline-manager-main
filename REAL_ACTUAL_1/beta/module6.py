import tkinter as tk  # импортирую модуль tkinter для создания графического интерфейса, сокращаю название до tk
from tkinter import ttk, scrolledtext, messagebox  # импортирую дополнительные компоненты tkinter:
# ttk - современные виджеты с улучшенным дизайном
# scrolledtext - текстовое поле с прокруткой
# messagebox - для показа всплывающих сообщений пользователю
import os  # импортирую модуль os для работы с файлами и папками
import datetime  # импортирую модуль datetime для работы с датой и временем
import glob  # импортирую модуль glob для поиска файлов по шаблону (маске)

class Module6(tk.Frame):  # создаю класс Module6, который наследуется от tk.Frame (контейнер для виджетов)
    def __init__(self, parent, app=None):  # конструктор класса, принимает родительский виджет и ссылку на приложение
        """Инициализация модуля 6 - архив отчетов."""  # описание назначения этого класса
        super().__init__(parent, bg="white")  # вызываю конструктор родительского класса с белым фоном
        self.parent = parent  # сохраняю ссылку на родительский виджет
        self.app = app  # сохраняю ссылку на основное приложение
        
        # Размер модуля будет адаптироваться под размер окна
        self.pack(fill="both", expand=True)  # размещаю модуль, заполняя всю доступную область и позволяя расширяться
        
        # Переменные
        # Папка отчетов в директории программы
        self.reports_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")  # создаю путь к папке reports в директории программы
        # os.path.abspath(__file__) - получаю полный путь к текущему файлу
        # os.path.dirname() - получаю директорию где находится файл
        # os.path.join() - соединяю путь к директории с названием папки "reports"
        self.current_report_file = None  # переменная для хранения пути к выбранному файлу отчета (пока не выбран)
        
        # Создание интерфейса
        self.setup_ui()  # вызываю метод для создания пользовательского интерфейса
        
        # Загружаем список отчетов
        self.refresh_reports_list()  # вызываю метод для загрузки и отображения списка существующих отчетов
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Верхняя панель с заголовком
        self.header_frame = tk.Frame(self, bg="white", height=25)
        self.header_frame.pack(fill="x", pady=2)
        
        # Заголовок
        self.title_label = tk.Label(self.header_frame, text="Архив отчетов", 
                                  font=("Arial", 12, "bold"), bg="white")
        self.title_label.pack(side="left", padx=5)
        
        # Кнопка обновления списка
        self.refresh_button = tk.Button(self.header_frame, text="Обновить", 
                                      font=("Arial", 9), width=8, height=1,
                                      command=self.refresh_reports_list)
        self.refresh_button.pack(side="right", padx=5)
        
        # Основная область с двумя панелями
        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=2)
        
        # Левая панель - список отчетов
        self.left_frame = tk.Frame(self.main_frame, bg="white", width=200)
        self.left_frame.pack(side="left", fill="y", padx=(0, 5))
        self.left_frame.pack_propagate(False)
        
        # Заголовок списка отчетов
        self.list_label = tk.Label(self.left_frame, text="Список отчетов:", 
                                 font=("Arial", 10, "bold"), bg="white")
        self.list_label.pack(anchor="w", pady=(0, 5))
        
        # Список отчетов с прокруткой
        self.list_frame = tk.Frame(self.left_frame, bg="white")
        self.list_frame.pack(fill="both", expand=True)
        
        self.reports_listbox = tk.Listbox(self.list_frame, font=("Arial", 9),
                                        selectmode=tk.SINGLE)
        self.reports_listbox.pack(side="left", fill="both", expand=True)
        
        self.list_scrollbar = tk.Scrollbar(self.list_frame)
        self.list_scrollbar.pack(side="right", fill="y")
        
        self.reports_listbox.config(yscrollcommand=self.list_scrollbar.set)
        self.list_scrollbar.config(command=self.reports_listbox.yview)
        
        # Привязываем событие выбора отчета
        self.reports_listbox.bind('<<ListboxSelect>>', self.on_report_select)
        
        # Правая панель - содержимое отчета
        self.right_frame = tk.Frame(self.main_frame, bg="white")
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        # Заголовок области просмотра
        self.view_label = tk.Label(self.right_frame, text="Содержимое отчета:", 
                                 font=("Arial", 10, "bold"), bg="white")
        self.view_label.pack(anchor="w", pady=(0, 5))
        
        # Текстовое поле для отображения отчета
        self.report_text = scrolledtext.ScrolledText(self.right_frame, 
                                                   font=("Arial", 10), 
                                                   bg="white", 
                                                   wrap="word",
                                                   state="disabled")
        self.report_text.pack(fill="both", expand=True)
        
        # Нижняя панель с информацией
        self.bottom_frame = tk.Frame(self, bg="white", height=25)
        self.bottom_frame.pack(fill="x", pady=2)
        
        # Информация о выбранном отчете
        self.info_label = tk.Label(self.bottom_frame, text="Выберите отчет для просмотра", 
                                 font=("Arial", 9), bg="white", fg="gray")
        self.info_label.pack(side="left", padx=5)
        
        # Кнопка удаления отчета
        self.delete_button = tk.Button(self.bottom_frame, text="Удалить отчет", 
                                     font=("Arial", 9), width=12, height=1,
                                     command=self.delete_selected_report,
                                     state="disabled")
        self.delete_button.pack(side="right", padx=5)
        
    def refresh_reports_list(self):
        """Обновляет список отчетов"""
        try:
            # Очищаем список
            self.reports_listbox.delete(0, tk.END)
            
            # Проверяем существование папки отчетов
            if not os.path.exists(self.reports_folder):
                self.info_label.config(text="Папка отчетов не найдена")
                return
            
            # Получаем список файлов отчетов
            report_files = glob.glob(os.path.join(self.reports_folder, "report_*.txt"))
            
            if not report_files:
                self.info_label.config(text="Отчеты не найдены")
                return
            
            # Сортируем файлы по дате (новые сверху)
            report_files.sort(reverse=True)
            
            # Добавляем файлы в список
            for file_path in report_files:
                filename = os.path.basename(file_path)
                # Извлекаем дату и время из имени файла
                try:
                    # Формат: report_YYYY-MM-DD_HH-MM-SS.txt
                    date_part = filename.replace("report_", "").replace(".txt", "")
                    date_obj = datetime.datetime.strptime(date_part, "%Y-%m-%d_%H-%M-%S")
                    display_name = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Добавляем в список с отображаемым именем
                    self.reports_listbox.insert(tk.END, display_name)
                    
                except ValueError:
                    # Если не удалось распарсить дату, показываем имя файла
                    self.reports_listbox.insert(tk.END, filename)
            
            self.info_label.config(text=f"Найдено отчетов: {len(report_files)}")
            
        except Exception as e:
            print(f"Module6: Ошибка при обновлении списка отчетов: {e}")
            self.info_label.config(text="Ошибка при загрузке отчетов")
    
    def on_report_select(self, event):
        """Обработчик выбора отчета из списка"""
        try:
            selection = self.reports_listbox.curselection()
            if not selection:
                return
            
            # Получаем индекс выбранного элемента
            index = selection[0]
            selected_text = self.reports_listbox.get(index)
            
            # Находим соответствующий файл
            report_files = glob.glob(os.path.join(self.reports_folder, "report_*.txt"))
            report_files.sort(reverse=True)
            
            if index < len(report_files):
                file_path = report_files[index]
                self.load_report(file_path)
                self.current_report_file = file_path
                self.delete_button.config(state="normal")
                
                # Обновляем информацию
                file_size = os.path.getsize(file_path)
                self.info_label.config(text=f"Отчет: {selected_text}, Размер: {file_size} байт")
            
        except Exception as e:
            print(f"Module6: Ошибка при выборе отчета: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить отчет: {e}")
    
    def load_report(self, file_path):
        """Загружает и отображает содержимое отчета"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Отображаем содержимое в текстовом поле
            self.report_text.config(state="normal")
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, content)
            self.report_text.config(state="disabled")
            
        except Exception as e:
            print(f"Module6: Ошибка при загрузке файла отчета: {e}")
            self.report_text.config(state="normal")
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, f"Ошибка при загрузке отчета:\n{e}")
            self.report_text.config(state="disabled")
    
    def delete_selected_report(self):
        """Удаляет выбранный отчет"""
        try:
            if not self.current_report_file:
                return
            
            # Подтверждение удаления
            filename = os.path.basename(self.current_report_file)
            result = messagebox.askyesno("Подтверждение", 
                                       f"Вы уверены, что хотите удалить отчет:\n{filename}?")
            
            if result:
                # Удаляем файл
                os.remove(self.current_report_file)
                
                # Очищаем текстовое поле
                self.report_text.config(state="normal")
                self.report_text.delete(1.0, tk.END)
                self.report_text.config(state="disabled")
                
                # Обновляем список
                self.refresh_reports_list()
                
                # Сбрасываем состояние
                self.current_report_file = None
                self.delete_button.config(state="disabled")
                self.info_label.config(text="Отчет удален")
                
                messagebox.showinfo("Успех", "Отчет успешно удален")
            
        except Exception as e:
            print(f"Module6: Ошибка при удалении отчета: {e}")
            messagebox.showerror("Ошибка", f"Не удалось удалить отчет: {e}")
    
    def on_close(self):
        """Вызывается при закрытии модуля"""
        pass  # Модуль 6 не требует специальной очистки при закрытии 