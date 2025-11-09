"""
Admin routes for MyBella - Analytics and Management
Handles admin dashboard, analytics, persona management, and system monitoring
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import json
from backend.database.models.models import User, PersonaProfile, Message, UserSubscription
from backend.database.utils.utils import get_db_connection
from sqlalchemy import func, and_, or_

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to ensure only admin users can access admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard page"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/api/dashboard-summary')
@login_required
@admin_required
def dashboard_summary():
    """Get summary statistics for admin dashboard"""
    try:
        db = get_db_connection()
        
        # Total users
        total_users = db.query(User).count()
        
        # Monthly revenue (current month)
        current_month = datetime.now().replace(day=1)
        monthly_revenue = db.query(func.sum(UserSubscription.subscription_amount)).filter(
            UserSubscription.subscription_start >= current_month,
            UserSubscription.subscription_status == 'active'
        ).scalar() or 0
        
        # Total personas
        total_personas = db.query(PersonaProfile).filter(PersonaProfile.is_active == True).count()
        
        # API usage today (mock data - implement based on your logging system)
        api_usage = get_daily_api_usage()
        
        return jsonify({
            'totalUsers': total_users,
            'monthlyRevenue': float(monthly_revenue),
            'totalPersonas': total_personas,
            'apiUsage': api_usage
        })
        
    except Exception as e:
        print(f"Error fetching dashboard summary: {e}")
        return jsonify({'error': 'Failed to fetch dashboard summary'}), 500

@admin_bp.route('/api/user-analytics')
@login_required
@admin_required
def user_analytics():
    """Get user analytics data"""
    try:
        period = request.args.get('period', 'month')
        db = get_db_connection()
        
        # Calculate date range based on period
        end_date = datetime.now()
        if period == 'day':
            start_date = end_date - timedelta(days=7)
            date_format = '%Y-%m-%d'
        elif period == 'week':
            start_date = end_date - timedelta(weeks=8)
            date_format = '%Y-W%U'
        elif period == 'month':
            start_date = end_date - timedelta(days=365)
            date_format = '%Y-%m'
        else:  # year
            start_date = end_date - timedelta(days=365*3)
            date_format = '%Y'
        
        # Active users (logged in within last 30 days)
        active_cutoff = datetime.now() - timedelta(days=30)
        active_users = db.query(User).filter(User.last_login >= active_cutoff).count()
        
        # Inactive users
        inactive_users = db.query(User).filter(
            or_(User.last_login < active_cutoff, User.last_login.is_(None))
        ).count()
        
        # New registrations in current period
        new_registrations = db.query(User).filter(
            User.created_at >= start_date
        ).count()
        
        # Calculate churn rate (simplified)
        total_users = db.query(User).count()
        churn_rate = round((inactive_users / total_users * 100), 2) if total_users > 0 else 0
        
        # Chart data (mock implementation - replace with actual data aggregation)
        chart_data = generate_user_chart_data(period, start_date, end_date)
        
        return jsonify({
            'activeUsers': active_users,
            'inactiveUsers': inactive_users,
            'newRegistrations': new_registrations,
            'churnRate': churn_rate,
            'chartData': chart_data
        })
        
    except Exception as e:
        print(f"Error fetching user analytics: {e}")
        return jsonify({'error': 'Failed to fetch user analytics'}), 500

@admin_bp.route('/api/revenue-analytics')
@login_required
@admin_required
def revenue_analytics():
    """Get revenue analytics data"""
    try:
        period = request.args.get('period', 'month')
        db = get_db_connection()
        
        # Calculate date range
        end_date = datetime.now()
        if period == 'day':
            start_date = end_date - timedelta(days=30)
        elif period == 'week':
            start_date = end_date - timedelta(weeks=12)
        elif period == 'month':
            start_date = end_date - timedelta(days=365)
        else:  # year
            start_date = end_date - timedelta(days=365*3)
        
        # Total revenue
        total_revenue = db.query(func.sum(UserSubscription.subscription_amount)).filter(
            UserSubscription.subscription_start >= start_date,
            UserSubscription.subscription_status == 'active'
        ).scalar() or 0
        
        # Average revenue per user
        total_users = db.query(User).count()
        avg_revenue = round(total_revenue / total_users, 2) if total_users > 0 else 0
        
        # Calculate growth rate (mock implementation)
        growth_rate = calculate_revenue_growth(period, start_date)
        
        # Subscription revenue (same as total for now)
        subscription_revenue = total_revenue
        
        # Chart data
        chart_data = generate_revenue_chart_data(period, start_date, end_date)
        
        return jsonify({
            'totalRevenue': float(total_revenue),
            'avgRevenue': avg_revenue,
            'growthRate': growth_rate,
            'subscriptionRevenue': float(subscription_revenue),
            'chartData': chart_data
        })
        
    except Exception as e:
        print(f"Error fetching revenue analytics: {e}")
        return jsonify({'error': 'Failed to fetch revenue analytics'}), 500

@admin_bp.route('/api/api-analytics')
@login_required
@admin_required
def api_analytics():
    """Get API usage analytics"""
    try:
        # Mock API usage data - implement based on your logging system
        api_data = {
            'chatApiCalls': get_api_usage('chat'),
            'voiceApiCalls': get_api_usage('voice'),
            'elevenLabsUsage': get_api_usage('elevenlabs'),
            'firebaseCalls': get_api_usage('firebase'),
            'avgResponseTime': get_avg_response_time(),
            'chartData': {
                'chatApi': get_api_usage('chat'),
                'voiceApi': get_api_usage('voice'),
                'elevenLabs': get_api_usage('elevenlabs'),
                'firebase': get_api_usage('firebase')
            }
        }
        
        return jsonify(api_data)
        
    except Exception as e:
        print(f"Error fetching API analytics: {e}")
        return jsonify({'error': 'Failed to fetch API analytics'}), 500

@admin_bp.route('/api/performance-metrics')
@login_required
@admin_required
def performance_metrics():
    """Get system performance metrics"""
    try:
        import psutil
        import os
        
        # Server uptime (simplified)
        uptime_seconds = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(uptime_seconds)
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
        
        # Database load (mock - implement based on your DB monitoring)
        db_load = get_database_load()
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = round(memory.percent, 1)
        
        # Active connections (mock)
        active_connections = get_active_connections()
        
        return jsonify({
            'serverUptime': uptime_str,
            'dbLoad': db_load,
            'memoryUsage': memory_usage,
            'activeConnections': active_connections
        })
        
    except Exception as e:
        print(f"Error fetching performance metrics: {e}")
        return jsonify({'error': 'Failed to fetch performance metrics'}), 500

@admin_bp.route('/api/personas')
@login_required
@admin_required
def get_personas():
    """Get all personas for management"""
    try:
        db = get_db_connection()
        personas = db.query(PersonaProfile).all()
        
        persona_list = []
        for persona in personas:
            persona_list.append({
                'id': persona.id,
                'name': persona.name,
                'description': persona.description,
                'avatar': persona.profile_picture,
                'personality': persona.personality_traits,
                'voice': persona.voice_settings,
                'active': persona.is_active,
                'created_at': persona.created_at.isoformat() if persona.created_at else None
            })
        
        return jsonify(persona_list)
        
    except Exception as e:
        print(f"Error fetching personas: {e}")
        return jsonify({'error': 'Failed to fetch personas'}), 500

@admin_bp.route('/api/personas', methods=['POST'])
@login_required
@admin_required
def create_persona():
    """Create a new persona"""
    try:
        data = request.get_json()
        db = get_db_connection()
        
        # Validate required fields
        if not data.get('name') or not data.get('description'):
            return jsonify({'error': 'Name and description are required'}), 400
        
        # Create new persona
        new_persona = PersonaProfile(
            name=data['name'],
            description=data['description'],
            profile_picture=data.get('avatar', ''),
            personality_traits=data.get('personality', ''),
            voice_settings=data.get('voice', 'default'),
            is_active=data.get('active', True),
            created_by=current_user.id
        )
        
        db.add(new_persona)
        db.commit()
        
        return jsonify({'message': 'Persona created successfully', 'id': new_persona.id}), 201
        
    except Exception as e:
        print(f"Error creating persona: {e}")
        db.rollback()
        return jsonify({'error': 'Failed to create persona'}), 500

@admin_bp.route('/api/personas/<int:persona_id>')
@login_required
@admin_required
def get_persona(persona_id):
    """Get specific persona details"""
    try:
        db = get_db_connection()
        persona = db.query(PersonaProfile).filter(PersonaProfile.id == persona_id).first()
        
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        return jsonify({
            'id': persona.id,
            'name': persona.name,
            'description': persona.description,
            'avatar': persona.profile_picture,
            'personality': persona.personality_traits,
            'voice': persona.voice_settings,
            'active': persona.is_active
        })
        
    except Exception as e:
        print(f"Error fetching persona: {e}")
        return jsonify({'error': 'Failed to fetch persona'}), 500

@admin_bp.route('/api/personas/<int:persona_id>', methods=['PUT'])
@login_required
@admin_required
def update_persona(persona_id):
    """Update an existing persona"""
    try:
        data = request.get_json()
        db = get_db_connection()
        
        persona = db.query(PersonaProfile).filter(PersonaProfile.id == persona_id).first()
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        # Update persona fields
        persona.name = data.get('name', persona.name)
        persona.description = data.get('description', persona.description)
        persona.profile_picture = data.get('avatar', persona.profile_picture)
        persona.personality_traits = data.get('personality', persona.personality_traits)
        persona.voice_settings = data.get('voice', persona.voice_settings)
        persona.is_active = data.get('active', persona.is_active)
        persona.updated_at = datetime.now()
        
        db.commit()
        
        return jsonify({'message': 'Persona updated successfully'})
        
    except Exception as e:
        print(f"Error updating persona: {e}")
        db.rollback()
        return jsonify({'error': 'Failed to update persona'}), 500

@admin_bp.route('/api/personas/<int:persona_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_persona(persona_id):
    """Delete a persona"""
    try:
        db = get_db_connection()
        
        persona = db.query(PersonaProfile).filter(PersonaProfile.id == persona_id).first()
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        # Check if persona is being used in active chats
        active_chats = db.query(Message).filter(
            Message.persona == persona.name
        ).count()
        
        if active_chats > 0:
            return jsonify({'error': 'Cannot delete persona with existing chat history'}), 400
        
        db.delete(persona)
        db.commit()
        
        return jsonify({'message': 'Persona deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting persona: {e}")
        db.rollback()
        return jsonify({'error': 'Failed to delete persona'}), 500

@admin_bp.route('/api/personas/<int:persona_id>/status', methods=['PATCH'])
@login_required
@admin_required
def toggle_persona_status(persona_id):
    """Toggle persona active status"""
    try:
        data = request.get_json()
        db = get_db_connection()
        
        persona = db.query(PersonaProfile).filter(PersonaProfile.id == persona_id).first()
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        persona.is_active = data.get('active', not persona.is_active)
        persona.updated_at = datetime.now()
        
        db.commit()
        
        status = 'activated' if persona.is_active else 'deactivated'
        return jsonify({'message': f'Persona {status} successfully'})
        
    except Exception as e:
        print(f"Error updating persona status: {e}")
        db.rollback()
        return jsonify({'error': 'Failed to update persona status'}), 500

@admin_bp.route('/api/system-logs')
@login_required
@admin_required
def get_system_logs():
    """Get system logs"""
    try:
        log_level = request.args.get('level', 'all')
        
        # Mock log data - implement based on your logging system
        logs = get_recent_logs(log_level)
        
        return jsonify(logs)
        
    except Exception as e:
        print(f"Error fetching system logs: {e}")
        return jsonify({'error': 'Failed to fetch system logs'}), 500

# Helper functions (implement based on your specific requirements)

def get_daily_api_usage():
    """Get API usage for today"""
    # Implement based on your API logging system
    return 1234  # Mock data

def get_api_usage(service):
    """Get API usage for specific service"""
    # Implement based on your API logging system
    mock_data = {
        'chat': 5000,
        'voice': 1200,
        'elevenlabs': 800,
        'firebase': 2000
    }
    return mock_data.get(service, 0)

def get_avg_response_time():
    """Get average API response time"""
    # Implement based on your monitoring system
    return 250  # milliseconds

def get_database_load():
    """Get current database load percentage"""
    # Implement based on your database monitoring
    return 35  # percentage

def get_active_connections():
    """Get number of active connections"""
    # Implement based on your connection monitoring
    return 150

def calculate_revenue_growth(period, start_date):
    """Calculate revenue growth rate"""
    # Implement revenue growth calculation
    return 15.5  # percentage

def generate_user_chart_data(period, start_date, end_date):
    """Generate chart data for user analytics"""
    # Implement chart data generation based on period
    return {
        'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'activeUsers': [100, 120, 150, 180],
        'newUsers': [20, 25, 30, 35]
    }

def generate_revenue_chart_data(period, start_date, end_date):
    """Generate chart data for revenue analytics"""
    # Implement chart data generation based on period
    return {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr'],
        'revenue': [1000, 1200, 1500, 1800]
    }

def get_recent_logs(level='all'):
    """Get recent system logs"""
    # Mock log data - implement based on your logging system
    logs = [
        {
            'timestamp': '2025-10-08 14:30:15',
            'level': 'info',
            'message': 'User authentication successful'
        },
        {
            'timestamp': '2025-10-08 14:29:45',
            'level': 'info',
            'message': 'Database connection established'
        },
        {
            'timestamp': '2025-10-08 14:25:30',
            'level': 'warning',
            'message': 'High API usage detected'
        }
    ]
    
    if level != 'all':
        logs = [log for log in logs if log['level'] == level]
    
    return logs