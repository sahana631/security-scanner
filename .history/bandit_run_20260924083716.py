import subprocess
import json
import sys

def run_bandit(target_path):
    result = subprocess.run(
        ['bandit', '-r', target_path, '-f', 'json'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def print_output(data):
    issues = data["results"]
    print(f"Found {len(issues)} issue(s) \n")
    for issue in issues:
        