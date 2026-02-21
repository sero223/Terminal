import os
import sys
import shlex
import shutil

BUILTINS = ["echo", "type", "exit", "pwd", "cd"]

def builtin_type(cmd):
    if cmd in BUILTINS:
        sys.stdout.write(f"{cmd} is a shell builtin\n")
        return

    found = shutil.which(cmd)
    if found:
        sys.stdout.write(f"{cmd} is {found}\n")
    else:
        sys.stdout.write(f"{cmd}: not found\n")

# ---- Redirection ----
def handle_redirection(argv):

    if ">" in argv:
        location = argv.index(">")
    elif "1>" in argv:
        location = argv.index("1>")
    else:
        return argv, None

    # Alles vor '>' ist Befehl, alles nach '>' die Datei
    command_args = argv[:location]
    target_file = argv[location + 1] if len(argv) > location + 1 else None

    if not target_file:
        sys.stdout.write("Syntax error: no file after redirection\n")
        return command_args, None

    return command_args, target_file

# ---- Command Split ----
def split_command(line):
    return shlex.split(line)  # vereinfacht mit shlex

# ---- Main ----
def main():
    sys.stdout.write("$ ")
    sys.stdout.flush()

    inp = input()
    if not inp.strip():
        return False

    argv = split_command(inp)
    argv, redirect_file = handle_redirection(argv)
    if not argv:
        return False

    command = argv[0]

    # ---- Builtins ----
    if command == "exit":
        return True

    if command == "echo":
        output = " ".join(argv[1:]) + "\n"
        if redirect_file:
            with open(redirect_file, "w") as f:  # überschreiben wie '>'
                f.write(output)
        else:
            sys.stdout.write(output)
        return False

    if command == "type":
        if len(argv) > 1:
            builtin_type(argv[1])
        return False

    if command == "pwd":
        output = os.getcwd() + "\n"
        if redirect_file:
            with open(redirect_file, "w") as f:
                f.write(output)
        else:
            sys.stdout.write(output)
        return False

    if command == "cd":
        target = os.path.expanduser("~") if len(argv) == 1 or argv[1] == "~" else argv[1]
        try:
            os.chdir(target)
        except FileNotFoundError:
            sys.stdout.write(f"cd: {target}: No such file or directory\n")
        except NotADirectoryError:
            sys.stdout.write(f"cd: {target}: Not a directory\n")
        except PermissionError:
            sys.stdout.write(f"cd: {target}: Permission denied\n")
        return False

    # ---- External commands ----
    found = shutil.which(command)
    if not found:
        sys.stdout.write(f"{command}: command not found\n")
        return False

    pid = os.fork()
    if pid == 0:
        # Child: stdout umleiten, falls nötig
        if redirect_file:
            fd = os.open(redirect_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
            os.dup2(fd, 1)  # stdout auf Datei
            os.close(fd)
        os.execv(found, argv)
    else:
        os.waitpid(pid, 0)

    return False

# ---- Run Shell ----
if __name__ == "__main__":
    while True:
        if main():
            break
