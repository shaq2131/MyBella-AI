"""
Admin Authentication Routes for MyBella
Handles admin login, registration, and access control
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from backend.database.models.models import db, User
from backend.funcs.admin.admin_crud import create_admin_user, AdminCRUDError
from functools import wraps
import logging

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin/auth')
logger = logging.getLogger(__name__)

def admin_required(f):
    """Decorator to ensure only admin users can access routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('admin_auth.admin_login'))
        if not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page and handler"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        if not email or not password:
            if request.is_json:
                return jsonify({'error': 'Email and password are required'}), 400
            flash('Email and password are required.', 'error')
            return render_template('admin/auth/login.html')
        
        # Find admin user
        user = User.query.filter_by(email=email, role='admin', active=True).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            logger.info(f"Admin login successful: {email}")
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'redirect': url_for('admin.dashboard')
                }), 200
            
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            logger.warning(f"Failed admin login attempt: {email}")
            if request.is_json:
                return jsonify({'error': 'Invalid admin credentials'}), 401
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin/auth/login.html')

@admin_auth_bp.route('/logout')
@login_required
@admin_required
def admin_logout():
    """Admin logout"""
    logger.info(f"Admin logout: {current_user.email}")
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('admin_auth.admin_login'))

@admin_auth_bp.route('/create-admin', methods=['GET', 'POST'])
@login_required
@admin_required
def create_new_admin():
    """Create a new admin user (super admin only)"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            error = 'All fields are required'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('admin/auth/create_admin.html')
        
        if password != confirm_password:
            error = 'Passwords do not match'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('admin/auth/create_admin.html')
        
        if len(password) < 8:
            error = 'Password must be at least 8 characters long'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('admin/auth/create_admin.html')
        
        try:
            # Create admin user
            new_admin = create_admin_user(
                name=name,
                email=email,
                password=password,
                created_by_admin_id=current_user.id
            )
            
            message = f'Admin user {email} created successfully'
            logger.info(message)
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': message,
                    'admin': {
                        'id': new_admin.id,
                        'name': new_admin.name,
                        'email': new_admin.email
                    }
                }), 201
            
            flash(message, 'success')
            return redirect(url_for('admin.user_management'))
            
        except AdminCRUDError as e:
            logger.error(f"Admin creation failed: {str(e)}")
            if request.is_json:
                return jsonify({'error': str(e)}), 400
            flash(str(e), 'error')
        except Exception as e:
            logger.error(f"Unexpected error creating admin: {str(e)}")
            if request.is_json:
                return jsonify({'error': 'An unexpected error occurred'}), 500
            flash('An unexpected error occurred.', 'error')
    
    return render_template('admin/auth/create_admin.html')

@admin_auth_bp.route('/check-session')
def check_admin_session():
    """Check if admin is authenticated (API endpoint)"""
    if current_user.is_authenticated and current_user.is_admin:
        return jsonify({
            'authenticated': True,
            'admin': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email
            }
        }), 200
    return jsonify({'authenticated': False}), 401
