import ast
import glob
import operator
import os
import re
import subprocess
import sys
import threading
import webbrowser

from PySide6.QtCore import QEvent, QMetaObject, Qt, Slot
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

try:
    import keyboard
except ImportError:
    print("Install the `keyboard` module first: pip install keyboard")
    sys.exit(1)
from fuzzywuzzy import process

# --- CONFIGURE SEARCH PATHS HERE ---
SEARCH_PATHS = [
    os.path.expanduser("~"),  # User home
    r"D:\PROJECTS",  # Custom directory
    r"D:\DEV",  # Another directory
    # Add more as needed
]


# --- Safe math evaluator ---
def safe_eval(expr):
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in allowed_operators:
                return allowed_operators[op_type](_eval(node.left), _eval(node.right))
            else:
                raise ValueError("Unsupported operator")
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in allowed_operators:
                return allowed_operators[op_type](_eval(node.operand))
            else:
                raise ValueError("Unsupported unary operator")
        elif isinstance(node, ast.Expression):
            return _eval(node.body)
        else:
            raise ValueError("Unsupported expression")

    parsed = ast.parse(expr, mode="eval")
    return _eval(parsed.body)


# --- Plugin system ---
class Plugin:
    def match(self, text):
        """Return (score, display_text) or None if not matched."""
        return None

    def activate(self, text):
        """Perform the action when selected."""
        pass


class ShutdownPlugin(Plugin):
    def match(self, text):
        if "shutdown" in text.lower():
            return (100, "Shutdown computer")
        return None

    def activate(self, text):
        os.system("shutdown /s /t 1")  # Windows; adapt for other OS


class RestartPlugin(Plugin):
    def match(self, text):
        if "restart" in text.lower():
            return (100, "Restart computer")
        return None

    def activate(self, text):
        os.system("shutdown /r /t 1")  # Windows; adapt for other OS


class OpenSettingsPlugin(Plugin):
    def match(self, text):
        if "settings" in text.lower():
            return (100, "Open Settings")
        return None

    def activate(self, text):
        os.system("start ms-settings:")  # Windows; adapt for other OS


class LLMPlugin(Plugin):
    def match(self, text):
        if text.lower().startswith("llm "):
            return (100, f"Ask LLM: {text[4:].strip()}")
        return None

    def activate(self, text):
        question = text[4:].strip()
        qbat_path = r"C:\Users\u674012\.local\q.bat"
        try:
            cmd = f"{qbat_path} " f'"{question}"'
            result = subprocess.run(
                [qbat_path, question], capture_output=True, text=True, shell=True
            )
            answer = result.stdout.strip() or result.stderr.strip() or "No response."
        except Exception as e:
            answer = f"Error: {e}"
        return answer  # Return the answer to be displayed in the results box


PLUGINS = [ShutdownPlugin(), RestartPlugin(), OpenSettingsPlugin(), LLMPlugin()]


# --- Spotlight Dialog ---
class SpotlightDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 250)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Spotlight")
        self.search.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.9);
                border: 1px solid rgba(0,0,0,0.15);
                padding: 4px 8px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.search)
        self.results = QListWidget(self)
        self.results.setStyleSheet("""
            QListWidget {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(0,0,0,0.15);
                font-size: 13px;
            }
            QListWidget::item:selected { background:#0060df; color:white; }
        """)
        layout.addWidget(self.results)
        self.results.hide()
        self.search.textChanged.connect(self.update_results)
        self.results.itemActivated.connect(self.handle_result_selected)
        self.search_files = self.index_search_files()
        self.last_results = []

        # Install event filters for keyboard navigation
        self.search.installEventFilter(self)
        self.results.installEventFilter(self)

    def index_search_files(self):
        files = []
        for path in SEARCH_PATHS:
            if os.path.exists(path):
                for f in glob.glob(os.path.join(path, "*"), recursive=True):
                    files.append(os.path.basename(f))

        return files

    def update_results(self, text):
        self.results.clear()
        self.last_results = []
        show_any = False

        # 1. Math evaluation
        if text.strip():
            try:
                if re.fullmatch(r"[0-9\.\+\-\*/\(\)\s]+", text):
                    result = safe_eval(text)
                    QListWidgetItem(f"Result: {result}", self.results)
                    self.last_results.append(("math", result))
                    show_any = True
            except Exception:
                pass

        # 2. Fuzzy file search in specified directories
        if text.strip() and self.search_files:
            matches = process.extract(text.strip(), self.search_files, limit=15)
            for filename, score in matches:
                if score > 60:
                    QListWidgetItem(f"Open: {filename}", self.results)
                    self.last_results.append(("file", filename))
                    show_any = True

        # 3. Plugins (custom actions)
        for plugin in PLUGINS:
            match = plugin.match(text)
            if match:
                score, display_text = match
                QListWidgetItem(display_text, self.results)
                self.last_results.append(("plugin", plugin, display_text))
                show_any = True

        # 4. Web search option
        if text.strip():
            QListWidgetItem(f"Search web for: '{text.strip()}'", self.results)
            self.last_results.append(("web", text.strip()))
            show_any = True

        if show_any:
            self.results.show()
            self.results.setCurrentRow(0)  # Select first item
        else:
            self.results.hide()

    def handle_result_selected(self, item):
        idx = self.results.row(item)
        if idx >= len(self.last_results):
            return
        kind = self.last_results[idx][0]
        if kind == "math":
            result = str(self.last_results[idx][1])
            QApplication.clipboard().setText(result)
        elif kind == "file":
            filename = self.last_results[idx][1]
            found = False
            for path in SEARCH_PATHS:
                matches = glob.glob(os.path.join(path, filename))
                if matches:
                    os.startfile(matches[0])  # Windows; adapt for other OS
                    found = True
                    break
            if not found:
                print("File not found.")
            self.hide()
        elif kind == "plugin":
            plugin = self.last_results[idx][1]
            display_text = self.last_results[idx][2]
            if isinstance(plugin, LLMPlugin):
                # Get the response from LLM
                answer = plugin.activate(self.search.text())
                self.results.clear()
                QListWidgetItem(f"LLM Response: {answer}", self.results)
                self.last_results = [("llm_response", answer)]
                self.results.setCurrentRow(0)
            else:
                plugin.activate(self.search.text())
                self.hide()
        elif kind == "web":
            query = self.last_results[idx][1]
            webbrowser.open(f"https://www.google.com/search?q={query}")
            self.hide()
        elif kind == "llm_response":
            # Optionally copy to clipboard
            QApplication.clipboard().setText(str(self.last_results[idx][1]))
            self.hide()

    @Slot()
    def show_and_focus(self):
        self.show()
        self.search.setFocus()
        self.search.setCursorPosition(0)

    # --- Keyboard navigation ---
    def eventFilter(self, obj, event):
        if obj == self.search and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Down and self.results.isVisible():
                self.results.setFocus()
                self.results.setCurrentRow(0)
                return True
            elif event.key() == Qt.Key_Escape:
                self.close()
                return True
        elif obj == self.results and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                item = self.results.currentItem()
                if item:
                    self.handle_result_selected(item)
                return True
            elif event.key() == Qt.Key_Up and self.results.currentRow() == 0:
                self.search.setFocus()
                return True
            elif event.key() == Qt.Key_Escape:
                self.close()
                return True
        return super().eventFilter(obj, event)


# --- Main ---
def create_app():
    """Create and return the QApplication instance."""
    return QApplication(sys.argv)


def run():
    """Run the Spotlight application."""
    app = create_app()
    dlg = SpotlightDialog()

    def on_hotkey():
        QMetaObject.invokeMethod(dlg, "show_and_focus", Qt.QueuedConnection)

    keyboard.add_hotkey("ctrl+alt+s", on_hotkey)
    threading.Thread(target=keyboard.wait, daemon=True).start()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
