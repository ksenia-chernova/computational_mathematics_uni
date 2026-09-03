"""
Парсер математических функций
"""
import math
import numpy as np


def parse_function(formula):
    """
    Парсит строку формулы и возвращает функцию
    
    Args:
        formula: строка с формулой (например, "sin(x) + cos(x)")
    
    Returns:
        callable: функция f(x)
    """
    # Безопасное пространство имен с математическими функциями
    safe_dict = {
        # Основные математические функции
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'sqrt': math.sqrt,
        'abs': abs,
        'pow': pow,
        'pi': math.pi,
        'e': math.e,
        # NumPy функции для работы с массивами
        'np': np,
        'numpy': np
    }
    
    def func(x):
        """Вычисление значения функции в точке x"""
        # Добавляем x в словарь
        local_dict = safe_dict.copy()
        local_dict['x'] = x
        
        # Вычисляем выражение
        try:
            # Используем eval, но с ограниченным пространством имен
            result = eval(formula, {"__builtins__": {}}, local_dict)
            
            # Проверка на допустимые типы
            if isinstance(result, (int, float, np.ndarray)):
                return float(result) if isinstance(result, (int, float)) else result
            else:
                raise ValueError(f"Неверный тип результата: {type(result)}")
                
        except Exception as e:
            raise ValueError(f"Ошибка при вычислении функции: {str(e)}")
    
    # Проверка парсинга
    try:
        # Проверяем на нескольких точках
        test_points = [0.0, 1.0, -1.0, 0.5]
        for x in test_points:
            func(x)
    except Exception as e:
        raise ValueError(f"Не удалось распарсить формулу: {str(e)}")
    
    return func