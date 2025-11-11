import tkinter as tk
from tkinter import messagebox

class DatabaseSelection(tk.Toplevel):
    def __init__(self, parent, databases, callback):
        super().__init__(parent)
        self.title("Выбор базы данных")
        self.geometry("300x200")
        self.databases = databases
        self.callback = callback
        
        self.label = tk.Label(self, text="Выберите базу данных:")
        self.label.pack(pady=10)
        
        self.var = tk.StringVar(value=databases[0] if databases else "")
        
        for db in databases:
            rb = tk.Radiobutton(self, text=db, variable=self.var, value=db)
            rb.pack(anchor='w')
        
        self.select_button = tk.Button(self, text="Выбрать", command=self.select_database)
        self.select_button.pack(pady=20)
        
        self.cancel_button = tk.Button(self, text="Отмена", command=self.destroy)
        self.cancel_button.pack(pady=5)

    def select_database(self):
        selected_db = self.var.get()
        if selected_db:
            self.callback(selected_db)
            self.destroy()
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите базу данных.") 