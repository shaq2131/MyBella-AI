"""
Admin authentication routes for MyBella
Handles admin login, logout, and admin-specific functionality
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from backend.database.models.models import db, User

admin_auth_bp = Blueprint('admin_auth', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('admin_auth.admin_login'))
        
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('user_auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page and handler"""
    if current_user.is_authenticated:
        if hasattr(current_user, 'role') and current_user.role == 'admin':
            return redirect(url_for('admin_views.dashboard'))
        else:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = (request.form.get('email') or "").strip().lower()
        password = request.form.get('password') or ""
        remember = bool(request.form.get('remember'))

        try:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                # Check if user has admin role
                if hasattr(user, 'role') and user.role == 'admin':
                    login_user(user, remember=remember)
                    session['is_admin'] = True
                    flash('Successfully logged in as admin!', 'success')
                    next_page = request.args.get('next')
                    return redirect(next_page if next_page else url_for('admin_views.dashboard'))
                else:
                    flash('Admin access required.', 'danger')
            else:
                flash('Invalid admin credentials.', 'danger')
        except Exception as e:
            flash('An error occurred during admin login. Please try again.', 'danger')

    return render_template('auth/admin/admin_login.html', title='Admin Login')

@admin_auth_bp.route('/admin/logout')
@login_required
@admin_required
def admin_logout():
    """Admin logout handler"""
    session.pop('is_admin', None)
    logout_user()
    flash('You have been logged out of admin panel.', 'info')
    return redirect(url_for('admin_auth.admin_login'))

@admin_auth_bp.route('/admin/create-admin', methods=['GET', 'POST'])
@login_required
@admin_required
def create_admin():
    """Create new admin user (only accessible by existing admins)"""
    if request.method == 'POST':
        name = (request.form.get('name') or "").strip()
        email = (request.form.get('email') or "").strip().lower()
        password = request.form.get('password') or ""
        confirm_password = request.form.get('confirm_password') or ""

        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return render_template('auth/admin/create_admin.html', title='Create Admin')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/admin/create_admin.html', title='Create Admin')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/admin/create_admin.html', title='Create Admin')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return render_template('auth/admin/create_admin.html', title='Create Admin')

        try:
            # Create new admin user
            admin_user = User(name=name, email=email, role='admin')
            admin_user.set_password(password)
            db.session.add(admin_user)
            db.session.commit()
            
            flash(f'Admin user {name} created successfully!', 'success')
            return redirect(url_for('admin_views.users'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating admin user. Please try again.', 'danger')
            return render_template('auth/admin/create_admin.html', title='Create Admin')

    return render_template('auth/admin/create_admin.html', title='Create Admin')

@admin_auth_bp.route('/admin/reset-user-password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset a user's password (admin only)"""
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    if not new_password or len(new_password) < 8:
        flash('Password must be at least 8 characters long.', 'danger')
        return redirect(url_for('admin_views.user_detail', user_id=user_id))
    
    try:
        user.set_password(new_password)
        db.session.commit()
        flash(f'Password reset successfully for user {user.name}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while resetting password.', 'danger')
    
    return redirect(url_for('admin_views.user_detail', user_id=user_id))