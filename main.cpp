#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <filesystem>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <cstdlib>
#include <cstring>

namespace fs = std::filesystem;

static const std::vector<std::string> BUILTINS = {
    "echo", "type", "exit", "pwd", "cd"
};

// ---- Utility ----
bool is_builtin(const std::string& cmd) {
    return std::find(BUILTINS.begin(), BUILTINS.end(), cmd) != BUILTINS.end();
}

// Simple PATH lookup (ähnlich shutil.which)
std::string which(const std::string& cmd) {
    if (cmd.find('/') != std::string::npos) {
        return fs::exists(cmd) ? cmd : "";
    }

    const char* path_env = std::getenv("PATH");
    if (!path_env) return "";

    std::stringstream ss(path_env);
    std::string dir;

    while (std::getline(ss, dir, ':')) {
        std::string full = dir + "/" + cmd;
        if (access(full.c_str(), X_OK) == 0) {
            return full;
        }
    }
    return "";
}

// ---- Tokenizer (vereinfacht, unterstützt einfache Quotes) ----
std::vector<std::string> split_command(const std::string& line) {
    std::vector<std::string> tokens;
    std::string token;
    bool in_quotes = false;

    for (char c : line) {
        if (c == '"') {
            in_quotes = !in_quotes;
        } else if (std::isspace(c) && !in_quotes) {
            if (!token.empty()) {
                tokens.push_back(token);
                token.clear();
            }
        } else {
            token += c;
        }
    }
    if (!token.empty()) tokens.push_back(token);

    return tokens;
}

// ---- Redirection ----
std::pair<std::vector<std::string>, std::string>
handle_redirection(const std::vector<std::string>& argv) {

    auto it = std::find_if(argv.begin(), argv.end(),
        [](const std::string& s){ return s == ">" || s == "1>"; });

    if (it == argv.end())
        return {argv, ""};

    size_t idx = std::distance(argv.begin(), it);

    std::vector<std::string> cmd_args(argv.begin(), argv.begin() + idx);
    std::string file = (idx + 1 < argv.size()) ? argv[idx + 1] : "";

    if (file.empty()) {
        std::cout << "Syntax error: no file after redirection\n";
        return {cmd_args, ""};
    }

    return {cmd_args, file};
}

// ---- Builtin: type ----
void builtin_type(const std::string& cmd) {
    if (is_builtin(cmd)) {
        std::cout << cmd << " is a shell builtin\n";
        return;
    }

    std::string found = which(cmd);
    if (!found.empty())
        std::cout << cmd << " is " << found << "\n";
    else
        std::cout << cmd << ": not found\n";
}

// ---- Main Shell Loop ----
bool shell_iteration() {

    std::cout << "$ " << std::flush;

    std::string input;
    if (!std::getline(std::cin, input))
        return true;

    if (input.find_first_not_of(" \t\n") == std::string::npos)
        return false;

    auto argv = split_command(input);
    auto [cmd_args, redirect_file] = handle_redirection(argv);

    if (cmd_args.empty())
        return false;

    std::string command = cmd_args[0];

    // ---- Builtins ----
    if (command == "exit")
        return true;

    if (command == "echo") {
        std::string output;
        for (size_t i = 1; i < cmd_args.size(); ++i) {
            output += cmd_args[i];
            if (i + 1 < cmd_args.size()) output += " ";
        }
        output += "\n";

        if (!redirect_file.empty()) {
            int fd = open(redirect_file.c_str(),
                          O_WRONLY | O_CREAT | O_TRUNC, 0644);
            write(fd, output.c_str(), output.size());
            close(fd);
        } else {
            std::cout << output;
        }
        return false;
    }

    if (command == "type") {
        if (cmd_args.size() > 1)
            builtin_type(cmd_args[1]);
        return false;
    }

    if (command == "pwd") {
        std::string cwd = fs::current_path().string() + "\n";
        if (!redirect_file.empty()) {
            int fd = open(redirect_file.c_str(),
                          O_WRONLY | O_CREAT | O_TRUNC, 0644);
            write(fd, cwd.c_str(), cwd.size());
            close(fd);
        } else {
            std::cout << cwd;
        }
        return false;
    }

    if (command == "cd") {
        std::string target;

        if (cmd_args.size() == 1 || cmd_args[1] == "~") {
            target = std::getenv("HOME");
        } else {
            target = cmd_args[1];
        }

        if (chdir(target.c_str()) != 0) {
            perror("cd");
        }
        return false;
    }

    // ---- External Commands ----
    std::string found = which(command);
    if (found.empty()) {
        std::cout << command << ": command not found\n";
        return false;
    }

    pid_t pid = fork();

    if (pid == 0) { // Child
        if (!redirect_file.empty()) {
            int fd = open(redirect_file.c_str(),
                          O_WRONLY | O_CREAT | O_TRUNC, 0644);
            dup2(fd, STDOUT_FILENO);
            close(fd);
        }

        std::vector<char*> args;
        for (auto& s : cmd_args)
            args.push_back(const_cast<char*>(s.c_str()));
        args.push_back(nullptr);

        execv(found.c_str(), args.data());
        perror("execv");
        exit(EXIT_FAILURE);
    }
    else {
        waitpid(pid, nullptr, 0);
    }

    return false;
}

// ---- Entry ----
int main() {
    while (true) {
        if (shell_iteration())
            break;
    }
    return 0;
}
