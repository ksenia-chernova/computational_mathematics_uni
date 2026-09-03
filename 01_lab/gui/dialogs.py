"""
Диалоговые окна для ввода данных
"""
import customtkinter as ctk


class InputDialog(ctk.CTkToplevel):
    """Диалог для ввода формулы"""
    
    def __init__(self, master, title="Ввод функции"):
        super().__init__(master)
        
        self.title(title)
        self.geometry("400x250")
        self.resizable(False, False)
        
        # Переменные
        self.result = None
        
        # Расположение по центру
        self.transient(master)
        self.grab_set()
        
        # Создание виджетов
        self._create_widgets()
        
    def _create_widgets(self):
        """Создание виджетов"""
        # Основной фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Подсказка
        hint_label = ctk.CTkLabel(
            main_frame,
            text="Введите функцию в виде f(x)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        hint_label.pack(pady=(0, 5))
        
        # Примеры
        examples_label = ctk.CTkLabel(
            main_frame,
            text="Примеры: sin(x), cos(x), x**2, exp(x), log(x)",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        examples_label.pack(pady=(0, 10))
        
        # Поле ввода
        self.formula_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="например: sin(x)",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.formula_entry.pack(pady=(0, 15))
        self.formula_entry.bind("<Return>", lambda e: self._on_ok())
        
        # Рамка для диапазона
        range_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        range_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(range_frame, text="Диапазон x:").pack(side="left", padx=(0, 10))
        
        self.x_min_entry = ctk.CTkEntry(range_frame, width=60, placeholder_text="-10")
        self.x_min_entry.pack(side="left", padx=2)
        self.x_min_entry.insert(0, "-10")
        
        ctk.CTkLabel(range_frame, text="до").pack(side="left", padx=5)
        
        self.x_max_entry = ctk.CTkEntry(range_frame, width=60, placeholder_text="10")
        self.x_max_entry.pack(side="left", padx=2)
        self.x_max_entry.insert(0, "10")
        
        # Кнопки
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(15, 0))
        
        ok_btn = ctk.CTkButton(
            button_frame,
            text="Построить",
            command=self._on_ok,
            width=100
        )
        ok_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=self._on_cancel,
            width=100,
            fg_color="#555555",
            hover_color="#444444"
        )
        cancel_btn.pack(side="left", padx=5)
        
        # Фокус на поле ввода
        self.after(100, lambda: self.formula_entry.focus_set())
    
    def _on_ok(self):
        """Обработка нажатия OK"""
        formula = self.formula_entry.get().strip()
        if not formula:
            return
        
        try:
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
            
            if x_min >= x_max:
                raise ValueError("x_min должно быть меньше x_max")
            
            self.result = (formula, x_min, x_max)
            self.destroy()
            
        except ValueError as e:
            # Ошибка уже будет обработана в главном окне
            self.result = (formula, -10, 10)
            self.destroy()
    
    def _on_cancel(self):
        """Обработка отмены"""
        self.result = None
        self.destroy()