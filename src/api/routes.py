from flask import Blueprint, request, jsonify, current_app

from src.utils.validators import is_valid_address
from src.api.errors import ApiErrorResponse, ValidationError, ServiceError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
api_bp = Blueprint("api", __name__)


def _token_service():
    svc = getattr(current_app, "token_service", None)
    if svc is None:
        raise ServiceError("Token service unavailable")
    return svc


@api_bp.app_errorhandler(ValidationError)
def handle_validation(err):
    logger.warning("Validation error: %s", err.safe_message)
    return jsonify(ApiErrorResponse(error=err.safe_message).__dict__), 400


@api_bp.app_errorhandler(Exception)
def handle_unexpected(err):
    logger.exception("Unhandled exception: %s", str(err)[:200])
    return jsonify(ApiErrorResponse(error="Internal server error").__dict__), 500


@api_bp.route("/get_balance", methods=["GET"])
def get_balance():
    address = request.args.get("address")
    if not address:
        return jsonify({"error": "Address parameter is required"}), 400
    if not is_valid_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400

    svc = _token_service()
    try:
        result = svc.get_balance(address)
        return jsonify(result)
    except Exception:
        logger.exception("Error in get_balance")
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/get_balance_batch", methods=["POST"])
def get_balance_batch():
    body = request.get_json() or {}
    addresses = body.get("addresses")
    if not addresses or not isinstance(addresses, list):
        return jsonify({"error": "Addresses array is required"}), 400
    for a in addresses:
        if not is_valid_address(a):
            return jsonify({"error": f"Invalid Ethereum address: {a}"}), 400

    svc = _token_service()
    try:
        results = svc.get_balance_batch(addresses)
        return jsonify({"balances": results, "count": len(results), "success": True})
    except ValidationError as e:
        return jsonify({"error": e.safe_message}), 400
    except Exception:
        logger.exception("Error in get_balance_batch")
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/get_token_info", methods=["GET"])
def get_token_info():
    svc = _token_service()
    try:
        result = svc.get_token_info()
        if result.get("success"):
            return jsonify(result)
        return jsonify({"error": result.get("error", "Unknown"), "success": False}), 502
    except Exception:
        logger.exception("Error in get_token_info")
        return jsonify({"error": "Internal server error", "success": False}), 500


@api_bp.route("/get_top", methods=["GET"])
def get_top():
    n_raw = request.args.get("n", "10")
    try:
        n = int(n_raw)
        if not (1 <= n <= 1000):
            return jsonify({"error": "Parameter n must be between 1 and 1000", "success": False}), 400
    except ValueError:
        return jsonify({"error": "Parameter n must be integer", "success": False}), 400

    svc = _token_service()
    try:
        holders = svc.get_top_holders(n)
        return jsonify({
            "top_holders": [{"address": a, "balance": b} for a, b in holders],
            "count": len(holders),
            "requested_count": n,
            "success": True
        })
    except Exception:
        logger.exception("Error in get_top")
        return jsonify({"error": "Internal server error", "success": False}), 500


@api_bp.route("/get_top_with_transactions", methods=["GET"])
def get_top_with_transactions():
    n_raw = request.args.get("n", "10")
    try:
        n = int(n_raw)
        if not (1 <= n <= 1000):
            return jsonify({"error": "Parameter n must be between 1 and 1000", "success": False}), 400
    except ValueError:
        return jsonify({"error": "Parameter n must be integer", "success": False}), 400

    svc = _token_service()
    try:
        holders = svc.get_top_holders_with_transactions(n)
        return jsonify({
            "top_holders": [
                {"address": a, "balance": b, "last_transaction_date": t}
                for a, b, t in holders
            ],
            "count": len(holders),
            "requested_count": n,
            "success": True
        })
    except Exception:
        logger.exception("Error in get_top_with_transactions")
        return jsonify({"error": "Internal server error", "success": False}), 500
