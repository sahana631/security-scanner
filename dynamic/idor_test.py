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

def create_trip(base_url, session, destination):
    trip_page = session.get(f"{base_url}/trips/new")
    csrf_token = extract_csrf_token(trip_page.text)
    data = {
        "destination": destination,
        "start_date": "2026-01-01",
        "end_date": "2026-01-05",
        "notes": "test trip"
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

def test_idor(base_url):
    print(f"\n--- Testing IDOR on {base_url} ---")

    session_a = requests.Session()
    print("Registering user A...")
    register_and_login(base_url, session_a, "user_a_test2", "password123")
    print("User A creating a trip...")
    create_trip(base_url, session_a, "User A's Secret Destination")
    trip_id = find_latest_trip_id(base_url, session_a)

    if trip_id is None:
        print("Could not find a trip ID for user A. Aborting test.")
        return
    print(f"User A's trip ID: {trip_id}")

    session_b = requests.Session()
    print("Registering user B...")
    register_and_login(base_url, session_b, "user_b_test2", "password123")

    print(f"User B attempting to view user A's trip ({trip_id})...")
    response = session_b.get(f"{base_url}/trips/{trip_id}")

    if "User A's Secret Destination" in response.text:
        print("VULNERABLE: User B could see User A's trip data")
    elif response.status_code == 404:
        print("PROTECTED: User B got a 404, access denied")
    elif "/dashboard" in response.url and "not found" in response.text.lower():
        print("PROTECTED: User B was redirected to dashboard with a 'not found' message")
    else:
        print(f"UNCLEAR: status {response.status_code}, final url {response.url}, check response manually")

if __name__ == "__main__":
    test_idor("http://localhost:5050")