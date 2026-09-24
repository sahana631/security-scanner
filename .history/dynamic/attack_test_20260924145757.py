import requests
import re

def extract_csrf_token(html):
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html, re.DOTALL)
    return match.group(1) if match else None

def test_sql_injection(base_url):
    print(f"\n--- Testing SQL injection on {base_url} ---")
    payload = {"username": "' OR '1'='1'", "password":"anything"}
    response = requests.post(f"{base_url}/login", data=payload)
    if "dashboard" in response.url or response.status_code == 302:
        print("VULNERABLE: Login may have bypassed authentication")
    else:
        print("SAFE: Injection payload did not bypass login")

def test_rate_limiting(base_url):
    print(f"\n--- Testing rate limiting on {base_url} ---")
    session = requests.Session()
    for i in range(10):
        login_page = session.get(f"{base_url}/login")
        csrf_token = extract_csrf_token(login_page.text)
        data = {"username": "nonexistent_user", "password": "wrongpass"}
        if csrf_token:
            data["csrf_token"] = csrf_token
        response = session.post(f"{base_url}/login", data=data)
        print(f"  Attempt {i+1}: GET={login_page.status_code}, POST={response.status_code}")
        if login_page.status_code == 429 or response.status_code == 429:
            print(f"PROTECTED: Rate limited on attempt {i+1}")
            return
    print(f"VULNERABLE: No rate limiting after 10 attempts")


def test_security_headers(base_url):
    print(f"\n--- Testing security headers on {base_url} ---")
    response = requests.get(base_url)
    headers_to_check = [
        "X-Frame-Options",
        "Content-Security-Policy",
        "X-Content-Type-Options"
    ]
    for header in headers_to_check:
        if header in response.headers:
            print(f"PRESENT: {header} = {response.headers[header]}")
        else:
            print(f"MISSING: {header}")


def test_csrf_protection(base_url):
    print(f"\n--- Testing CSRF protection on {base_url} ---")
    session = requests.Session()
    login_page = session.get(f"{base_url}/login")

    response = session.post(
        f"{base_url}/login",
        data={"username": "someuser", "password": "somepass"}
    )

    if "csrf_token" in login_page.text:
        print("PROTECTED: CSRF token found in login form")
    else:
        print("VULNERABLE: No CSRF token found in login form")

if __name__ == "__main__":
    v1_url = "http://localhost:5050"
    v2_url = "http://localhost:5051"

    for url in [v1_url, v2_url]:
        test_sql_injection(url)
        test_rate_limiting(url)
        test_security_headers(url)
        test_csrf_protection(url)