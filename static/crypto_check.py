import os
import sys

def find_python_files(target_dir):
    py_files = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in (".history", "venv", "__pycache__", ".git")]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files

def check_tls_enforcement(files):
    session_cookie = False
    has_talisman = False
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            for line in file:
                # .strip() removes trailing newlines (\n) and extra whitespace
                line = line.strip()
                if "SESSION_COOKIE_SECURE" in line:
                    session_cookie = True
                if "Talisman" in line:
                    has_talisman = True
    return (session_cookie, has_talisman)

if __name__ == "__main__":
    target = sys.argv[1]
    files = find_python_files(target)
    print(f"Found {len(files)} Python files")

    session_cookie, has_talisman = check_tls_enforcement(files)
    print(f"SESSION_COOKIE_SECURE config found: {session_cookie}")
    print(f"Talisman (security headers/TLS) found: {has_talisman}")