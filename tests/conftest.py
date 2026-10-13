import pytest
import requests

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_BASE_URL


@pytest.fixture
def auth_token():
    payload = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }

    response = requests.post(f"{API_BASE_URL}/v1/user/login/usernamepassword", json=payload)
    assert response.status_code == 200
    token = response.json()["token"]
    return token


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
