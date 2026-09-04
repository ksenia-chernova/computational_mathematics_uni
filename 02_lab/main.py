"""
Лабораторная работа №2: Решение нелинейных уравнений
Метод хорд
Уравнение: f(x) = (x - 2.5) * (cos(3 * pi * x) / (x - 1.5))
Точность: epsilon = 1e-4
"""

import math


class Equation:
    """Класс уравнения f(x) = 0"""
    
    @staticmethod
    def f(x):
        """
        Вычисление значения функции
        
        Args:
            x: значение аргумента
            
        Returns:
            float: значение функции
        """
        # Проверка на особую точку (знаменатель обращается в ноль)
        if abs(x - 1.5) < 1e-15:
            return float('inf')
        
        try:
            cos_val = math.cos(3 * math.pi * x)
            result = (x - 2.5) * (cos_val / (x - 1.5))
            return result
        except (OverflowError, ValueError, ZeroDivisionError):
            return float('inf')
    
    @staticmethod
    def get_formula():
        """Возвращает строковое представление формулы"""
        return "f(x) = (x - 2.5) * (cos(3πx) / (x - 1.5))"


class ChordMethod:
    """Реализация метода хорд"""
    
    def __init__(self, equation_func, epsilon=1e-4, max_iterations=1000):
        """
        Инициализация метода хорд
        
        Args:
            equation_func: функция f(x)
            epsilon: требуемая точность
            max_iterations: максимальное число итераций
        """
        self.f = equation_func
        self.epsilon = epsilon
        self.max_iterations = max_iterations
        
    def solve(self, a, b):
        """
        Решение уравнения методом хорд на отрезке [a, b]
        
        Args:
            a: левая граница отрезка
            b: правая граница отрезка
            
        Returns:
            tuple: (корень, история_итераций, статистика)
        """
        history = []
        
        # Вычисляем значения функции на концах отрезка
        fa = self.f(a)
        fb = self.f(b)
        
        # Проверка на особые точки
        if not math.isfinite(fa) or not math.isfinite(fb):
            return None, [], {
                'error': f'Функция имеет особую точку на границе отрезка [{a}, {b}]'
            }
        
        # Проверка, что функция имеет разные знаки на концах отрезка
        if fa * fb >= 0:
            return None, [], {
                'error': f'Функция не меняет знак на отрезке [{a}, {b}]'
            }
        
        print(f"\n{'='*80}")
        print(f"МЕТОД ХОРД")
        print(f"Уравнение: {Equation.get_formula()}")
        print(f"Отрезок: [{a}, {b}]")
        print(f"Точность: ε = {self.epsilon}")
        print(f"{'='*80}\n")
        
        # Текущие границы отрезка
        a_curr = a
        b_curr = b
        f_a_curr = fa
        f_b_curr = fb
        
        print(f"Начальные значения:")
        print(f"  f({a:.10f}) = {fa:.10f}")
        print(f"  f({b:.10f}) = {fb:.10f}\n")
        print(f"{'№':>4} | {'a':>14} | {'b':>14} | {'x':>14} | {'f(x)':>14} | {'|f(x)|':>14}")
        print(f"{'-'*85}")
        
        # Основной цикл метода хорд
        for iteration in range(1, self.max_iterations + 1):
            # Вычисляем новое приближение по формуле метода хорд
            # x = a - f(a) * (b - a) / (f(b) - f(a))
            denominator = f_b_curr - f_a_curr
            
            # Проверка на деление на ноль
            if abs(denominator) < 1e-15:
                print(f"\n❌ Деление на ноль на итерации {iteration}")
                break
                
            x_new = a_curr - f_a_curr * (b_curr - a_curr) / denominator
            f_x_new = self.f(x_new)
            
            # Проверка на особые точки
            if not math.isfinite(f_x_new):
                print(f"\n❌ Попадание в особую точку x = {x_new:.10f} на итерации {iteration}")
                break
            
            # Сохраняем историю
            history.append({
                'iteration': iteration,
                'a': a_curr,
                'b': b_curr,
                'x': x_new,
                'f_a': f_a_curr,
                'f_b': f_b_curr,
                'f_x': f_x_new,
                'error': abs(f_x_new)
            })
            
            # Выводим информацию об итерации
            print(f"{iteration:>4} | {a_curr:>14.10f} | {b_curr:>14.10f} | "
                  f"{x_new:>14.10f} | {f_x_new:>14.2e} | {abs(f_x_new):>14.2e}")
            
            # Проверка на достижение точности
            if abs(f_x_new) < self.epsilon:
                print(f"\n{'='*85}")
                print(f"✅ СХОДИМОСТЬ ДОСТИГНУТА на итерации {iteration}")
                print(f"{'='*85}\n")
                return x_new, history, {
                    'converged': True,
                    'iterations': iteration,
                    'root': x_new,
                    'f_root': f_x_new,
                    'epsilon': self.epsilon
                }
            
            # Обновление отрезка
            if f_a_curr * f_x_new < 0:
                # Корень между a и x_new
                b_curr = x_new
                f_b_curr = f_x_new
            else:
                # Корень между x_new и b
                a_curr = x_new
                f_a_curr = f_x_new
        
        # Если не сошлось за максимальное число итераций
        if history:
            last = history[-1]
            print(f"\n⚠️ Достигнуто максимальное число итераций ({self.max_iterations})")
            print(f"Последнее приближение: x = {last['x']:.10f}")
            return last['x'], history, {
                'converged': False,
                'iterations': len(history),
                'root': last['x'],
                'f_root': last['f_x'],
                'epsilon': self.epsilon
            }
        
        return None, [], {'error': 'Решение не найдено'}


def find_initial_segment():
    """
    Поиск начального отрезка для локализации корня
    
    Returns:
        tuple: (a, b) - отрезок с корнем
    """
    print("\n🔍 ЛОКАЛИЗАЦИЯ КОРНЯ")
    print("-" * 50)
    
    # Проверяем несколько отрезков
    segments = [
        (-5.0, -2.0),
        (-1.0, 0.5),
        (0.8, 1.4),
        (1.6, 2.0),
        (2.2, 2.8),
        (3.0, 4.0)
    ]
    
    for a, b in segments:
        fa = Equation.f(a)
        fb = Equation.f(b)
        
        if math.isfinite(fa) and math.isfinite(fb) and fa * fb < 0:
            print(f"✓ Найден отрезок с корнем: [{a}, {b}]")
            print(f"  f({a}) = {fa:.10f}")
            print(f"  f({b}) = {fb:.10f}")
            print(f"  f({a}) * f({b}) = {fa * fb:.10f} < 0\n")
            return a, b
    
    # Если не нашли, используем отрезок по умолчанию
    print("⚠️ Отрезок с корнем не найден. Используем [2.2, 2.8]")
    return 2.2, 2.8


def print_final_results(root, history, stats):
    """
    Вывод финальных результатов
    """
    print(f"\n{'='*80}")
    print(f"РЕЗУЛЬТАТЫ РЕШЕНИЯ")
    print(f"{'='*80}\n")
    
    if stats.get('converged', False):
        print(f"✅ Статус: Сходимость достигнута")
    else:
        print(f"⚠️ Статус: Сходимость не достигнута")
    
    print(f"\n📌 Найденный корень:")
    print(f"  x = {root:.12f}")
    
    # Проверяем значение функции в корне
    f_root = Equation.f(root)
    print(f"  f(x) = {f_root:.12e}")
    print(f"  |f(x)| = {abs(f_root):.12e}")
    
    print(f"\n📊 Статистика:")
    print(f"  Количество итераций: {stats.get('iterations', 0)}")
    print(f"  Требуемая точность: ε = {stats.get('epsilon', 1e-4)}")
    
    if history:
        last = history[-1]
        print(f"\n📈 Последняя итерация:")
        print(f"  x_{last['iteration']} = {last['x']:.12f}")
        print(f"  f(x_{last['iteration']}) = {last['f_x']:.12e}")
        print(f"  |f(x_{last['iteration']})| = {abs(last['f_x']):.12e}")
    
    print(f"\n{'='*80}\n")


def main():
    """Главная функция"""
    print("="*80)
    print("ЛАБОРАТОРНАЯ РАБОТА №2")
    print("РЕШЕНИЕ НЕЛИНЕЙНЫХ УРАВНЕНИЙ")
    print("МЕТОД ХОРД")
    print("="*80)
    
    # Локализация корня
    a, b = find_initial_segment()
    
    # Параметры метода
    epsilon = 1e-4
    max_iterations = 1000
    
    # Решение методом хорд
    solver = ChordMethod(Equation.f, epsilon, max_iterations)
    root, history, stats = solver.solve(a, b)
    
    if root is None:
        print("\n❌ Ошибка: Корень не найден")
        print(f"Причина: {stats.get('error', 'Неизвестная ошибка')}")
        return
    
    # Вывод результатов
    print_final_results(root, history, stats)
    
    # Дополнительная проверка
    print("🔍 ПРОВЕРКА РЕШЕНИЯ")
    print("-" * 50)
    print(f"Подстановка корня в уравнение:")
    print(f"  f({root:.12f}) = {Equation.f(root):.12e}")
    print(f"  |f({root:.12f})| = {abs(Equation.f(root)):.12e}")
    
    if abs(Equation.f(root)) < epsilon:
        print(f"  ✅ |f(x)| < ε = {epsilon}")
    else:
        print(f"  ⚠️ |f(x)| > ε = {epsilon}")
    
    print(f"\n{'='*80}")
    print("РАСЧЕТЫ ЗАВЕРШЕНЫ")
    print("="*80)


if __name__ == "__main__":
    main()