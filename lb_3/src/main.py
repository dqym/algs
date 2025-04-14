DEBUG = False  # Общий режим отладки
DEBUG_VERBOSE = True  # Выводить матрицу после каждой итерации


def print_matrix(matrix, s1, s2):
    print("     ", end="")
    for ch in " " + s2:
        print(f"{ch:>5}", end="")
    print()
    for i in range(len(matrix)):
        ch = " " if i == 0 else s1[i - 1] if i - 1 < len(s1) else " "
        print(f"{ch:>3} |", end="")
        for j in range(len(matrix[0])):
            print(f"{matrix[i][j]:5}", end="")
        print()
    print()


def levenshtein(price, s1, s2):
    # price[0] - replace, price[1] - insert, price[2] - delete
    m, n = len(s1), len(s2)
    matrix = [[0] * (n + 1) for _ in range(m + 1)]

    if DEBUG:
        print("==> Инициализация первой строки (вставки):")
    for j in range(1, n + 1):
        matrix[0][j] = j * price[1]
        if DEBUG:
            print(f"  Вставить '{s2[j - 1]}' в позицию 0: {j} * {price[1]} = {matrix[0][j]}")

    if DEBUG:
        print("\n==> Инициализация первого столбца (удаления):")
    for i in range(1, m + 1):
        matrix[i][0] = i * price[2]
        if DEBUG:
            print(f"  Удалить '{s1[i - 1]}' из позиции {i - 1}: {i} * {price[2]} = {matrix[i][0]}")

    if DEBUG_VERBOSE:
        print("\nНачальная матрица:")
        print_matrix(matrix, s1, s2)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            a, b = s1[i - 1], s2[j - 1]
            match_or_replace = 0 if a == b else price[0]
            cost_replace = matrix[i - 1][j - 1] + match_or_replace
            cost_insert = matrix[i][j - 1] + price[1]
            cost_delete = matrix[i - 1][j] + price[2]
            matrix[i][j] = min(cost_replace, cost_insert, cost_delete)

            if DEBUG:
                print(f"\n==> Позиция s1[{i - 1}]='{a}' и s2[{j - 1}]='{b}' (i={i}, j={j}):")
                if a == b:
                    print("  Символы совпадают")
                    print(f"  Стоимость: dp[{i - 1}][{j - 1}] = {matrix[i - 1][j - 1]}")
                else:
                    print("  Символы разные")
                    print(f"  Стоимость замены: dp[{i - 1}][{j - 1}] + {price[0]} = {cost_replace}")
                print(f"  Стоимость вставки : dp[{i}][{j - 1}] + {price[1]} = {cost_insert}")
                print(f"  Стоимость удаления : dp[{i - 1}][{j}] + {price[2]} = {cost_delete}")
                print(f"  --> Выбрано минимальное значение: {matrix[i][j]}")

            if DEBUG_VERBOSE:
                print("\nТекущая матрица:")
                print_matrix(matrix, s1, s2)

    if DEBUG:
        print("\n==> Финальная матрица:")
        print_matrix(matrix, s1, s2)

    return matrix[m][n], matrix


def extend_levenshtein_first(matrix, price, s1, s2, extension):
    """
    Расширение первой строки. Предполагается, что matrix уже содержит матрицу расстояний для старой s1.
    После расширения s1 = s1 + extension, вычисляем только новые строки.
    Временная сложность: O( |extension| * len(s2) )
    """
    old_m = len(s1)
    s1_extended = s1 + extension
    new_m = len(s1_extended)
    n = len(s2)

    if DEBUG:
        print(f"\n==> Расширяем первую строку '{s1}' на: '{extension}'")

    # Для новых строк создаём строки в матрицы
    for i in range(old_m + 1, new_m + 1):
        # Вычисляем dp[i][0]: удаление всех символов s1_extended[0:i]
        new_row = [0] * (n + 1)
        new_row[0] = i * price[2]
        for j in range(1, n + 1):
            a = s1_extended[i - 1]
            b = s2[j - 1]
            cost_replace = matrix[i - 1][j - 1] + (0 if a == b else price[0])
            cost_insert = new_row[j - 1] + price[1]
            cost_delete = matrix[i - 1][j] + price[2]
            new_row[j] = min(cost_replace, cost_insert, cost_delete)

            if DEBUG:
                print(f"\n==> Расширение: новая позиция s1[{i - 1}]='{a}' и s2[{j - 1}]='{b}' (i={i}, j={j}):")
                if a == b:
                    print("  Символы совпадают")
                    print(f"  Стоимость: dp[{i - 1}][{j - 1}] = {matrix[i - 1][j - 1]}")
                else:
                    print(f"  Стоимость замены: dp[{i - 1}][{j - 1}] + {price[0]} = {cost_replace}")
                print(f"  Стоимость вставки: dp[{i}][{j - 1}] + {price[1]} = {cost_insert}")
                print(f"  Стоимость удаления: dp[{i - 1}][{j}] + {price[2]} = {cost_delete}")
                print(f"  --> Выбрано: {new_row[j]}")
        matrix.append(new_row)

    if DEBUG:
        print("\n==> Финальная матрица после расширения первой строки:")
        print_matrix(matrix, s1_extended, s2)
    return matrix[new_m][n], s1_extended


def extend_levenshtein_second(matrix, price, s1, s2, extension):
    """
    Расширение второй строки. Предполагается, что matrix уже содержит матрицу расстояний для старой s2.
    После расширения s2 = s2 + extension, вычисляем только новые столбцы.
    Временная сложность: O( |extension| * len(s1) )
    """
    old_n = len(s2)
    s2_extended = s2 + extension
    new_n = len(s2_extended)
    m = len(s1)

    if DEBUG:
        print(f"\n==> Расширяем вторую '{s2}' строку на: '{extension}'")

    # Добавляем новые столбцы ко всем строкам матрицы
    for i in range(m + 1):
        # Для строки 0, базовая инициализация, если i == 0: dp[0][j] = j * price[1]
        for j in range(old_n + 1, new_n + 1):
            if i == 0:
                val = j * price[1]
                matrix[0].append(val)
            else:
                a = s1[i - 1]
                b = s2_extended[j - 1]
                cost_replace = matrix[i - 1][j - 1] + (0 if a == b else price[0])
                cost_insert = matrix[i][j - 1] + price[1]
                cost_delete = matrix[i - 1][j] + price[2]
                matrix[i].append(min(cost_replace, cost_insert, cost_delete))

                if DEBUG:
                    print(f"\n==> Расширение: новая позиция s1[{i - 1}]='{a}' и s2[{j - 1}]='{b}' (i={i}, j={j}):")
                    if a == b:
                        print("  Символы совпадают")
                        print(f"  Стоимость: dp[{i - 1}][{j - 1}] = {matrix[i - 1][j - 1]}")
                    else:
                        print(f"  Стоимость замены: dp[{i - 1}][{j - 1}] + {price[0]} = {cost_replace}")
                    print(f"  Стоимость вставки: dp[{i}][{j - 1}] + {price[1]} = {cost_insert}")
                    print(f"  Стоимость удаления: dp[{i - 1}][{j}] + {price[2]} = {cost_delete}")
                    print(f"  --> Выбрано: {matrix[i][j]}")

    if DEBUG:
        print("\n==> Финальная матрица после расширения второй строки:")
        print_matrix(matrix, s1, s2_extended)
    return matrix[m][new_n], s2_extended


if __name__ == '__main__':
    if not DEBUG:
        DEBUG_VERBOSE = False

    price = list(map(int, input().split()))
    s1 = input().strip()
    s2 = input().strip()

    dist, matrix = levenshtein(price, s1, s2)
    print(f"\nРедакционное расстояние: {dist}")

    print("\nВыберите строку для расширения:")
    print("1 - расширить первую строку")
    print("2 - расширить вторую строку")
    print("0 - не расширять")
    choice = input("Ваш выбор: ").strip()

    if choice == "1":
        extension = input("Введите продолжение первой строки: ")
        new_dist, s1_extended = extend_levenshtein_first(matrix, price, s1, s2, extension)
        print(f"\nНовое редакционное расстояние для '{s1_extended}' и '{s2}': {new_dist}")
    elif choice == "2":
        extension = input("Введите продолжение второй строки: ")
        new_dist, s2_extended = extend_levenshtein_second(matrix, price, s1, s2, extension)
        print(f"\nНовое редакционное расстояние для '{s1}' и '{s2_extended}': {new_dist}")
    else:
        print("\nРасширение не выполнено.")
