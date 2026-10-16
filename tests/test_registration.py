import uuid
from dataclasses import asdict

import pytest
import requests
from config import API_BASE_URL
from models.user import User


def test_registration_success(new_user):
    # unique_email = f"student_{uuid.uuid4().hex[:8]}@gmail.com"

    # payload = {
    #     "username": unique_email,
    #     "password": "Password123$"
    # }

    # user = User(
    #     username=unique_email,
    #     password="Password123$"
    # )
    payload = asdict(new_user)

    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert len(body["token"]) > 0


def test_registration_invalid_email_rejected():
    #
    # payload = {
    #     "username": "notanemail",
    #     "password": "Password123$"
    # }

    user = User(
        username="notanemail",
        password="Password123$"
    )
    payload = asdict(user)

    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert "username" in response.json()["message"]
    body = response.json()
    assert body["status"] == 400
    assert body["error"] == "Bad Request"
    assert body["path"] == "/v1/user/registration/usernamepassword"


def test_registration_password_without_uppercase_rejected(unique_email):
    # unique_email = f"student_{uuid.uuid4().hex[:8]}@gmail.com"

    # payload = {
    #     "username": unique_email,
    #     "password": "password123$"
    # }

    user = User(
        username=unique_email,
        password="password123$"
    )
    payload = asdict(user)

    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)

    assert response.status_code == 400
    assert "password" in response.json()["message"]


def test_registration_password_too_short_rejected(unique_email):
    # unique_email = f"student_{uuid.uuid4().hex[:8]}@gmail.com"

    # payload = {
    #     "username": unique_email,
    #     "password": "Pass12$"
    # }

    user = User(
        username=unique_email,
        password="Pass12$"
    )
    payload = asdict(user)

    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)

    assert response.status_code == 400
    assert "password" in response.json()["message"]


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("username","notanemail"),
        ("password","Pass12$"),
        ("password","password123$"),
        ("username","user@"),
    ]
)

def test_registration_with_invalid_value_rejected(new_user, field, bad_value):
    payload = asdict(new_user)
    payload[field] = bad_value

    response=requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)

    assert response.status_code == 400
    assert field in response.json()["message"]
    body = response.json()
    assert "token" not in body
