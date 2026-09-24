import requests

def test_sql_injection(base_url):
    print(f"\n--- Testing SQL injection on {base_url} ---")
    payload = {"username": "' OR '1'='1'", "password":"anything"}
    response = requests.post(f"{base_url}/login", data=payload)
    if "dashboard" in response.url or response.status_code == 302:
        print("VULNERABLE: Login may have bypassed authentication")
    else:
        print("SAFE: Injection payload did not bypass login")

if __name__ == "__main__":
    v1_url = "http://localhost:5050"
    v2_url = "http://localhost:5051"

test_sql_injection(v1_url)
test_sql_injection(v2_url)
