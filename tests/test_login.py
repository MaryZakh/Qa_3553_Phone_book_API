from dataclasses import asdict

import pytest
import requests

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_BASE_URL
from exploration import payload
from models.user import User
from tests.conftest import new_user, anonimus_client


def test_login_with_valid_credentials_return_token():
    # payload = {
    #     "username": TEST_USER_EMAIL,
    #     "password": TEST_USER_PASSWORD
    # }

    user = User(username=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
    payload = asdict(user)

    response = requests.post(f"{API_BASE_URL}/v1/user/login/usernamepassword",json=payload)
    assert response.status_code ==200

    body = response.json()
    assert "token" in body
    assert len(body["token"])>0
    assert "application/json" in response.headers["Content-Type"]




@pytest.mark.parametrize(
    "username,password",
    [
        pytest.param(TEST_USER_EMAIL,"wrongpass1$", id="wrong_pass_without_uppercase"),
        pytest.param(TEST_USER_EMAIL,"", id="wrong_pass_empty"),
        pytest.param("notanemail",TEST_USER_PASSWORD, id="username_not_an_email"),
        pytest.param("",TEST_USER_PASSWORD, id="username_empty"),
    ]
)
def test_login_with_invalid_credentials_rejected(anonimus_client,username,password):
    payload = asdict(User(username=username,password=password))

    response = anonimus_client.post("/v1/user/login/usernamepassword", json=payload)
    assert response.status_code==401
    assert "incorrect" in response.json()["message"].lower()


def test_login_unknown_user_error_rejected(new_user):
    payload = asdict(new_user)

    response = requests.post(f"{API_BASE_URL}/v1/user/login/usernamepassword", json=payload)
    assert response.status_code==401
    assert "incorrect" in response.json()["message"].lower()
    assert response.json()["error"]=="Unauthorized"