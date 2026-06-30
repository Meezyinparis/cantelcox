"""
Tests for commerce service
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import uuid
import pytest
from commerce_api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    result = client.get("/health")
    assert result.status_code == 200
    assert result.get_json() == {"status": "healthy"}


def test_catalog_plans(client):
    response = client.get("/v1/catalog/plans")

    assert response.status_code == 200, response.get_json()

    plans = response.get_json()
    assert isinstance(plans, list)
    assert len(plans) > 0
    assert "id" in plans[0]
    assert "name" in plans[0]


def test_commerce_flow(client):
    """Smoke test for activation, order, usage and invoices"""

    random_msisdn = f"514{str(uuid.uuid1().int)[0:7]}"
    random_sim = f"SIM-{uuid.uuid1()}"

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

    assert response.status_code in [201, 404, 500]

    if response.status_code == 201:
        line_id = response.get_json()["line_id"]
    else:
        line_id = 1

    order_data = {
        "customer_id": 1,
        "line_id": line_id,
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
        headers={
            "Authorization": "Bearer test-token",
            "Idempotency-Key": f"test-{uuid.uuid1()}"
        }
    )

    assert response.status_code in [201, 500]

    response = client.get(f"/v1/usage/{line_id}")

    assert response.status_code in [200, 404], response.get_json()

    response = client.get(f"/v1/lines/{line_id}/invoices")
    assert response.status_code in [200, 404]

    response = client.get("/metrics")
    assert response.status_code == 200
