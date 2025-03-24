import math
import random
import argparse
from copy import deepcopy


DEBUG = False


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def generate_matrix(n, symmetric=True, max_weight=100):
    """
    Генерирует матрицу весов для полного графа с n вершинами.
    Если symmetric=True, матрица делается симметричной.
    """
    matrix = [[0 if i == j else random.randint(1, max_weight) for j in range(n)] for i in range(n)]
    if symmetric:
        for i in range(n):
            for j in range(i + 1, n):
                matrix[j][i] = matrix[i][j]
    return matrix


def save_matrix(matrix, filename):
    """
    Сохраняет матрицу в файл.
    """
    with open(filename, 'w') as f:
        n = len(matrix)
        f.write(str(n) + "\n")
        for row in matrix:
            f.write(" ".join(map(str, row)) + "\n")


def load_matrix(filename):
    """
    Загружает матрицу из файла.
    """
    with open(filename, 'r') as f:
        n = int(f.readline())
        matrix = []
        for _ in range(n):
            row = list(map(int, f.readline().split()))
            matrix.append(row)
    return matrix


def get_pieces(chain, remaining):
    """
    Формирует список кусков.
    Первый кусок – текущая цепочка (представлена парой: (начало, конец)).
    Остальные куски – одиночные вершины из remaining, где начало = конец.
    """
    pieces = [(chain[0], chain[-1])]
    for v in remaining:
        pieces.append((v, v))
    return pieces


def lower_bound_half_sum(matrix, pieces):
    """
    Вычисляет нижнюю оценку на основе полусуммы двух легчайших допустимых дуг для каждого куска.
    """
    total = 0
    for i, (s_i, e_i) in enumerate(pieces):
        min_out = math.inf
        min_in = math.inf
        for j, (s_j, e_j) in enumerate(pieces):
            if i == j:
                continue
            weight_out = matrix[e_i][s_j]
            if weight_out < min_out:
                min_out = weight_out
            weight_in = matrix[e_j][s_i]
            if weight_in < min_in:
                min_in = weight_in
        total += (min_out + min_in)
    return total / 2


def lower_bound_MST(matrix, pieces):
    """
    Вычисляет нижнюю оценку на основе веса минимального остовного дерева (МОД).
    """
    n = len(pieces)
    if n == 0:
        return 0
    in_mst = [False] * n
    key = [math.inf] * n
    key[0] = 0
    total_weight = 0
    for _ in range(n):
        u = None
        min_val = math.inf
        for i in range(n):
            if not in_mst[i] and key[i] < min_val:
                min_val = key[i]
                u = i
        if u is None:
            break
        in_mst[u] = True
        total_weight += key[u]
        for v in range(n):
            if not in_mst[v]:
                w1 = matrix[pieces[u][1]][pieces[v][0]]
                w2 = matrix[pieces[v][1]][pieces[u][0]]
                w = min(w1, w2)
                if w < key[v]:
                    key[v] = w
    return total_weight


def compute_lower_bound(matrix, chain, remaining):
    """
    Вычисляет нижнюю оценку остатка пути.
    Если remaining пуст, возвращает 0.
    """
    if not remaining:
        return 0
    pieces = get_pieces(chain, remaining)
    lb1 = lower_bound_half_sum(matrix, pieces)
    lb2 = lower_bound_MST(matrix, pieces)
    return max(lb1, lb2)


def tsp_branch_and_bound(matrix, start=0):
    """
    Решение задачи коммивояжёра методом МВиГ (ветвление с отсечением).
    """
    n = len(matrix)
    best = {'cost': math.inf, 'path': None}

    def search(chain, current_cost, remaining):
        nonlocal best
        if len(chain) == n:
            tour_cost = current_cost + matrix[chain[-1]][start]
            if tour_cost < best['cost']:
                best['cost'] = tour_cost
                best['path'] = chain + [start]
                debug_print(f"Найден новый тур: {best['path']} с ценой {best['cost']}")
            return

        candidates = []
        for v in remaining:
            edge_cost = matrix[chain[-1]][v]
            new_chain = chain + [v]
            new_remaining = remaining.copy()
            new_remaining.remove(v)
            lb = compute_lower_bound(matrix, new_chain, new_remaining)
            candidates.append((v, edge_cost, lb))
            debug_print(f"Кандидат: добавляем {v}, edge_cost={edge_cost}, lb={lb}, chain={chain}")

        candidates.sort(key=lambda x: x[1] + x[2])
        for v, edge_cost, lb in candidates:
            total_estimate = current_cost + edge_cost + lb
            debug_print(
                f"Проверка: текущая стоимость={current_cost}, edge_cost={edge_cost}, lb={lb}, total_estimate={total_estimate}, best={best['cost']}")
            if total_estimate > best['cost']:
                debug_print("Отсекаем ветку")
                continue
            new_chain = chain + [v]
            new_remaining = remaining.copy()
            new_remaining.remove(v)
            search(new_chain, current_cost + edge_cost, new_remaining)

    remaining = [i for i in range(n) if i != start]
    search([start], 0, remaining)
    return best['path'], best['cost']


def tour_cost(matrix, tour):
    """
    Вычисляет стоимость данного тура.
    """
    cost = 0
    for i in range(len(tour) - 1):
        cost += matrix[tour[i]][tour[i + 1]]
    return cost


def tsp_approx(matrix, start=0):
    """
    Приближённый алгоритм (АМР).
    """
    n = len(matrix)
    tour = [start] + [i for i in range(n) if i != start] + [start]
    best_cost = tour_cost(matrix, tour)
    debug_print(f"Первая модификация: {tour} с ценой {best_cost}")
    F = n
    modifications = 0
    improved = True
    while improved and modifications < F:
        improved = False
        for idx in range(1, n):
            for j in range(1, n):
                if j == idx:
                    continue
                new_tour = tour[:]
                city = new_tour.pop(idx)
                new_tour.insert(j, city)
                new_cost = tour_cost(matrix, new_tour)
                if new_cost < best_cost:
                    tour = new_tour
                    best_cost = new_cost
                    improved = True
                    modifications += 1
                    debug_print(f"Найдена улучшенная модификация: {tour} с ценой {best_cost}")
                    break
            if improved:
                break
    return tour, best_cost


def main():
    global DEBUG
    parser = argparse.ArgumentParser(description="Решение задачи коммивояжёра методами МВиГ и АМР")
    parser.add_argument("--n", type=int, default=5, help="Количество вершин")
    parser.add_argument("--symmetric", action="store_true", help="Симметричная матрица")
    parser.add_argument("--matrix_file", type=str, help="Файл с матрицей весов")
    parser.add_argument("--method", type=str, choices=["vig", "amr"], default="vig", help="Метод решения: vig или amr")
    parser.add_argument("--debug", action="store_true", help="Включить режим отладки")
    args = parser.parse_args()

    DEBUG = args.debug

    if args.matrix_file:
        matrix = load_matrix(args.matrix_file)
    else:
        matrix = generate_matrix(args.n, symmetric=args.symmetric)
        save_matrix(matrix, "last_matrix")

    print("Матрица весов:")
    for row in matrix:
        print(row)

    start = 0
    if args.method == "vig":
        path, cost = tsp_branch_and_bound(matrix, start)
        print("\nРешение МВиГ (ветвление + отсечение):")
    else:
        path, cost = tsp_approx(matrix, start)
        print("\nРешение АМР (приближённый метод):")
    print("Путь:", path)
    print("Стоимость:", cost)


if __name__ == "__main__":
    main()
