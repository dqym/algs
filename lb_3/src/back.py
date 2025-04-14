DEBUG = False


def print_matrix(matrix, A, B):
    m, n = len(matrix), len(matrix[0])
    header = "       " + "   ".join([" "] + list(B))
    print(header)
    for i in range(m):
        label = " " if i == 0 else A[i - 1]
        row = "  ".join(f"{matrix[i][j]:2}" for j in range(n))
        print(f"{label:>3} | {row}")
    print()


def compute_dp(price, A, B):
    m, n = len(A), len(B)
    matrix = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        matrix[i][0] = i * price[2]
        if DEBUG:
            print(f"Инициализация dp[{i}][0] = {matrix[i][0]} (удаление символа '{A[i - 1]}')")

    for j in range(1, n + 1):
        matrix[0][j] = j * price[1]
        if DEBUG:
            print(f"Инициализация dp[0][{j}] = {matrix[0][j]} (вставка символа '{B[j - 1]}')")

    if DEBUG:
        print("\nНачальная матрица DP:")
        print_matrix(matrix, A, B)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost_replace = matrix[i - 1][j - 1] + (0 if A[i - 1] == B[j - 1] else price[0])
            cost_insert = matrix[i][j - 1] + price[1]
            cost_delete = matrix[i - 1][j] + price[2]

            matrix[i][j] = min(cost_replace, cost_insert, cost_delete)

            if DEBUG:
                print(f"\nВычисляем dp[{i}][{j}] для A[{i - 1}]='{A[i - 1]}' и B[{j - 1}]='{B[j - 1]}':",
                      f" Заменить = {cost_replace}, Вставить = {cost_insert}, Удалить = {cost_delete}   => dp[{i}][{j}] = {matrix[i][j]}")

    if DEBUG:
        print("\nИтоговая матрица DP:")
        print_matrix(matrix, A, B)

    return matrix


def backtrace(dp, price, A, B):
    i, j = len(A), len(B)
    ops = []
    if DEBUG:
        print("\nОбратный ход по матрице для восстановления операций:")
    while i > 0 or j > 0:
        if DEBUG:
            print(f"\nНа позиции dp[{i}][{j}], текущая стоимость: {dp[i][j]}")

        if i == 0:
            ops.append('I')
            if DEBUG:
                print(f"(I) Вставляем символ '{B[j - 1]}' (i={i}, j={j})")
            j -= 1
        elif j == 0:
            ops.append('D')
            if DEBUG:
                print(f"(D) Удаляем символ '{A[i - 1]}' (i={i}, j={j})")
            i -= 1
        elif A[i - 1] == B[j - 1] and dp[i][j] == dp[i - 1][j - 1]:
            ops.append('M')
            if DEBUG:
                print(f"(M) Символы равны: A[{i - 1}]='{A[i - 1]}' и B[{j - 1}]='{B[j - 1]}'")
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i - 1][j - 1] + price[0]:
            ops.append('R')
            if DEBUG:
                print(f"(R) Заменяем A[{i - 1}]='{A[i - 1]}' на B[{j - 1}]='{B[j - 1]}'")
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i][j - 1] + price[1]:
            ops.append('I')
            if DEBUG:
                print(f"(I) Вставляем символ '{B[j - 1]}'")
            j -= 1
        elif dp[i][j] == dp[i - 1][j] + price[2]:
            ops.append('D')
            if DEBUG:
                print(f"(D) Удаляем символ '{A[i - 1]}'")
            i -= 1

    ops.reverse()
    if DEBUG:
        print("\nПоследовательность операций:", "".join(ops))
    return "".join(ops)


if __name__ == '__main__':
    price = list(map(int, input().split()))
    A = input().strip()
    B = input().strip()

    dp = compute_dp(price, A, B)
    ops = backtrace(dp, price, A, B)

    print(ops)
    print(A)
    print(B)
