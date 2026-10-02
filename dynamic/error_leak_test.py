import requests
import re

def extract_csrf_token(html):
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html, re.DOTALL)
    return match.group(1) if match else None

def register_and_login(base_url, session, username, password):
    reg_page = session.get(f"{base_url}/register")
    csrf_token = extract_csrf_token(reg_page.text)
    data = {"username": username, "password": password}
    if csrf_token:
        data["csrf_token"] = csrf_token
    reg_response = session.post(f"{base_url}/register", data=data)
    print(f"  [debug] register status: {reg_response.status_code}")

    login_page = session.get(f"{base_url}/login")
    csrf_token = extract_csrf_token(login_page.text)
    data = {"username": username, "password": password}
    if csrf_token:
        data["csrf_token"] = csrf_token
    login_response = session.post(f"{base_url}/login", data=data)
    print(f"  [debug] login status: {login_response.status_code}, final url: {login_response.url}")

def test_error_leakage(base_url):
    print(f"\n--- Testing error leakage on {base_url} ---")

    session = requests.Session()
    register_and_login(base_url, session, "error_test_user", "password123")

    trip_page = session.get(f"{base_url}/trips/new")
    csrf_token = extract_csrf_token(trip_page.text)
    data = {
        "destination": "Test",
        "start_date": "not-a-date",
        "end_date": "also-not-a-date",
        #"notes": "test"
    }
    if csrf_token:
        data["csrf_token"] = csrf_token
    response = session.post(f"{base_url}/trips/new", data=data)

    dashboard = session.get(f"{base_url}/dashboard")
    print(f"  [debug] 'not-a-date' appears on dashboard: {'not-a-date' in dashboard.text}")

    print(f"  [debug] status: {response.status_code}")

    leak_indicators = [
        "Traceback (most recent call last)",
        "File \"",
        "Werkzeug Debugger",
        "line ",
        "raise ",
    ]

    found = [indicator for indicator in leak_indicators if indicator in response.text]

    if found:
        print(f"VULNERABLE: response appears to leak internals. Matched indicators: {found}")
    else:
        print("PROTECTED: no stack trace or debugger output found in response")

if __name__ == "__main__":
    test_error_leakage("http://localhost:5051")  # or 5051 depending on target