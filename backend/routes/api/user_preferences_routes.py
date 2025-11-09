"""
API routes for user preferences and settings
Handles chat mode toggle, profile settings, etc.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.database.models.models import db

user_prefs_bp = Blueprint('user_prefs', __name__, url_prefix='/api/user')

@user_prefs_bp.route('/chat-mode', methods=['GET'])
@login_required
def get_chat_mode():
    """Get user's preferred chat mode (chat or voice)"""
    try:
        if not current_user.settings:
            from backend.database.models.models import UserSettings
            current_user.settings = UserSettings(user_id=current_user.id)
            db.session.add(current_user.settings)
            db.session.commit()
        
        mode = current_user.settings.preferred_chat_mode or 'chat'
        
        return jsonify({
            'success': True,
            'preferred_chat_mode': mode
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_prefs_bp.route('/chat-mode', methods=['POST'])
@login_required
def set_chat_mode():
    """Save user's preferred chat mode"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'chat')
        
        if mode not in ['chat', 'voice']:
            return jsonify({
                'success': False,
                'error': 'Invalid mode. Must be "chat" or "voice".'
            }), 400
        
        if not current_user.settings:
            from backend.database.models.models import UserSettings
            current_user.settings = UserSettings(user_id=current_user.id)
            db.session.add(current_user.settings)
        
        current_user.settings.preferred_chat_mode = mode
        db.session.commit()
        
        return jsonify({
            'success': True,
            'preferred_chat_mode': mode,
            'message': f'Chat mode set to {mode}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
