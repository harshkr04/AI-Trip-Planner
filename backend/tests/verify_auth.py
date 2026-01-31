import requests
import uuid

BASE_URL = "http://localhost:8000"
EMAIL = f"test_user_{uuid.uuid4()}@example.com"
PASSWORD = "password123"
NAME = "Test User"

def test_registration():
    print(f"Testing registration for {EMAIL}...")
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "name": NAME
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
    
    if response.status_code == 200:
        print("✅ Registration successful")
        data = response.json()
        if "user" in data and "token" in data:
            print("   - User and token received")
        else:
            print("   ❌ Missing user or token in response")
    else:
        print(f"❌ Registration failed: {response.status_code} - {response.text}")

def test_duplicate_registration():
    print("Testing duplicate registration...")
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "name": NAME
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
    
    if response.status_code == 409:
        print("✅ Duplicate registration correctly returned 409 Conflict")
    else:
        print(f"❌ Expected 409, got {response.status_code} - {response.text}")

def test_login():
    print("Testing login...")
    payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
    
    if response.status_code == 200:
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        test_registration()
        test_duplicate_registration()
        test_login()
    except Exception as e:
        print(f"❌ Test script error: {e}")
