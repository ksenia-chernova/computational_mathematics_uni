import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# 1. Определение функции (правой части ОДУ)
def f(x, y):
    arg = x - 0.53 * y
    if arg <= 0:
        return np.nan
    return np.log(arg) + np.exp(x * y)

def f_for_ivp(t, y):
    arg = t - 0.53 * y[0]
    if arg <= 0:
        return [np.nan]
    return [np.log(arg) + np.exp(t * y[0])]

# 2. Реализация метода Эйлера-Коши (предиктор-корректор)
def euler_cauchy(f, x0, y0, x_end, h):
    x_values = [x0]
    y_values = [y0]
    
    x = x0
    y = y0
    
    while x < x_end - 1e-9:
        y_pred = y + h * f(x, y)
        y = y + (h / 2) * (f(x, y) + f(x + h, y_pred))
        x = x + h
        
        if np.isnan(y):
            break  # Обрываем решение, если получили NaN
        
        x_values.append(x)
        y_values.append(y)
        
    return np.array(x_values), np.array(y_values)

# Параметры задачи
x0, y0 = 1.0, 0.0
x_end = 2.0
h = 0.1

# Получаем решение методом Эйлера-Коши
x_vals, y_vals = euler_cauchy(f, x0, y0, x_end, h)

# 3. Эталонное решение через scipy
# Используем события (events) для остановки при x - 0.53*y = 0
def event_stop(t, y):
    return t - 0.53 * y[0]

event_stop.terminal = True  # Остановить интегрирование
event_stop.direction = -1   # Срабатывает, когда функция переходит от + к -

sol_ref = solve_ivp(
    f_for_ivp,
    t_span=(x0, x_end),
    y0=[y0],
    method='DOP853',
    rtol=1e-10,
    atol=1e-12,
    events=event_stop,
    dense_output=True
)

# Интерполируем эталонное решение в точках x_vals (только до точки останова)
x_exact = sol_ref.t
y_exact = sol_ref.y[0]

# 4. Вывод таблицы проверки
check_indices = [0, 5, min(10, len(x_vals)-1)]

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

# 5. Построение графика
plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals, 'o-', label=f'Решение Эйлера-Коши (h={h})', color='blue')
plt.plot(x_exact, y_exact, '--', label='Эталонное решение (scipy DOP853)',
         color='red', alpha=0.7)

plt.scatter([x0], [y0], color='green', s=100, zorder=5,
            label=f'Нач. условие y({x0})={y0}')

plt.title(r"Решение ОДУ: \(y' = \ln(x - 0.53y) + e^{xy}\)" + "\n(метод Эйлера-Коши)")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True)
plt.legend()
plt.show()