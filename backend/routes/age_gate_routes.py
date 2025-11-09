"""
Age Verification Routes
Handles age gate at signup and feature access checks
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from flask_login import login_required, current_user
from datetime import datetime, date

from backend.services.age_verification_service import AgeVerificationService
from backend.database.models.age_verification_models import FeatureAccess


age_gate_bp = Blueprint('age_gate', __name__)


@age_gate_bp.route('/api/age-verification/verify', methods=['POST'])
@login_required
def verify_age():
    """
    Verify user's age from date of birth
    
    Request Body:
        {
            "date_of_birth": "1995-06-15"  # YYYY-MM-DD format
        }
    
    Returns:
        JSON with verification status and age tier
    """
    try:
        data = request.get_json()
        
        if not data or 'date_of_birth' not in data:
            return jsonify({
                'success': False,
                'error': 'Date of birth is required'
            }), 400
        
        # Parse date of birth
        try:
            dob_str = data['date_of_birth']
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Please use YYYY-MM-DD'
            }), 400
        
        # Check if date is in the future
        if dob > date.today():
            return jsonify({
                'success': False,
                'error': 'Date of birth cannot be in the future'
            }), 400
        
        # Verify age
        result = AgeVerificationService.verify_age(
            user_id=current_user.id,
            date_of_birth=dob,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # Check if user is too young (under 16)
        if result.get('is_minor'):
            return jsonify({
                'success': False,
                'error': 'You must be at least 16 years old to use MyBella',
                'min_age_required': 16
            }), 403
        
        # Set session flags
        session['age_verified'] = True
        session['age_tier'] = result['age_tier']
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@age_gate_bp.route('/api/age-verification/status', methods=['GET'])
@login_required
def get_age_status():
    """
    Get user's age verification status
    
    Returns:
        JSON with age info and verification status
    """
    try:
        age_info = AgeVerificationService.get_user_age_info(current_user.id)
        
        if not age_info:
            return jsonify({
                'success': True,
                'verified': False,
                'requires_verification': True
            })
        
        return jsonify({
            'success': True,
            'verified': True,
            **age_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@age_gate_bp.route('/api/age-verification/feature-access/<feature_key>', methods=['GET'])
@login_required
def check_feature_access(feature_key):
    """
    Check if user has access to a specific feature
    
    Args:
        feature_key: Feature identifier (URL parameter)
    
    Returns:
        JSON with access status and reason
    """
    try:
        result = AgeVerificationService.check_feature_access(current_user.id, feature_key)
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@age_gate_bp.route('/api/age-verification/accessible-features', methods=['GET'])
@login_required
def get_accessible_features():
    """
    Get list of features accessible to user
    
    Returns:
        JSON list of accessible feature keys
    """
    try:
        features = AgeVerificationService.get_accessible_features(current_user.id)
        
        return jsonify({
            'success': True,
            'features': features,
            'count': len(features)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@age_gate_bp.route('/api/age-verification/restricted-features', methods=['GET'])
@login_required
def get_restricted_features():
    """
    Get list of features NOT accessible to user (with reasons)
    
    Returns:
        JSON list of restricted features with reasons
    """
    try:
        restricted = AgeVerificationService.get_restricted_features(current_user.id)
        
        return jsonify({
            'success': True,
            'restricted_features': restricted,
            'count': len(restricted)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@age_gate_bp.route('/api/age-verification/persona-behavior/<int:persona_id>', methods=['GET'])
@login_required
def get_persona_behavior(persona_id):
    """
    Get age-appropriate persona behavior settings
    
    Args:
        persona_id: Persona ID (URL parameter)
    
    Returns:
        JSON with persona behavior configuration
    """
    try:
        behavior = AgeVerificationService.get_persona_behavior(persona_id, current_user.id)
        
        return jsonify({
            'success': True,
            'persona_id': persona_id,
            **behavior
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@age_gate_bp.route('/age-gate', methods=['GET'])
@login_required
def age_gate_page():
    """
    Display age verification page for users who haven't verified
    """
    # Check if already verified
    if not AgeVerificationService.requires_age_verification(current_user.id):
        return redirect(url_for('main.dashboard'))
    
    return render_template('age_gate/verify.html')


@age_gate_bp.route('/teen-mode-info', methods=['GET'])
@login_required
def teen_mode_info():
    """
    Display information about teen mode restrictions
    """
    age_info = AgeVerificationService.get_user_age_info(current_user.id)
    
    if not age_info or not age_info['is_teen']:
        return redirect(url_for('main.dashboard'))
    
    # Get accessible and restricted features
    accessible = AgeVerificationService.get_accessible_features(current_user.id)
    restricted = AgeVerificationService.get_restricted_features(current_user.id)
    
    return render_template(
        'age_gate/teen_mode.html',
        age_info=age_info,
        accessible_features=accessible,
        restricted_features=restricted
    )
