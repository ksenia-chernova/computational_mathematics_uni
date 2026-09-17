"""
Виджет для отображения графика с поддержкой масштабирования,
полосами прокрутки и обработкой точек разрыва
"""
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math

from core.function_parser import evaluate_safe, detect_discontinuities


class PlotFrame(ctk.CTkFrame):
    """Фрейм с графиком и элементами управления"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ---------- Панель управления масштабом ----------
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.controls_frame.grid_columnconfigure(4, weight=1)

        self.zoom_in_btn = ctk.CTkButton(
            self.controls_frame, text="🔍+", width=40, command=self.zoom_in
        )
        self.zoom_in_btn.grid(row=0, column=0, padx=2)

        self.zoom_out_btn = ctk.CTkButton(
            self.controls_frame, text="🔍−", width=40, command=self.zoom_out
        )
        self.zoom_out_btn.grid(row=0, column=1, padx=2)

        self.reset_btn = ctk.CTkButton(
            self.controls_frame, text="⟲", width=40, command=self.reset_view
        )
        self.reset_btn.grid(row=0, column=2, padx=2)

        self.zoom_scale = ctk.CTkSlider(
            self.controls_frame,
            from_=0.0001,
            to=10000.0,
            number_of_steps=1000,
            command=self._on_zoom_slider,
        )
        self.zoom_scale.set(1.0)
        self.zoom_scale.grid(row=0, column=3, padx=(10, 5), sticky="ew")

        self.zoom_label = ctk.CTkLabel(self.controls_frame, text="1x", width=70)
        self.zoom_label.grid(row=0, column=4, padx=5)

        # ---------- Контейнер для графика и скроллбаров ----------
        self.plot_container = ctk.CTkFrame(self)
        self.plot_container.grid(row=1, column=0, sticky="nsew")
        self.plot_container.grid_rowconfigure(0, weight=1)
        self.plot_container.grid_columnconfigure(0, weight=1)

        # ---------- Создание графика matplotlib ----------
        self.figure = Figure(figsize=(8, 6), dpi=100, facecolor="#1a1a2e")
        self.ax = self.figure.add_subplot(111)          # ← ВОТ ОНА, наша ось
        self.ax.set_facecolor("#16213e")
        self.ax.grid(True, alpha=0.3, color="#ffffff")
        self.ax.axhline(y=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.axvline(x=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.tick_params(colors="#ffffff")
        self.ax.xaxis.label.set_color("#ffffff")
        self.ax.yaxis.label.set_color("#ffffff")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_container)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # ---------- Скроллбары ----------
        self.v_scrollbar = ctk.CTkScrollbar(
            self.plot_container, orientation="vertical", command=self._on_vscroll
        )
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.h_scrollbar = ctk.CTkScrollbar(
            self.plot_container, orientation="horizontal", command=self._on_hscroll
        )
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # ---------- Состояние ----------
        self.current_func = None
        self.current_formula = None
        self.base_x_range = None
        self.base_y_range = None
        self.full_x_range = None
        self.full_y_range = None
        self.zoom_factor = 1.0
        self.is_data_plotted = False
        self.current_center_x = 0
        self.current_center_y = 0
        self.scroll_position_x = 0.5
        self.scroll_position_y = 0.5

        # Порог для разрывов и количество точек
        self.jump_threshold = 1e6
        self.num_points = 10000

        # ---------- Привязки событий мыши ----------
        self.canvas.mpl_connect("scroll_event", self._on_scroll)
        self.canvas.mpl_connect("button_press_event", self._on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self._on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_motion)

        self.pan_start_x = None
        self.pan_start_y = None
        self.pan_xlim = None
        self.pan_ylim = None
        self.is_panning = False

        # Скрываем скроллбары, пока нет данных
        self.v_scrollbar.grid_remove()
        self.h_scrollbar.grid_remove()

    # ================================================================
    #                    ОБРАБОТКА МЫШИ
    # ================================================================

    def _on_scroll(self, event):
        """Масштабирование колёсиком мыши"""
        if event.inaxes != self.ax:
            return

        if event.button == "up":
            self.zoom_factor = min(self.zoom_factor * 1.1, 10000.0)
        else:
            self.zoom_factor = max(self.zoom_factor / 1.1, 0.0001)

        self._apply_zoom(self.zoom_factor)
        self.zoom_scale.set(self.zoom_factor)
        self._update_zoom_label()
        self._update_scroll_positions()
        self.canvas.draw()

    def _on_mouse_press(self, event):
        if event.inaxes != self.ax:
            return
        if event.button in (2, 3):  # средняя или правая кнопка
            self.is_panning = True
            self.pan_start_x = event.xdata
            self.pan_start_y = event.ydata
            self.pan_xlim = self.ax.get_xlim()
            self.pan_ylim = self.ax.get_ylim()

    def _on_mouse_release(self, event):
        self.is_panning = False
        self.pan_start_x = None
        self.pan_start_y = None

    def _on_mouse_motion(self, event):
        if not self.is_panning or event.inaxes != self.ax:
            return
        dx = event.xdata - self.pan_start_x
        dy = event.ydata - self.pan_start_y

        new_xlim = (self.pan_xlim[0] - dx, self.pan_xlim[1] - dx)
        new_ylim = (self.pan_ylim[0] - dy, self.pan_ylim[1] - dy)

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        self.current_center_x = (new_xlim[0] + new_xlim[1]) / 2
        self.current_center_y = (new_ylim[0] + new_ylim[1]) / 2

        self._update_scroll_positions()
        self.canvas.draw()

    # ================================================================
    #                    МАСШТАБИРОВАНИЕ
    # ================================================================

    def _apply_zoom(self, zoom_factor):
        if not self.is_data_plotted or self.base_x_range is None:
            return

        base_x_range = self.base_x_range[1] - self.base_x_range[0]
        base_y_range = self.base_y_range[1] - self.base_y_range[0]

        new_x_range = base_x_range / zoom_factor
        new_y_range = base_y_range / zoom_factor

        new_xlim = [
            self.current_center_x - new_x_range / 2,
            self.current_center_x + new_x_range / 2,
        ]
        new_ylim = [
            self.current_center_y - new_y_range / 2,
            self.current_center_y + new_y_range / 2,
        ]

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

    def _update_zoom_label(self):
        z = self.zoom_factor
        if z >= 1:
            if z >= 10000:
                text = "10000x"
            elif z >= 1000:
                text = f"{int(z)}x"
            elif z == int(z):
                text = f"{int(z)}x"
            else:
                text = f"{z:.1f}x"
        else:
            if z <= 0.0001:
                text = "0.0001x"
            elif z <= 0.001:
                text = f"{z:.4f}x"
            elif z <= 0.01:
                text = f"{z:.3f}x"
            else:
                text = f"{z:.2f}x"
        self.zoom_label.configure(text=text)

    def _on_zoom_slider(self, value):
        if not self.is_data_plotted or self.base_x_range is None:
            return
        self.zoom_factor = value
        self._apply_zoom(value)
        self._update_zoom_label()
        self._update_scroll_positions()
        self.canvas.draw()

    def zoom_in(self):
        new_value = min(self.zoom_factor * 1.2, 10000.0)
        self.zoom_factor = new_value
        self.zoom_scale.set(new_value)
        self._apply_zoom(new_value)
        self._update_zoom_label()
        self._update_scroll_positions()
        self.canvas.draw()

    def zoom_out(self):
        new_value = max(self.zoom_factor / 1.2, 0.0001)
        self.zoom_factor = new_value
        self.zoom_scale.set(new_value)
        self._apply_zoom(new_value)
        self._update_zoom_label()
        self._update_scroll_positions()
        self.canvas.draw()

    def reset_view(self):
        if self.base_x_range is None:
            return
        self.ax.set_xlim(self.base_x_range)
        self.ax.set_ylim(self.base_y_range)

        self.current_center_x = (self.base_x_range[0] + self.base_x_range[1]) / 2
        self.current_center_y = (self.base_y_range[0] + self.base_y_range[1]) / 2

        self.zoom_factor = 1.0
        self.zoom_scale.set(1.0)
        self.zoom_label.configure(text="1x")

        self.scroll_position_x = 0.5
        self.scroll_position_y = 0.5
        self._update_scrollbars()
        self.canvas.draw()

    # ================================================================
    #                       СКРОЛЛБАРЫ
    # ================================================================

    def _update_scroll_positions(self):
        if not self.is_data_plotted or self.full_x_range is None:
            return

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        x_range = self.full_x_range[1] - self.full_x_range[0]
        if x_range > 0:
            x_center = (xlim[0] + xlim[1]) / 2
            self.scroll_position_x = (x_center - self.full_x_range[0]) / x_range
            self.scroll_position_x = max(0, min(1, self.scroll_position_x))

        y_range = self.full_y_range[1] - self.full_y_range[0]
        if y_range > 0:
            y_center = (ylim[0] + ylim[1]) / 2
            self.scroll_position_y = (y_center - self.full_y_range[0]) / y_range
            self.scroll_position_y = max(0, min(1, self.scroll_position_y))

        self._update_scrollbars()

    def _update_scrollbars(self, event=None):
        if not self.is_data_plotted or self.full_x_range is None:
            self.v_scrollbar.grid_remove()
            self.h_scrollbar.grid_remove()
            return

        self.v_scrollbar.grid()
        self.h_scrollbar.grid()

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        x_visible = (xlim[1] - xlim[0]) / (self.full_x_range[1] - self.full_x_range[0])
        y_visible = (ylim[1] - ylim[0]) / (self.full_y_range[1] - self.full_y_range[0])

        x_visible = max(0.01, min(1.0, x_visible))
        y_visible = max(0.01, min(1.0, y_visible))

        self.h_scrollbar.set(
            self.scroll_position_x - x_visible / 2,
            self.scroll_position_x + x_visible / 2,
        )
        self.v_scrollbar.set(
            self.scroll_position_y - y_visible / 2,
            self.scroll_position_y + y_visible / 2,
        )

    def _on_hscroll(self, *args):
        if not self.is_data_plotted or self.full_x_range is None:
            return
        try:
            if args[0] == "moveto":
                self.scroll_position_x = float(args[1])
            elif args[0] == "scroll":
                step = float(args[1])
                if args[2] == "units":
                    self.scroll_position_x += step * 0.05
                elif args[2] == "pages":
                    self.scroll_position_x += step * 0.5
            self.scroll_position_x = max(0, min(1, self.scroll_position_x))
        except Exception:
            return

        x_range = self.full_x_range[1] - self.full_x_range[0]
        current_xlim = self.ax.get_xlim()
        x_width = current_xlim[1] - current_xlim[0]
        new_center_x = self.full_x_range[0] + self.scroll_position_x * x_range
        self.current_center_x = new_center_x
        self.ax.set_xlim(new_center_x - x_width / 2, new_center_x + x_width / 2)

        self._update_scrollbars()
        self.canvas.draw()

    def _on_vscroll(self, *args):
        if not self.is_data_plotted or self.full_y_range is None:
            return
        try:
            if args[0] == "moveto":
                self.scroll_position_y = float(args[1])
            elif args[0] == "scroll":
                step = float(args[1])
                if args[2] == "units":
                    self.scroll_position_y += step * 0.05
                elif args[2] == "pages":
                    self.scroll_position_y += step * 0.5
            self.scroll_position_y = max(0, min(1, self.scroll_position_y))
        except Exception:
            return

        y_range = self.full_y_range[1] - self.full_y_range[0]
        current_ylim = self.ax.get_ylim()
        y_height = current_ylim[1] - current_ylim[0]
        new_center_y = self.full_y_range[0] + self.scroll_position_y * y_range
        self.current_center_y = new_center_y
        self.ax.set_ylim(new_center_y - y_height / 2, new_center_y + y_height / 2)

        self._update_scrollbars()
        self.canvas.draw()

    # ================================================================
    #                    ПОСТРОЕНИЕ ГРАФИКОВ
    # ================================================================

    def _setup_axes(self):
        """Сброс и настройка осей"""
        self.ax.clear()
        self.ax.set_facecolor("#16213e")
        self.ax.grid(True, alpha=0.3, color="#ffffff")
        self.ax.axhline(y=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.axvline(x=0, color="#ffffff", alpha=0.5, linewidth=0.8)
        self.ax.tick_params(colors="#ffffff")
        self.ax.xaxis.label.set_color("#ffffff")
        self.ax.yaxis.label.set_color("#ffffff")

    def plot_function(self, func, x_min=-10, x_max=10, formula=""):
        """
        Построение графика функции с корректной обработкой точек разрыва.
        Линия уходит за пределы видимой области, создавая эффект бесконечности,
        но между ветвями разрыва НЕ рисуется вертикальная линия.
        """
        self._setup_axes()

        self.current_func = func
        self.current_formula = formula

        # ------------------------------------------------------------
        # 1. Генерация точек
        # ------------------------------------------------------------
        x = np.linspace(x_min, x_max, self.num_points)

        # Безопасное вычисление значений
        y = evaluate_safe(func, x)

        # ------------------------------------------------------------
        # 2. Определяем «нормальный» диапазон Y по устойчивым точкам
        # ------------------------------------------------------------
        y_finite = y[np.isfinite(y)]

        if len(y_finite) > 0:
            y_low = np.percentile(y_finite, 2)
            y_high = np.percentile(y_finite, 98)

            y_median = np.median(y_finite)
            y_mad = np.median(np.abs(y_finite - y_median))

            if y_mad > 0:
                y_low = max(y_low, y_median - 10 * y_mad)
                y_high = min(y_high, y_median + 10 * y_mad)
        else:
            y_low, y_high = -10, 10

        y_range = y_high - y_low
        if y_range <= 0:
            y_range = 1
        margin = y_range * 0.1

        y_view_min = y_low - margin
        y_view_max = y_high + margin

        # «Безопасная зона» — примерно во сколько раз значение должно
        # превышать нормальный диапазон, чтобы считаться выбросом
        threshold = 10 * max(abs(y_view_min), abs(y_view_max), 1.0)

        # ------------------------------------------------------------
        # 3. КЛЮЧЕВОЙ МОМЕНТ: находим точки разрыва и разрываем линию
        #    между ветвями, чтобы не было вертикального «уса».
        # ------------------------------------------------------------
        for i in range(1, len(y)):
            y_prev = y[i - 1]
            y_curr = y[i]

            # Если оба значения огромные и разных знаков — это асимптота
            # (например, 1/x при x -> 0- даёт -inf, при x -> 0+ даёт +inf)
            if (math.isfinite(y_prev) and math.isfinite(y_curr)
                    and abs(y_prev) > threshold
                    and abs(y_curr) > threshold
                    and y_prev * y_curr < 0):
                # Ставим NaN в одной из точек, чтобы линия разорвалась
                y[i] = np.nan
                continue

            # Если одно из значений улетает в бесконечность, а другое — нет,
            # значит мы вошли в разрыв. Обрываем линию прямо здесь.
            if math.isfinite(y_prev) and math.isfinite(y_curr):
                if abs(y_prev) > threshold and abs(y_curr) <= threshold:
                    # выходим из разрыва — оставляем y[i-1] огромным,
                    # но y[i] уже нормальный, поэтому линия от y[i-1]
                    # до y[i] уйдёт вверх/вниз за пределы окна — это ок.
                    pass
                elif abs(y_curr) > threshold and abs(y_prev) <= threshold:
                    # входим в разрыв — тоже оставляем как есть,
                    # линия уйдёт за край окна
                    pass

            # Также проверяем резкие скачки значений (на случай, если
            # асимптота «размазана» на несколько точек)
            dx = x[i] - x[i - 1]
            if dx > 0 and math.isfinite(y_prev) and math.isfinite(y_curr):
                if abs(y_curr - y_prev) / dx > 1e6:
                    y[i] = np.nan

        # ------------------------------------------------------------
        # 4. Также разрываем линию там, где evaluate_safe уже поставила NaN
        #    (это настоящие inf/nan, например, если x точно попал в 0)
        #    — их не трогаем, matplotlib сам не будет рисовать через них.
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # 5. Рисуем график
        # ------------------------------------------------------------
        self.ax.plot(x, y, color="#00d4ff", linewidth=2, label=formula)
        self.ax.set_xlabel("x", color="#ffffff")
        self.ax.set_ylabel("y", color="#ffffff")

        if formula:
            self.ax.legend(
                loc="upper right", facecolor="#1a1a2e", edgecolor="#ffffff"
            )

        # ------------------------------------------------------------
        # 6. Устанавливаем пределы осей
        # ------------------------------------------------------------
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_view_min, y_view_max)

        # Сохраняем диапазоны
        self.full_x_range = (x_min, x_max)
        self.full_y_range = (y_view_min, y_view_max)
        self.base_x_range = (x_min, x_max)
        self.base_y_range = (y_view_min, y_view_max)
        self.is_data_plotted = True

        self.current_center_x = (x_min + x_max) / 2
        self.current_center_y = (y_view_min + y_view_max) / 2

        self.scroll_position_x = 0.5
        self.scroll_position_y = 0.5

        self.zoom_factor = 1.0
        self.zoom_scale.set(1.0)
        self.zoom_label.configure(text="1x")

        self._update_scrollbars()
        self.canvas.draw()

    def plot_data(self, x_data, y_data, filename=""):
        """Построение графика по точкам из файла"""
        self._setup_axes()

        self.current_func = None
        self.current_formula = filename

        # Интерполяция для плавности (если есть scipy)
        if len(x_data) > 2:
            x_smooth = np.linspace(min(x_data), max(x_data), self.num_points)
            try:
                from scipy.interpolate import CubicSpline

                cs = CubicSpline(x_data, y_data)
                y_smooth = cs(x_smooth)
                self.ax.plot(
                    x_smooth, y_smooth, color="#00d4ff", linewidth=2, alpha=0.7
                )
            except Exception:
                self.ax.plot(
                    x_data, y_data, color="#00d4ff", linewidth=2, alpha=0.7
                )
        else:
            self.ax.plot(x_data, y_data, color="#00d4ff", linewidth=2, alpha=0.7)

        self.ax.scatter(x_data, y_data, color="#ff6b6b", s=50, zorder=5, label="Данные")
        self.ax.set_xlabel("x", color="#ffffff")
        self.ax.set_ylabel("y", color="#ffffff")

        if filename:
            self.ax.legend(
                loc="upper right", facecolor="#1a1a2e", edgecolor="#ffffff"
            )

        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)

        x_margin = max((x_max - x_min) * 0.1, 0.5)
        y_margin = max((y_max - y_min) * 0.1, 0.5)

        x_min_plot, x_max_plot = x_min - x_margin, x_max + x_margin
        y_min_plot, y_max_plot = y_min - y_margin, y_max + y_margin

        self.ax.set_xlim(x_min_plot, x_max_plot)
        self.ax.set_ylim(y_min_plot, y_max_plot)

        self.full_x_range = (x_min_plot, x_max_plot)
        self.full_y_range = (y_min_plot, y_max_plot)
        self.base_x_range = (x_min_plot, x_max_plot)
        self.base_y_range = (y_min_plot, y_max_plot)
        self.is_data_plotted = True

        self.current_center_x = (x_min_plot + x_max_plot) / 2
        self.current_center_y = (y_min_plot + y_max_plot) / 2

        self.scroll_position_x = 0.5
        self.scroll_position_y = 0.5

        self.zoom_factor = 1.0
        self.zoom_scale.set(1.0)
        self.zoom_label.configure(text="1x")

        self._update_scrollbars()
        self.canvas.draw()

    def clear(self):
        """Очистка графика"""
        self._setup_axes()
        self.ax.set_xlabel("x", color="#ffffff")
        self.ax.set_ylabel("y", color="#ffffff")

        self.base_x_range = None
        self.base_y_range = None
        self.full_x_range = None
        self.full_y_range = None
        self.is_data_plotted = False
        self.current_center_x = 0
        self.current_center_y = 0
        self.current_func = None
        self.current_formula = None

        self.zoom_factor = 1.0
        self.zoom_scale.set(1.0)
        self.zoom_label.configure(text="1x")

        self.v_scrollbar.grid_remove()
        self.h_scrollbar.grid_remove()

        self.canvas.draw()