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
    logger = Logger.get_instance("test")

    random_email = f"test-{uuid.uuid1()}@example.com"
    password = "Password123!"

    customer_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": random_email,
        "phone_number": "5145551234",
        "password": password
    }

    logger.info("Registering customer")

    response = client.post(
        "/v1/customers/register",
        data=json.dumps(customer_data),
        content_type="application/json"
    )

    assert response.status_code == 201, response.get_json()

    customer_id = response.get_json()["customer_id"]
    logger.info(f"Customer created (id={customer_id})")

    response = client.get(f"/v1/customers/{customer_id}")

    logger.info("Reading customer")

    assert response.status_code == 200, response.get_json()

    customer = response.get_json()
    assert customer["id"] == customer_id
    assert customer["email"] == random_email

    logger.info("Requesting MFA")

    response = client.post(
        "/v1/auth/mfa/request",
        data=json.dumps({
            "email": random_email,
            "password": password
        }),
        content_type="application/json"
    )

    assert response.status_code == 200, response.get_json()

    otp = response.get_json()["otp"]

    logger.info(f"OTP generated: {otp}")

    logger.info("Verifying MFA")

    response = client.post(
        "/v1/auth/mfa/verify",
        data=json.dumps({
            "email": random_email,
            "otp": otp
        }),
        content_type="application/json"
    )

    assert response.status_code == 200, response.get_json()

    result = response.get_json()
    assert "token" in result
    assert result["message"] == "MFA verified"

    logger.info("JWT generated successfully")

    logger.info("Validating JWT")

    response = client.post(
        "/v1/auth/validate",
        headers={
            "Authorization": f"Bearer {result['token']}"
        }
    )

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["valid"] is True

    logger.info("JWT validated successfully")
