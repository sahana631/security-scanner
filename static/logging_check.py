import os
import sys
import re

def find_python_files(target_dir):
    py_files = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in (".history", "venv", "__pycache__", ".git")]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files

def check_logging_setup(files):
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            for line in file:
                # .strip() removes trailing newlines (\n) and extra whitespace
                line = line.strip()
                if "import logging" in line or "app.logger" in line:
                    return True
    return False

def split_into_functions(content):
    matches = list(re.finditer(r"def (\w+)\(", content))
    functions = []
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.start()
        end = matches[i+1].start() if i < len(matches)-1 else len(content)
        body = content[start:end]
        functions.append((name, body))
    return functions

def check_security_events(functions):
    SECURITY_KEYWORDS = ["login", "password", "abort(", "401", "403", "404", "unauthorized", "access denied", "not found"]
    LOG_KEYWORDS = ["logger.", "logging.", "app.logger"]

    findings = []
    for name, body in functions:
        body_lower = body.lower()

        is_security_relevant = any(keyword in body_lower for keyword in SECURITY_KEYWORDS)
        has_log = any(keyword in body for keyword in LOG_KEYWORDS)

        if is_security_relevant and not has_log:
            findings.append(name)
    return findings

def print_report(has_logging, findings):
    print(f"\nLogging setup detected: {has_logging}")
    print(f"Security-relevant functions with no adjacent log call: {len(findings)}")
    if findings:
        print("\nReview these manually:")
        for name in findings:
            print(f"  - {name}")

if __name__ == "__main__":
    target = sys.argv[1]
    files = find_python_files(target)
    print(f"Found {len(files)} Python files")

    has_logging = check_logging_setup(files)

    all_functions = []
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
        all_functions.extend(split_into_functions(content))

    findings = check_security_events(all_functions)
    print_report(has_logging, findings)