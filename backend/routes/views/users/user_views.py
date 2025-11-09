"""
User-specific view routes for MyBella
Handles user dashboard, profile, and user settings
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.database.models.models import db, User, UserSettings, Message, Chat
from backend.database.utils.utils import get_persona, get_mode
from backend.funcs.users import (
    UserCRUDError,
    update_user_profile,
    change_user_password,
    get_user_statistics,
    get_user_messages,
    search_user_messages,
    update_user_settings,
    delete_user_account,
    get_user_profile_picture_url
)
from sqlalchemy import func

user_views_bp = Blueprint('user_views', __name__)

@user_views_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard page"""
    try:
        # Get user statistics
        stats = get_user_statistics(current_user.id)
        
        # Get recent messages  
        recent_messages = get_user_messages(
            user_id=current_user.id,
            limit=10
        )
        
        # Get current user info
        user_data = {
            'name': current_user.name,
            'email': current_user.email,
            'created_at': current_user.created_at
        }
        
        return render_template('users/dashboard.html', 
                             title='Dashboard', 
                             stats=stats,
                             recent_messages=recent_messages,
                             user=user_data)
        
    except Exception as e:
        # Log the actual error for debugging
        print(f"Dashboard error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return dashboard with empty data instead of redirecting
        return render_template('users/dashboard.html', 
                             title='Dashboard',
                             stats={},
                             recent_messages=[],
                             user={'name': current_user.name, 'email': current_user.email})

@user_views_bp.route('/chat')
@login_required  
def chat():
    """Chat interface page"""
    return render_template('users/chat.html', title='Chat with MyBella')

@user_views_bp.route('/chat-modern')
@login_required  
def chat_modern():
    """Modern ChatGPT-style chat interface"""
    persona = request.args.get('persona', 'Bella')
    return render_template('chat_modern.html', persona=persona)

@user_views_bp.route('/personas')
@login_required
def personas():
    """Persona management page"""
    return render_template('personas.html', title='My Personas • MyBella')

@user_views_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    from backend.services.age_verification_service import AgeVerificationService
    from datetime import date
    
    try:
        # Get user statistics using CRUD function
        stats = get_user_statistics(current_user.id)
        
        # Get recent messages using CRUD function
        recent_messages = get_user_messages(
            user_id=current_user.id,
            limit=5
        )
        
        # Get user profile picture URL
        profile_picture_url = get_user_profile_picture_url(current_user.id)
        
        # Get age verification info
        age_info = AgeVerificationService.get_user_age_info(current_user.id)
        
        # Add years until adult if teen
        if age_info and age_info.get('is_teen'):
            age_info['years_until_adult'] = 18 - age_info.get('age', 0)
        
        return render_template('users/profile.html', 
                             title='My Profile', 
                             stats=stats,
                             recent_messages=recent_messages,
                             profile_picture_url=profile_picture_url,
                             age_verification_info=age_info)
    except Exception as e:
        flash('Error loading profile data.', 'danger')
        return render_template('users/profile.html', 
                             title='My Profile', 
                             stats={},
                             recent_messages=[],
                             profile_picture_url=None,
                             age_verification_info=None)

@user_views_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        name = (request.form.get('name') or "").strip()
        email = (request.form.get('email') or "").strip().lower()
        
        if not name or not email:
            flash('Name and email are required.', 'danger')
            return render_template('users/edit_profile.html', title='Edit Profile')
        
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
    
    return render_template('users/edit_profile.html', title='Edit Profile')

@user_views_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password') or ""
        new_password = request.form.get('new_password') or ""
        confirm_password = request.form.get('confirm_password') or ""
        
        # Basic validation
        if not new_password or len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'danger')
            return render_template('users/change_password.html', title='Change Password')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('users/change_password.html', title='Change Password')
        
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
        except Exception as e:
            flash('An unexpected error occurred.', 'danger')
    
    return render_template('users/change_password.html', title='Change Password')

@user_views_bp.route('/chat-history')
@login_required
def chat_history():
    """User's chat history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    persona_filter = request.args.get('persona', '')
    search_term = request.args.get('search', '')
    
    try:
        if search_term:
            # Use search function for filtering by content
            messages = search_user_messages(
                user_id=current_user.id,
                search_term=search_term,
                limit=per_page
            )
            total_count = len(messages)
            has_prev = False
            has_next = False
        else:
            # Use regular get messages function with pagination
            offset = (page - 1) * per_page
            messages = get_user_messages(
                user_id=current_user.id,
                limit=per_page,
                offset=offset,
                persona_filter=persona_filter if persona_filter else None
            )
            
            # Get total count for pagination (simplified)
            total_messages = Message.query.filter_by(user_id=current_user.id)
            if persona_filter:
                total_messages = total_messages.filter_by(persona=persona_filter)
            total_count = total_messages.count()
            
            has_prev = page > 1
            has_next = (page * per_page) < total_count
        
        # Get user's personas for filter
        user_personas = db.session.query(Message.persona).filter_by(
            user_id=current_user.id
        ).distinct().all()
        personas = [p[0] for p in user_personas if p[0]]
        
        pagination = {
            'page': page,
            'has_prev': has_prev,
            'has_next': has_next,
            'total': total_count
        }
        
        return render_template('users/chat_history.html', 
                             title='Chat History', 
                             messages=messages,
                             personas=personas,
                             persona_filter=persona_filter,
                             search_term=search_term,
                             pagination=pagination)
    except Exception as e:
        flash('Error loading chat history.', 'danger')
        return render_template('users/chat_history.html', 
                             title='Chat History', 
                             messages=[],
                             personas=[],
                             persona_filter='',
                             search_term='',
                             pagination={})

@user_views_bp.route('/export-data')
@login_required
def export_data():
    """Export user's data"""
    # This would typically generate a downloadable file
    # For now, just show the data export page
    return render_template('users/export_data.html', title='Export My Data')

@user_views_bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Delete user account"""
    if request.method == 'POST':
        password = request.form.get('password') or ""
        confirm_delete = request.form.get('confirm_delete') or ""
        
        if confirm_delete.lower() != 'delete my account':
            flash('Please type "delete my account" to confirm.', 'danger')
            return render_template('users/delete_account.html', title='Delete Account')
        
        try:
            success = delete_user_account(
                user_id=current_user.id,
                password=password
            )
            if success:
                flash('Your account has been deleted successfully.', 'info')
                return redirect(url_for('main.home'))
        except UserCRUDError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('An unexpected error occurred.', 'danger')
    
    return render_template('users/delete_account.html', title='Delete Account')

@user_views_bp.route('/api/user-stats')
@login_required
def api_user_stats():
    """API endpoint for user statistics"""
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

