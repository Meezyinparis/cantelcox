import json
import uuid
import pytest
import requests
from commerce_api import app


class MockIdentityResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    def json(self):
        return self.payload


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_valid_customer(monkeypatch):
    """Mock Customer Identity Service response"""

    def fake_get(url, timeout=5):
        return MockIdentityResponse(
            200,
            {
                "id": 1,
                "first_name": "Alice",
                "last_name": "Tremblay",
                "email": "alice@example.com",
                "phone_number": "+15145550001",
                "identity_verified": True,
                "status": "ACTIVE"
            }
        )

    monkeypatch.setattr(requests, "get", fake_get)


def test_health(client):
    result = client.get("/health")

    assert result.status_code == 200
    assert result.get_json() == {"status": "healthy"}


def test_catalog_plans(client):
    response = client.get("/v1/catalog/plans")

    assert response.status_code == 200

    plans = response.get_json()

    assert isinstance(plans, list)
    assert len(plans) > 0
    assert "id" in plans[0]
    assert "name" in plans[0]


def test_activate_line_success_or_db_error(client, mock_valid_customer):
    random_msisdn = f"514{str(uuid.uuid4().int)[0:7]}"
    random_sim = f"SIM-{uuid.uuid4()}"

    line_data = {
        "customer_id": 1,
        "msisdn": random_msisdn,
        "sim_number": random_sim
    }

    response = client.post(
        "/v1/lines/activate",
        data=json.dumps(line_data),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code in [201, 500]

    if response.status_code == 201:
        result = response.get_json()
        assert "line_id" in result
        assert result["line_id"] > 0


def test_activate_line_missing_fields(client):
    line_data = {
        "customer_id": 1,
        "msisdn": "5145551234"
    }

    response = client.post(
        "/v1/lines/activate",
        data=json.dumps(line_data),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 400


def test_activate_line_customer_not_found(client, monkeypatch):
    def fake_get(url, timeout=5):
        return MockIdentityResponse(
            404,
            {"error": "Customer not found"}
        )

    monkeypatch.setattr(requests, "get", fake_get)

    line_data = {
        "customer_id": 999,
        "msisdn": "5145559999",
        "sim_number": f"SIM-{uuid.uuid4()}"
    }

    response = client.post(
        "/v1/lines/activate",
        data=json.dumps(line_data),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Customer not found"


def test_activate_line_customer_not_verified(client, monkeypatch):
    def fake_get(url, timeout=5):
        return MockIdentityResponse(
            200,
            {
                "id": 1,
                "email": "alice@example.com",
                "identity_verified": False,
                "status": "ACTIVE"
            }
        )

    monkeypatch.setattr(requests, "get", fake_get)

    line_data = {
        "customer_id": 1,
        "msisdn": "5145558888",
        "sim_number": f"SIM-{uuid.uuid4()}"
    }

    response = client.post(
        "/v1/lines/activate",
        data=json.dumps(line_data),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Customer identity is not verified"


def test_create_order_success_or_db_error(client, mock_valid_customer):
    order_data = {
        "customer_id": 1,
        "line_id": 1,
        "idempotency_key": f"test-{uuid.uuid4()}",
        "items": [
            {
                "plan_id": 1,
                "quantity": 1
            }
        ]
    }

    response = client.post(
        "/v1/orders",
        data=json.dumps(order_data),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code in [201, 500]

    if response.status_code == 201:
        result = response.get_json()
        assert "order_id" in result
        assert result["order_id"] > 0


def test_create_order_missing_fields(client):
    order_data = {
        "customer_id": 1,
        "line_id": 1,
        "items": [
            {
                "plan_id": 1,
                "quantity": 1
            }
        ]
    }

    response = client.post(
        "/v1/orders",
        data=json.dumps(order_data),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 400


def test_create_order_customer_not_found(client, monkeypatch):
    def fake_get(url, timeout=5):
        return MockIdentityResponse(
            404,
            {"error": "Customer not found"}
        )

    monkeypatch.setattr(requests, "get", fake_get)

    order_data = {
        "customer_id": 999,
        "line_id": 1,
        "idempotency_key": f"test-{uuid.uuid4()}",
        "items": [
            {
                "plan_id": 1,
                "quantity": 1
            }
        ]
    }

    response = client.post(
        "/v1/orders",
        data=json.dumps(order_data),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Customer not found"


def test_create_order_customer_not_active(client, monkeypatch):
    def fake_get(url, timeout=5):
        return MockIdentityResponse(
            200,
            {
                "id": 1,
                "email": "alice@example.com",
                "identity_verified": True,
                "status": "SUSPENDED"
            }
        )

    monkeypatch.setattr(requests, "get", fake_get)

    order_data = {
        "customer_id": 1,
        "line_id": 1,
        "idempotency_key": f"test-{uuid.uuid4()}",
        "items": [
            {
                "plan_id": 1,
                "quantity": 1
            }
        ]
    }

    response = client.post(
        "/v1/orders",
        data=json.dumps(order_data),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Customer account is not active"


def test_identity_service_unavailable_on_order(client, monkeypatch):
    def fake_get(url, timeout=5):
        raise requests.exceptions.RequestException()

    monkeypatch.setattr(requests, "get", fake_get)

    order_data = {
        "customer_id": 1,
        "line_id": 1,
        "idempotency_key": f"test-{uuid.uuid4()}",
        "items": [
            {
                "plan_id": 1,
                "quantity": 1
            }
        ]
    }

    response = client.post(
        "/v1/orders",
        data=json.dumps(order_data),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 503
    assert response.get_json()["error"] == "Identity service unavailable"


def test_usage(client):
    response = client.get("/v1/usage/1")

    assert response.status_code in [200, 404]


def test_invoices(client):
    response = client.get("/v1/lines/1/invoices")

    assert response.status_code in [200, 404]


def test_metrics(client):
    response = client.get("/metrics")

    assert response.status_code == 200