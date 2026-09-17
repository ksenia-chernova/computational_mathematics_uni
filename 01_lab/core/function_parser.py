"""
Парсер математических функций с обработкой точек разрыва
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
        'np': np,
        'numpy': np
    }
    
    def func(x):
        """Вычисление значения функции в точке x"""
        local_dict = safe_dict.copy()
        local_dict['x'] = x
        
        try:
            result = eval(formula, {"__builtins__": {}}, local_dict)
            
            if isinstance(result, (int, float, np.ndarray)):
                return float(result) if isinstance(result, (int, float)) else result
            else:
                raise ValueError(f"Неверный тип результата: {type(result)}")
                
        except (ZeroDivisionError, ValueError, OverflowError) as e:
            # Возвращаем бесконечность вместо выброса исключения
            return float('inf')
        except Exception as e:
            raise ValueError(f"Ошибка при вычислении функции: {str(e)}")
    
    # Проверка парсинга
    try:
        test_points = [0.0, 1.0, -1.0, 0.5]
        for x in test_points:
            func(x)
    except Exception as e:
        raise ValueError(f"Не удалось распарсить формулу: {str(e)}")
    
    return func


def evaluate_safe(func, x_values):
    """
    Безопасное вычисление значений функции.
    Возвращает NaN ТОЛЬКО для настоящих inf/nan и исключений,
    но не для больших чисел.
    """
    y = np.empty(len(x_values), dtype=float)

    for i, x in enumerate(x_values):
        try:
            val = func(x)
            if isinstance(val, complex) or not math.isfinite(val):
                y[i] = np.nan
            else:
                y[i] = val  # ← большие значения сохраняем как есть!
        except (ZeroDivisionError, ValueError, OverflowError):
            y[i] = np.nan

    return y


def detect_discontinuities(func, x_values, y_values, jump_threshold=1e6):
    """
    Обнаружение точек разрыва по резким скачкам значений
    
    Args:
        func: функция f(x)
        x_values: массив x
        y_values: массив y
        jump_threshold: порог для определения скачка
        
    Returns:
        list: список индексов, где происходит разрыв
    """
    discontinuities = []
    
    for i in range(1, len(y_values)):
        y_prev = y_values[i-1]
        y_curr = y_values[i]
        
        # Пропускаем уже помеченные NaN
        if not math.isfinite(y_prev) or not math.isfinite(y_curr):
            if i not in discontinuities:
                discontinuities.append(i)
            continue
        
        # Проверка на огромный скачок
        dy = abs(y_curr - y_prev)
        dx = x_values[i] - x_values[i-1]
        
        # Если скачок очень большой (производная улетает), это разрыв
        if dx > 0 and dy / dx > jump_threshold:
            discontinuities.append(i)
    
    return discontinuities