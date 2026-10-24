def func():
    # Коэффициенты системы Ax = b
    # 4.75x1 - 1.32x2 + 0.21x3 - 0.67x4 = 3.21
    # -0.45x1 + 5.02x2 + 1.43x3 + 0.34x4 = 1.89
    # 0.98x1 + 0.76x2 + 3.51x3 - 0.12x4 = 2.05
    # -0.32x1 + 0.54x2 - 0.87x3 + 6.23x4 = 0.45

    A = [
        [4.75, -1.32,  0.21, -0.67],
        [-0.45, 5.02,  1.43,  0.34],
        [0.98,  0.76,  3.51, -0.12],
        [-0.32, 0.54, -0.87,  6.23]
    ]

    b = [3.21, 1.89, 2.05, 0.45]
    n = 4
    eps = 1e-4

    # Начальное приближение
    x = [0.0, 0.0, 0.0, 0.0]

    iteration = 0
    while True:
        x_old = x[:]
        iteration += 1

        for i in range(n):
            sigma = 0.0
            for j in range(n):
                if j != i:
                    sigma += A[i][j] * x[j]  # используем уже обновлённые значения
            x[i] = (b[i] - sigma) / A[i][i]

        # Проверка сходимости: максимальная разность компонент
        max_diff = max(abs(x[i] - x_old[i]) for i in range(n))

        print(f"Итерация {iteration}: x = {[round(xi, 6) for xi in x]}, "
              f"max_diff = {max_diff:.2e}")

        if max_diff < eps:
            break

    # Вычисление невязки r = b - Ax
    residual = [0.0] * n
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += A[i][j] * x[j]
        residual[i] = b[i] - s

    print("\n\nРешение СЛАУ методом Зейделя")
    print(f"Количество итераций: {iteration}")
    print(f"Точность: ε = {eps}")
    print()
    print("Столбец-вектор переменных:")
    for i in range(n):
        print(f"  x{i+1} = {x[i]:.6f}")
    print()
    print("Вектор невязки (r = b - Ax):")
    for i in range(n):
        print(f"  r{i+1} = {residual[i]:.2e}")


func()