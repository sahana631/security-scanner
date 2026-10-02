import subprocess
import json
import sys

def run_pip_audit(requirements_path):
    result = subprocess.run(
        ["pip-audit", "-r", requirements_path, "-f", "json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def print_report(data):
    dependencies = data["dependencies"]
    vulnerable_packages = [dep for dep in dependencies if dep["vulns"]]

    total_unique_cves = set()
    for dep in vulnerable_packages:
        for vuln in dep["vulns"]:
            total_unique_cves.add(vuln["id"])
    
    print(f"\nScanned {len(dependencies)} packages")
    print(f"Vulnerable packages: {len(vulnerable_packages)}")
    print(f"Unique CVEs found: {len(total_unique_cves)}\n")

    for dep in vulnerable_packages:
        print(f"--- {dep['name']} {dep['version']} ---")
        seen_ids = set()
        for vuln in dep["vulns"]:
            if vuln["id"] in seen_ids:
                continue
            seen_ids.add(vuln["id"])
            fix = ", ".join(vuln["fix_versions"]) if vuln["fix_versions"] else "no fix available"
            print(f"  {vuln['id']} -> fix: {fix}")
        print()

if __name__ == "__main__":
    target = sys.argv[1]
    data = run_pip_audit(target)
    print_report(data)