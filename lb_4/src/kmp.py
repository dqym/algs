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


def vector_kmp(sub_str, search_str):
    if "~" in search_str or "~" in sub_str:
        raise ValueError("Символ разделитель присутствует в строке")

    full_str = sub_str + "~" + search_str
    if DEBUG:
        print(f"Сформированная строка для алгоритма КМП: {full_str}")
    p = vector_prefix(full_str)
    sub_len = len(sub_str)
    matching_indices = []

    if DEBUG:
        print(f"\nИщем подстроку '{sub_str}' в строке '{search_str}'")

    for i in range(sub_len + 1, len(full_str)):
        if DEBUG:
            print(f"Проверяем позицию i = {i} с префиксным значением {p[i]}")
        if p[i] == sub_len:
            index = i - 2 * sub_len
            if DEBUG:
                print(f"Найдено вхождение (len({sub_str}) = p[{i}] = {p[i]})). Индекс начала в поисковой строке: {index}")
            matching_indices.append(index)

    if DEBUG:
        if matching_indices:
            print(f"\nВсе найденные индексы вхождений: {matching_indices}")
        else:
            print("\nВхождения не найдены.")

    return matching_indices


if __name__ == "__main__":
    sub_str = input()
    search_str = input()

    res = vector_kmp(sub_str, search_str)
    print(','.join(map(str, res)) if res else -1)
