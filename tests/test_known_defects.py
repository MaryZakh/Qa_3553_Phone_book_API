from dataclasses import asdict

import pytest
import requests

from config import API_BASE_URL


def delete_if_created(response,auth_headers):
    if response.status_code ==200:
        created_id = response.json()["message"].split(": ")[1]
        requests.delete(f"{API_BASE_URL}/v1/contacts/{created_id}",headers=auth_headers)


@pytest.mark.parametrize("missing_field",["email","phone"])
def test_add_contact_without_email_or_phone_rejected(auth_headers,contact_data,missing_field):
    payload = asdict(contact_data)
    del payload[missing_field]

    response = requests.post(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)

    try:
        assert response.status_code ==400
        assert missing_field in response.json()["message"]
    finally:
        delete_if_created(response,auth_headers)



def test_duplicate_contact_rejected(auth_headers,created_contact,contact_data):

    response = requests.post(f"{API_BASE_URL}/v1/contacts", json=asdict(contact_data), headers=auth_headers)

    try:
        assert response.status_code ==409
    finally:
        delete_if_created(response,auth_headers)

