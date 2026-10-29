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
        fx = f(x, y)
        y_pred = y + h * fx
        y = y + (h / 2) * (fx + f(x + h, y_pred))
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
def event_stop(t, y):
    return t - 0.53 * y[0]

event_stop.terminal = True
event_stop.direction = -1

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

# Максимальный x, до которого корректно эталонное решение
x_max_ref = sol_ref.t[-1]
# 4. Вывод таблицы с f(x,y) и y' для обоих решений
# Выбираем только те индексы, которые входят в область определения эталона (x <= 1.6493)
valid_indices = [i for i in range(len(x_vals)) if x_vals[i] <= x_max_ref + 1e-6]

# Берём первые 7 валидных точек (x = 1.0, 1.1, ..., 1.6)
check_indices = valid_indices[:7]

# Формируем заголовок
col_f_ec = "f(x,y) ЭК"
col_y_num_ec = "y' ЭК"
col_f_et = "f(x,y) Эт"
col_y_num_et = "y' Эт"

header = (f"{'x':<6} | {'y (ЭК)':<8} | {col_f_ec:<10} | {col_y_num_ec:<11} | "
          f"{'y (Эт)':<8} | {col_f_et:<10} | {col_y_num_et:<11}")
print(header)
print("-" * len(header))

for idx in check_indices:
    x_curr = x_vals[idx]
    y_calc = y_vals[idx]
    
    # === Для метода Эйлера-Коши ===
    # 1. Аналитическая правая часть f(x,y)
    f_calc = f(x_curr, y_calc)
    
    # 2. Численная производная y' (конечная разность вперёд)
    if idx < len(x_vals) - 1:
        y_prime_num_ec = (y_vals[idx+1] - y_vals[idx]) / h
    else:
        y_prime_num_ec = np.nan
    
    # === Для эталонного решения ===
    # 3. Эталонное значение y
    y_ref = sol_ref.sol(x_curr)[0]
    
    # 4. Эталонная правая часть f(x,y)
    f_ref = f(x_curr, y_ref)
    
    # 5. Численная производная y' для эталона (конечная разность вперёд)
    if idx < len(check_indices) - 1:
        y_ref_next = sol_ref.sol(x_vals[idx+1])[0]
        y_prime_num_et = (y_ref_next - y_ref) / h
    else:
        y_prime_num_et = np.nan
    
    print(f"{x_curr:<6.2f} | {y_calc:<8.5f} | {f_calc:<10.5f} | {y_prime_num_ec:<11.5f} | "
          f"{y_ref:<8.5f} | {f_ref:<10.5f} | {y_prime_num_et:<11.5f}")

# 5. Построение графика
plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals, 'o-', label=f'Эйлер-Коши (h={h})', color='blue')
plt.plot(sol_ref.t, sol_ref.y[0], '--', label='Эталон (DOP853)', color='red', alpha=0.7)
plt.scatter([x0], [y0], color='green', s=100, zorder=5, label=f'y({x0})={y0}')

plt.title(r"Решение ОДУ: \(y' = \ln(x - 0.53y) + e^{xy}\)")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True)
plt.legend()
plt.show()