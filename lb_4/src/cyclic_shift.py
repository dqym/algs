DEBUG = False


def vector_prefix(s):
    print(f"\nСтроится префиксный вектор для строки: {s}")
    n = len(s)
    p = [0] * n
    j = 0
    for i in range(1, n):
        if DEBUG:
            print(f"\nИтерация i = {i}; j = {j}:")
            print(f"Текущий символ на позиции i: s[{i}] = '{s[i]}', текущее значение по j: s[{j}] = '{s[j]}'")
        while j and s[i] != s[j]:
            if DEBUG:
                print(f"Несоответствие: s[{i}] = '{s[i]}' != s[{j}] = '{s[j]}'. Обновляем j: {j} -> {p[j-1]}")
            j = p[j - 1]
        if s[i] == s[j]:
            j += 1
            if DEBUG:
                print(f"Совпадение: s[{i}] = '{s[i]}' == s[{j-1}] = '{s[j-1]}'. Увеличиваем j до {j}")
        p[i] = j
        if DEBUG:
            print(f"Промежуточный префиксный вектор: {p}")
    if DEBUG:
        print(f"\nИтоговый префиксный вектор: {p}\n")
    return p


def kmp(A, B):
    n = len(B)
    m = len(A)

    if DEBUG:
        print(f"\nПоиск строки A = '{A}' в удвоенной строке B + B = '{B + B}'")
        print(f"Длина A = {m}, длина B = {n}, перебор от i = 0 до i = {2 * n - 1}")

    p = vector_prefix(A)
    j = 0
    for i in range(2 * n):
        ch = B[i % n]
        a_ch = A[j] if j < m else "-"
        if DEBUG:
            print(f"\nПроверка для i = {i} (B[{i % n}] = '{ch}'); j = {j} (A[{j}] = '{a_ch}')")

        while j > 0 and ch != A[j]:
            if DEBUG:
                print(f"Несовпадение: '{ch}' != '{A[j]}'. Откат j: {j} -> {p[j - 1]}")
            j = p[j - 1]

        if ch == A[j]:
            j += 1
            if DEBUG:
                print(f"Совпадение: '{ch}' == '{A[j - 1]}'. Увеличиваем j -> {j}")
        else:
            if DEBUG:
                print(f"Нет совпадения: '{ch}' != '{A[j]}' (j = {j})")

        if j == m:
            idx = i - m + 1
            if DEBUG:
                print(f"Подстрока найдена! Начало совпадения в удвоенной строке: {idx}")
            if idx < n:
                if DEBUG:
                    print(f"Индекс {idx} < длина строки {n}, это корректный сдвиг")
                return idx
            j = p[j - 1]
            if DEBUG:
                print(f"Продолжаем поиск, j откат -> {j}")

    if DEBUG:
        print("Совпадений не найдено")
    return -1



def cyclic_shift_check(A, B):
    if len(A) != len(B):
        if DEBUG:
            print("Строки разной длины — циклический сдвиг невозможен.")
        return -1

    if not A and not B:
        if DEBUG:
            print("Обе строки пусты — сдвиг 0")
        return 0

    k = kmp(A, B)
    if k == -1:
        if DEBUG:
            print("Циклический сдвиг не найден")
        return -1

    result = (len(B) - k) % len(B)
    if DEBUG:
        print(f"Циклический сдвиг найден. Сдвиг = {result}")
    return result


if __name__ == "__main__":
    first_str = input()
    second_str = input()

    print(cyclic_shift_check(first_str, second_str))
