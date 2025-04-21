import sys
from collections import deque
from AhoGUI import AutomatonVisualizer


DEBUG_MODE = True


def debug_print(*args, **kwargs):
    if DEBUG_MODE:
        print("[DEBUG]", *args, **kwargs)


class AhoCorasickNode:
    def __init__(self, alphabet_size):
        self.transitions = [-1] * alphabet_size
        self.output = []
        self.failure_link = -1
        self.term_link = -1

    def __repr__(self):
        return (f"Node(trans={self.transitions}, out={self.output}, "
                f"fail={self.failure_link}, term={self.term_link})")


class AhoCorasickAutomaton:
    ALPHABET = ['A', 'C', 'G', 'T', 'N']
    ALPHABET_MAP = {char: idx for idx, char in enumerate(ALPHABET)}

    def __init__(self):
        self.nodes = [AhoCorasickNode(len(self.ALPHABET))]
        debug_print("Инициализирован корень узла:", self.nodes[0])

    def _create_node(self):
        node_id = len(self.nodes)
        self.nodes.append(AhoCorasickNode(len(self.ALPHABET)))
        debug_print(f"Создан новый узел {node_id}")
        return node_id

    def _char_index(self, char):
        return self.ALPHABET_MAP[char]

    def add_pattern(self, pattern, pattern_index):
        node = 0
        debug_print(f"=== Вставка паттерна [{pattern_index}] '{pattern}' ===")
        for pos, char in enumerate(pattern):
            debug_print(f"Текущий узел: {node}, символ[{pos}]='{char}'")
            if char not in self.ALPHABET_MAP:
                raise ValueError(f"Недопустимый символ '{char}' в паттерне '{pattern}'")
            idx = self._char_index(char)
            next_node = self.nodes[node].transitions[idx]
            debug_print(f"  Индекс символа: {idx}, переход из {node} -> {next_node}")
            if next_node == -1:
                next_node = self._create_node()
                self.nodes[node].transitions[idx] = next_node
                debug_print(f"  Установлен переход: {node} --{char}--> {next_node}")
            node = next_node
            debug_print(f"  Переходим в узел {node}")
        self.nodes[node].output.append(pattern_index)
        debug_print(f"Узел {node} помечен выходом для паттерна {pattern_index}")
        debug_print("Текущее состояние узлов после вставки:")
        for i, n in enumerate(self.nodes): debug_print(f"  {i}: {n}")

    def build(self):
        queue = deque()
        root = self.nodes[0]
        root.failure_link = 0
        root.term_link = -1
        debug_print("=== Начало построения суффиксных ссылок ===")
        # Инициализация первого уровня
        for idx in range(len(self.ALPHABET)):
            child = root.transitions[idx]
            if child != -1:
                self.nodes[child].failure_link = 0
                self.nodes[child].term_link = -1
                queue.append(child)
                debug_print(f"Корневой переход по '{self.ALPHABET[idx]}' -> узел {child}")
            else:
                root.transitions[idx] = 0

        while queue:
            debug_print("Очередь для BFS:", list(queue))
            current = queue.popleft()
            debug_print(f"Взят из очереди узел {current}")
            for idx in range(len(self.ALPHABET)):
                child = self.nodes[current].transitions[idx]
                if child != -1:
                    fallback = self.nodes[current].failure_link
                    debug_print(f" По символу '{self.ALPHABET[idx]}' сначала fallback={fallback}")
                    while self.nodes[fallback].transitions[idx] == -1:
                        fallback = self.nodes[fallback].failure_link
                        debug_print(f"  Шаг назад по failure: {fallback}")
                    failure = self.nodes[fallback].transitions[idx]
                    self.nodes[child].failure_link = failure
                    if self.nodes[failure].output:
                        self.nodes[child].term_link = failure
                    else:
                        self.nodes[child].term_link = self.nodes[failure].term_link
                    debug_print(f"  Для узла {child}: failure -> {failure}, term -> {self.nodes[child].term_link}")
                    queue.append(child)
                else:
                    self.nodes[current].transitions[idx] = self.nodes[
                        self.nodes[current].failure_link
                    ].transitions[idx]
                    debug_print(f"  Доработан переход из {current} по '{self.ALPHABET[idx]}' на {self.nodes[current].transitions[idx]}")
        debug_print("=== Завершено построение. Итоговое состояние узлов: ===")
        for i, n in enumerate(self.nodes): debug_print(f"  {i}: {n}")

    def search(self, text):
        matches = []
        node = 0
        debug_print("=== Начало поиска в тексте ===")
        for i, char in enumerate(text):
            if char not in self.ALPHABET_MAP:
                debug_print(f"Символ '{char}' пропускается (не в алфавите)")
                node = 0
                continue
            idx = self._char_index(char)
            prev_node = node
            node = self.nodes[node].transitions[idx]
            debug_print(f"Символ[{i}]='{char}', idx={idx}, переход {prev_node}->{node}")
            check = node
            while check != -1:
                if self.nodes[check].output:
                    for pattern_index in self.nodes[check].output:
                        debug_print(f"  Найден паттерн {pattern_index} на позиции {i}")
                        matches.append((i, pattern_index))
                check = self.nodes[check].term_link
                if check != -1:
                    debug_print(f"  Переход по term_link к узлу {check}")
        debug_print("=== Поиск завершён ===")
        return matches


def wildcard_search(text: str, pattern: str, joker: str):
    debug_print("ШАГ 1: Инициализация")
    debug_print(f"Текст: {text}")
    debug_print(f"Шаблон: {pattern}")
    debug_print(f"Джокер: '{joker}'")

    n, m = len(text), len(pattern)

    segments = []
    i = 0
    debug_print("\nШАГ 2: Разбиение шаблона на подстроки (сегменты)")
    while i < m:
        if pattern[i] == joker:
            i += 1
            continue
        j = i
        while j < m and pattern[j] != joker:
            j += 1
        segment = pattern[i:j]
        segments.append((segment, i))
        debug_print(f"  -> Сегмент '{segment}' с позицией в шаблоне {i}")
        i = j

    debug_print("\nШАГ 3: Добавление сегментов в автомат")
    aho = AhoCorasickAutomaton()
    for idx, (seg, _) in enumerate(segments):
        aho.add_pattern(seg, idx)
        debug_print(f"  -> Добавлен сегмент '{seg}' как шаблон с ID {idx}")

    aho.build()
    AutomatonVisualizer.render_png(aho)

    debug_print("\nШАГ 4: Поиск совпадений сегментов в тексте")
    raw = aho.search(text)
    if DEBUG_MODE:
        debug_print("  Результаты поиска:")
        for end_pos, seg_id in raw:
            seg, seg_off = segments[seg_id]
            debug_print(f"    -> Найден сегмент '{seg}' (ID={seg_id}) заканчивается на позиции {end_pos}")

    debug_print("\nШАГ 5: Проверка согласованности позиций")
    count = [0] * (n - m + 1)
    for end_pos, seg_id in raw:
        seg, seg_off = segments[seg_id]
        start_of_match = end_pos - len(seg) + 1
        top = start_of_match - seg_off
        debug_print(f"  -> Сегмент '{seg}' (offset {seg_off}) найден с {start_of_match} по {end_pos} => потенциальная позиция шаблона: {top}")
        if 0 <= top <= n - m:
            count[top] += 1

    debug_print("\nШАГ 6: Финальные совпадения")
    for i in range(n - m + 1):
        if count[i] == len(segments):
            debug_print(f"  >> Шаблон совпадает на позиции {i + 1}")
            print(i + 1)
        else:
            debug_print(f"  .. Позиция {i + 1} отклонена (совпадений: {count[i]}/{len(segments)})")


def main():
    data = sys.stdin.read().split()
    if len(data) < 3:
        return
    T, P, W = data[0], data[1], data[2]

    wildcard_search(T, P, W)


if __name__ == '__main__':
    main()
