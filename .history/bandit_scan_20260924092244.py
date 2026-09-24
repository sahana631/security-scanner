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
        print(f"[{issue['issue_severity']}] {issue['test_id']} - {issue['test_name']}")
        print(f"  File: {issue['filename']}:{issue['line_number']}")
        print(f"  Issue: {issue['issue_text']}")
        print()

if __name__ == "__main__":
    target = sys.argv[1]
    data = run_bandit(target)
    print_output(data)