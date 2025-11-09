"""
Example usage of User CRUD functions
Integration examples for user routes and views
"""

from flask import request, jsonify, flash, redirect, url_for
from flask_login import current_user
from backend.funcs.users import (
    UserCRUDError,
    update_user_profile,
    change_user_password,
    get_user_statistics,
    get_user_messages,
    update_user_settings
)

# Example: Update user profile in route
def example_update_profile_route():
    """Example of how to use update_user_profile in a route"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        try:
            success = update_user_profile(
                user_id=current_user.id,
                name=name,
                email=email
            )
            if success:
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('user_views.profile'))
        except UserCRUDError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('An unexpected error occurred.', 'danger')
    
    return redirect(url_for('user_views.edit_profile'))

# Example: Change password
def example_change_password_route():
    """Example of how to use change_user_password in a route"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        try:
            success = change_user_password(
                user_id=current_user.id,
                current_password=current_password,
                new_password=new_password
            )
            if success:
                flash('Password changed successfully!', 'success')
                return redirect(url_for('user_views.profile'))
        except UserCRUDError as e:
            flash(str(e), 'danger')
    
    return redirect(url_for('user_views.change_password'))

# Example: Get user dashboard data
def example_user_dashboard_data():
    """Example of getting user dashboard data"""
    try:
        stats = get_user_statistics(current_user.id)
        recent_messages = get_user_messages(
            user_id=current_user.id,
            limit=10
        )
        
        return {
            'stats': stats,
            'recent_messages': recent_messages
        }
    except Exception as e:
        return {'stats': {}, 'recent_messages': []}

# Example: API endpoint for user statistics
def example_api_user_stats():
    """Example API endpoint returning user statistics"""
    try:
        stats = get_user_statistics(current_user.id)
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch user statistics'
        }), 500

# Example: Update user settings
def example_update_settings_route():
    """Example of updating user settings"""
    if request.method == 'POST':
        settings_data = {
            'current_persona': request.form.get('persona'),
            'mode': request.form.get('mode'),
            'tts_enabled': request.form.get('tts_enabled') == 'on',
            'voice_override': request.form.get('voice_override'),
            'age_confirmed': request.form.get('age_confirmed') == 'on',
            'show_ads': request.form.get('show_ads') == 'on'
        }
        
        try:
            success = update_user_settings(current_user.id, settings_data)
            if success:
                flash('Settings updated successfully!', 'success')
        except UserCRUDError as e:
            flash(str(e), 'danger')
    
    return redirect(url_for('main.settings'))