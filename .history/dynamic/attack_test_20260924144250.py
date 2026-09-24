import requests

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
    attempts = 0
    for i in range(10):
        response = requests.post(
            f"{base_url}/login",
            data={"username": "nonexistent_user", "password": "wrongpass"}
        )
        attempts += 1
        if response.status_code == 429:
            print(f"PROTECTED: Rate limited after {attempts} attempts")
            return
    print(f"VULNERABLE: No rate limiting after {attempts} attempts (all returned {response.status_code})")


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
