import requests

try:
    # Try to hit the login endpoint with a dummy payload
    # We expect 401 (Invalid credentials) or 422 (Validation error), NOT 404.
    response = requests.post("http://localhost:8000/api/auth/login", json={"email": "test@example.com", "password": "password"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
