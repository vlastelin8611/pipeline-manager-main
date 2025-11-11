import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime, timedelta
import os
import pickle

class ReportDatabase:
    def __init__(self):
        self.db_filename = "reports_db.pkl"
        self.reports = []

        if not os.path.exists(self.db_filename):
            self._save_db()

        self._load_db()

    def _save_db(self):
        with open(self.db_filename, "wb") as f:
            pickle.dump(self.reports, f)

    def _load_db(self):
        if os.path.exists(self.db_filename):
            with open(self.db_filename, "rb") as f:
                self.reports = pickle.load(f)

    def add_report(self, report):
        self.reports.append(report)
        self._save_db()

    def get_reports_list(self):
        return self.reports

class PipelineMonitoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг состояния трубопровода")
        self.root.geometry("1400x800")

        self.start_time = datetime.now()
        self.current_animation_id = None

        # More realistic initial values
        self.data = {
            "Температура на улице (°C)": (5, -20, 40),
            "Температура в трубопровода (°C)": (60, 40, 80), 
            "Скорость откачки (литры в минуту)": (1000, 500, 1500),  # liters/minute
            "Угол наклона трубопровода (градусы)": (1, -5, 5), 
            "Показания вибраций трубопровода (мм/с)": (2, 0, 10),  # mm/second
            "Давление внутри трубопровода (Па)": (90000, 80000, 100000), 
            "Давление на улице (мм рт. ст.)": (760, 720, 780),
            "Нефтепродукт": ("Нефть", ["Нефть", "Газ", "Мазут", "Дизель", "Бензин"])
        }

        self.report_db = ReportDatabase()

        self.create_gui()
        
        # Создаем отдельное окно для экспериментальных функций
        self.experimental_functions_window = tk.Toplevel(self.root)
        self.experimental_functions_window.title("Экспериментальные функции")
        self.experimental_functions_window.geometry("600x600")  # Increased height
        self.create_experimental_functions()

        self.update_data()  # Начать обновление данных

        self.start_timer()

        self.create_initial_reports()

        self.broken_cell = None  # To store the broken cell

        self.update_product_label()  # Start updating the product label
        self.product_label_timer = self.root.after(60000, self.update_product_label)


    def create_gui(self):
        self.indicator_frame = ttk.Frame(self.root, width=50, height=200, borderwidth=1, relief="solid")
        self.indicator_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        self.indicators = []
        for i in range(4):
            line_frame = ttk.Frame(self.indicator_frame, width=5, height=200)
            line_frame.pack(side="left", padx=5)

            line_indicators = []
            for j in range(10):
                cell = tk.Canvas(line_frame, width=5, height=20, bg="black")
                cell.pack(side="top", pady=1)
                line_indicators.append(cell)

            self.indicators.append(line_indicators)

        self.main_frame = ttk.Frame(self.root, width=500, height=700, borderwidth=1, relief="solid")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nw")

        self.timer_label = ttk.Label(self.main_frame, text="", font=("Arial", 16))
        self.timer_label.grid(row=0, column=0, columnspan=3, pady=10)

        self.scales = {}
        # Skip "Нефтепродукт" when creating scales
        for i, (label_text, data) in enumerate(self.data.items()):
            if label_text == "Нефтепродукт":
                continue
            if isinstance(data, tuple):
                value, min_value, max_value = data
            else:
                value, min_value, max_value = data[0], data[1], data[2]
            self.create_scale(label_text, i, value, min_value, max_value)

        self.text_frame = ttk.Frame(self.root, width=800, height=350, borderwidth=1, relief="solid")
        self.text_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nw")

        self.text_data = tk.Text(self.text_frame, wrap="word", width=100, height=20)
        self.text_data.pack(padx=10, pady=10)

        self.reports_frame = ttk.Frame(self.root, width=800, height=350, borderwidth=1, relief="solid")
        self.reports_frame.grid(row=1, column=2, padx=20, pady=20, sticky="nw")

        self.reports_listbox = tk.Listbox(self.reports_frame, width=100, height=20)
        self.reports_listbox.pack(padx=10, pady=10)
        self.reports_listbox.bind("<Double-Button-1>", self.show_report_window)

        self.update_reports_list()

        self.control_frame = ttk.Frame(self.root, width=300, height=200, borderwidth=1, relief="solid")
        self.control_frame.grid(row=1, column=1, padx=20, pady=0, sticky="nw")

        self.create_control_panel()

        # Блок 5: изменен размер в 2 раза
        self.weather_frame = ttk.Frame(self.root, width=1600, height=200, borderwidth=1, relief="solid")
        self.weather_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nw")

        self.weather_label = ttk.Label(self.weather_frame, text="Пользователь", font=("Arial", 14))
        self.weather_label.pack(pady=10)

        self.user_info = {
            "Имя": ttk.Label(self.weather_frame, text="Зубенко Михаил Петрович", font=("Arial", 12)),
            "Должность": ttk.Label(self.weather_frame, text="Оператор промежуточной станции", font=("Arial", 12))
        }

        for i, (label_text, label_widget) in enumerate(self.user_info.items()):
            label_widget.pack(pady=5)

        # Блок 2: Статус БД
        self.status_frame = ttk.Frame(self.root, width=600, height=200, borderwidth=1, relief="solid")
        self.status_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nw")

        ttk.Label(self.status_frame, text="Статус БД", font=("Arial", 14)).pack(pady=10)

        self.status_labels = []
        # All copies available, only copy 1 is active
        for i in range(1, 4):
            status_label = ttk.Label(self.status_frame, text=f"Копия {i}: Доступна, {'Активна' if i == 1 else 'Не активна'}", font=("Arial", 12))  
            status_label.pack(pady=5)
            self.status_labels.append(status_label)

        # Блок 7: Резервные копии
        self.backup_frame = ttk.Frame(self.root, width=300, height=200, borderwidth=1, relief="solid")
        self.backup_frame.grid(row=3, column=1, padx=20, pady=20, sticky="nw")

        ttk.Label(self.backup_frame, text="Резервные копии БД", font=("Arial", 14)).pack(pady=10)

        self.backup_var = tk.StringVar(value="1")
        self.backup_radios = []
        for i in range(1, 4):
            radio = ttk.Radiobutton(self.backup_frame, text=f"Копия {i}", variable=self.backup_var, value=str(i), command=self.select_backup)
            radio.pack(pady=5)
            self.backup_radios.append(radio)

        # Блок 8: Переключатели для выбора копий
        self.backup_selector_frame = ttk.Frame(self.root, width=300, height=200, borderwidth=1, relief="solid")
        self.backup_selector_frame.grid(row=2, column=1, padx=20, pady=20, sticky="nw")

        ttk.Label(self.backup_selector_frame, text="Выбор резервных копий", font=("Arial", 14)).pack(pady=10)

        # Используем одну и ту же переменную для выбора резервных копий
        self.backup_var = tk.StringVar(value="1") 
        self.backup_selector_radios = []
        for i in range(1, 4):
            radio = ttk.Radiobutton(self.backup_selector_frame, text=f"Копия {i}", variable=self.backup_var, value=str(i), command=self.select_backup)
            radio.pack(pady=5)
            self.backup_selector_radios.append(radio)

        # Label for the current product
        self.product_label = ttk.Label(self.status_frame, text=f"Нефтепродукт: {self.data['Нефтепродукт'][0]}", font=("Arial", 12))
        self.product_label.pack(pady=5)


    def create_scale(self, label_text, row, initial_value, min_value, max_value):
        label = ttk.Label(self.main_frame, text=label_text, font=("Arial", 10))
        label.grid(row=row + 1, column=0, padx=10, pady=5, sticky="w")

        scale_frame = ttk.Frame(self.main_frame, width=300, height=20)
        scale_frame.grid(row=row + 1, column=1, columnspan=3, padx=10, pady=5, sticky="ew")

        green_frame = tk.Frame(scale_frame, width=0, height=20, bg="green")
        green_frame.pack(fill='x', expand=True, side="left")

        red_frame = tk.Frame(scale_frame, width=300, height=20, bg="red")
        red_frame.pack(fill='x', expand=True, side="right")

        value_label = ttk.Label(self.main_frame, text=str(initial_value), font=("Arial", 10))
        value_label.grid(row=row + 1, column=4, padx=10, pady=5, sticky="w")

        self.scales[label_text] = (green_frame, red_frame, value_label, min_value, max_value)

    def update_data(self):
        for label_text, data in self.data.items():
            if label_text == "Скорость откачки (литры в минуту)":
                current_value = self.speed_scale.get()
            elif label_text == "Давление внутри трубопровода (Па)":
                current_value = self.pressure_scale.get()
            elif label_text == "Температура в трубопровода (°C)":
                current_value = self.temperature_scale.get()
            elif label_text == "Температура на улице (°C)":
                current_value = self.outdoor_temperature_scale.get()
            elif label_text == "Угол наклона трубопровода (градусы)":
                current_value = self.angle_scale.get()
            elif label_text == "Показания вибраций трубопровода (мм/с)":
                current_value = self.vibration_scale.get()
            elif label_text == "Давление на улице (мм рт. ст.)":
                current_value = self.outdoor_pressure_scale.get()
            elif label_text == "Нефтепродукт":
                current_value = self.data['Нефтепродукт'][0]
            else:
                current_value = getattr(self, f"{label_text}_value", data[0])

            if isinstance(current_value, (int, float)):
                step = random.uniform(-5, 5)  # Adjusted step for more realistic changes
                new_value = current_value + step
                new_value = max(data[1], min(data[2], new_value))
                setattr(self, f"{label_text}_value", new_value)
                self.update_scale(label_text, new_value)
            else:
                # For "Нефтепродукт", just update the label directly
                self.update_scale(label_text, current_value)

        self.update_text_data()

        if self.current_animation_id:
            self.root.after_cancel(self.current_animation_id)

        self.animate_indicators()

        # Планируем следующее обновление данных через 5 секунд
        self.current_animation_id = self.root.after(5000, self.update_data)

    def animate_indicators(self):
        def fade_color(canvas, start_color, end_color, duration, step=0):
            r1, g1, b1 = start_color
            r2, g2, b2 = end_color
            r = int(r1 + (r2 - r1) * step / duration)
            g = int(g1 + (g2 - g1) * step / duration)
            b = int(b1 + (b2 - b1) * step / duration)
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.config(bg=color)
            if step < duration:
                canvas.after(50, fade_color, canvas, start_color, end_color, duration, step + 1)
            else:
                canvas.after(50, fade_color, canvas, end_color, start_color, duration, 0)

        start_color = (0, 0, 0)  # Черный
        end_color = (0, 255, 0)  # Зеленый
        duration = 50  # Длительность перехода

        for line_indicators in self.indicators:
            for cell in line_indicators:
                current_color = cell.cget("bg")
                if current_color == "black":
                    fade_color(cell, start_color, end_color, duration)

        self.current_animation_id = self.root.after(5000, self.fade_out_indicators)

    def fade_out_indicators(self):
        def fade_color(canvas, start_color, end_color, duration, step=0):
            r1, g1, b1 = start_color
            r2, g2, b2 = end_color
            r = int(r1 + (r2 - r1) * step / duration)
            g = int(g1 + (g2 - g1) * step / duration)
            b = int(b1 + (b2 - b1) * step / duration)
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.config(bg=color)
            if step < duration:
                canvas.after(50, fade_color, canvas, start_color, end_color, duration, step + 1)
            else:
                canvas.after(50, fade_color, canvas, end_color, start_color, duration, 0)

        start_color = (0, 255, 0)  # Зеленый
        end_color = (0, 0, 0)  # Черный
        duration = 50  # Длительность перехода

        for line_indicators in self.indicators:
            for cell in line_indicators:
                current_color = cell.cget("bg")
                if current_color == "green":
                    fade_color(cell, start_color, end_color, duration)

        self.current_animation_id = self.root.after(5000, self.update_data)

    def update_scale(self, label_text, new_value):
        if label_text == "Нефтепродукт":  # Handle "Нефтепродукт" directly
            self.product_label.config(text=f"Нефтепродукт: {new_value}")
        else:
            green_frame, red_frame, value_label, min_value, max_value = self.scales[label_text]
            value_range = max_value - min_value
            green_width = int((new_value - min_value) / value_range * 300)
            green_frame.config(width=green_width)
            red_frame.config(width=300 - green_width)
            value_label.config(text=str(round(new_value, 2)))

    def update_text_data(self):
        text = ""
        for label_text, data in self.data.items():
            if label_text == "Нефтепродукт":
                current_value = self.data['Нефтепродукт'][0]
            else:
                current_value = getattr(self, f"{label_text}_value", data[0])
            text += f"{label_text}: {current_value}\n"
        self.text_data.delete(1.0, tk.END)
        self.text_data.insert(tk.END, text)

    def start_timer(self):
        self.update_timer()
        self.root.after(1000, self.start_timer)

    def update_timer(self):
        elapsed_time = datetime.now() - self.start_time
        hours, remainder = divmod(elapsed_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timer_label.config(text=f"Время работы: {hours:02}:{minutes:02}:{seconds:02}")

    def create_initial_reports(self):
        initial_reports = [
            "Показания вибраций трубопровода превысили норму",
            "Обнаружено утечка на участке трубопровода 3",
            "Температура в трубопроводе снизилась ниже допустимого уровня",
            "Давление внутри трубопровода превысило критические значения"
        ]

        for report_text in initial_reports:
            self.report_db.add_report(report_text)

        self.update_reports_list()

    def update_reports_list(self):
        self.reports_listbox.delete(0, tk.END)
        reports = self.report_db.get_reports_list()
        for report in reports:
            self.reports_listbox.insert(tk.END, report)

    def show_report_window(self, event):
        index = self.reports_listbox.curselection()[0]
        report = self.report_db.get_reports_list()[index]
        report_window = tk.Toplevel(self.root)
        report_window.title("Отчет")
        report_window.geometry("400x300")
        report_label = tk.Label(report_window, text=report, font=("Arial", 12), wraplength=380, justify="left")
        report_label.pack(padx=20, pady=20)

    def create_control_panel(self):
        ttk.Label(self.control_frame, text="Управление нефтепроводом", font=("Arial", 14)).pack(pady=10)

        ttk.Label(self.control_frame, text="Скорость откачки (литры в минуту)", font=("Arial", 10)).pack(pady=5)  # Add units
        self.speed_scale = ttk.Scale(self.control_frame, from_=500, to=1500, orient="horizontal",
                                    command=self.update_pumping_speed)
        self.speed_scale.pack(pady=5)

        ttk.Label(self.control_frame, text="Давление в трубопроводе (Па)", font=("Arial", 10)).pack(pady=5)
        self.pressure_scale = ttk.Scale(self.control_frame, from_=80000, to=100000, orient="horizontal", command=self.update_pipeline_pressure)
        self.pressure_scale.pack(pady=5)

        ttk.Label(self.control_frame, text="Температура в трубопроводе (°C)", font=("Arial", 10)).pack(pady=5)
        self.temperature_scale = ttk.Scale(self.control_frame, from_=40, to=80, orient="horizontal",
                                        command=self.update_pipeline_temperature)
        self.temperature_scale.pack(pady=5)

        self.toggles = []
        self.toggle_states = [False] * 4  # Начальное состояние тумблеров - выключены
        for i in range(4):
            toggle = ttk.Checkbutton(self.control_frame, text=f"Трубопровод {i+1}", command=lambda i=i: self.toggle_pipeline(i))
            toggle.pack(pady=5)
            self.toggles.append(toggle)

        self.call_maintenance_button = ttk.Button(self.control_frame, text="Вызвать ремонтную бригаду", 
                                                command=self.call_maintenance)
        self.call_maintenance_button.pack(pady=20)

    def update_pumping_speed(self, value):
        value = float(value)
        self.data["Скорость откачки (литры в минуту)"] = (value, 500, 1500)
        self.update_scale("Скорость откачки (литры в минуту)", value)

    def update_pipeline_pressure(self, value):
        value = float(value)
        self.data["Давление внутри трубопровода (Па)"] = (value, 80000, 100000)
        self.update_scale("Давление внутри трубопровода (Па)", value)

    def update_pipeline_temperature(self, value):
        value = float(value)
        self.data["Температура в трубопроводе (°C)"] = (value, 40, 80)
        self.update_scale("Температура в трубопроводе (°C)", value)

    def call_maintenance(self):
        messagebox.showinfo("Ремонтная бригада", "Ремонтная бригада скоро прибудет")
        self.reset_indicators()
        if self.broken_cell:
            self.broken_cell.config(bg="black")
            self.broken_cell.delete("circle")  # Remove circle if present
            self.broken_cell = None
        # Update database status to "Доступна" after maintenance
        self.update_db_status(force_available=True)

    def toggle_pipeline(self, pipeline_index):
        self.toggle_states[pipeline_index] = not self.toggle_states[pipeline_index]
        new_color = "green" if self.toggle_states[pipeline_index] else "red"

        for cell in self.indicators[pipeline_index]:
            cell.delete("cross")
            if new_color == "red":
                cell.create_line(0, 0, 5, 20, fill="red", width=2, tags="cross")
                cell.create_line(5, 0, 0, 20, fill="red", width=2, tags="cross")
            cell.config(bg=new_color)

    def select_backup(self):
        selected_backup = int(self.backup_var.get())
        self.update_db_status(selected_backup)

    def update_db_status(self, selected_backup=1, force_available=False):
        for i, label in enumerate(self.status_labels):
            if force_available:
                status = "Доступна"
            else:
                status = "Доступна"  # os.path.exists(f"reports_db_backup_{i+1}.pkl") else "Не доступна"
            if i + 1 == selected_backup:
                active = "Активна"
            else:
                active = "Не активна"
            label.config(text=f"Копия {i+1}: {status}, {active}")

    def create_experimental_functions(self):
        ttk.Label(self.experimental_functions_window, text="Экспериментальные функции", font=("Arial", 14)).pack(pady=10)

        # Шкала регулировки температуры на улице
        ttk.Label(self.experimental_functions_window, text="Температура на улице (°C)", font=("Arial", 10)).pack(pady=5)
        self.outdoor_temperature_scale = ttk.Scale(self.experimental_functions_window, from_=-20, to=40, orient="horizontal", command=self.update_outdoor_temperature)
        self.outdoor_temperature_scale.pack(pady=5)

        # Шкала регулировки угла наклона трубопровода
        ttk.Label(self.experimental_functions_window, text="Угол наклона трубопровода (градусы)", font=("Arial", 10)).pack(pady=5)
        self.angle_scale = ttk.Scale(self.experimental_functions_window, from_=-5, to=5, orient="horizontal", command=self.update_angle)
        self.angle_scale.pack(pady=5)

        # Шкала регулировки показаний вибрации трубопровода
        ttk.Label(self.experimental_functions_window, text="Показания вибраций трубопровода (мм/с)", font=("Arial", 10)).pack(pady=5)
        self.vibration_scale = ttk.Scale(self.experimental_functions_window, from_=0, to=10, orient="horizontal", command=self.update_vibration)
        self.vibration_scale.pack(pady=5)

        # Шкала регулировки давления на улице
        ttk.Label(self.experimental_functions_window, text="Давление на улице (мм рт. ст.)", font=("Arial", 10)).pack(pady=5)
        self.outdoor_pressure_scale = ttk.Scale(self.experimental_functions_window, from_=720, to=780, orient="horizontal", command=self.update_outdoor_pressure)
        self.outdoor_pressure_scale.pack(pady=5)

        # Кнопки поломки копий
        self.backup_break_buttons = []
        for i in range(1, 4):
            button = ttk.Button(self.experimental_functions_window, text=f"Поломка копии {i}", command=lambda i=i: self.break_backup(i))
            button.pack(pady=5)
            self.backup_break_buttons.append(button)

        # Кнопка случайной поломки
        self.random_break_button = ttk.Button(self.experimental_functions_window, text="Случайная поломка трубопровода", command=self.random_break)
        self.random_break_button.pack(pady=20)

    def update_outdoor_temperature(self, value):
        value = float(value)
        self.data["Температура на улице (°C)"] = (value, -20, 40)
        self.update_scale("Температура на улице (°C)", value)

    def update_angle(self, value):
        value = float(value)
        self.data["Угол наклона трубопровода (градусы)"] = (value, -5, 5)
        self.update_scale("Угол наклона трубопровода (градусы)", value)

    def update_vibration(self, value):
        value = float(value)
        self.data["Показания вибраций трубопровода (мм/с)"] = (value, 0, 10)
        self.update_scale("Показания вибраций трубопровода (мм/с)", value)

    def update_outdoor_pressure(self, value):
        value = float(value)
        self.data["Давление на улице (мм рт. ст.)"] = (value, 720, 780)
        self.update_scale("Давление на улице (мм рт. ст.)", value)

    def break_backup(self, copy_number):
        self.status_labels[copy_number - 1].config(text=f"Копия {copy_number}: Не доступна, Не активна")
        self.backup_radios[copy_number - 1].config(state=tk.DISABLED)
        # Keep the status of other backups unchanged
        for i in range(3):
            if i != copy_number - 1:
                self.status_labels[i].config(text=f"Копия {i+1}: Доступна, {'Активна' if i+1 == int(self.backup_var.get()) else 'Не активна'}")

    def random_break(self):
        random_line = random.randint(0, 3)
        random_cell = random.randint(0, 9)
        self.broken_cell = self.indicators[random_line][random_cell]
        self.broken_cell.config(bg="black")  # Reset color to black
        self.broken_cell.create_oval(1, 1, 4, 19, fill="yellow", outline="yellow", tags="circle")  # Add yellow circle

    def reset_indicators(self):
        for line_indicators in self.indicators:
            for cell in line_indicators:
                cell.config(bg="black")
                cell.delete("cross")  # Remove the cross if it exists
                cell.delete("circle")  # Remove the circle if it exists

    def update_product_label(self):
        """Updates the "Нефтепродукт" label every minute"""
        products = self.data['Нефтепродукт'][1]
        self.data['Нефтепродукт'] = (random.choice(products), products)
        self.product_label.config(text=f"Нефтепродукт: {self.data['Нефтепродукт'][0]}")
        self.product_label_timer = self.root.after(60000, self.update_product_label) 

def authenticate():
    auth_window = tk.Toplevel()
    auth_window.title("Аутентификация")
    auth_window.geometry("300x150")
    tk.Label(auth_window, text="Вставьте ключ-карту", font=("Arial", 12)).pack(pady=10)

    correct_key_button = ttk.Button(auth_window, text="Вставить верную ключ-карту", command=auth_window.destroy)
    correct_key_button.pack(pady=5)

    incorrect_key_button = ttk.Button(auth_window, text="Вставить неверную ключ-карту", command=lambda: messagebox.showerror("Ошибка", "Тревога! Несанкционированный доступ!"))
    incorrect_key_button.pack(pady=5)

    return auth_window

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Скрываем основное окно до прохождения аутентификации
    auth_window = authenticate()
    auth_window.wait_window()  # Ожидаем закрытия окна аутентификации
    root.after(0, root.deiconify)  # Показываем основное окно после прохождения аутентификации
    app = PipelineMonitoringApp(root)
    root.mainloop()