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
    return login_response


def test_weak_password(base_url):
    print(f"\n--- Testing weak password acceptance on {base_url} ---")

    session = requests.Session()
    weak_password = "a"
    register_and_login(base_url, session, "weak_pw_user", weak_password)

    response = session.get(f"{base_url}/dashboard")
    print(f"  [debug] dashboard status: {response.status_code}, final url: {response.url}")

    if response.url.rstrip("/").endswith("/dashboard"):
        print("VULNERABLE: weak password ('a') was accepted and logged in successfully")
    else:
        print("PROTECTED: weak password was rejected somewhere along registration/login")


def test_session_fixation(base_url):
    print(f"\n--- Testing session fixation on {base_url} ---")

    session = requests.Session()
    planted_value = "attacker_planted_fake_session_value"
    session.cookies.set("session", planted_value, domain="localhost.local")

    username = "fixation_test_user"
    password = "password123"

    reg_page = session.get(f"{base_url}/register")
    csrf_token = extract_csrf_token(reg_page.text)
    data = {"username": username, "password": password}
    if csrf_token:
        data["csrf_token"] = csrf_token
    session.post(f"{base_url}/register", data=data)

    login_page = session.get(f"{base_url}/login")
    csrf_token = extract_csrf_token(login_page.text)
    data = {"username": username, "password": password}
    if csrf_token:
        data["csrf_token"] = csrf_token
    session.post(f"{base_url}/login", data=data)

    print("  [debug] all cookies in jar:")
    for cookie in session.cookies:
        print(f"    name={cookie.name}, value={cookie.value}, domain={cookie.domain}, path={cookie.path}")

    post_login_cookie = session.cookies.get("session")
    print(f"  [debug] post-login session cookie: {post_login_cookie}")

    if post_login_cookie == planted_value:
        print("VULNERABLE: session cookie did not change after login (session fixation possible)")
    else:
        print("PROTECTED: session cookie was regenerated after login")


if __name__ == "__main__":
    base_url = "http://localhost:5051"  # or 5051 depending on target
    test_weak_password(base_url)
    test_session_fixation(base_url)