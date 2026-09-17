import sympy as sp
from sympy import pi, lambdify

x_sym = sp.Symbol('x')
f_sym = (x_sym - 2.5) * (sp.cos(3 * pi * x_sym) / (x_sym - 1.5))

f_prime_sym = sp.diff(f_sym, x_sym)
f_double_prime_sym = sp.diff(f_prime_sym, x_sym)

# Преобразуем символьные выражения в быстрые числовые функции (lambdify)
# Используем 'numpy' модуль для векторизации и скорости
f_num = lambdify(x_sym, f_sym, 'numpy')
f_prime_num = lambdify(x_sym, f_prime_sym, 'numpy')
f_double_prime_num = lambdify(x_sym, f_double_prime_sym, 'numpy')

# 2. Реализация метода Ньютона
def newton_method(x0, epsilon=1e-4, max_iter=50):
    """
    Поиск экстремума функции методом Ньютона.
    Экстремум ищется как корень уравнения f'(x) = 0.
    Итерационная формула: x_{n+1} = x_n - f'(x_n) / f''(x_n)
    """
    print(f"{'№':<4} | {'x_n':<12} | {'f(x_n)':<12} | {'f\'(x_n)':<12} | {'|Δx|':<12}")
    print("-" * 65)
    
    x_curr = float(x0)
    history = [(0, x_curr, f_num(x_curr))]
    
    # Вывод нулевой итерации
    print(f"{0:<4} | {x_curr:<12.6f} | {f_num(x_curr):<12.6f} | {'-':<12} | {'-':<12}")

    for i in range(1, max_iter + 1):
        fp = f_prime_num(x_curr)
        fpp = f_double_prime_num(x_curr)
        
        # Проверка на деление на ноль или слишком малую вторую производную
        if abs(fpp) < 1e-12:
            print(f"\nОшибка: Вторая производная близка к нулю ({fpp}). Метод расходится.")
            return None, history
            
        # Шаг метода Ньютона для поиска корня f'(x)
        delta_x = fp / fpp
        x_next = x_curr - delta_x
        
        fx_next = f_num(x_next)
        
        # Вывод строки таблицы
        print(f"{i:<4} | {x_next:<12.6f} | {fx_next:<12.6f} | {fp:<12.6f} | {abs(delta_x):<12.6f}")
        
        history.append((i, x_next, fx_next))
        
        # Условие остановки по точности изменения аргумента
        if abs(delta_x) < epsilon:
            print("-" * 65)
            return x_next, history
            
        x_curr = x_next
        
    print("-" * 65)
    print("Достигнут лимит итераций. Точность не достигнута.")
    return x_curr, history

# 3. Запуск расчётов
print("Метод: Ньютона")
print(f"Функция: f(x) = (x - 2.5) * cos(3πx) / (x - 1.5)")
print("Точность ε = 10⁻⁴")

x_start = 2.0 

extremum_x, iterations_data = newton_method(x_start)

if extremum_x is not None:
    f_val = f_num(extremum_x)
    fpp_val = f_double_prime_num(extremum_x)
    
    print(f"Найденная точка экстремума: x* = {extremum_x:.6f}")
    print(f"Значение функции в точке:     f(x*) = {f_val:.6f}")
    print(f"Вторая производная в точке:   f''(x*) = {fpp_val:.6f}")
    
    if fpp_val > 0:
        print(f"Тип экстремума:             МИНИМУМ (так как f'' > 0)")
    else:
        print(f"Тип экстремума:             МАКСИМУМ (так как f'' < 0)")