from main import AhoCorasickAutomaton, get_result
from tkinter import Tk, Label, Button, Text, Scrollbar, filedialog, END, Frame, BOTH
from PIL import Image, ImageTk
import graphviz


class AutomatonVisualizer:
    @staticmethod
    def render_png(automaton: AhoCorasickAutomaton, filename_base: str = "tree"):
        dot = graphviz.Digraph('AhoCorasick', format='png')
        for i, node in enumerate(automaton.nodes):
            label = f"{i}\n{node.output}"
            dot.node(str(i), label)

        for u, node in enumerate(automaton.nodes):
            for idx, v in enumerate(node.transitions):
                if v != -1 and v != 0:
                    dot.edge(str(u), str(v), label=AhoCorasickAutomaton.ALPHABET[idx])

        for v, node in enumerate(automaton.nodes):
            if v != 0:
                dot.edge(str(v), str(node.failure_link), style='dashed', label='fail')
            if node.term_link != -1:
                dot.edge(str(v), str(node.term_link), style='dotted', label='term')

        output_path = dot.render(filename=filename_base, cleanup=True)
        return output_path


class AhoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Aho-Corasick Visualizer")
        self.root.geometry("1000x700")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)

        left_frame = Frame(root)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_rowconfigure(5, weight=1)

        Label(left_frame, text="Text to search in:").pack(anchor="w")
        self.text_input = Text(left_frame, height=5, wrap="word")
        self.text_input.pack(fill=BOTH, expand=False)

        Label(left_frame, text="Patterns (one per line):").pack(anchor="w", pady=(10, 0))
        self.pattern_input = Text(left_frame, height=5, wrap="word")
        self.pattern_input.pack(fill=BOTH, expand=False)

        self.run_button = Button(left_frame, text="Build Automaton & Visualize", command=self.run)
        self.run_button.pack(pady=10)

        Label(left_frame, text="Matches:").pack(anchor="w")
        self.result_output = Text(left_frame, height=10, wrap="word")
        self.result_output.pack(fill=BOTH, expand=True)

        right_frame = Frame(root)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.image_label = Label(right_frame)
        self.image_label.grid(row=0, column=0, sticky="nsew")

    def run(self):
        text = self.text_input.get("1.0", END).strip()
        patterns = self.pattern_input.get("1.0", END).strip().splitlines()
        self.result_output.delete("1.0", END)

        if not text or not patterns:
            self.result_output.insert(END, "Введите текст и хотя бы один паттерн.\n")
            return

        try:
            matches, automaton = get_result(text, patterns)

            self.result_output.insert(END, "\n".join(matches))

            image_path = AutomatonVisualizer.render_png(automaton)
            image = Image.open(image_path)
            image.thumbnail((800, 600), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo

        except ValueError as e:
            self.result_output.insert(END, f"Ошибка: {e}\n")
