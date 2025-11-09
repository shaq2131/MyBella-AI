"""
Content Moderation Routes - MyBella
Admin and user-facing content moderation endpoints
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from backend.services.content_moderation_service import ContentModerationService
from backend.database.models.onboarding_models import ContentModerationLog
from backend.database.models.models import User
from datetime import datetime, timedelta
from functools import wraps

moderation_bp = Blueprint('moderation', __name__, url_prefix='/moderation')


def admin_required(f):
    """Decorator to ensure only admin users can access admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# PUBLIC API (Content Filtering)
# ============================================================================

@moderation_bp.route('/api/check-content', methods=['POST'])
@login_required
def check_content():
    """
    Check if content passes moderation
    Used by chat, profile, and other user-generated content
    """
    try:
        data = request.json
        content = data.get('content', '')
        content_type = data.get('content_type', 'message')
        
        # Get user's age tier
        age_tier = 'adult'
        if hasattr(current_user, 'age_tier'):
            age_tier = current_user.age_tier
        
        # Moderate content
        result = ContentModerationService.moderate_content(
            content=content,
            user_id=current_user.id,
            content_type=content_type,
            age_tier=age_tier
        )
        
        return jsonify({
            'success': True,
            'allowed': result['allowed'],
            'filtered_content': result['filtered_content'],
            'flags': result['flags'],
            'severity': result['severity'],
            'action': result['action']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@moderation_bp.route('/api/sanitize', methods=['POST'])
@login_required
def sanitize_content():
    """
    Sanitize content by removing profanity
    Returns cleaned version
    """
    try:
        data = request.json
        content = data.get('content', '')
        
        sanitized = ContentModerationService.sanitize_for_display(content)
        
        return jsonify({
            'success': True,
            'original': content,
            'sanitized': sanitized
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# USER ROUTES (View Own Moderation History)
# ============================================================================

@moderation_bp.route('/my-history')
@login_required
def my_history():
    """View user's own moderation history"""
    return render_template('moderation/history.html')


@moderation_bp.route('/api/my-stats')
@login_required
def my_stats():
    """Get user's moderation statistics"""
    try:
        days = int(request.args.get('days', 30))
        
        stats = ContentModerationService.get_user_moderation_stats(
            user_id=current_user.id,
            days=days
        )
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ADMIN ROUTES
# ============================================================================

@moderation_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin moderation dashboard"""
    return render_template('admin/moderation_dashboard.html')


@moderation_bp.route('/admin/api/overview')
@login_required
@admin_required
def admin_overview():
    """Get moderation overview statistics"""
    try:
        days = int(request.args.get('days', 7))
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total flags
        total_flags = ContentModerationLog.query.filter(
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.flagged == True
        ).count()
        
        # Critical flags
        critical_flags = ContentModerationLog.query.filter(
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.severity == 'critical'
        ).count()
        
        # Blocks
        total_blocks = ContentModerationLog.query.filter(
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.action == 'block'
        ).count()
        
        # Unique users flagged
        unique_users = ContentModerationLog.query.filter(
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.flagged == True
        ).distinct(ContentModerationLog.user_id).count()
        
        # Flags by type
        profanity_count = ContentModerationLog.query.filter(
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.flag_reason.like('%profanity%')
        ).count()
        
        sexual_count = ContentModerationLog.query.filter(
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.flag_reason.like('%sexual%')
        ).count()
        
        violence_count = ContentModerationLog.query.filter(
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.flag_reason.like('%violence%')
        ).count()
        
        harassment_count = ContentModerationLog.query.filter(
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.flag_reason.like('%harassment%')
        ).count()
        
        return jsonify({
            'success': True,
            'overview': {
                'total_flags': total_flags,
                'critical_flags': critical_flags,
                'total_blocks': total_blocks,
                'unique_users_flagged': unique_users,
                'flags_by_type': {
                    'profanity': profanity_count,
                    'sexual_content': sexual_count,
                    'violence': violence_count,
                    'harassment': harassment_count
                },
                'period_days': days
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@moderation_bp.route('/admin/api/recent-flags')
@login_required
@admin_required
def admin_recent_flags():
    """Get recent flagged content"""
    try:
        limit = int(request.args.get('limit', 50))
        severity = request.args.get('severity', 'all')
        
        query = ContentModerationLog.query.filter(
            ContentModerationLog.flagged == True
        )
        
        if severity != 'all':
            query = query.filter(ContentModerationLog.severity == severity)
        
        flags = query.order_by(
            ContentModerationLog.created_at.desc()
        ).limit(limit).all()
        
        flags_data = []
        for flag in flags:
            user = User.query.get(flag.user_id)
            flags_data.append({
                'id': flag.id,
                'user_id': flag.user_id,
                'username': user.username if user else 'Unknown',
                'content_type': flag.content_type,
                'content_excerpt': flag.content_excerpt,
                'flag_reason': flag.flag_reason,
                'severity': flag.severity,
                'action': flag.action,
                'created_at': flag.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'flags': flags_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@moderation_bp.route('/admin/api/user-flags/<int:user_id>')
@login_required
@admin_required
def admin_user_flags(user_id):
    """Get all flags for a specific user"""
    try:
        days = int(request.args.get('days', 30))
        
        stats = ContentModerationService.get_user_moderation_stats(
            user_id=user_id,
            days=days
        )
        
        # Get recent flags
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        flags = ContentModerationLog.query.filter(
            ContentModerationLog.user_id == user_id,
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.flagged == True
        ).order_by(ContentModerationLog.created_at.desc()).all()
        
        flags_data = [{
            'id': flag.id,
            'content_type': flag.content_type,
            'content_excerpt': flag.content_excerpt,
            'flag_reason': flag.flag_reason,
            'severity': flag.severity,
            'action': flag.action,
            'created_at': flag.created_at.isoformat()
        } for flag in flags]
        
        return jsonify({
            'success': True,
            'stats': stats,
            'flags': flags_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@moderation_bp.route('/admin/api/flag/<int:flag_id>/review', methods=['POST'])
@login_required
@admin_required
def admin_review_flag(flag_id):
    """Mark a flag as reviewed by admin"""
    try:
        flag = ContentModerationLog.query.get(flag_id)
        if not flag:
            return jsonify({
                'success': False,
                'error': 'Flag not found'
            }), 404
        
        flag.reviewed_by = current_user.id
        flag.reviewed_at = datetime.utcnow()
        
        from backend.database.models.models import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Flag reviewed'
        })
        
    except Exception as e:
        from backend.database.models.models import db
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
