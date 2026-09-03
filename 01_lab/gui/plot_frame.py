"""
Виджет для отображения графика с поддержкой масштабирования
"""
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class PlotFrame(ctk.CTkFrame):
    """Фрейм с графиком и элементами управления"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Панель управления масштабом
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.controls_frame.grid_columnconfigure(4, weight=1)
        
        # Кнопки масштабирования
        self.zoom_in_btn = ctk.CTkButton(
            self.controls_frame,
            text="🔍+",
            width=40,
            command=self.zoom_in
        )
        self.zoom_in_btn.grid(row=0, column=0, padx=2)
        
        self.zoom_out_btn = ctk.CTkButton(
            self.controls_frame,
            text="🔍−",
            width=40,
            command=self.zoom_out
        )
        self.zoom_out_btn.grid(row=0, column=1, padx=2)
        
        self.reset_btn = ctk.CTkButton(
            self.controls_frame,
            text="⟲",
            width=40,
            command=self.reset_view
        )
        self.reset_btn.grid(row=0, column=2, padx=2)
        
        # Слайдер масштаба - теперь от 0.0001 до 10000 (в 10000 раз)
        self.zoom_scale = ctk.CTkSlider(
            self.controls_frame,
            from_=0.0001,
            to=10000.0,
            number_of_steps=1000,  # 1000 шагов для точной настройки
            command=self._on_zoom_slider
        )
        self.zoom_scale.set(1.0)
        self.zoom_scale.grid(row=0, column=3, padx=(10, 5), sticky="ew")
        
        # Информация о масштабе
        self.zoom_label = ctk.CTkLabel(
            self.controls_frame,
            text="1x",
            width=70
        )
        self.zoom_label.grid(row=0, column=4, padx=5)
        
        # Создание графика
        self.figure = Figure(figsize=(8, 6), dpi=100, facecolor="#1a1a2e")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#16213e")
        self.ax.grid(True, alpha=0.3, color="#ffffff")
        self.ax.axhline(y=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.axvline(x=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        
        # Настройка цветов текста
        self.ax.tick_params(colors="#ffffff")
        self.ax.xaxis.label.set_color("#ffffff")
        self.ax.yaxis.label.set_color("#ffffff")
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        
        # Настройка взаимодействия с мышью
        self._setup_interaction()
        
        # Хранение данных
        self.current_x = None
        self.current_y = None
        self.current_formula = None
        self.base_x_range = None
        self.base_y_range = None
        self.zoom_factor = 1.0
        self.is_data_plotted = False
        self.current_center_x = 0
        self.current_center_y = 0
        
        # Привязка событий мыши для панорамирования
        self._bind_mouse_events()
    
    def _setup_interaction(self):
        """Настройка интерактивности"""
        # Масштабирование колесиком мыши
        self.canvas.mpl_connect('scroll_event', self._on_scroll)
    
    def _bind_mouse_events(self):
        """Привязка событий мыши"""
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_motion)
        
        self.pan_start_x = None
        self.pan_start_y = None
        self.pan_xlim = None
        self.pan_ylim = None
        self.is_panning = False
    
    def _on_mouse_press(self, event):
        """Обработка нажатия мыши"""
        if event.inaxes != self.ax:
            return
        
        if event.button == 2 or event.button == 3:  # Middle or right click
            self.is_panning = True
            self.pan_start_x = event.xdata
            self.pan_start_y = event.ydata
            self.pan_xlim = self.ax.get_xlim()
            self.pan_ylim = self.ax.get_ylim()
    
    def _on_mouse_release(self, event):
        """Обработка отпускания мыши"""
        self.is_panning = False
        self.pan_start_x = None
        self.pan_start_y = None
    
    def _on_mouse_motion(self, event):
        """Обработка движения мыши"""
        if not self.is_panning or event.inaxes != self.ax:
            return
        
        dx = event.xdata - self.pan_start_x
        dy = event.ydata - self.pan_start_y
        
        new_xlim = (self.pan_xlim[0] - dx, self.pan_xlim[1] - dx)
        new_ylim = (self.pan_ylim[0] - dy, self.pan_ylim[1] - dy)
        
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        
        # Обновляем центр для корректного масштабирования
        self.current_center_x = (new_xlim[0] + new_xlim[1]) / 2
        self.current_center_y = (new_ylim[0] + new_ylim[1]) / 2
        
        self.canvas.draw()
    
    def _on_scroll(self, event):
        """Обработка колесика мыши с масштабированием в 10000 раз"""
        if event.inaxes != self.ax:
            return
        
        # Коэффициент масштабирования (логарифмическая шкала для плавности)
        if event.button == 'up':
            # Увеличение
            self.zoom_factor *= 1.1
            if self.zoom_factor > 10000:
                self.zoom_factor = 10000
        else:
            # Уменьшение
            self.zoom_factor /= 1.1
            if self.zoom_factor < 0.0001:
                self.zoom_factor = 0.0001
        
        # Применяем масштабирование
        self._apply_zoom(self.zoom_factor)
        
        # Обновляем слайдер и метку
        self.zoom_scale.set(self.zoom_factor)
        self._update_zoom_label()
        
        self.canvas.draw()
    
    def _apply_zoom(self, zoom_factor):
        """
        Применение масштабирования с коэффициентом zoom_factor
        zoom_factor = 1 - исходный масштаб
        zoom_factor > 1 - увеличение
        zoom_factor < 1 - уменьшение
        """
        if not self.is_data_plotted or self.base_x_range is None:
            return
        
        # Получаем текущий центр
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()
        
        # Если центр не задан, используем центр текущего вида
        if self.current_center_x is None:
            self.current_center_x = (current_xlim[0] + current_xlim[1]) / 2
        if self.current_center_y is None:
            self.current_center_y = (current_ylim[0] + current_ylim[1]) / 2
        
        # Базовые диапазоны
        base_x_range = self.base_x_range[1] - self.base_x_range[0]
        base_y_range = self.base_y_range[1] - self.base_y_range[0]
        
        # Новые диапазоны с учетом коэффициента масштабирования
        new_x_range = base_x_range / zoom_factor
        new_y_range = base_y_range / zoom_factor
        
        # Новые пределы
        new_xlim = [
            self.current_center_x - new_x_range / 2,
            self.current_center_x + new_x_range / 2
        ]
        new_ylim = [
            self.current_center_y - new_y_range / 2,
            self.current_center_y + new_y_range / 2
        ]
        
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
    
    def _update_zoom_label(self):
        """Обновление текста метки масштаба"""
        if self.zoom_factor >= 1:
            if self.zoom_factor >= 10000:
                self.zoom_label.configure(text="10000x")
            elif self.zoom_factor >= 1000:
                self.zoom_label.configure(text=f"{int(self.zoom_factor)}x")
            else:
                # Для чисел от 1 до 999 показываем с округлением
                if self.zoom_factor == int(self.zoom_factor):
                    self.zoom_label.configure(text=f"{int(self.zoom_factor)}x")
                else:
                    self.zoom_label.configure(text=f"{self.zoom_factor:.1f}x")
        else:
            # Для уменьшения показываем как дробь
            if self.zoom_factor <= 0.0001:
                self.zoom_label.configure(text="0.0001x")
            elif self.zoom_factor <= 0.001:
                self.zoom_label.configure(text=f"{self.zoom_factor:.4f}x")
            elif self.zoom_factor <= 0.01:
                self.zoom_label.configure(text=f"{self.zoom_factor:.3f}x")
            else:
                self.zoom_label.configure(text=f"{self.zoom_factor:.2f}x")
    
    def _on_zoom_slider(self, value):
        """Обработка изменения слайдера"""
        if not self.is_data_plotted or self.base_x_range is None:
            return
        
        self.zoom_factor = value
        self._apply_zoom(value)
        self._update_zoom_label()
        self.canvas.draw()
    
    def zoom_in(self):
        """Увеличение в 1.2 раза"""
        new_value = min(self.zoom_factor * 1.2, 10000.0)
        self.zoom_factor = new_value
        self.zoom_scale.set(new_value)
        self._apply_zoom(new_value)
        self._update_zoom_label()
        self.canvas.draw()
    
    def zoom_out(self):
        """Уменьшение в 1.2 раза"""
        new_value = max(self.zoom_factor / 1.2, 0.0001)
        self.zoom_factor = new_value
        self.zoom_scale.set(new_value)
        self._apply_zoom(new_value)
        self._update_zoom_label()
        self.canvas.draw()
    
    def reset_view(self):
        """Сброс вида"""
        if self.base_x_range is not None:
            self.ax.set_xlim(self.base_x_range)
            self.ax.set_ylim(self.base_y_range)
            
            # Сбрасываем центр
            self.current_center_x = (self.base_x_range[0] + self.base_x_range[1]) / 2
            self.current_center_y = (self.base_y_range[0] + self.base_y_range[1]) / 2
            
            self.zoom_factor = 1.0
            self.zoom_scale.set(1.0)
            self.zoom_label.configure(text="1x")
            self.canvas.draw()
    
    def plot_function(self, func, x_min=-10, x_max=10, formula=""):
        """Построение графика функции"""
        self.ax.clear()
        
        # Настройка внешнего вида
        self.ax.set_facecolor("#16213e")
        self.ax.grid(True, alpha=0.3, color="#ffffff")
        self.ax.axhline(y=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.axvline(x=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.tick_params(colors="#ffffff")
        
        # Генерация точек с высоким разрешением для детального отображения
        # При большом увеличении нужно больше точек
        x = np.linspace(x_min, x_max, 10000)
        y = np.array([func(xi) for xi in x])
        
        # Построение графика
        line, = self.ax.plot(x, y, color="#00d4ff", linewidth=2, label=formula)
        self.ax.set_xlabel("x", color="#ffffff")
        self.ax.set_ylabel("y", color="#ffffff")
        
        if formula:
            self.ax.legend(loc="upper right", facecolor="#1a1a2e", edgecolor="#ffffff")
        
        # Установка диапазонов
        y_min, y_max = self._get_good_y_range(y, x_min, x_max)
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        
        self.base_x_range = (x_min, x_max)
        self.base_y_range = (y_min, y_max)
        self.is_data_plotted = True
        
        # Сохраняем центр
        self.current_center_x = (x_min + x_max) / 2
        self.current_center_y = (y_min + y_max) / 2
        
        self.zoom_factor = 1.0
        self.zoom_scale.set(1.0)
        self.zoom_label.configure(text="1x")
        
        self.canvas.draw()
    
    def _get_good_y_range(self, y, x_min, x_max):
        """Получение хорошего диапазона для Y с учетом масштаба"""
        y_min = np.min(y)
        y_max = np.max(y)
        
        # Добавляем отступы
        y_range = y_max - y_min
        if y_range == 0:
            y_range = 1
        
        margin = max(abs(y_range) * 0.1, 0.1)
        return (y_min - margin, y_max + margin)
    
    def plot_data(self, x_data, y_data, filename=""):
        """Построение графика по точкам"""
        self.ax.clear()
        
        # Настройка внешнего вида
        self.ax.set_facecolor("#16213e")
        self.ax.grid(True, alpha=0.3, color="#ffffff")
        self.ax.axhline(y=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.axvline(x=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.tick_params(colors="#ffffff")
        
        # Интерполяция для плавного графика
        if len(x_data) > 2:
            x_smooth = np.linspace(min(x_data), max(x_data), 10000)
            try:
                from scipy.interpolate import CubicSpline
                cs = CubicSpline(x_data, y_data)
                y_smooth = cs(x_smooth)
                self.ax.plot(x_smooth, y_smooth, color="#00d4ff", linewidth=2, alpha=0.7)
            except:
                # Если scipy нет, используем линейную интерполяцию
                self.ax.plot(x_data, y_data, color="#00d4ff", linewidth=2, alpha=0.7)
        else:
            # Если точек мало, просто соединяем их линией
            self.ax.plot(x_data, y_data, color="#00d4ff", linewidth=2, alpha=0.7)
        
        # Точки
        self.ax.scatter(x_data, y_data, color="#ff6b6b", s=50, zorder=5, label="Данные")
        self.ax.set_xlabel("x", color="#ffffff")
        self.ax.set_ylabel("y", color="#ffffff")
        
        if filename:
            self.ax.legend(loc="upper right", facecolor="#1a1a2e", edgecolor="#ffffff")
        
        # Установка диапазонов
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)
        
        x_margin = max((x_max - x_min) * 0.1, 0.5)
        y_margin = max((y_max - y_min) * 0.1, 0.5)
        
        self.ax.set_xlim(x_min - x_margin, x_max + x_margin)
        self.ax.set_ylim(y_min - y_margin, y_max + y_margin)
        
        self.base_x_range = (x_min - x_margin, x_max + x_margin)
        self.base_y_range = (y_min - y_margin, y_max + y_margin)
        self.is_data_plotted = True
        
        # Сохраняем центр
        self.current_center_x = (self.base_x_range[0] + self.base_x_range[1]) / 2
        self.current_center_y = (self.base_y_range[0] + self.base_y_range[1]) / 2
        
        self.zoom_factor = 1.0
        self.zoom_scale.set(1.0)
        self.zoom_label.configure(text="1x")
        
        self.canvas.draw()
    
    def clear(self):
        """Очистка графика"""
        self.ax.clear()
        self.ax.set_facecolor("#16213e")
        self.ax.grid(True, alpha=0.3, color="#ffffff")
        self.ax.axhline(y=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.axvline(x=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.tick_params(colors="#ffffff")
        self.ax.set_xlabel("x", color="#ffffff")
        self.ax.set_ylabel("y", color="#ffffff")
        
        self.base_x_range = None
        self.base_y_range = None
        self.is_data_plotted = False
        self.current_center_x = 0
        self.current_center_y = 0
        self.zoom_factor = 1.0
        self.zoom_scale.set(1.0)
        self.zoom_label.configure(text="1x")
        
        self.canvas.draw()