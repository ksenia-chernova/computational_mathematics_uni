import numpy as np
import matplotlib.pyplot as plt

# 1. Определение функции (правой части ОДУ)
def f(x, y):
    # Ограничение области определения логарифма: x - 0.53y > 0
    return np.log(x - 0.53 * y) + np.exp(x * y)

# 2. Реализация метода Эйлера-Коши (предиктор-корректор)
def euler_cauchy(f, x0, y0, x_end, h):
    x_values = [x0]
    y_values = [y0]
    
    x = x0
    y = y0
    
    while x < x_end - 1e-9:
        # Предиктор (обычный шаг Эйлера)
        y_pred = y + h * f(x, y)
        
        # Корректор (уточнение по среднему значению производных)
        y = y + (h / 2) * (f(x, y) + f(x + h, y_pred))
        x = x + h
        
        x_values.append(x)
        y_values.append(y)
        
    return np.array(x_values), np.array(y_values)

# Параметры задачи
x0, y0 = 1.0, 0.0
x_end = 2.0
h = 0.1  # Шаг

# Получаем решение методом Эйлера-Коши
x_vals, y_vals = euler_cauchy(f, x0, y0, x_end, h)

# Для проверки погрешности получим "эталонное" решение с очень мелким шагом
# (используем тот же метод Эйлера-Коши, но с шагом 0.0001)
x_exact, y_exact = euler_cauchy(f, x0, y0, x_end, 0.0001)

# 3. Вывод таблицы проверки в 3 заданных точках
# При h=0.1 и x0=1.0 индексы 0, 5, 10 соответствуют x = 1.0, 1.5, 2.0
check_indices = [0, 2, 5]

data = []
print(f"{'x':<10} | {'y (Эйл-Коши)':<15} | {'y (Эталон)':<15} | {'Погрешность':<15}")
print("-" * 65)

for idx in check_indices:
    if idx < len(x_vals):
        x_curr = x_vals[idx]
        y_calc = y_vals[idx]
        
        # Находим ближайшее значение в эталонном массиве
        idx_exact = np.abs(x_exact - x_curr).argmin()
        y_ref = y_exact[idx_exact]
        
        error = abs(y_calc - y_ref)
        
        print(f"{x_curr:<10.2f} | {y_calc:<15.6f} | {y_ref:<15.6f} | {error:<15.2e}")
        
        data.append([x_curr, y_calc, y_ref, error])

# 4. Построение графика
plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals, 'o-', label=f'Решение Эйлера-Коши (h={h})', color='blue')
plt.plot(x_exact, y_exact, '--', label='Эталонное решение', color='red', alpha=0.5)

# Отметим начальное условие
plt.scatter([x0], [y0], color='green', s=100, zorder=5, label=f'Нач. условие y({x0})={y0}')

plt.title(r"Решение ОДУ: \(y' = \ln(x - 0.53y) + e^{xy}\)" + "\n(метод Эйлера-Коши)")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True)
plt.legend()
plt.show()