# Custom Python Shell

A simple command-line shell implemented in Python, supporting **built-in commands** and **output redirection**. This project demonstrates basic shell functionality like `echo`, `cd`, `pwd`, `type`, and external command execution with `>` redirection.

---

## Features

- **Built-in commands**
  - `echo` – prints text to stdout
  - `cd` – change the current working directory
  - `pwd` – display the current directory
  - `type` – identifies if a command is a shell builtin or external
  - `exit` – exits the shell

- **External commands**
  - Executes any command available in the system path

- **Output redirection**
  - Use `>` or `1>` to redirect standard output to a file
  - Example:
    ```bash
    echo Hello > output.txt
    ```

- **Error handling**
  - Handles invalid commands, missing files, directories, and permission errors gracefully

---

## Usage

1. Clone the repository or download the `shell.py` file:
    ```bash
    git clone <repo_url>
    cd <repo_folder>
    ```

2. Run the shell:
    ```bash
    python shell.py
    ```

3. Try commands inside the shell:
    ```bash
    $ echo Hello World
    Hello World
    $ pwd
    /home/username
    $ cd ..
    $ type echo
    echo is a shell builtin
    $ echo Hello > out.txt
    $ cat out.txt
    Hello
    ```

---

## Notes

- The shell **does not support reading directories** with `cat` – only files can be read.
- Output redirection only affects **standard output**, errors are still printed to the terminal.
- Currently, only **overwrite mode (`>`)** is supported. Append mode (`>>`) is not yet implemented.

---

## Requirements

- Python 3.x
- Unix-like system recommended (Linux, macOS)
- Works on Windows with minor path adjustments

---

## Planned Features

### Autocompletion
- Builtin completion
- Completion with arguments
- Missing completions
- Executable completion
- Multiple completions
- Partial completions

### Pipelines
- Dual-command pipelines
- Pipelines with built-ins
- Multi-command pipelines

### History
- The `history` builtin
- Listing history
- Limiting history entries
- Up-arrow navigation
- Down-arrow navigation
- Executing commands from history

### History Persistence
- Read history from file
- Write history to file
- Append history to file
- Read history on startup
- Write history on exit
- Append history on exit

---

## Future Improvements

- Implement **append mode (`>>`)** for redirection
- Support **piping (`|`)** between commands
- Add **environment variables** and `export`
- Handle **signals** like Ctrl+C more gracefully
- Improve **tab completion** and history

---
