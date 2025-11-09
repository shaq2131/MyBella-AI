"""
Secrets Vault Routes
PIN-protected private journaling
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from backend.services.secrets_vault_service import SecretsVaultService

secrets_bp = Blueprint('secrets', __name__, url_prefix='/secrets')


@secrets_bp.route('/vault')
@login_required
def vault_page():
    """Main secrets vault page"""
    has_vault = SecretsVaultService.has_vault(current_user.id)
    return render_template('secrets/vault.html',
                         title='Secrets Vault',
                         has_vault=has_vault)


@secrets_bp.route('/api/setup-pin', methods=['POST'])
@login_required
def setup_pin():
    """Set up or change vault PIN"""
    try:
        data = request.get_json()
        pin = data.get('pin', '').strip()
        
        if not pin:
            return jsonify({'success': False, 'error': 'PIN is required'}), 400
        
        result = SecretsVaultService.set_pin(current_user.id, pin)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@secrets_bp.route('/api/verify-pin', methods=['POST'])
@login_required
def verify_pin():
    """Verify vault PIN"""
    try:
        data = request.get_json()
        pin = data.get('pin', '').strip()
        
        if not pin:
            return jsonify({'success': False, 'error': 'PIN is required'}), 400
        
        is_valid = SecretsVaultService.verify_pin(current_user.id, pin)
        
        return jsonify({
            'success': True,
            'valid': is_valid
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@secrets_bp.route('/api/entries', methods=['GET'])
@login_required
def get_entries():
    """Get all vault entries"""
    try:
        pin = request.args.get('pin', '').strip()
        
        if not pin:
            return jsonify({'success': False, 'error': 'PIN is required'}), 400
        
        result = SecretsVaultService.get_entries(current_user.id, pin)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@secrets_bp.route('/api/entry/<int:entry_id>', methods=['GET'])
@login_required
def get_entry(entry_id):
    """Get single vault entry"""
    try:
        pin = request.args.get('pin', '').strip()
        
        if not pin:
            return jsonify({'success': False, 'error': 'PIN is required'}), 400
        
        result = SecretsVaultService.get_entry(current_user.id, entry_id, pin)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@secrets_bp.route('/api/entry', methods=['POST'])
@login_required
def create_entry():
    """Create new vault entry"""
    try:
        data = request.get_json()
        
        pin = data.get('pin', '').strip()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        tags = data.get('tags', [])
        mood = data.get('mood')
        
        if not pin:
            return jsonify({'success': False, 'error': 'PIN is required'}), 400
        
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        result = SecretsVaultService.create_entry(
            user_id=current_user.id,
            title=title,
            content=content,
            pin=pin,
            tags=tags,
            mood=mood
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@secrets_bp.route('/api/entry/<int:entry_id>', methods=['PUT'])
@login_required
def update_entry(entry_id):
    """Update vault entry"""
    try:
        data = request.get_json()
        
        pin = data.get('pin', '').strip()
        
        if not pin:
            return jsonify({'success': False, 'error': 'PIN is required'}), 400
        
        result = SecretsVaultService.update_entry(
            user_id=current_user.id,
            entry_id=entry_id,
            pin=pin,
            title=data.get('title'),
            content=data.get('content'),
            tags=data.get('tags'),
            mood=data.get('mood')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@secrets_bp.route('/api/entry/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id):
    """Delete vault entry"""
    try:
        data = request.get_json()
        pin = data.get('pin', '').strip()
        
        if not pin:
            return jsonify({'success': False, 'error': 'PIN is required'}), 400
        
        result = SecretsVaultService.delete_entry(current_user.id, entry_id, pin)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@secrets_bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get vault statistics"""
    try:
        pin = request.args.get('pin', '').strip()
        
        if not pin:
            return jsonify({'success': False, 'error': 'PIN is required'}), 400
        
        result = SecretsVaultService.get_stats(current_user.id, pin)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
