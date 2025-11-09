"""
User authentication routes for MyBella
Handles user login, registr        try:
            # Create new user with default role
            user = User()
            user.name = username
            user.email = email
            user.role = 'user'
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # Get user.id

            # Create default settings
            settings = UserSettings(user_id=user.id)
            db.session.add(settings)

            db.session.commit()
            
            # Automatically log in the user
            login_user(user)
            flash('Registration successful! Welcome to MyBella!', 'success')
            return redirect(url_for('user_views.dashboard'))"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from backend.database.models.models import db, User, UserSettings

user_auth_bp = Blueprint('user_auth', __name__)

@user_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('user_views.dashboard'))

    if request.method == 'POST':
        email = (request.form.get('email') or "").strip().lower()
        password = request.form.get('password') or ""
        remember = bool(request.form.get('remember'))

        try:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash('Successfully logged in!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('user_views.dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'danger')
            flash('An error occurred during login. Please try again.', 'danger')

    return render_template('auth/login.html', title='Sign In')

@user_auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Multi-step user registration page"""
    from datetime import date
    
    if current_user.is_authenticated:
        return redirect(url_for('user_views.dashboard'))
    
    # If POST, redirect to register handler
    if request.method == 'POST':
        return register()
    
    # Show multi-step signup page
    return render_template('auth/register_multistep.html', 
                         title='Join MyBella',
                         today_date=date.today().isoformat())

@user_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler"""
    from datetime import date
    from backend.services.age_verification_service import AgeVerificationService
    
    if current_user.is_authenticated:
        return redirect(url_for('user_views.dashboard'))

    if request.method == 'POST':
        display_name = (request.form.get('display_name') or "").strip()
        nickname = (request.form.get('nickname') or "").strip()
        email = (request.form.get('email') or "").strip().lower()
        gender = (request.form.get('gender') or "").strip()
        pronouns = (request.form.get('pronouns') or "").strip()
        support_focus = (request.form.get('support_focus') or "").strip()
        support_topics = request.form.getlist('support_topics[]') or request.form.getlist('support_topics')
        conversation_style = (request.form.get('conversation_style') or "").strip()
        check_in_preference = (request.form.get('check_in_preference') or "").strip()
        date_of_birth_str = (request.form.get('date_of_birth') or "").strip()
        password = request.form.get('password') or ""
        confirm_password = request.form.get('confirm_password') or ""
        terms = (request.form.get('terms') or "").lower()

        # Validation
        required_fields = [display_name, email, gender, date_of_birth_str, password, confirm_password, terms, support_focus, conversation_style]
        if not all(required_fields):
            flash('Please complete all required fields.', 'danger')
            return render_template('auth/register_multistep.html', title='Join MyBella', today_date=date.today().isoformat())

        try:
            dob = date.fromisoformat(date_of_birth_str)
        except ValueError:
            flash('Invalid date of birth format.', 'danger')
            return render_template('auth/register_multistep.html', title='Join MyBella', today_date=date.today().isoformat())

        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < 16:
            flash('You must be at least 16 years old to use MyBella.', 'danger')
            return render_template('auth/register_multistep.html', title='Join MyBella', today_date=date.today().isoformat())

        if gender not in ['male', 'female', 'other', 'prefer_not_to_say']:
            flash('Please select a valid gender option.', 'danger')
            return render_template('auth/register_multistep.html', title='Join MyBella', today_date=date.today().isoformat())

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register_multistep.html', title='Join MyBella', today_date=date.today().isoformat())

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/register_multistep.html', title='Join MyBella', today_date=date.today().isoformat())

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return render_template('auth/register_multistep.html', title='Join MyBella', today_date=date.today().isoformat())

        if terms not in ('on', 'true', '1', 'yes'):
            flash('You must accept the terms of service.', 'danger')
            return render_template('auth/register_multistep_modern.html', title='Join MyBella', today_date=date.today().isoformat())

        try:
            user = User()
            user.name = display_name
            user.email = email
            user.role = 'user'
            user.gender = gender
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            age_result = AgeVerificationService.verify_age(
                user_id=user.id,
                date_of_birth=dob,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            ) or {}

            default_persona = user.get_default_persona()
            is_teen = bool(age_result.get('is_teen'))
            focus_personality_map = {
                'emotional_support': 'introverted',
                'motivation': 'extroverted',
                'calm': 'balanced',
                'productivity': 'balanced'
            }
            style_map = {
                'gentle': 'therapeutic',
                'cheerleader': 'enthusiastic',
                'direct': 'professional'
            }

            settings = UserSettings()
            settings.user_id = user.id
            settings.current_persona = default_persona
            settings.nickname = nickname or None
            settings.pronouns = pronouns or None
            settings.personality_type = focus_personality_map.get(support_focus, settings.personality_type or 'balanced')
            settings.support_focus = support_focus or None
            settings.support_topics = ",".join(support_topics) if support_topics else None
            settings.communication_style = style_map.get(conversation_style, settings.communication_style)
            settings.check_in_preference = check_in_preference or 'as_needed'
            settings.mode = 'Wellness' if is_teen else 'Companion'
            settings.age_confirmed = True
            db.session.add(settings)

            db.session.commit()

            login_user(user)

            persona_msg = f"Your AI companion {default_persona} is ready to chat with you!"
            if is_teen:
                flash(f'{display_name}, welcome to MyBella Teen Mode! {persona_msg} You have access to wellness tools, CBT exercises, and supportive companions.', 'info')
            else:
                flash(f'Welcome to MyBella, {display_name}! {persona_msg} Enjoy full access to all features including companionship and wellness tools.', 'success')

            return redirect(url_for('user_views.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('auth/register_multistep.html', title='Join MyBella', today_date=date.today().isoformat())

    return render_template('auth/register_multistep.html', title='Join MyBella', today_date=date.today().isoformat())

@user_auth_bp.route('/logout')
@login_required
def logout():
    """User logout handler"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user_auth.login'))

@user_auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """User password reset request"""
    if current_user.is_authenticated:
        return redirect(url_for('main.app_main'))
    
    if request.method == 'POST':
        email = (request.form.get('email') or "").strip().lower()
        
        if not email:
            flash('Please enter your email address.', 'danger')
            return render_template('auth/users/forgot_password.html', title='Forgot Password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            # TODO: Implement password reset email functionality
            flash('If an account with that email exists, you will receive password reset instructions.', 'info')
        else:
            flash('If an account with that email exists, you will receive password reset instructions.', 'info')
        
        return redirect(url_for('user_auth.login'))
    
    return render_template('auth/users/forgot_password.html', title='Forgot Password')