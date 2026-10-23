import uuid
from dataclasses import asdict

import pytest
import requests

from config import API_BASE_URL
from faker import Faker

from exploration import response
from models.contact import Contact
from tests.conftest import anonimus_client

fake = Faker()


def test_get_contacts_without_token_rejected(anonimus_client):
    response = anonimus_client.get("/v1/contacts")
    assert response.status_code == 403


def test_get_contacts_with_valid_token(api_client):
    #response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    response = api_client.get("/v1/contacts")
    assert response.status_code == 200

    body = response.json()
    assert "contacts" in body
    assert isinstance(body["contacts"], list)


@pytest.mark.parametrize(
    "authorization",
    [
        pytest.param("Bearer asd123", id="garbage_token"),
        pytest.param("Bearer ", id="empty_token"),
        pytest.param("Basic asd123 ", id="wrong_scheme"),
    ]
)
def test_get_contacts_with_malformed_token_rejected(anonimus_client, authorization):
    response = anonimus_client.get("/v1/contacts", headers={"Authorization": authorization})
    assert response.status_code == 401
    assert "message" in response.json()


# def test_add_contact_success(auth_headers, contact_data):
#     contact_data_dict = asdict(contact_data)
#     response = requests.post(f"{API_BASE_URL}/v1/contacts", json=contact_data_dict, headers=auth_headers)
#     assert response.status_code == 200
#     assert "contact was added" in response.json()["message"].lower()
#
#     list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
#     contacts = list_response.json()["contacts"]
#
#     matching_contacts = [
#         contact
#         for contact in contacts
#         if contact["name"] == contact_data_dict["name"]
#            and contact["lastName"] == contact_data_dict["lastName"]
#            and contact["email"] == contact_data_dict["email"]
#            and contact["phone"] == contact_data_dict["phone"]
#            and contact["address"] == contact_data_dict["address"]
#     ]
#     assert len(matching_contacts) > 0


def test_add_contact_success_1(auth_headers, created_contact):
    response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    contacts = response.json()["contacts"]

    matching_contacts = [contact for contact in response.json()["contacts"] if contact["id"] == created_contact["id"]]
    assert len(matching_contacts) == 1
    assert matching_contacts[0] == created_contact


@pytest.mark.parametrize("missing_field",["name","lastName","address"])

def test_add_contact_with_missing_reqiuired_fields_rejeted(auth_headers,contact_data,missing_field):
    payload = asdict(contact_data)
    del payload[missing_field]

    response = requests.post(f"{API_BASE_URL}/v1/contacts",json=payload,headers=auth_headers)

    assert  response.status_code==400
    assert missing_field in response.json()["message"]


@pytest.mark.parametrize(
    "field, bad_value",
    [
        pytest.param("name", "", id="name_empty"),
        pytest.param("lastName","", id="last_name_empty"),
        pytest.param("address","", id="address_empty"),
        pytest.param("phone","0532649", id="phone_too_short"),
        pytest.param("phone","0532649455355353456", id="phone_too_long"),
        pytest.param("phone", "053264945jfdk", id="phone_letters"),
        pytest.param("phone", "+972053264945", id="phone_plus_and_spaces"),
        pytest.param("email", "notanemail", id="email_no_at_sign"),
    ]
)

def test_add_contact_with_invalid_value_rejected(auth_headers,contact_data,field,bad_value):
    payload = asdict(contact_data)
    payload[field] = bad_value

    response = requests.post(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert field in response.json()["message"]



def test_add_contact_without_token_rejected(contact_data):
    response = requests.post(f"{API_BASE_URL}/v1/contacts", json=asdict(contact_data))
    assert response.status_code == 403


def test_contact_full_lifecycle(auth_headers):
    contact = {
        "name": "Olga",
        "lastName": "Linn",
        "email": "olga@gmail.com",
        "phone": "64985570801",
        "address": "NY",
        "description": "lifecycle demo"
    }
    # CREATE
    create_response = requests.post(f"{API_BASE_URL}/v1/contacts", json=contact, headers=auth_headers)
    assert create_response.status_code == 200
    message = create_response.json()["message"]
    contact_id = message.split(": ")[1]

    # READ
    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == contact_id]
    assert len(matching_contact) == 1
    assert matching_contact[0]["name"] == "Olga"

    payload = dict(contact)
    payload["id"] = contact_id
    payload["name"] = "Anna-Maria"

    # UPDATE
    update_response = requests.put(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)
    assert update_response.status_code == 200

    # READ
    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == contact_id]
    assert len(matching_contact) == 1
    assert matching_contact[0]["name"] == "Anna-Maria"

    # DELETE
    delete_response = requests.delete(f"{API_BASE_URL}/v1/contacts/{contact_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    # READ
    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    contact_ids = [c["id"] for c in list_response.json()["contacts"]]
    assert contact_id not in contact_ids


def test_update_contact_phone(auth_headers, created_contact):
    payload = dict(created_contact)
    payload["phone"] = "059999999999"

    response = requests.put(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)
    assert response.status_code == 200

    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == created_contact["id"]]
    assert len(matching_contact) == 1
    assert matching_contact[0]["phone"] == "059999999999"
    assert matching_contact[0] == payload


def test_update_contact_email(auth_headers, created_contact):
    payload = dict(created_contact)
    payload["email"] = "update@test.com"

    response = requests.put(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)
    assert response.status_code == 200

    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == created_contact["id"]]
    assert len(matching_contact) == 1
    assert matching_contact[0]["email"] == "update@test.com"
    assert matching_contact[0] == payload


@pytest.mark.parametrize(
    "field,new_value",
    [
        pytest.param("name", "Updated", id="name"),
        pytest.param("lastName", "Changed", id="lastName"),
        pytest.param("email", f"updated_{uuid.uuid4().hex[:8]}@test.com", id="email"),
        pytest.param("phone", "05" + str(uuid.uuid4().int)[:8], id="phone"),
        pytest.param("address", "New Street", id="address"),
        pytest.param("description", "updated by autotest", id="description")
    ]
)
def test_update_single_field_changes(auth_headers, created_contact, field, new_value):
    payload = dict(created_contact)
    payload[field] = new_value

    response = requests.put(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)
    assert response.status_code == 200

    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == created_contact["id"]]
    assert len(matching_contact) == 1
    assert matching_contact[0][field] == new_value
    assert matching_contact[0] == payload


@pytest.mark.parametrize("missing_field",["id","name", "lastName","address"])

def test_update_contact_with_missing_reqiuired_fields_rejeted(auth_headers,created_contact,missing_field):
    payload = dict(created_contact)
    del payload[missing_field]

    response = requests.put(f"{API_BASE_URL}/v1/contacts",json=payload,headers=auth_headers)

    assert  response.status_code==400
    assert missing_field in response.json()["message"]


@pytest.mark.parametrize(
    "field, bad_value",
    [
        pytest.param("id", "", id="id_empty"),
        pytest.param("id", str(uuid.uuid4()), id="id_invalid"),
        pytest.param("name", "", id="name_empty"),
        pytest.param("lastName","", id="last_name_empty"),
        pytest.param("address","", id="address_empty"),
        pytest.param("phone","0532649", id="phone_too_short"),
        pytest.param("phone","0532649455355353456", id="phone_too_long"),
        pytest.param("phone", "053264945jfdk", id="phone_letters"),
        pytest.param("phone", "+972053264945", id="phone_plus_and_spaces"),
        pytest.param("email", "notanemail", id="email_no_at_sign"),
    ]
)

def test_update_contact_with_invalid_value_rejected(auth_headers,created_contact,field,bad_value):
    payload = dict(created_contact)
    payload[field] = bad_value

    response = requests.put(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert field in response.json()["message"]


def test_update_contact_without_token_rejected(created_contact):
    payload = dict(created_contact)

    response = requests.put(f"{API_BASE_URL}/v1/contacts", json=payload)
    assert response.status_code == 403


def test_delete_contact_success(auth_headers,created_contact):
    delete_response = requests.delete(f"{API_BASE_URL}/v1/contacts/{created_contact['id']}", headers=auth_headers)
    assert delete_response.status_code == 200

    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    contact_ids = [c["id"] for c in list_response.json()["contacts"]]
    assert created_contact["id"] not in contact_ids


def test_delete_unknown_contact_success(auth_headers):
    response = requests.delete(f"{API_BASE_URL}/v1/contacts/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 400
    assert "not found" in response.json()["message"]

def test_delete_contact_without_token_rejected(created_contact):
    response = requests.delete(f"{API_BASE_URL}/v1/contacts/{created_contact['id']}")
    assert response.status_code == 403

def test_clear_removes_all_contacts_of_a_throwway_account(new_user,contact_data):
    registration = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=asdict(new_user))
    assert registration.status_code==200
    headers = {"Authorization": f"Bearer {registration.json()['token']}"}

    for _ in range(2):
        response = requests.post(f"{API_BASE_URL}/v1/contacts", json=asdict(contact_data), headers=headers)
        assert registration.status_code == 200

    before = requests.get(f"{API_BASE_URL}/v1/contacts", headers=headers).json()["contacts"]
    assert len(before) ==2

    response_delete_all = requests.delete(f"{API_BASE_URL}/v1/contacts/clear",headers=headers)
    assert registration.status_code == 200

    after = requests.get(f"{API_BASE_URL}/v1/contacts", headers=headers).json()["contacts"]
    assert after ==[]