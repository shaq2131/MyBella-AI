"""
Example usage of Admin CRUD functions
Integration examples for admin routes and views
"""

from flask import request, jsonify, flash, redirect, url_for, render_template
from flask_login import current_user
from backend.funcs.admin import (
    AdminCRUDError,
    get_all_users,
    get_user_details,
    admin_update_user,
    admin_delete_user,
    get_system_statistics,
    bulk_user_action
)

# Example: Admin dashboard
def example_admin_dashboard():
    """Example admin dashboard view"""
    try:
        stats = get_system_statistics()
        return render_template('admin/dashboard.html', stats=stats)
    except Exception as e:
        flash('Error loading dashboard data.', 'danger')
        return render_template('admin/dashboard.html', stats={})

# Example: User management page
def example_admin_users_list():
    """Example admin users list with pagination and search"""
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
        users, total_count = get_all_users(
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
        
        return render_template('admin/users.html',
                             users=users,
                             pagination={
                                 'page': page,
                                 'total_pages': total_pages,
                                 'total_count': total_count,
                                 'has_prev': has_prev,
                                 'has_next': has_next
                             },
                             search=search,
                             role_filter=role_filter,
                             active_filter=active_filter)
    except Exception as e:
        flash('Error loading users list.', 'danger')
        return render_template('admin/users.html', users=[], pagination={})

# Example: User detail view
def example_admin_user_detail(user_id):
    """Example admin user detail view"""
    try:
        user_data = get_user_details(user_id)
        if not user_data:
            flash('User not found.', 'danger')
            return redirect(url_for('admin_views.users'))
        
        return render_template('admin/user_detail.html', data=user_data)
    except Exception as e:
        flash('Error loading user details.', 'danger')
        return redirect(url_for('admin_views.users'))

# Example: Update user (admin)
def example_admin_update_user_route(user_id):
    """Example admin user update route"""
    if request.method == 'POST':
        update_data = {}
        
        # Get form data
        if request.form.get('name'):
            update_data['name'] = request.form.get('name')
        if request.form.get('email'):
            update_data['email'] = request.form.get('email')
        if request.form.get('role'):
            update_data['role'] = request.form.get('role')
        if 'active' in request.form:
            update_data['active'] = request.form.get('active') == 'on'
        
        try:
            success = admin_update_user(
                user_id=user_id,
                admin_id=current_user.id,
                **update_data
            )
            if success:
                flash('User updated successfully!', 'success')
            else:
                flash('No changes were made.', 'info')
        except AdminCRUDError as e:
            flash(str(e), 'danger')
    
    return redirect(url_for('admin_views.user_detail', user_id=user_id))

# Example: Bulk user actions
def example_admin_bulk_actions():
    """Example bulk user actions"""
    if request.method == 'POST':
        user_ids = request.form.getlist('user_ids')
        action = request.form.get('action')
        
        if not user_ids:
            flash('No users selected.', 'warning')
            return redirect(url_for('admin_views.users'))
        
        if not action:
            flash('No action selected.', 'warning')
            return redirect(url_for('admin_views.users'))
        
        try:
            # Convert user_ids to integers
            user_ids = [int(uid) for uid in user_ids]
            
            # Additional parameters for role update
            kwargs = {}
            if action == 'update_role':
                kwargs['role'] = request.form.get('new_role', 'user')
            
            result = bulk_user_action(
                user_ids=user_ids,
                action=action,
                admin_id=current_user.id,
                **kwargs
            )
            
            if result['success_count'] > 0:
                flash(f'Successfully processed {result["success_count"]} users.', 'success')
            
            if result['error_count'] > 0:
                flash(f'Failed to process {result["error_count"]} users.', 'warning')
                for error in result['errors'][:5]:  # Show first 5 errors
                    flash(f'Error: {error}', 'danger')
        
        except (ValueError, AdminCRUDError) as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('An unexpected error occurred during bulk operation.', 'danger')
    
    return redirect(url_for('admin_views.users'))

# Example: API endpoints for admin
def example_admin_api_user_toggle_status(user_id):
    """Example API endpoint to toggle user status"""
    try:
        user_data = get_user_details(user_id)
        if not user_data:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        current_status = user_data['user'].active
        new_status = not current_status
        
        success = admin_update_user(
            user_id=user_id,
            admin_id=current_user.id,
            active=new_status
        )
        
        if success:
            status_text = "activated" if new_status else "deactivated"
            return jsonify({
                'success': True,
                'message': f'User has been {status_text}.',
                'active': new_status
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update user status.'
            }), 500
    
    except AdminCRUDError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred.'
        }), 500

def example_admin_api_delete_user(user_id):
    """Example API endpoint to delete user"""
    try:
        success = admin_delete_user(
            user_id=user_id,
            admin_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'User deleted successfully.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete user.'
            }), 500
    
    except AdminCRUDError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred.'
        }), 500

def example_admin_api_system_stats():
    """Example API endpoint for system statistics"""
    try:
        stats = get_system_statistics()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch system statistics.'
        }), 500