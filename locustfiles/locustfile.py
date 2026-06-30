import uuid
from locust import HttpUser, task, between


class CanTelcoXUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def get_catalog(self):
        self.client.get("/v1/catalog/plans")

    @task(3)
    def get_health(self):
        self.client.get("/health")

    @task(2)
    def activate_line(self):
        payload = {
            "customer_id": 1,
            "msisdn": f"514{str(uuid.uuid4().int)[:7]}",
            "sim_number": f"SIM-{uuid.uuid4()}"
        }

        self.client.post(
            "/v1/lines/activate",
            json=payload,
            headers={
                "Authorization": "Bearer test-token"
            }
        )

    @task(2)
    def create_order(self):
        payload = {
            "customer_id": 1,
            "line_id": 1,
            "items": [
                {
                    "plan_id": 1,
                    "quantity": 1
                }
            ]
        }

        self.client.post(
            "/v1/orders",
            json=payload,
            headers={
                "Authorization": "Bearer test-token",
                "Idempotency-Key": str(uuid.uuid4())
            }
        )

    @task(2)
    def usage(self):
        self.client.get("/v1/usage/1")

    @task(1)
    def invoices(self):
        self.client.get("/v1/lines/1/invoices")
