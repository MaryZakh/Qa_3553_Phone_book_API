import requests

from config import API_BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD


login = requests.post(f"{API_BASE_URL}/v1/user/login/usernamepassword",
                      json={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD})
token = login.json()["token"]

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}"})


response = session.get(f"{API_BASE_URL}/v1/contacts")
print("session.get without headers =", response.status_code," Authorization:", "Authorization" in response.request.headers)
