"""
Лабораторная работа №1: Визуализация данных
Главный модуль приложения
"""
import sys
from gui.main_window import MainWindow


def main():
    """Точка входа в приложение"""
    app = MainWindow()
    app.mainloop()
    sys.exit(0)


if __name__ == "__main__":
    main()