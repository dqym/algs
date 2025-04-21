import sys
from collections import deque
import argparse

DEBUG_MODE = False


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


def get_result(text: str, patterns: list[str]):
    automaton = AhoCorasickAutomaton()
    lengths = [len(p) for p in patterns]
    for i, p in enumerate(patterns):
        automaton.add_pattern(p, i)
    automaton.build()
    raw = automaton.search(text)
    res = []
    for end, pid in raw:
        start = end - lengths[pid] + 1
        res.append((start+1, pid+1))
    res.sort()
    return res, automaton


def run_console():
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    text = data[0]
    n = int(data[1])
    patterns = data[2:2+n]
    matches, _ = get_result(text, patterns)
    w = sys.stdout.write
    for pos, idx in matches:
        w(f"{pos} {idx}\n")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", choices=["gui","console"], default="console")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main():
    global DEBUG_MODE
    args = parse_args()
    DEBUG_MODE = args.debug
    if args.output == "console":
        run_console()
    else:
        from AhoGUI import AhoGUI, Tk
        root = Tk()
        AhoGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()
