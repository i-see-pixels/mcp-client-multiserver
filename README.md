# MCP Client

MCP Client is a Python application designed to communicate with multiple servers using the standard input/output (stdio) protocol. This allows the client to interact with various backend services in a unified and efficient manner, making it suitable for scenarios where you need to connect to and manage multiple server processes concurrently.

This project is a Python application. The recommended way to manage dependencies and run the project is with [`uv`](https://github.com/astral-sh/uv).

## Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv) (install with `pip install uv`)
- [Gemini API Key](https://aistudio.google.com/apikey)

## Installation

1. Install dependencies:

   ```sh
   uv sync
   ```

2. (Optional) If you use a `.venv`:

   ```sh
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

## Running the Project

To run the main application:

```sh
uv sync
uv run main.py
```

## Resources

- [uv documentation](https://github.com/astral-sh/uv)
- [Python documentation](https://docs.python.org/3/)
