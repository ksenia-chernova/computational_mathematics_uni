import math

def f(x):
    """f(x) = (x - 2.5) * cos(3*pi*x) / (x - 1.5)"""
    # В точке x = 1.5 — устранимый разрыв.
    # Предел: lim_{x->1.5} f(x) = -3*pi
    if abs(x - 1.5) < 1e-12:
        return -3.0 * math.pi
    return (x - 2.5) * math.cos(3.0 * math.pi * x) / (x - 1.5)

def trapezoidal(a, b, n):
    """
    Вычисляет интеграл f(x) на [a, b] методом трапеций с n отрезками.
    Возвращает значение интеграла.
    """
    h = (b - a) / n
    s = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        s += f(a + i * h)
    return s * h

# ---------- Итерационный подбор сетки ----------
def integrate_adaptive(a, b, epsilon):
    """
    Итерационное вычисление интеграла методом трапеций.
    На каждом шаге число отрезков удваивается.
    Остановка: |I_n - I_{n/2}| < epsilon.
    Возвращает: (значение интеграла, оценка погрешности, число узлов, число итераций)
    """
    n = 1            # начинаем с 1 отрезка (2 узла)
    I_prev = trapezoidal(a, b, n)
    iterations = 0

    while True:
        n *= 2       # удваиваем число отрезков
        I_curr = trapezoidal(a, b, n)
        iterations += 1
        error = abs(I_curr - I_prev)
        if error < epsilon:
            break
        I_prev = I_curr

    # Число узлов = n + 1
    nodes = n + 1
    return I_curr, error, nodes, iterations

# ---------- Основная программа ----------
if __name__ == "__main__":
    # Пределы интегрирования (изменить при необходимости)
    a = 0.0
    b = 3.0
    epsilon = 1e-4

    print(f"Функция: f(x) = (x - 2.5) * cos(3*pi*x) / (x - 1.5)")
    print(f"Пределы интегрирования: a = {a}, b = {b}")
    print(f"Требуемая точность: epsilon = {epsilon}")

    result, error, nodes, iterations = integrate_adaptive(a, b, epsilon)

    print(f"\nРезультаты вычисления:")
    print(f"  Значение интеграла : {result:.10f}")
    print(f"  Оценка погрешности : {error:.2e}")
    print(f"  Количество узлов   : {nodes}")
    print(f"  Количество итераций: {iterations}")