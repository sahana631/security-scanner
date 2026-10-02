import requests
import re

def extract_csrf_token(html):
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html, re.DOTALL)
    return match.group(1) if match else None

response = requests.get("http://localhost:5051/register")
print(f"Status: {response.status_code}")
print(f"Token extracted: {extract_csrf_token(response.text)}")
print("\n--- Searching for 'csrf' in the HTML ---")
for line in response.text.split("\n"):
    if "csrf" in line.lower():
        print(line.strip())