import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────
# Исходная функция
# ─────────────────────────────────────────────
def f(x):
    return (x - 2.5) * (np.cos(3 * np.pi * x) / (x - 1.5))

# ─────────────────────────────────────────────
# Генерация узлов интерполяции
# ─────────────────────────────────────────────
def generate_nodes(a, b, n_nodes, exclude_point=1.5, exclude_radius=0.1):
    """
    Генерация равномерно распределённых узлов, избегая окрестности разрыва.
    """
    # Создаём плотную сетку
    x_dense = np.linspace(a, b, 10000)
    
    # Исключаем окрестность разрыва
    mask = np.abs(x_dense - exclude_point) > exclude_radius
    x_dense = x_dense[mask]
    
    # Равномерно выбираем n_nodes точек из оставшихся
    indices = np.linspace(0, len(x_dense) - 1, n_nodes, dtype=int)
    x_nodes = x_dense[indices]
    
    return x_nodes

# Задаём узлы интерполяции (20 узлов, избегаем x = 1.5)
n_nodes = 20
x_nodes = generate_nodes(0.1, 4.0, n_nodes, exclude_point=1.5, exclude_radius=0.1)
y_nodes = f(x_nodes)

# ────────────────────────────────────────────
# Построение таблицы разделённых разностей
# ─────────────────────────────────────────────
def divided_differences(x, y):
    """Вычисление таблицы разделённых разностей Ньютона."""
    n = len(x)
    dd = np.zeros((n, n))
    dd[:, 0] = y
    for j in range(1, n):
        for i in range(n - j):
            dd[i, j] = (dd[i + 1, j - 1] - dd[i, j - 1]) / (x[i + j] - x[i])
    return dd

# ─────────────────────────────────────────────
# Вычисление значения интерполяционного многочлена Ньютона
# ─────────────────────────────────────────────
def newton_interpolation(x_nodes, dd, x_val):
    """
    Вычисление значения многочлена Ньютона в точке x_val.
    dd — таблица разделённых разностей.
    """
    n = len(x_nodes)
    result = dd[0, 0]
    product = 1.0
    for j in range(1, n):
        product *= (x_val - x_nodes[j - 1])
        result += dd[0, j] * product
    return result

# ─────────────────────────────────────────────
# Построение многочленов различной степени (от 1 до 50)
# и вычисление СКО
# ─────────────────────────────────────────────
# Точки для проверки СКО
x_test = np.linspace(0.1, 4.0, 1000)
mask = np.abs(x_test - 1.5) > 0.05
x_test = x_test[mask]
y_test = f(x_test)

# Максимальная степень = количество узлов - 1
max_degree = len(x_nodes) - 1

rms_values = {}

print(f"{'Степень':<10} {'СКО (RMS)':<20}")
print("-" * 30)

for degree in range(1, max_degree + 1):
    # Берём первые (degree + 1) узлов
    x_sub = x_nodes[:degree + 1]
    y_sub = y_nodes[:degree + 1]

    dd = divided_differences(x_sub, y_sub)

    y_approx = np.array([newton_interpolation(x_sub, dd, xi) for xi in x_test])

    # СКО
    rms = np.sqrt(np.mean((y_test - y_approx) ** 2))
    rms_values[degree] = rms
    print(f"{degree:<10} {rms:<20.6f}")

# ─────────────────────────────────────────────
# График: исходная функция, интерполяционный многочлен, узловые точки
# ─────────────────────────────────────────────
# Используем все узлы для демонстрации
dd_full = divided_differences(x_nodes, y_nodes)

x_plot = np.linspace(0.1, 4.0, 2000)
mask_plot = np.abs(x_plot - 1.5) > 0.05
x_plot = x_plot[mask_plot]

y_original = f(x_plot)
y_newton = np.array([newton_interpolation(x_nodes, dd_full, xi) for xi in x_plot])

plt.figure(figsize=(14, 8))

# Исходная функция — синий
plt.plot(x_plot, y_original, 'b-', linewidth=2, label='Исходная функция f(x)')

# Интерполяционный многочлен Ньютона — красный
plt.plot(x_plot, y_newton, 'r--', linewidth=2, label=f'Многочлен Ньютона (степень {max_degree})')

# Узловые точки — зелёные звёздочки
plt.plot(x_nodes, y_nodes, 'g*', markersize=12, label='Узловые точки')

# Произвольная точка — чёрная звёздочка
x_arbitrary = 2.2
y_arbitrary_newton = newton_interpolation(x_nodes, dd_full, x_arbitrary)
y_arbitrary_true = f(x_arbitrary)
plt.plot(x_arbitrary, y_arbitrary_newton, 'k*', markersize=18,
         label=f'x*={x_arbitrary}, N(x*)={y_arbitrary_newton:.4f}')
plt.plot(x_arbitrary, y_arbitrary_true, 'mo', markersize=10,
         label=f'f(x*)={y_arbitrary_true:.4f}')

plt.xlabel('x', fontsize=12)
plt.ylabel('y', fontsize=12)
plt.title('Интерполяционный многочлен Ньютона', fontsize=14)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.axvline(x=1.5, color='gray', linestyle=':', alpha=0.5, label='Разрыв x=1.5')
plt.tight_layout()

# ─────────────────────────────────────────────
# Вывод значения многочлена в произвольной точке
# ─────────────────────────────────────────────
print(f"\nЗначение многочлена Ньютона в точке x = {x_arbitrary}:")
print(f"  N({x_arbitrary}) = {y_arbitrary_newton:.6f}")
print(f"  f({x_arbitrary}) = {y_arbitrary_true:.6f}")
print(f"  Погрешность      = {abs(y_arbitrary_newton - y_arbitrary_true):.6f}")

print("\nСКО для каждой степени:")
for deg, rms in rms_values.items():
    print(f"  Степень {deg}: СКО = {rms:.6f}")

plt.show()