"""
Admin User Management Routes for MyBella
Handles user CRUD operations, statistics, and monitoring
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from backend.database.models.models import db, User, Chat, Message, UserSettings
from backend.database.models.wellness_models import (
    MoodEntry, WellnessGoal, FinanceEntry, SocialConnection,
    CopingStrategy, CBTSession, WellnessAchievement
)
from sqlalchemy import func, desc, or_
import logging

user_mgmt_bp = Blueprint('user_mgmt', __name__, url_prefix='/admin/users')
logger = logging.getLogger(__name__)

def admin_required(f):
    """Decorator to ensure only admin users can access admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@user_mgmt_bp.route('')
@login_required
@admin_required
def user_list():
    """User management page"""
    return render_template('admin/users/user_list.html')

@user_mgmt_bp.route('/api/list')
@login_required
@admin_required
def get_users_list():
    """Get paginated list of users with filters"""
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filters
        search = request.args.get('search', '').strip()
        role_filter = request.args.get('role', '').strip()
        status_filter = request.args.get('status', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = User.query
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )
        
        # Apply role filter
        if role_filter:
            query = query.filter(User.role == role_filter)
        
        # Apply status filter
        if status_filter == 'active':
            query = query.filter(User.active == True)
        elif status_filter == 'inactive':
            query = query.filter(User.active == False)
        
        # Apply sorting
        if sort_order == 'desc':
            query = query.order_by(desc(getattr(User, sort_by)))
        else:
            query = query.order_by(getattr(User, sort_by))
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Format user data
        users = []
        for user in pagination.items:
            # Get user statistics
            message_count = Message.query.filter_by(user_id=user.id).count()
            chat_count = Chat.query.filter_by(user_id=user.id).count()
            mood_count = MoodEntry.query.filter_by(user_id=user.id).count()
            
            users.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'gender': user.gender,
                'active': user.active,
                'created_at': user.created_at.isoformat(),
                'stats': {
                    'messages': message_count,
                    'chats': chat_count,
                    'mood_entries': mood_count
                }
            })
        
        return jsonify({
            'users': users,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching users list: {str(e)}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@user_mgmt_bp.route('/api/<int:user_id>')
@login_required
@admin_required
def get_user_details(user_id):
    """Get detailed information about a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get user statistics
        message_count = Message.query.filter_by(user_id=user.id).count()
        chat_count = Chat.query.filter_by(user_id=user.id).count()
        mood_count = MoodEntry.query.filter_by(user_id=user.id).count()
        goal_count = WellnessGoal.query.filter_by(user_id=user.id).count()
        achievement_count = WellnessAchievement.query.filter_by(user_id=user.id).count()
        
        # Get recent activity
        recent_chats = Chat.query.filter_by(user_id=user.id).order_by(desc(Chat.updated_at)).limit(5).all()
        recent_moods = MoodEntry.query.filter_by(user_id=user.id).order_by(desc(MoodEntry.timestamp)).limit(5).all()
        
        return jsonify({
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'gender': user.gender,
                'active': user.active,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat()
            },
            'stats': {
                'messages': message_count,
                'chats': chat_count,
                'mood_entries': mood_count,
                'wellness_goals': goal_count,
                'achievements': achievement_count
            },
            'recent_activity': {
                'chats': [{
                    'id': chat.id,
                    'title': chat.title,
                    'persona': chat.persona,
                    'mode': chat.mode,
                    'updated_at': chat.updated_at.isoformat()
                } for chat in recent_chats],
                'moods': [{
                    'id': mood.id,
                    'mood': mood.mood,
                    'intensity': mood.intensity,
                    'timestamp': mood.timestamp.isoformat()
                } for mood in recent_moods]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user details: {str(e)}")
        return jsonify({'error': 'Failed to fetch user details'}), 500

@user_mgmt_bp.route('/api/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Activate or deactivate a user account"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deactivating themselves
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        # Toggle active status
        user.active = not user.active
        db.session.commit()
        
        status = 'activated' if user.active else 'deactivated'
        logger.info(f"Admin {current_user.id} {status} user {user.id}")
        
        return jsonify({
            'success': True,
            'message': f'User {status} successfully',
            'active': user.active
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling user status: {str(e)}")
        return jsonify({'error': 'Failed to update user status'}), 500

@user_mgmt_bp.route('/api/<int:user_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account (soft delete - mark as inactive)"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Prevent deleting other admins
        if user.is_admin:
            return jsonify({'error': 'Cannot delete admin accounts'}), 400
        
        # Soft delete - mark as inactive
        user.active = False
        db.session.commit()
        
        logger.info(f"Admin {current_user.id} deleted user {user.id}")
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'Failed to delete user'}), 500

@user_mgmt_bp.route('/api/<int:user_id>/update', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """Update user information"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            user.name = data['name'].strip()
        
        if 'email' in data:
            new_email = data['email'].strip().lower()
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = new_email
        
        if 'gender' in data:
            user.gender = data['gender']
        
        if 'role' in data and current_user.is_admin:
            # Only allow changing role if current user is admin
            user.role = data['role']
        
        db.session.commit()
        logger.info(f"Admin {current_user.id} updated user {user.id}")
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'gender': user.gender
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({'error': 'Failed to update user'}), 500

@user_mgmt_bp.route('/api/stats')
@login_required
@admin_required
def get_user_stats():
    """Get overall user statistics"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(active=True).count()
        admin_count = User.query.filter_by(role='admin').count()
        
        # Users created in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
        
        # Gender distribution
        gender_stats = db.session.query(
            User.gender, 
            func.count(User.id)
        ).group_by(User.gender).all()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'admin_count': admin_count,
            'new_users_30d': new_users,
            'gender_distribution': {
                gender: count for gender, count in gender_stats if gender
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500
