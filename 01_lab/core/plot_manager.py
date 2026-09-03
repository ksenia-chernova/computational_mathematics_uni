"""
Управление построением графиков
"""
import matplotlib.pyplot as plt
import numpy as np


class PlotManager:
    """Менеджер для управления графиками"""
    
    @staticmethod
    def get_plot_limits(x_data, y_data, margin=0.1):
        """Вычисление оптимальных пределов для графика"""
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)
        
        x_range = x_max - x_min
        y_range = y_max - y_min
        
        if x_range == 0:
            x_range = 1
        if y_range == 0:
            y_range = 1
            
        x_margin = x_range * margin
        y_margin = y_range * margin
        
        return (x_min - x_margin, x_max + x_margin), (y_min - y_margin, y_max + y_margin)