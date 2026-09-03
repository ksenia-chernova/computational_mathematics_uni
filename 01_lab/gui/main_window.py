"""
Главное окно приложения
"""
import customtkinter as ctk
from tkinter import messagebox
from gui.plot_frame import PlotFrame
from gui.dialogs import InputDialog
from core.data_loader import load_from_file
from core.function_parser import parse_function


class MainWindow(ctk.CTk):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        self.title("Визуализация данных - Лабораторная работа №1")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Переменные состояния
        self.current_function = None
        self.current_data = None
        self.is_table_data = False
        
        # Создание интерфейса
        self._create_widgets()
        
    def _create_widgets(self):
        """Создание виджетов интерфейса"""
        # Основной контейнер
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Левая панель с кнопками
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Управление", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Кнопка: Ввод по формуле
        self.formula_btn = ctk.CTkButton(
            self.sidebar,
            text="📐 По формуле",
            command=self._input_formula,
            height=40
        )
        self.formula_btn.grid(row=1, column=0, padx=20, pady=5)
        
        # Кнопка: Загрузка из файла
        self.file_btn = ctk.CTkButton(
            self.sidebar,
            text="📂 Из файла",
            command=self._load_from_file,
            height=40
        )
        self.file_btn.grid(row=2, column=0, padx=20, pady=5)
        
        # Кнопка: Сбросить масштаб
        self.reset_zoom_btn = ctk.CTkButton(
            self.sidebar,
            text="🔄 Сбросить масштаб",
            command=self._reset_zoom,
            height=40
        )
        self.reset_zoom_btn.grid(row=3, column=0, padx=20, pady=5)
        
        # Кнопка: Очистить график
        self.clear_btn = ctk.CTkButton(
            self.sidebar,
            text="🗑 Очистить график",
            command=self._clear_plot,
            height=40
        )
        self.clear_btn.grid(row=4, column=0, padx=20, pady=5)
        
        # Информационная метка
        self.info_label = ctk.CTkLabel(
            self.sidebar,
            text="Готов к работе",
            font=ctk.CTkFont(size=12),
            wraplength=180
        )
        self.info_label.grid(row=5, column=0, padx=20, pady=20)
        
        # Правая область - виджет с графиком
        self.plot_frame = PlotFrame(self)
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
    def _input_formula(self):
        """Открытие диалога для ввода формулы"""
        dialog = InputDialog(self, title="Ввод аналитической функции")
        self.wait_window(dialog)
        
        if dialog.result:
            formula, x_min, x_max = dialog.result
            try:
                # Проверка парсинга
                func = parse_function(formula)
                # Проверка на точках
                test_x = [0.0, 1.0, 2.0]
                for x in test_x:
                    if x_min <= x <= x_max:
                        func(x)
                
                self.current_function = func
                self.current_data = None
                self.is_table_data = False
                
                # Отрисовка графика
                self.plot_frame.plot_function(
                    func, 
                    x_min=x_min, 
                    x_max=x_max,
                    formula=formula
                )
                self.info_label.configure(
                    text=f"Функция: {formula}\nДиапазон: [{x_min}, {x_max}]"
                )
                
            except Exception as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Не удалось построить график функции:\n{str(e)}"
                )
    
    def _load_from_file(self):
        """Загрузка данных из файла"""
        from tkinter import filedialog
        import os
        
        file_path = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            x_data, y_data = load_from_file(file_path)
            
            if len(x_data) < 2:
                raise ValueError("Недостаточно точек для построения графика")
            
            self.current_data = (x_data, y_data)
            self.current_function = None
            self.is_table_data = True
            
            # Отрисовка графика
            self.plot_frame.plot_data(x_data, y_data, filename=os.path.basename(file_path))
            self.info_label.configure(
                text=f"Данные из файла: {os.path.basename(file_path)}\nТочек: {len(x_data)}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить данные из файла:\n{str(e)}"
            )
    
    def _reset_zoom(self):
        """Сброс масштаба до начального"""
        if self.is_table_data and self.current_data:
            x_data, y_data = self.current_data
            self.plot_frame.plot_data(x_data, y_data)
        elif self.current_function:
            # Восстанавливаем последний диапазон
            # (сохраняем его в plot_frame)
            pass
        self.plot_frame.reset_view()
    
    def _clear_plot(self):
        """Очистка графика"""
        self.plot_frame.clear()
        self.current_function = None
        self.current_data = None
        self.is_table_data = False
        self.info_label.configure(text="Готов к работе")