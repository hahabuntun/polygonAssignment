from flask import Flask, jsonify
from flask_cors import CORS

from config import AppConfig
from src.utils.logger import setup_logger
from src.services.polygon_client import PolygonClient
from src.services.token_service import TokenService
from src.api.routes import api_bp

_cfg = AppConfig()
logger = setup_logger(__name__, level=_cfg.log_level)


def create_app(config: AppConfig = _cfg) -> Flask:
    app = Flask(__name__)
    app.config["DEBUG"] = config.debug
    CORS(app)

    polygon_client = PolygonClient(rpc_urls=config.rpc.urls, contract_address=config.contract.address, abi=config.contract.abi)
    token_service = TokenService(polygon_client)
    app.token_service = token_service

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "service": "Polygon Token API", "version": "1.0.0"})

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Endpoint not found", "success": False}), 404

    return app


def main():
    app = create_app()
    logger.info("Starting Polygon Token API on %s:%d", _cfg.host, _cfg.port)
    app.run(host=_cfg.host, port=_cfg.port, debug=_cfg.debug)


if __name__ == "__main__":
    main()
