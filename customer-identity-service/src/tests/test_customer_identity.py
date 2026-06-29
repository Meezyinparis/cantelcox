

import json
import uuid
import pytest
from logger import Logger
from customer_identity_api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    result = client.get("/health")
    assert result.status_code == 200
    assert result.get_json()["status"] == "healthy"


def test_customer_identity_flow(client):
    """Smoke test for registration and MFA flow"""
    logger = Logger.get_instance("test")

    random_email = f"test-{uuid.uuid1()}@example.com"

    customer_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": random_email,
        "phone_number": "5145551234"
    }

    response = client.post(
        "/v1/customers/register",
        data=json.dumps(customer_data),
        content_type="application/json"
    )

    assert response.status_code == 201, f"Failed to create customer: {response.get_json()}"
    customer_id = response.get_json()["customer_id"]
    assert customer_id > 0
    logger.debug(f"Created customer with ID: {customer_id}")

    response = client.get(f"/v1/customers/{customer_id}")
    assert response.status_code == 200, f"Failed to get customer: {response.get_json()}"

    customer = response.get_json()
    assert customer["id"] == customer_id
    assert customer["email"] == random_email

    response = client.post(
        "/v1/auth/mfa/request",
        data=json.dumps({"email": random_email}),
        content_type="application/json"
    )

    assert response.status_code == 200, f"Failed to request MFA: {response.get_json()}"
    otp = response.get_json()["otp"]
    assert otp is not None
    logger.debug(f"Generated OTP: {otp}")

    response = client.post(
        "/v1/auth/mfa/verify",
        data=json.dumps({
            "email": random_email,
            "otp": otp
        }),
        content_type="application/json"
    )

    assert response.status_code == 200, f"Failed to verify MFA: {response.get_json()}"
    result = response.get_json()
    assert "token" in result
    assert result["message"] == "MFA verified"