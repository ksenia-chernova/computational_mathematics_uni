"""
Загрузка данных из файлов
"""
import re


def load_from_file(file_path):
    """
    Загрузка данных из текстового файла
    
    Формат файла:
    x | y
    0 | 0
    1 | 1
    
    Разделители: пробел, табуляция, точка с запятой, запятая, |
    
    Returns:
        tuple: (x_data, y_data) - списки чисел
    """
    x_data = []
    y_data = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines:
        raise ValueError("Файл пуст")
    
    # Пропускаем заголовок, если он есть
    start_line = 0
    first_line = lines[0].strip()
    if re.search(r'[xX]\s*[|;,]\s*[yY]', first_line) or re.match(r'^[a-zA-Z]', first_line):
        start_line = 1
    
    for line_num, line in enumerate(lines[start_line:], start=start_line + 1):
        line = line.strip()
        if not line:
            continue
        
        # Разбиваем строку на части
        # Поддерживаем разные разделители: |, ;, ,, табуляция, пробел
        parts = re.split(r'[|;, \t]+', line)
        parts = [p.strip() for p in parts if p.strip()]
        
        if len(parts) < 2:
            continue
        
        try:
            x = float(parts[0].replace(',', '.'))
            y = float(parts[1].replace(',', '.'))
            x_data.append(x)
            y_data.append(y)
        except ValueError as e:
            raise ValueError(f"Ошибка в строке {line_num}: {line}\n{str(e)}")
    
    if len(x_data) < 2:
        raise ValueError("Недостаточно данных для построения графика (нужно минимум 2 точки)")
    
    return x_data, y_data