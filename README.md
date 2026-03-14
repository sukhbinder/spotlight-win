# spotlight-win

[![PyPI](https://img.shields.io/pypi/v/spotlight-win.svg)](https://pypi.org/project/spotlight-win/)
[![Tests](https://github.com/sukhbinder/spotlight-win/actions/workflows/test.yml/badge.svg)](https://github.com/sukhbinder/spotlight-win/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/spotlight-win/blob/master/LICENSE)

A Spotlight-like launcher for Windows. Quickly search files, perform calculations, execute system commands, and integrate with LLMs via a plugin system.

## Features

- **File Search**: Fuzzy search for files in configured directories
- **Calculator**: Evaluate mathematical expressions instantly (result copied to clipboard)
- **System Commands**: Shutdown, restart, open Windows Settings
- **Web Search**: Quick Google search from the launcher
- **LLM Integration**: Ask questions directly (requires `q.bat` configured)
- **Plugin System**: Extensible architecture for custom actions
- **Keyboard Shortcut**: Press `Ctrl+Alt+S` to open the launcher

## Installation

Install this tool using `pip`:

```bash
pip install spotlight-win
```

## Usage

Run the application:

```bash
spotlight
```

Or use as a module:

```bash
python -m spotlight_win
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Alt+S` | Open/close the launcher |
| `↓` (Down Arrow) | Navigate to results list |
| `↑` (Up Arrow) | Navigate back to search box |
| `Enter` | Select highlighted item |
| `Esc` | Close the launcher |

### Features

1. **Calculator**: Type a math expression like `2 + 2 * 3` and press Enter. The result is copied to clipboard.

2. **File Search**: Start typing a filename to search through configured directories. Press Enter to open the file.

3. **System Commands**:
   - Type `shutdown` to shut down the computer
   - Type `restart` to restart the computer
   - Type `settings` to open Windows Settings

4. **Web Search**: Type any text and select "Search web for: 'query'" to open a Google search.

5. **LLM Questions**: Type `llm your question` to ask a question using the configured LLM.

6. **Plugin System**: Extend functionality by creating custom plugins (see below).

## Configuration

The application uses a config file at `~/.config/spotlight-win/config.ini`:

```ini
[DEFAULT]
search_path = ~
llm_location = q.bat
max_results = 10
```

Edit `search_path` in `spotlight_win/config.py` to customize the directories searched:

```python
# In spotlight_win/config.py
config['DEFAULT'] = {
    'search_path': os.path.expanduser("~"),
    'llm_location': 'q.bat',  # Path to your LLM runner
    'max_results': '10'
}
```

## Plugin System

spotlight-win uses a pluggy-based plugin system. Create custom plugins by implementing the `match` and `activate` hooks.

### Plugin Structure

```python
from spotlight_win.plugin_manager import hookimpl, hookspec

class MyPlugin:
    @hookimpl
    def match(self, text):
        # Return (score, display_text) or None
        if "mycommand" in text.lower():
            return (100, "Run my command")
        return None

    @hookimpl
    def activate(self, text):
        # Perform the action
        import subprocess
        subprocess.run(["mycommand"])
```

### Registering Plugins

Add your plugin to `spotlight_win/spotlight.py`:

```python
from .my_plugin import MyPlugin
plugin_manager.register(MyPlugin())
```

### Plugin Hook Specification

Plugins implement two hooks:

- `match(text)`: Determines if the plugin should handle the input. Returns `(score, display_text)` or `None`.
- `activate(text)`: Executes the action. Returns a string (e.g., LLM response) or `None`.

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

```bash
cd spotlight-win
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
python -m pytest
```

## License

Apache 2.0