from logger import Logger
from flask import Flask, request, jsonify

from controllers.customer_controller import create_customer, get_customer
from controllers.auth_controller import request_mfa, verify_mfa

app = Flask(__name__)
logger = Logger.get_instance("customer_identity")


@app.route("/")
def home():
    """Handle requests to base URL of the microservice"""
    return jsonify({"service": "CustomerIdentityService", "status": "running"})


@app.get("/health")
def health():
    """Return OK if app is up and running"""
    return jsonify({"status": "healthy"})


@app.post("/v1/customers/register")
def post_register_customer():
    """Register a new customer"""
    logger.debug("Endpoint: POST /v1/customers/register")
    return create_customer(request)


@app.get("/v1/customers/<int:customer_id>")
def get_customer_details(customer_id):
    """Get customer details by ID"""
    logger.debug(f"Endpoint: GET /v1/customers/{customer_id}")
    return get_customer(customer_id)


@app.post("/v1/auth/mfa/request")
def post_request_mfa():
    """Request an MFA/OTP code"""
    logger.debug("Endpoint: POST /v1/auth/mfa/request")
    return request_mfa(request)


@app.post("/v1/auth/mfa/verify")
def post_verify_mfa():
    """Verify an MFA/OTP code"""
    logger.debug("Endpoint: POST /v1/auth/mfa/verify")
    return verify_mfa(request)


@app.errorhandler(404)
def handle_404(error):
    logger.error(error)
    return jsonify({
        "code": "NOT_FOUND",
        "message": "Endpoint ou ressource introuvable",
        "traceId": request.headers.get("X-Request-Id")
    }), 404


@app.errorhandler(500)
def handle_500(error):
    logger.exception(error)
    return jsonify({
        "code": "INTERNAL_ERROR",
        "message": "Erreur interne du service",
        "traceId": request.headers.get("X-Request-Id")
    }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)