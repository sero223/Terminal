import os
import sys, shlex
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

def split_command(line):
    tokens = []
    current = []
    escape = False

    for ch in line:
        if escape:
            current.append(ch)
            escape = False
        elif ch == "\\":
            escape = True
        elif ch.isspace():
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(ch)

    if escape:
        # trailing backslash → treated as literal backslash
        current.append("\\")

    if current:
        tokens.append("".join(current))

    return tokens


def main():
    sys.stdout.write("$ ")
    sys.stdout.flush()

    inp = input()
    tokens = split_command(inp)
    if not tokens:
        return Flase
	

    command = tokens[0]
    argv = tokens

    # ---- builtins ----
    if command == "exit":
        return True

    if command == "echo":
        sys.stdout.write(" ".join(argv[1:]) + "\n")
        return False

    if command == "type":
        if len(argv) > 1:
            builtin_type(argv[1])
        return False

    if command == "pwd":
        sys.stdout.write(os.getcwd() + "\n")
        return False

    if command == "cd":
        if len(argv) == 1 or argv[1] == "~":
            target = os.path.expanduser("~")
        else:
            target = argv[1]

        try:
            os.chdir(target)
        except FileNotFoundError:
            sys.stdout.write(f"cd: {target}: No such file or directory\n")
        except NotADirectoryError:
            sys.stdout.write(f"cd: {target}: Not a directory\n")
        except PermissionError:
            sys.stdout.write(f"cd: {target}: Permission denied\n")

        return False

    # ---- external commands ----
    found = shutil.which(command)
    if not found:
        sys.stdout.write(f"{command}: command not found\n")
        return False

    pid = os.fork()
    if pid == 0:
        os.execv(found, argv)
    else:
        os.waitpid(pid, 0)

    return False


if __name__ == "__main__":
    while True:
        if main():
            break
