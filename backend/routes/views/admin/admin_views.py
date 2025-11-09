"""
Admin view routes for MyBella
Handles admin dashboard, user management, and system monitoring
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.routes.auth.admin.admin_auth import admin_required
from backend.database.models.models import db
from backend.services.firebase.firebase_service import get_firebase_status
from backend.services.chat.pinecone_service import get_pinecone_status
from backend.funcs.admin import (
    AdminCRUDError,
    get_all_users,
    get_user_details,
    admin_update_user,
    admin_delete_user,
    get_system_statistics,
    get_user_messages_admin,
    get_all_messages,
    bulk_user_action,
    admin_reset_user_password
)
from datetime import datetime, timedelta

admin_views_bp = Blueprint('admin_views', __name__)

@admin_views_bp.route('/admin')
@admin_views_bp.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    try:
        # Get comprehensive system statistics using CRUD function
        stats = get_system_statistics()
        
        # Service status
        stats['firebase_status'] = get_firebase_status()
        stats['pinecone_status'] = get_pinecone_status()
        
        return render_template('admin/dashboard.html', title='Admin Dashboard', stats=stats)
    except Exception as e:
        flash('Error loading dashboard data.', 'danger')
        return render_template('admin/dashboard.html', title='Admin Dashboard', stats={})

@admin_views_bp.route('/admin/users')
@login_required
@admin_required
def users():
    """Admin user management page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    active_filter = request.args.get('active', '')
    
    # Convert active filter to boolean
    active_bool = None
    if active_filter == 'true':
        active_bool = True
    elif active_filter == 'false':
        active_bool = False
    
    try:
        users_list, total_count = get_all_users(
            page=page,
            per_page=20,
            search=search if search else None,
            role_filter=role_filter if role_filter else None,
            active_filter=active_bool
        )
        
        # Calculate pagination info
        total_pages = (total_count + 19) // 20  # Ceiling division
        has_prev = page > 1
        has_next = page < total_pages
        
        pagination = {
            'page': page,
            'total_pages': total_pages,
            'total_count': total_count,
            'has_prev': has_prev,
            'has_next': has_next
        }
        
        return render_template('admin/users.html', 
                             title='User Management', 
                             users=users_list,
                             pagination=pagination,
                             search=search,
                             role_filter=role_filter,
                             active_filter=active_filter)
    except Exception as e:
        flash('Error loading users list.', 'danger')
        return render_template('admin/users.html', 
                             title='User Management', 
                             users=[],
                             pagination={},
                             search='',
                             role_filter='',
                             active_filter='')

@admin_views_bp.route('/admin/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """Detailed view of a specific user"""
    try:
        user_data = get_user_details(user_id)
        if not user_data:
            flash('User not found.', 'danger')
            return redirect(url_for('admin_views.users'))
        
        return render_template('admin/user_detail.html', 
                             title=f'User: {user_data["user"].name}', 
                             data=user_data)
    except Exception as e:
        flash('Error loading user details.', 'danger')
        return redirect(url_for('admin_views.users'))

@admin_views_bp.route('/admin/messages')
@login_required
@admin_required
def messages():
    """Admin message monitoring"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    user_filter = request.args.get('user_id', type=int)
    persona_filter = request.args.get('persona', '')
    
    try:
        messages_data = get_all_messages(
            page=page,
            per_page=per_page,
            user_id=user_filter,
            persona_filter=persona_filter
        )
        
        return render_template('admin/messages.html', 
                             title='Message Monitor',
                             **messages_data)
    except Exception as e:
        flash('Error loading messages.', 'danger')
        return redirect(url_for('admin_views.dashboard'))

@admin_views_bp.route('/admin/system')
@login_required
@admin_required
def system():
    """System configuration and status page"""
    try:
        # Get system statistics using CRUD function
        system_stats = get_system_statistics()
        
        # Service status
        firebase_status = get_firebase_status()
        pinecone_status = get_pinecone_status()
        
        system_info = {
            'firebase_status': firebase_status,
            'pinecone_status': pinecone_status,
            'database_stats': {
                'users_table_size': system_stats.get('users', {}).get('total', 0),
                'messages_table_size': system_stats.get('activity', {}).get('total_messages', 0),
                'chats_table_size': system_stats.get('activity', {}).get('total_chats', 0),
                'settings_table_size': system_stats.get('users', {}).get('total', 0)  # Approximation
            }
        }
        
        return render_template('admin/system.html', 
                             title='System Status', 
                             system_info=system_info)
    except Exception as e:
        flash('Error loading system status.', 'danger')
        return redirect(url_for('admin_views.dashboard'))

@admin_views_bp.route('/admin/api/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active/inactive status"""
    try:
        user_data = get_user_details(user_id)
        if not user_data:
            return jsonify({
                'success': False, 
                'message': 'User not found.'
            }), 404
        
        user = user_data['user']
        new_status = not user.active
        
        admin_update_user(
            user_id=user_id,
            admin_id=current_user.id,
            active=new_status
        )
        
        status = "activated" if new_status else "deactivated"
        return jsonify({
            'success': True, 
            'message': f'User {user.name} has been {status}.',
            'active': new_status
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': 'An error occurred while updating user status.'
        }), 500

@admin_views_bp.route('/admin/api/stats/dashboard')
@login_required
@admin_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        # Get system statistics using CRUD function
        system_stats = get_system_statistics()
        
        # Return daily stats if available, otherwise basic stats
        if 'daily_activity' in system_stats:
            return jsonify({'daily_stats': system_stats['daily_activity']})
        else:
            # Fallback to basic stats
            return jsonify({
                'total_users': system_stats.get('users', {}).get('total', 0),
                'total_messages': system_stats.get('activity', {}).get('total_messages', 0),
                'total_chats': system_stats.get('activity', {}).get('total_chats', 0)
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error retrieving dashboard statistics.'
        }), 500

@admin_views_bp.route('/admin/api/user/<int:user_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user and all associated data"""
    try:
        # Prevent self-deletion
        if user_id == current_user.id:
            return jsonify({
                'success': False, 
                'message': 'You cannot delete your own account.'
            }), 400
        
        user_data = get_user_details(user_id)
        if not user_data:
            return jsonify({
                'success': False, 
                'message': 'User not found.'
            }), 404
        
        user_name = user_data['user'].name
        admin_delete_user(user_id, current_user.id)
        
        return jsonify({
            'success': True, 
            'message': f'User {user_name} and all associated data have been deleted.'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': 'An error occurred while deleting the user.'
        }), 500