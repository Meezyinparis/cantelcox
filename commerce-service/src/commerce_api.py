"""
Commerce service application
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import time
from flask import Flask, request, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from controllers.plan_controller import (
    get_plans,
    get_plan,
    create_plan,
    remove_plan
)

from controllers.mobile_line_controller import (
    activate_line,
    remove_line,
    get_line,
    get_customer_lines
)

from controllers.order_controller import (
    create_order,
    remove_order,
    get_order
)

from controllers.usage_controller import (
    create_usage,
    get_usage
)

from controllers.invoice_controller import (
    create_invoice,
    remove_invoice,
    get_invoice,
    get_line_invoices
)


app = Flask(__name__)

counter_catalog = Counter("catalog_requests", "Calls to catalog endpoints")
counter_line_activation = Counter("line_activation_requests", "Calls to line activation")
counter_orders = Counter("orders_requests", "Calls to orders")
counter_usage = Counter("usage_requests", "Calls to usage endpoints")
counter_invoices = Counter("invoice_requests", "Calls to invoice endpoints")


@app.get("/")
def home():
    """Base URL"""
    return jsonify({"service": "CommerceService", "status": "running"})


@app.get("/health")
def health():
    """Return OK if app is up and running"""
    return jsonify({"status": "healthy"})


@app.get("/test/slow/<int:delay_seconds>")
def test_slow_endpoint(delay_seconds):
    """Endpoint pour tester les timeouts"""
    time.sleep(delay_seconds)
    return jsonify({"message": f"Response after {delay_seconds} seconds"}), 200

@app.get("/v1/catalog/plans")
def get_catalog_plans():
    """Get all active plans"""
    counter_catalog.inc()
    return get_plans()


@app.get("/v1/catalog/plans/<int:plan_id>")
def get_catalog_plan_id(plan_id):
    """Get plan by ID"""
    counter_catalog.inc()
    return get_plan(plan_id)


@app.post("/v1/catalog/plans")
def post_catalog_plans():
    """Create a new plan"""
    counter_catalog.inc()
    return create_plan(request)


@app.delete("/v1/catalog/plans/<int:plan_id>")
def delete_catalog_plan_id(plan_id):
    """Delete a plan"""
    counter_catalog.inc()
    return remove_plan(plan_id)

@app.post("/v1/lines/activate")
def post_activate_line():
    """Activate a mobile line"""
    counter_line_activation.inc()
    return activate_line(request)


@app.get("/v1/lines/<int:line_id>")
def get_line_id(line_id):
    """Get mobile line by ID"""
    return get_line(line_id)


@app.get("/v1/customers/<int:customer_id>/lines")
def get_customer_lines_id(customer_id):
    """Get all lines for a customer"""
    return get_customer_lines(customer_id)


@app.delete("/v1/lines/<int:line_id>")
def delete_line_id(line_id):
    """Delete a mobile line"""
    return remove_line(line_id)


# ============================================================
# Order routes
# ============================================================

@app.post("/v1/orders")
def post_orders():
    """Create a new order"""
    counter_orders.inc()
    return create_order(request)


@app.get("/v1/orders/<int:order_id>")
def get_order_id(order_id):
    """Get order by ID"""
    counter_orders.inc()
    return get_order(order_id)


@app.delete("/v1/orders/<int:order_id>")
def delete_order_id(order_id):
    """Delete order by ID"""
    counter_orders.inc()
    return remove_order(order_id)

@app.post("/v1/usage")
def post_usage():
    """Create usage record"""
    counter_usage.inc()
    return create_usage(request)


@app.get("/v1/usage/<int:line_id>")
def get_usage_line_id(line_id):
    """Get usage by line ID"""
    counter_usage.inc()
    return get_usage(line_id)


@app.post("/v1/invoices")
def post_invoices():
    """Create invoice"""
    counter_invoices.inc()
    return create_invoice(request)


@app.get("/v1/invoices/<int:invoice_id>")
def get_invoice_id(invoice_id):
    """Get invoice by ID"""
    counter_invoices.inc()
    return get_invoice(invoice_id)


@app.get("/v1/lines/<int:line_id>/invoices")
def get_line_invoices_id(line_id):
    """Get invoices for one mobile line"""
    counter_invoices.inc()
    return get_line_invoices(line_id)


@app.delete("/v1/invoices/<int:invoice_id>")
def delete_invoice_id(invoice_id):
    """Delete invoice"""
    counter_invoices.inc()
    return remove_invoice(invoice_id)


@app.route("/metrics")
def metrics():
    """Expose Prometheus metrics"""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)