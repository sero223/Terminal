import os
import sys
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


def main():
    sys.stdout.write("$ ")
    sys.stdout.flush()

    inp = input().strip()
    if not inp:
        return False

    tokens = inp.split()
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
        splitted = inp.split()
        directory = str(splitted[1])
        if directory == "~" or len(splitted) == 1:
            os.chdir(os.path.expanduser("~"))
        else:
            os.chdir(directory)
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
