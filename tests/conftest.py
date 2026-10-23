import uuid
from dataclasses import asdict

import pytest
import requests

from api.api_client import APIClient
from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_BASE_URL
from models.contact import Contact
from models.user import User
from faker import Faker

fake = Faker()


@pytest.fixture
def auth_token():
    client = APIClient(API_BASE_URL)
    login_payload = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }

    response = client.post("/v1/user/login/usernamepassword", json=login_payload)
    client.close()
    assert response.status_code == 200
    token = response.json()["token"]
    return token


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def unique_email():
    return f"student_{uuid.uuid4().hex[:8]}@gmail.com"


@pytest.fixture
def new_user(unique_email):
    return User(username=unique_email, password="Pass12345$")


@pytest.fixture
def contact_data():
    return Contact(
        name=fake.first_name(),
        lastName=fake.last_name(),
        email=fake.email(),
        phone=fake.numerify("05##########"),
        address=fake.address(),
        description="autotes contact"
    )


@pytest.fixture
def created_contact(api_client, contact_data):
    response = api_client.post("/v1/contacts", json=asdict(contact_data))
    assert response.status_code == 200
    message = response.json()["message"]
    contact_id = message.split(": ")[1]

    created = asdict(contact_data)
    created["id"] = contact_id

    yield created

    list_response = api_client.get("/v1/contacts")
    existing_ids = [contact["id"] for contact in list_response.json()["contacts"]]
    if contact_id in existing_ids:
        delete_response = api_client.delete("/v1/contacts/{contact_id}")
        assert delete_response.status_code ==200


@pytest.fixture
def api_client(auth_token):
    client = APIClient(API_BASE_URL, token=auth_token)
    yield  client
    client.close()


@pytest.fixture
def anonimus_client():
    client = APIClient(API_BASE_URL)
    yield  client
    client.close()