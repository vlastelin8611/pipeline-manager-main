import tkinter as tk  # импортирую модуль tkinter для создания графического интерфейса, сокращаю название до tk
from tkinter import ttk, messagebox  # импортирую дополнительные компоненты tkinter:
# ttk - современные виджеты с улучшенным дизайном
# messagebox - для показа всплывающих сообщений пользователю
import sqlite3  # импортирую модуль sqlite3 для работы с базой данных SQLite
import time  # импортирую модуль time для работы со временем (паузы, измерения)
import os  # импортирую модуль os для работы с файлами и папками
from datetime import datetime  # импортирую класс datetime для работы с датой и временем

class Module5(tk.Frame):  # создаю класс Module5, который наследуется от tk.Frame (контейнер для виджетов)
    def __init__(self, parent, app=None):  # конструктор класса, принимает родительский виджет и ссылку на приложение
        """Инициализация модуля 5 - панель управления нефтепроводом."""  # описание назначения этого класса
        super().__init__(parent, bg="white")  # вызываю конструктор родительского класса с белым фоном
        self.parent = parent  # сохраняю ссылку на родительский виджет
        self.app = app  # сохраняю ссылку на основное приложение
        
        # Размер модуля будет адаптироваться под размер окна
        self.pack(fill="both", expand=True)  # размещаю модуль, заполняя всю доступную область и позволяя расширяться
        
        # Находим ссылку на основное приложение, если не передана
        if self.app is None:  # если ссылка на приложение не была передана
            self.find_app_reference()  # ищу ссылку на основное приложение
        
        # Переменные состояния системы
        self.pressure_setpoint = 55.0  # Заданное давление (МПа)  # устанавливаю целевое значение давления 55.0 мегапаскалей
        self.pumping_speed_setpoint = 5.0  # Заданная скорость откачки (м/с)  # устанавливаю целевую скорость откачки 5.0 метров в секунду
        self.temperature_setpoint = 20.0  # Заданная температура (°C)  # устанавливаю целевую температуру 20.0 градусов Цельсия
        
        # Состояние линий (True = включена, False = отключена)
        self.line_states = {  # создаю словарь для хранения состояния каждой линии нефтепровода
            1: True,  # линия 1 включена (True означает работает)
            2: True,  # линия 2 включена
            3: True,  # линия 3 включена
            4: True   # линия 4 включена
        }
        
        # Переменные для слайдеров
        self.pressure_var = tk.DoubleVar(value=self.pressure_setpoint)  # создаю переменную для слайдера давления, связанную с tkinter
        self.pumping_var = tk.DoubleVar(value=self.pumping_speed_setpoint)  # создаю переменную для слайдера скорости откачки
        self.temperature_var = tk.DoubleVar(value=self.temperature_setpoint)  # создаю переменную для слайдера температуры
        
        # Создание интерфейса
        self.setup_ui()  # вызываю метод для создания пользовательского интерфейса
        
        # Обновляем интерфейс каждые 2 секунды
        self.after(2000, self.update_interface)  # запускаю автоматическое обновление интерфейса через 2000 миллисекунд (2 секунды)
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Основной заголовок
        title_frame = tk.Frame(self, bg="white")
        title_frame.pack(fill="x", pady=5)
        
        title_label = tk.Label(title_frame, text="ПАНЕЛЬ УПРАВЛЕНИЯ НЕФТЕПРОВОДОМ", 
                             font=("Arial", 14, "bold"), bg="white", fg="darkblue")
        title_label.pack()
        
        # Создаем основную область с прокруткой
        main_canvas = tk.Canvas(self, bg="white")
        scrollbar = tk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Секция управления параметрами
        self.create_parameters_section(scrollable_frame)
        
        # Секция управления линиями
        self.create_lines_section(scrollable_frame)
        
        # Секция аварийного управления
        self.create_emergency_section(scrollable_frame)
        
        # Секция состояния системы
        self.create_status_section(scrollable_frame)
        
    def create_parameters_section(self, parent):
        """Создает секцию управления параметрами."""
        # Рамка для управления параметрами
        params_frame = tk.LabelFrame(parent, text="УПРАВЛЕНИЕ ПАРАМЕТРАМИ", 
                                   font=("Arial", 12, "bold"), bg="white", fg="darkgreen")
        params_frame.pack(fill="x", padx=10, pady=5)
        
        # Управление давлением
        pressure_frame = tk.Frame(params_frame, bg="white")
        pressure_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(pressure_frame, text="Давление в трубопроводе (МПа):", 
                font=("Arial", 10, "bold"), bg="white").pack(anchor="w")
        
        pressure_control_frame = tk.Frame(pressure_frame, bg="white")
        pressure_control_frame.pack(fill="x", pady=2)
        
        self.pressure_scale = tk.Scale(pressure_control_frame, from_=40.0, to=60.0, 
                                     resolution=0.1, orient="horizontal", 
                                     variable=self.pressure_var, bg="lightblue",
                                     command=self.on_pressure_change)
        self.pressure_scale.pack(side="left", fill="x", expand=True)
        
        self.pressure_label = tk.Label(pressure_control_frame, text=f"{self.pressure_setpoint} МПа", 
                                     font=("Arial", 10, "bold"), bg="white", fg="blue", width=10)
        self.pressure_label.pack(side="right", padx=5)
        
        # Управление скоростью откачки
        pumping_frame = tk.Frame(params_frame, bg="white")
        pumping_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(pumping_frame, text="Скорость откачки (м/с):", 
                font=("Arial", 10, "bold"), bg="white").pack(anchor="w")
        
        pumping_control_frame = tk.Frame(pumping_frame, bg="white")
        pumping_control_frame.pack(fill="x", pady=2)
        
        self.pumping_scale = tk.Scale(pumping_control_frame, from_=3.0, to=7.0, 
                                    resolution=0.1, orient="horizontal",
                                    variable=self.pumping_var, bg="lightgreen",
                                    command=self.on_pumping_change)
        self.pumping_scale.pack(side="left", fill="x", expand=True)
        
        self.pumping_label = tk.Label(pumping_control_frame, text=f"{self.pumping_speed_setpoint} м/с", 
                                    font=("Arial", 10, "bold"), bg="white", fg="green", width=10)
        self.pumping_label.pack(side="right", padx=5)
        
        # Управление температурой
        temp_frame = tk.Frame(params_frame, bg="white")
        temp_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(temp_frame, text="Температура в трубопроводе (°C):", 
                font=("Arial", 10, "bold"), bg="white").pack(anchor="w")
        
        temp_control_frame = tk.Frame(temp_frame, bg="white")
        temp_control_frame.pack(fill="x", pady=2)
        
        self.temperature_scale = tk.Scale(temp_control_frame, from_=15.0, to=25.0, 
                                        resolution=0.1, orient="horizontal",
                                        variable=self.temperature_var, bg="lightyellow",
                                        command=self.on_temperature_change)
        self.temperature_scale.pack(side="left", fill="x", expand=True)
        
        self.temperature_label = tk.Label(temp_control_frame, text=f"{self.temperature_setpoint} °C", 
                                        font=("Arial", 10, "bold"), bg="white", fg="red", width=10)
        self.temperature_label.pack(side="right", padx=5)
        
    def create_lines_section(self, parent):
        """Создает секцию управления линиями."""
        # Рамка для управления линиями
        lines_frame = tk.LabelFrame(parent, text="УПРАВЛЕНИЕ ЛИНИЯМИ НЕФТЕПРОВОДА", 
                                  font=("Arial", 12, "bold"), bg="white", fg="darkred")
        lines_frame.pack(fill="x", padx=10, pady=5)
        
        # Информация о линиях
        info_frame = tk.Frame(lines_frame, bg="white")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(info_frame, text="Каждая линия содержит 10 ячеек нефтепровода (всего 40 ячеек)", 
                font=("Arial", 9), bg="white", fg="gray").pack()
        
        # Создаем кнопки управления линиями в сетке 2x2
        buttons_frame = tk.Frame(lines_frame, bg="white")
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        self.line_buttons = {}
        self.line_indicators = {}
        
        for i in range(4):
            line_num = i + 1
            row = i // 2
            col = i % 2
            
            # Фрейм для каждой кнопки с индикатором
            line_frame = tk.Frame(buttons_frame, bg="white", relief="ridge", bd=2)
            line_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # Индикатор состояния линии
            indicator = tk.Canvas(line_frame, width=20, height=20, bg="green", 
                                bd=0, highlightthickness=0)
            indicator.pack(side="left", padx=5, pady=5)
            self.line_indicators[line_num] = indicator
            
            # Кнопка управления линией
            button_text = f"Линия {line_num}: ВКЛ"
            button = tk.Button(line_frame, text=button_text, 
                             font=("Arial", 10, "bold"), width=15,
                             bg="lightgreen", activebackground="green",
                             command=lambda ln=line_num: self.toggle_line(ln))
            button.pack(side="left", padx=5, pady=5)
            self.line_buttons[line_num] = button
        
        # Настраиваем равномерное распределение колонок
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
    def create_emergency_section(self, parent):
        """Создает секцию аварийного управления."""
        # Рамка для аварийного управления
        emergency_frame = tk.LabelFrame(parent, text="АВАРИЙНОЕ УПРАВЛЕНИЕ", 
                                      font=("Arial", 12, "bold"), bg="white", fg="red")
        emergency_frame.pack(fill="x", padx=10, pady=5)
        
        # Кнопка вызова ремонтной бригады
        repair_frame = tk.Frame(emergency_frame, bg="white")
        repair_frame.pack(fill="x", padx=10, pady=10)
        
        self.repair_button = tk.Button(repair_frame, text="🔧 ВЫЗВАТЬ РЕМОНТНУЮ БРИГАДУ", 
                                     font=("Arial", 12, "bold"), bg="red", fg="white",
                                     activebackground="darkred", activeforeground="white",
                                     command=self.call_repair_team, height=2)
        self.repair_button.pack(fill="x")
        
        # Статус последнего вызова
        self.last_call_label = tk.Label(emergency_frame, text="Ремонтные бригады не вызывались", 
                                      font=("Arial", 9), bg="white", fg="gray")
        self.last_call_label.pack(pady=5)
        
    def create_status_section(self, parent):
        """Создает секцию состояния системы."""
        # Рамка для состояния системы
        status_frame = tk.LabelFrame(parent, text="СОСТОЯНИЕ СИСТЕМЫ", 
                                   font=("Arial", 12, "bold"), bg="white", fg="purple")
        status_frame.pack(fill="x", padx=10, pady=5)
        
        # Общий статус
        self.system_status_label = tk.Label(status_frame, text="Система функционирует в штатном режиме", 
                                          font=("Arial", 11, "bold"), bg="white", fg="green")
        self.system_status_label.pack(pady=5)
        
        # Детальная информация
        details_frame = tk.Frame(status_frame, bg="white")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        # Левая колонка
        left_frame = tk.Frame(details_frame, bg="white")
        left_frame.pack(side="left", fill="both", expand=True)
        
        self.active_lines_label = tk.Label(left_frame, text="Активные линии: 4/4", 
                                         font=("Arial", 10), bg="white")
        self.active_lines_label.pack(anchor="w")
        
        self.active_cells_label = tk.Label(left_frame, text="Активные ячейки: 40/40", 
                                         font=("Arial", 10), bg="white")
        self.active_cells_label.pack(anchor="w")
        
        # Правая колонка
        right_frame = tk.Frame(details_frame, bg="white")
        right_frame.pack(side="right", fill="both", expand=True)
        
        self.control_mode_label = tk.Label(right_frame, text="Режим: Автоматический", 
                                         font=("Arial", 10), bg="white")
        self.control_mode_label.pack(anchor="e")
        
        self.last_update_label = tk.Label(right_frame, text="Обновлено: --:--:--", 
                                        font=("Arial", 10), bg="white", fg="gray")
        self.last_update_label.pack(anchor="e")
        
    def on_pressure_change(self, value):
        """Обработчик изменения давления."""
        self.pressure_setpoint = float(value)
        self.pressure_label.config(text=f"{self.pressure_setpoint:.1f} МПа")
        self.apply_pressure_control()
        
    def on_pumping_change(self, value):
        """Обработчик изменения скорости откачки."""
        self.pumping_speed_setpoint = float(value)
        self.pumping_label.config(text=f"{self.pumping_speed_setpoint:.1f} м/с")
        self.apply_pumping_control()
        
    def on_temperature_change(self, value):
        """Обработчик изменения температуры."""
        self.temperature_setpoint = float(value)
        self.temperature_label.config(text=f"{self.temperature_setpoint:.1f} °C")
        self.apply_temperature_control()
        
    def apply_pressure_control(self):
        """Применяет управление давлением."""
        try:
            # Здесь должна быть логика управления давлением
            # Пока просто логируем изменение
            print(f"Module5: Установка давления на {self.pressure_setpoint:.1f} МПа")
            
            # Обновляем данные в БД, если возможно
            self.update_control_parameters()
            
        except Exception as e:
            print(f"Module5: Ошибка управления давлением: {e}")
            
    def apply_pumping_control(self):
        """Применяет управление скоростью откачки."""
        try:
            # Здесь должна быть логика управления насосами
            print(f"Module5: Установка скорости откачки на {self.pumping_speed_setpoint:.1f} м/с")
            
            # Обновляем данные в БД, если возможно
            self.update_control_parameters()
            
        except Exception as e:
            print(f"Module5: Ошибка управления скоростью откачки: {e}")
            
    def apply_temperature_control(self):
        """Применяет управление температурой."""
        try:
            # Здесь должна быть логика управления температурой
            print(f"Module5: Установка температуры на {self.temperature_setpoint:.1f} °C")
            
            # Обновляем данные в БД, если возможно
            self.update_control_parameters()
            
        except Exception as e:
            print(f"Module5: Ошибка управления температурой: {e}")
            
    def toggle_line(self, line_number):
        """Переключает состояние линии."""
        current_state = self.line_states[line_number]
        new_state = not current_state
        self.line_states[line_number] = new_state
        
        # Обновляем интерфейс кнопки
        button = self.line_buttons[line_number]
        indicator = self.line_indicators[line_number]
        
        if new_state:
            # Линия включена
            button.config(text=f"Линия {line_number}: ВКЛ", bg="lightgreen")
            indicator.config(bg="green")
            print(f"Module5: Линия {line_number} ВКЛЮЧЕНА")
        else:
            # Линия отключена
            button.config(text=f"Линия {line_number}: ОТКЛ", bg="orange")
            indicator.config(bg="orange")
            print(f"Module5: Линия {line_number} ОТКЛЮЧЕНА")
        
        # Обновляем ячейки в модуле 1
        self.update_line_cells(line_number, new_state)
        
        # Обновляем общий статус
        self.update_system_status()
        
    def update_line_cells(self, line_number, is_active):
        """Обновляет цвет ячеек в модуле 1 для указанной линии."""
        try:
            if self.app and hasattr(self.app, 'module1') and self.app.module1:
                module1 = self.app.module1
                
                # Рассчитываем индексы ячеек для линии
                # Линия 1: ячейки 0-9, Линия 2: ячейки 10-19, и т.д.
                start_index = (line_number - 1) * 10
                end_index = start_index + 9
                
                # Обновляем цвет ячеек
                for i in range(start_index, end_index + 1):
                    if i < len(module1.cell_indicators):
                        cell = module1.cell_indicators[i]
                        if is_active:
                            # Линия включена - возвращаем нормальный цвет (будет установлен при обновлении данных)
                            # Пока ставим серый, цвет обновится при следующем обновлении данных
                            cell.config(bg="gray")
                        else:
                            # Линия отключена - ставим оранжевый (приоритет выше других цветов)
                            cell.config(bg="orange")
                
                print(f"Module5: Обновлены ячейки {start_index}-{end_index} для линии {line_number}")
                
        except Exception as e:
            print(f"Module5: Ошибка обновления ячеек линии {line_number}: {e}")
            
    def call_repair_team(self):
        """Вызывает ремонтную бригаду."""
        try:
            # Показываем сообщение пользователю
            messagebox.showinfo("Вызов ремонтной бригады", 
                              "Отправлен вызов ремонтной бригаде!\nОжидайте звонка.")
            
            # Логируем вызов
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Module5: Вызов ремонтной бригады в {current_time}")
            
            # Обновляем статус
            self.last_call_label.config(text=f"Последний вызов: {current_time}")
            
            # Отправляем сообщение через шлюз (заготовка для Kafka)
            self.send_repair_notification(current_time)
            
        except Exception as e:
            print(f"Module5: Ошибка вызова ремонтной бригады: {e}")
            messagebox.showerror("Ошибка", f"Не удалось вызвать ремонтную бригаду: {e}")
            
    def send_repair_notification(self, timestamp):
        """Шлюз для отправки уведомления о вызове ремонта (заготовка для Kafka)."""
        try:
            # Формируем сообщение
            message = {
                "type": "repair_call",
                "timestamp": timestamp,
                "system_id": "nefteprovod_monitoring",
                "priority": "high",
                "description": "Вызов ремонтной бригады через панель управления"
            }
            
            # ЗАГОТОВКА ДЛЯ KAFKA - здесь будет отправка через Kafka
            # Пока просто логируем
            print(f"Module5: [KAFKA_GATEWAY] Сообщение готово к отправке: {message}")
            
            # TODO: Интеграция с Kafka
            # kafka_producer.send('repair_notifications', message)
            
            return True
            
        except Exception as e:
            print(f"Module5: Ошибка отправки уведомления: {e}")
            return False
            
    def update_control_parameters(self):
        """Обновляет параметры управления в базе данных."""
        try:
            if self.app and hasattr(self.app, 'get_db_connection'):
                conn = self.app.get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    
                    # Обновляем параметры в БД (в таблице raw_data)
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("""
                        UPDATE raw_data 
                        SET cell_pressure = ?, 
                            cell_pumping_speed = ?, 
                            cell_temperature = ?,
                            timestamp = ?
                        WHERE id = (SELECT MAX(id) FROM raw_data)
                    """, (self.pressure_setpoint, self.pumping_speed_setpoint, 
                          self.temperature_setpoint, current_time))
                    
                    conn.commit()
                    print(f"Module5: Параметры управления обновлены в БД")
                    
        except Exception as e:
            print(f"Module5: Ошибка обновления параметров в БД: {e}")
            
    def update_system_status(self):
        """Обновляет общий статус системы."""
        try:
            # Подсчитываем активные линии
            active_lines = sum(1 for state in self.line_states.values() if state)
            total_lines = len(self.line_states)
            
            # Подсчитываем активные ячейки
            active_cells = active_lines * 10
            total_cells = total_lines * 10
            
            # Обновляем метки
            self.active_lines_label.config(text=f"Активные линии: {active_lines}/{total_lines}")
            self.active_cells_label.config(text=f"Активные ячейки: {active_cells}/{total_cells}")
            
            # Обновляем общий статус
            if active_lines == total_lines:
                status_text = "Система функционирует в штатном режиме"
                status_color = "green"
            elif active_lines > 0:
                status_text = f"Внимание: {total_lines - active_lines} линий отключено"
                status_color = "orange"
            else:
                status_text = "КРИТИЧНО: Все линии отключены!"
                status_color = "red"
                
            self.system_status_label.config(text=status_text, fg=status_color)
            
        except Exception as e:
            print(f"Module5: Ошибка обновления статуса системы: {e}")
            
    def update_interface(self):
        """Периодическое обновление интерфейса."""
        try:
            # Обновляем время последнего обновления
            current_time = time.strftime("%H:%M:%S")
            self.last_update_label.config(text=f"Обновлено: {current_time}")
            
            # Планируем следующее обновление
            self.after(2000, self.update_interface)
            
        except Exception as e:
            print(f"Module5: Ошибка обновления интерфейса: {e}")
            
    def get_line_states_for_report(self):
        """Возвращает состояние линий для отчетов."""
        return {
            "line_1": "Активна" if self.line_states[1] else "Отключена",
            "line_2": "Активна" if self.line_states[2] else "Отключена", 
            "line_3": "Активна" if self.line_states[3] else "Отключена",
            "line_4": "Активна" if self.line_states[4] else "Отключена",
            "active_lines_count": sum(1 for state in self.line_states.values() if state),
            "total_lines_count": len(self.line_states)
        }
        
    def get_control_parameters_for_report(self):
        """Возвращает параметры управления для отчетов."""
        return {
            "pressure_setpoint": self.pressure_setpoint,
            "pumping_speed_setpoint": self.pumping_speed_setpoint,
            "temperature_setpoint": self.temperature_setpoint
        }
        
    def find_app_reference(self):
        """Поиск ссылки на главное приложение."""
        try:
            # Навигация вверх по иерархии виджетов для поиска главного приложения
            widget = self.parent
            while widget:
                # Проверяем является ли виджет корневым окном
                if isinstance(widget, tk.Tk):
                    self.app = widget
                    return True
                # Пробуем получить родительский виджет
                if hasattr(widget, 'master'):
                    widget = widget.master
                else:
                    break
            
            return False
        except Exception as e:
            print(f"Module5: Ошибка при поиске главного приложения: {e}")
            return False