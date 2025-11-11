import tkinter as tk
from tkinter import ttk
import module3
import module7
import module8
import module9

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система управления базами данных")
        self.geometry("1200x800")
        
        print("Инициализация основного приложения")
        
        # Создаем фрейм для вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Инициализируем модули
        self.initialize_modules()
        
        # Обрабатываем взаимосвязи между модулями
        self.setup_module_connections()
        
        # Запускаем сканирование баз данных
        if hasattr(self, 'module7') and self.module7:
            self.module7.scan_databases()
            
        print("Инициализация приложения завершена")
        
    def initialize_modules(self):
        """Инициализирует все модули приложения."""
        print("Инициализация модулей")
        
        # Создаем вкладки и инициализируем модули
        # Модуль 7 - управление базами данных
        module7_frame = ttk.Frame(self.notebook)
        self.module7 = module7.Module7(module7_frame, app=self)
        self.notebook.add(module7_frame, text="Модуль 7")
        
        # Модуль 8 - управление активной БД
        module8_frame = ttk.Frame(self.notebook)
        self.module8 = module8.Module8(module8_frame, app=self)
        self.notebook.add(module8_frame, text="Модуль 8")
        
        # Модуль 3 - генерация отчетов
        module3_frame = ttk.Frame(self.notebook)
        self.module3 = module3.Module3(module3_frame, app=self)
        self.notebook.add(module3_frame, text="Модуль 3")
        
        # Модуль 9 - дополнительные функции
        module9_frame = ttk.Frame(self.notebook)
        self.module9 = module9.Module9(module9_frame, app=self)
        self.notebook.add(module9_frame, text="Модуль 9")
        
    def setup_module_connections(self):
        """Устанавливает связи между модулями."""
        print("Установка связей между модулями")
        
        # Связь между модулями 7 и 8
        if hasattr(self, 'module7') and self.module7 and hasattr(self, 'module8') and self.module8:
            print("Связывание модулей 7 и 8")
            self.module7.set_module8_ref(self.module8)
            self.module8.set_module7_ref(self.module7)
            
        # Связь между модулями 8 и 3
        if hasattr(self, 'module8') and self.module8 and hasattr(self, 'module3') and self.module3:
            print("Связывание модулей 8 и 3")
            self.module8.set_module3_ref(self.module3)
            
        # Связь между модулями 8 и 9
        if hasattr(self, 'module8') and self.module8 and hasattr(self, 'module9') and self.module9:
            print("Связывание модулей 8 и 9")
            self.module8.set_module9_ref(self.module9)
            self.module9.set_module8_ref(self.module8)
        
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop() 