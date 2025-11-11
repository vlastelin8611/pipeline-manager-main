import tkinter as tk
import sys

def test_mouse_scroll():
    """Тест прокрутки мышью и дублирования"""
    root = tk.Tk()
    root.title("Тест прокрутки мышью")
    root.geometry("400x300")
    
    # Создаем прокручиваемый контейнер
    container = tk.Frame(root)
    container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Canvas для прокрутки
    canvas = tk.Canvas(container, bg="lightgray")
    
    # Scrollbars
    v_scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # Размещение
    canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    
    # Содержимое для прокрутки
    content_frame = tk.Frame(canvas, bg="white")
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
    # Добавляем много элементов для тестирования прокрутки
    for i in range(50):
        label = tk.Label(content_frame, text=f"Элемент {i+1}: Тест прокрутки мышью", 
                        bg="white", relief="ridge", bd=1)
        label.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
        
        # Добавляем широкие элементы для горизонтальной прокрутки
        if i % 10 == 0:
            wide_label = tk.Label(content_frame, 
                                 text=f"Широкий элемент {i+1}: " + "А" * 100,
                                 bg="lightblue", relief="ridge", bd=1)
            wide_label.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
    
    # Настройка области прокрутки
    def update_scroll_region():
        content_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def configure_content_frame(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind('<Configure>', configure_content_frame)
    content_frame.bind('<Configure>', lambda e: update_scroll_region())
    
    # Привязка прокрутки мышью
    def on_mousewheel(event):
        if canvas.cget("yscrollcommand"):
            if sys.platform == "win32":
                delta = int(-1 * (event.delta / 120))
            else:
                delta = -1 if event.num == 4 else 1
            canvas.yview_scroll(delta, "units")
    
    def on_shift_mousewheel(event):
        if canvas.cget("xscrollcommand"):
            if sys.platform == "win32":
                delta = int(-1 * (event.delta / 120))
            else:
                delta = -1 if event.num == 4 else 1
            canvas.xview_scroll(delta, "units")
    
    def bind_mousewheel_recursive(widget):
        try:
            # Windows и macOS
            widget.bind("<MouseWheel>", on_mousewheel)
            widget.bind("<Shift-MouseWheel>", on_shift_mousewheel)
            
            # Linux
            widget.bind("<Button-4>", on_mousewheel)
            widget.bind("<Button-5>", on_mousewheel)
            widget.bind("<Shift-Button-4>", on_shift_mousewheel)
            widget.bind("<Shift-Button-5>", on_shift_mousewheel)
            
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        except:
            pass
    
    # Привязываем прокрутку
    bind_mousewheel_recursive(root)
    
    # Первоначальное обновление
    root.after(100, update_scroll_region)
    
    # Инструкции
    instructions = tk.Label(root, 
                           text="Тест прокрутки:\\n- Колесико мыши: вертикальная прокрутка\\n- Shift + колесико: горизонтальная прокрутка",
                           bg="lightyellow", justify="left")
    instructions.pack(side="bottom", fill="x")
    
    print("Тест прокрутки мышью запущен:")
    print("- Наведите курсор на область с контентом")
    print("- Прокручивайте колесиком мыши для вертикальной прокрутки")
    print("- Держите Shift и прокручивайте для горизонтальной прокрутки")
    
    root.mainloop()

if __name__ == "__main__":
    test_mouse_scroll() 