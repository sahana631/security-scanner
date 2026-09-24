import subprocess
import json
import sys

def run_bandit(target_path):
    result = subprocess.run(
        ["bandit", "-r", target_path, "-f", "json", "-x", "*/.history/*"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def print_output(data):
    issues = data["results"]
    high = [i for i in issues if i["issue_severity"] == "HIGH"]
    medium = [i for i in issues if i["issue_severity"] == "MEDIUM"]
    low = [i for i in issues if i["issue_severity"] == "LOW"]

    print(f"\nScan Summary: {len(high)} High, {len(medium)} Medium, {len(low)} Low\n")

    for severity_group, label in [(high, "HIGH"), (medium, "MEDIUM"), (low, "LOW")]:
        if not severity_group:
            continue
        print(f"--- {label} ---")
        for issue in severity_group:
            print(f"{issue['test_id']} - {issue['test_name']}")
            print(f"  File: {issue['filename']}:{issue['line_number']}")
            print(f"  Issue: {issue['issue_text']}")
            print()

if __name__ == "__main__":
    target = sys.argv[1]
    data = run_bandit(target)
    print_output(data)