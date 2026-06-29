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


@app.route("/v1/customers/register", methods=["POST"])
def post_register_customer():
    """Register a new customer"""
    logger.debug("Endpoint: POST /v1/customers/register")
    try:
        result = create_customer(request)
        return jsonify(result), 201
    except Exception as e:
        logger.error(e)
        return jsonify({
            "code": "CUSTOMER_REGISTRATION_ERROR",
            "message": str(e),
            "traceId": request.headers.get("X-Request-Id")
        }), 400


@app.route("/v1/customers/<int:customer_id>", methods=["GET"])
def get_customer_details(customer_id):
    """Get customer details by ID"""
    logger.debug(f"Endpoint: GET /v1/customers/{customer_id}")
    try:
        result = get_customer(customer_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(e)
        return jsonify({
            "code": "CUSTOMER_NOT_FOUND",
            "message": str(e),
            "traceId": request.headers.get("X-Request-Id")
        }), 404


@app.route("/v1/auth/mfa/request", methods=["POST"])
def post_request_mfa():
    """Request an MFA/OTP code"""
    logger.debug("Endpoint: POST /v1/auth/mfa/request")
    try:
        result = request_mfa(request)
        return jsonify(result), 200
    except Exception as e:
        logger.error(e)
        return jsonify({
            "code": "MFA_REQUEST_ERROR",
            "message": str(e),
            "traceId": request.headers.get("X-Request-Id")
        }), 400


@app.route("/v1/auth/mfa/verify", methods=["POST"])
def post_verify_mfa():
    """Verify an MFA/OTP code"""
    logger.debug("Endpoint: POST /v1/auth/mfa/verify")
    try:
        result = verify_mfa(request)
        return jsonify(result), 200
    except Exception as e:
        logger.error(e)
        return jsonify({
            "code": "MFA_VERIFY_ERROR",
            "message": str(e),
            "traceId": request.headers.get("X-Request-Id")
        }), 401


@app.errorhandler(404)
def handle_404(error):
    """Handle 404 errors with JSON response"""
    logger.error(error)
    return jsonify({
        "code": "NOT_FOUND",
        "message": "Endpoint ou ressource introuvable",
        "traceId": request.headers.get("X-Request-Id")
    }), 404


@app.errorhandler(500)
def handle_500(error):
    """Handle 500 errors with JSON response"""
    logger.error(error)
    return jsonify({
        "code": "INTERNAL_ERROR",
        "message": "Erreur interne du service",
        "traceId": request.headers.get("X-Request-Id")
    }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
