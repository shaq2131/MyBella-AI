"""
Lightweight analytics events endpoint for MVP
Note: No PII; accepts generic event names and metadata and logs to server.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

analytics_events_bp = Blueprint('analytics_events', __name__, url_prefix='/api/analytics')


@analytics_events_bp.route('/track', methods=['POST'])
def track_event():
    """Accept a simple analytics event and log it.
    Expected JSON: { name: str, meta: dict?, path: str?, ts: str? }
    """
    try:
        data = request.get_json(force=True) or {}
        name = (data.get('name') or '').strip()[:64]
        meta = data.get('meta') or {}
        path = (data.get('path') or request.path)[:256]
        ts = data.get('ts') or datetime.utcnow().isoformat()

        if not name:
            return jsonify({"ok": False, "error": "Missing event name"}), 400

        # Log to server; can be extended to DB/file later
        current_app.logger.info(f"analytics_event name=%s path=%s ts=%s meta=%s", name, path, ts, meta)

        return jsonify({"ok": True}), 200
    except Exception as e:
        current_app.logger.warning(f"analytics_event_error: {e}")
        return jsonify({"ok": False}), 500
