# Development Setup Guide

This guide helps you set up your development environment for the YouTube Video Summarizer project.

## 🐍 Python Environment

### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🔧 IDE Configuration

### VS Code / Cursor Setup

1. **Select Python Interpreter**:
   - Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose: `./.venv/bin/python`

2. **Install Recommended Extensions**:
   - Python (Microsoft)
   - Pylance (Microsoft)
   - Black Formatter (optional)

3. **Verify Setup**:
   - Open any Python file
   - Bottom-left should show: `Python 3.9.6 ('.venv': venv)`
   - Try `Cmd+Click` on function names - should navigate to definitions

### Alternative IDEs

**PyCharm**:
- Open project
- Go to Settings → Project → Python Interpreter
- Add interpreter: `./.venv/bin/python`

**Vim/Neovim**:
- Install `coc-pyright` or `ale` for Python support
- The `pyrightconfig.json` file will be automatically detected

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src
```

## 🚀 Running the Application

```bash
# Basic usage
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

# With debug configuration (VS Code/Cursor)
# Use the "Python: Main App" debug configuration
```

## 📁 Project Structure

- `src/` - Core application code
- `src/plugins/` - Plugin system and example plugins
- `tests/` - Unit tests
- `main.py` - Application entry point
- `pyrightconfig.json` - Python type checking configuration

## 🔍 Troubleshooting

**Code navigation not working?**
- Make sure you're using the virtual environment Python interpreter
- Reload your IDE window
- Check that `pyrightconfig.json` is in the project root

**Import errors?**
- Verify virtual environment is activated
- Check that `src/` and `src/plugins/` are in your Python path
- The `pyrightconfig.json` should handle this automatically

**Still having issues?**
- Delete and recreate the virtual environment
- Check the main README.md for more detailed setup instructions 