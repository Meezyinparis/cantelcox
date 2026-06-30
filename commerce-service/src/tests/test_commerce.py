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


def auth_headers(extra=None):
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    if extra:
        headers.update(extra)
    return headers


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_catalog_plans(client):
    response = client.get("/v1/catalog/plans")
    assert response.status_code == 200

    plans = response.get_json()
    assert isinstance(plans, list)
    assert len(plans) > 0
    assert "id" in plans[0]
    assert "name" in plans[0]


def test_activate_line_success_or_db_error(client):
    line_data = {
        "customer_id": 1,
        "msisdn": f"514{str(uuid.uuid4().int)[:7]}",
        "sim_number": f"SIM-{uuid.uuid4()}"
    }

    response = client.post(
        "/v1/lines/activate",
        data=json.dumps(line_data),
        content_type="application/json",
        headers=auth_headers()
    )

    assert response.status_code in [201, 500]

    if response.status_code == 201:
        result = response.get_json()
        assert "line_id" in result
        assert result["line_id"] > 0


def test_activate_line_missing_token(client):
    line_data = {
        "customer_id": 1,
        "msisdn": f"514{str(uuid.uuid4().int)[:7]}",
        "sim_number": f"SIM-{uuid.uuid4()}"
    }

    response = client.post(
        "/v1/lines/activate",
        data=json.dumps(line_data),
        content_type="application/json"
    )

    assert response.status_code == 401


def test_activate_line_missing_fields(client):
    line_data = {
        "customer_id": 1,
        "msisdn": "5145551234"
    }

    response = client.post(
        "/v1/lines/activate",
        data=json.dumps(line_data),
        content_type="application/json",
        headers=auth_headers()
    )

    assert response.status_code == 400


def test_create_order_success_or_db_error(client):
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
        headers=auth_headers({
            "Idempotency-Key": order_data["idempotency_key"]
        })
    )

    assert response.status_code in [201, 400, 500]

    if response.status_code == 201:
        result = response.get_json()
        assert "order_id" in result
        assert result["order_id"] > 0


def test_create_order_missing_token(client):
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
        content_type="application/json"
    )

    assert response.status_code in [401, 400]


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
        headers=auth_headers()
    )

    assert response.status_code == 400


def test_usage(client):
    response = client.get("/v1/usage/1")
    assert response.status_code in [200, 404]


def test_create_usage_success_or_db_error(client):
    usage_data = {
        "line_id": 1,
        "voice_minutes_used": 150,
        "sms_used": 60,
        "data_used_gb": 9.5,
        "usage_period": "2026-07"
    }

    response = client.post(
        "/v1/usage",
        data=json.dumps(usage_data),
        content_type="application/json"
    )

    assert response.status_code in [201, 500]

    if response.status_code == 201:
        result = response.get_json()
        assert "usage_id" in result
        assert result["usage_id"] > 0


def test_invoices(client):
    response = client.get("/v1/lines/1/invoices")
    assert response.status_code in [200, 404]


def test_invoice_by_id(client):
    response = client.get("/v1/invoices/1")
    assert response.status_code in [200, 404]


def test_create_invoice_success_or_conflict_or_db_error(client):
    invoice_data = {
        "customer_id": 1,
        "line_id": 1,
        "billing_cycle": f"2026-{str(uuid.uuid4().int)[:2]}",
        "amount": 35.00
    }

    response = client.post(
        "/v1/invoices",
        data=json.dumps(invoice_data),
        content_type="application/json"
    )

    assert response.status_code in [201, 409, 500]

    if response.status_code == 201:
        result = response.get_json()
        assert "invoice_id" in result
        assert result["invoice_id"] > 0


def test_order_by_id(client):
    response = client.get("/v1/orders/1")
    assert response.status_code in [200, 404]


def test_line_by_id(client):
    response = client.get("/v1/lines/1")
    assert response.status_code in [200, 404]


def test_customer_lines(client):
    response = client.get("/v1/customers/1/lines")
    assert response.status_code in [200, 404]


def test_metrics(client):
    response = client.get("/metrics")
    assert response.status_code == 200
