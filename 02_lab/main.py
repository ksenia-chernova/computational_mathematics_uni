import math

def f(x):
    """
    Функция f(x) = (x - 2.5) * cos(3 * pi * x) / (x - 1.5)
    """
    if abs(x - 1.5) < 1e-15:
        raise ValueError("Division by zero at x=1.5")
    
    return ((x - 2.5) * math.cos(3 * math.pi * x)) / (x - 1.5)

def chord_method(a, b, epsilon=1e-4):
    """
    Решение нелинейного уравнения методом хорд.
    a, b - границы интервала
    epsilon - точность
    """
    
    fa = f(a)
    fb = f(b)
    
    if fa * fb >= 0:
        print("Ошибка: На концах интервала функция имеет одинаковый знак или равна нулю.")
        return None

    # Заголовки таблицы (добавлены f(a) и f(b))
    header = (f"{'N':<4} {'a':<12} {'b':<12} {'f(a)':<14} {'f(b)':<14} "
              f"{'x_new':<12} {'f(x_new)':<12} {'|b-a|':<12}")
    print(header)
    print("-" * len(header))

    iteration = 0
    current_a = a
    current_b = b
    
    f_a = fa
    f_b = fb

    while True:
        iteration += 1
        
        denominator = f_b - f_a
        if abs(denominator) < 1e-15:
            print("Ошибка: Деление на ноль в знаменателе формулы хорд.")
            return None
            
        x_new = current_a - ((current_b - current_a) / (f(current_b) - f(current_a))) * f(current_a)
        f_new = f(x_new)
        
        # Вывод строки таблицы с новыми столбцами
        row = (f"{iteration:<4} {current_a:<12.6f} {current_b:<12.6f} "
               f"{f_a:<14.6e} {f_b:<14.6e} "
               f"{x_new:<12.6f} {f_new:<12.6e} {abs(current_b - current_a):<12.6e}")
        print(row)
        
        # Проверка условия остановки
        if abs(f_new) < epsilon or abs(current_b - current_a) < epsilon:
            print("-" * len(header))
            print(f"Решение найдено: x = {x_new:.6f}")
            print(f"f(x) = {f_new:.6e}")
            return x_new
        
        # Сужение интервала
        if f_a * f_new < 0:
            current_b = x_new
            f_b = f_new
        else:
            current_a = x_new
            f_a = f_new
            
        if iteration > 100:
            print("Превышено максимальное количество итераций.")
            return None

if __name__ == "__main__":
    a_start = 0
    b_start = 0.3
    eps = 1e-4
    
    print("Решение уравнения f(x) = (x - 2.5) * cos(3 * pi * x) / (x - 1.5) = 0")
    print(f"Интервал: [{a_start}, {b_start}], Точность: {eps}\n")
    
    root = chord_method(a_start, b_start, eps)