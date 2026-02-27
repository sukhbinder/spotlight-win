# spotlight-win

[![PyPI](https://img.shields.io/pypi/v/spotlight-win.svg)](https://pypi.org/project/spotlight-win/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/spotlight-win?include_prereleases&label=changelog)](https://github.com/sukhbinder/spotlight-win/releases)
[![Tests](https://github.com/sukhbinder/spotlight-win/actions/workflows/test.yml/badge.svg)](https://github.com/sukhbinder/spotlight-win/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/spotlight-win/blob/master/LICENSE)

A Spotlight-like launcher for Windows, inspired by macOS Spotlight. Quickly search files, perform calculations, execute system commands, and more.

## Features

- **File Search**: Fuzzy search for files in configured directories
- **Calculator**: Evaluate mathematical expressions instantly
- **System Commands**: Shutdown, restart, open settings
- **Web Search**: Quick Google search from the launcher
- **LLM Integration**: Ask questions directly from the launcher (requires `qbat`)
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

4. **Web Search**: Type any text and select "Search web for..." to open a Google search.

5. **LLM Questions**: Type `llm your question` to ask a question using the configured LLM.

## Configuration

Edit `SEARCH_PATHS` in `spotlight_win/spotlight.py` to customize the directories searched:

```python
SEARCH_PATHS = [
    os.path.expanduser("~"),  # User home
    r"D:\PROJECTS",
    r"D:\DEV",
    # Add more as needed
]
```

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
