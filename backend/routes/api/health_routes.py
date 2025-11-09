"""
Basic health and readiness endpoints
These endpoints allow uptime checks from load balancers and simple diagnostics.
"""

from flask import Blueprint, jsonify

health_bp = Blueprint('health_api', __name__, url_prefix='/health')


@health_bp.route('/healthz')
def healthz():
    """Liveness probe"""
    return jsonify({"status": "ok"}), 200


@health_bp.route('/readyz')
def readyz():
    """Readiness probe (extend later to check DB, external services)"""
    # For now, always ready. You can add DB ping or service checks here.
    checks = {
        "database": "unknown",  # TODO: implement quick SELECT 1
        "socketio": "unknown",
    }
    return jsonify({"status": "ready", "checks": checks}), 200
