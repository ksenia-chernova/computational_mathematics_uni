"""
Валидация данных
"""
import re


def validate_formula(formula):
    """
    Проверка формулы на безопасность
    
    Returns:
        bool: корректна ли формула
    """
    # Разрешенные символы: буквы, цифры, математические операторы, скобки
    # и запятые (для десятичных дробей)
    allowed_pattern = r'^[a-zA-Z0-9+\-*/()., \t\n\r\^_]+$'
    
    if not re.match(allowed_pattern, formula):
        return False
    
    # Проверка на опасные конструкции
    dangerous = ['__', 'import', 'exec', 'eval', 'compile', 'open', 'file']
    for word in dangerous:
        if word in formula.lower():
            return False
    
    return True


def validate_file_data(x_data, y_data):
    """
    Проверка данных из файла
    
    Returns:
        bool: корректны ли данные
    """
    if not x_data or not y_data:
        return False
    
    if len(x_data) != len(y_data):
        return False
    
    if len(x_data) < 2:
        return False
    
    # Проверка, что все числа конечные
    import math
    for x, y in zip(x_data, y_data):
        if not math.isfinite(x) or not math.isfinite(y):
            return False
    
    return True