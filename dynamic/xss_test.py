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

def create_trip(base_url, session, destination, notes):
    trip_page = session.get(f"{base_url}/trips/new")
    csrf_token = extract_csrf_token(trip_page.text)
    data = {
        "destination": destination,
        "start_date": "2026-01-01",
        "end_date": "2026-01-05",
        "notes": notes
    }
    if csrf_token:
        data["csrf_token"] = csrf_token
    response = session.post(f"{base_url}/trips/new", data=data)
    print(f"  [debug] create trip status: {response.status_code}, final url: {response.url}")
    return response

def find_latest_trip_id(base_url, session):
    dashboard = session.get(f"{base_url}/dashboard")
    print(f"  [debug] dashboard status: {dashboard.status_code}, final url: {dashboard.url}")
    matches = re.findall(r'/trips/(\d+)', dashboard.text)
    print(f"  [debug] trip id matches found: {matches}")
    if not matches:
        return None
    return max(int(m) for m in matches)

def test_xss(base_url):
    print(f"\n--- Testing XSS on {base_url} ---")

    session = requests.Session()
    print("Registering user...")
    register_and_login(base_url, session, "xss_test_user2", "password123")

    payload = "<script>alert('xss')</script>"
    print("Creating trip with XSS payload in notes...")
    create_trip(base_url, session, "Test Destination", payload)

    trip_id = find_latest_trip_id(base_url, session)
    if trip_id is None:
        print("Could not find a trip ID. Aborting test.")
        return

    response = session.get(f"{base_url}/trips/{trip_id}")

    if "<script>" in response.text:
        print("VULNERABLE: raw <script> tag found in response, XSS payload not escaped")
    else:
        print("PROTECTED: no executable <script> tag survived in the response")
    
if __name__ == "__main__":
    test_xss("http://localhost:5050")  # or 5050 depending on target