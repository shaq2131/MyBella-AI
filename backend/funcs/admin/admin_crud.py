"""
Admin CRUD Functions for MyBella
Database operations for administrative user management
"""

from typing import Optional, List, Dict, Any, Tuple
from flask import current_app
from backend.database.models.models import db, User, UserSettings, Message, Chat
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, desc, asc, or_
from datetime import datetime, timedelta

class AdminCRUDError(Exception):
    """Custom exception for admin CRUD operations"""
    pass

def create_admin_user(name: str, email: str, password: str, created_by_admin_id: int) -> User:
    """
    Create a new admin user (admin only)
    
    Args:
        name: Admin's full name
        email: Admin's email address
        password: Admin's password (will be hashed)
        created_by_admin_id: ID of the admin creating this user
    
    Returns:
        User: The created admin user object
    
    Raises:
        AdminCRUDError: If admin creation fails
    """
    try:
        # Check if email already exists
        if User.query.filter_by(email=email.lower()).first():
            raise AdminCRUDError(f"Email {email} is already registered")
        
        # Create new admin user
        admin_user = User(
            name=name.strip(),
            email=email.lower().strip(),
            role='admin'
        )
        admin_user.set_password(password)
        
        db.session.add(admin_user)
        db.session.commit()
        
        current_app.logger.info(f"Admin {created_by_admin_id} created new admin user: {email}")
        return admin_user
        
    except IntegrityError as e:
        db.session.rollback()
        raise AdminCRUDError(f"Database error: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise AdminCRUDError(f"Error creating admin user: {str(e)}")

def get_all_users(page: int = 1, per_page: int = 20, search: Optional[str] = None, 
                  role_filter: Optional[str] = None, active_filter: Optional[bool] = None) -> Tuple[List[User], int]:
    """
    Get all users with pagination and filtering
    
    Args:
        page: Page number (1-based)
        per_page: Number of users per page
        search: Search term for name or email
        role_filter: Filter by role ('user' or 'admin')
        active_filter: Filter by active status
    
    Returns:
        Tuple of (users list, total count)
    """
    try:
        query = User.query
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.like(search_term),
                    User.email.like(search_term)
                )
            )
        
        # Apply role filter
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        # Apply active filter
        if active_filter is not None:
            query = query.filter_by(active=active_filter)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        users = query.order_by(desc(User.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return users, total
        
    except Exception as e:
        current_app.logger.error(f"Error getting all users: {str(e)}")
        return [], 0

def get_user_details(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get comprehensive user details for admin view
    
    Args:
        user_id: User's ID
    
    Returns:
        Dictionary containing user details and statistics
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Get user statistics
        message_count = Message.query.filter_by(user_id=user_id).count()
        chat_count = Chat.query.filter_by(user_id=user_id).count()
        user_message_count = Message.query.filter_by(user_id=user_id, role='user').count()
        
        # Recent activity
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_messages = Message.query.filter(
            Message.user_id == user_id,
            Message.timestamp >= week_ago
        ).count()
        
        # Last activity
        last_message = Message.query.filter_by(user_id=user_id).order_by(
            desc(Message.timestamp)
        ).first()
        
        # Persona usage
        persona_stats = db.session.query(
            Message.persona,
            func.count(Message.id).label('count')
        ).filter_by(user_id=user_id).group_by(Message.persona).all()
        
        # Recent messages
        recent_message_list = Message.query.filter_by(user_id=user_id).order_by(
            desc(Message.timestamp)
        ).limit(10).all()
        
        # User settings
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        
        return {
            'user': user,
            'settings': settings,
            'stats': {
                'total_messages': message_count,
                'user_messages': user_message_count,
                'chat_sessions': chat_count,
                'recent_activity': recent_messages,
                'last_activity': last_message.timestamp if last_message else None,
                'persona_usage': [(p.persona, p.count) for p in persona_stats]
            },
            'recent_messages': recent_message_list
        }
        
    except Exception as e:
        current_app.logger.error(f"Error getting user details for {user_id}: {str(e)}")
        return None

def admin_update_user(user_id: int, admin_id: int, **kwargs) -> bool:
    """
    Update user information (admin only)
    
    Args:
        user_id: User's ID to update
        admin_id: ID of admin performing the update
        **kwargs: Fields to update (name, email, role, active)
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        AdminCRUDError: If update fails
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise AdminCRUDError("User not found")
        
        # Prevent admin from demoting themselves
        if user_id == admin_id and kwargs.get('role') == 'user':
            raise AdminCRUDError("Cannot demote yourself from admin role")
        
        # Update allowed fields
        allowed_fields = ['name', 'email', 'role', 'active']
        updated_fields = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(user, field):
                old_value = getattr(user, field)
                if field == 'email':
                    value = value.lower().strip()
                    # Check if email is taken
                    existing = User.query.filter(
                        User.email == value,
                        User.id != user_id
                    ).first()
                    if existing:
                        raise AdminCRUDError(f"Email {value} is already in use")
                
                setattr(user, field, value)
                updated_fields.append(f"{field}: {old_value} -> {value}")
        
        if updated_fields:
            db.session.commit()
            current_app.logger.info(f"Admin {admin_id} updated user {user_id}: {', '.join(updated_fields)}")
            return True
        
        return False
        
    except IntegrityError as e:
        db.session.rollback()
        raise AdminCRUDError(f"Database error: {str(e)}")
    except AdminCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise AdminCRUDError(f"Error updating user: {str(e)}")

def admin_reset_user_password(user_id: int, new_password: str, admin_id: int) -> bool:
    """
    Reset user's password (admin only)
    
    Args:
        user_id: User's ID
        new_password: New password to set
        admin_id: ID of admin performing the reset
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        AdminCRUDError: If password reset fails
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise AdminCRUDError("User not found")
        
        # Set new password
        user.set_password(new_password)
        db.session.commit()
        
        current_app.logger.info(f"Admin {admin_id} reset password for user {user_id} ({user.email})")
        return True
        
    except AdminCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise AdminCRUDError(f"Error resetting password: {str(e)}")

def admin_delete_user(user_id: int, admin_id: int) -> bool:
    """
    Permanently delete user account (admin only)
    
    Args:
        user_id: User's ID to delete
        admin_id: ID of admin performing the deletion
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        AdminCRUDError: If deletion fails
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise AdminCRUDError("User not found")
        
        # Prevent admin from deleting themselves
        if user_id == admin_id:
            raise AdminCRUDError("Cannot delete your own account")
        
        email = user.email  # Store for logging
        
        # Delete user (cascade will handle related data)
        db.session.delete(user)
        db.session.commit()
        
        current_app.logger.info(f"Admin {admin_id} deleted user account: {email}")
        return True
        
    except AdminCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise AdminCRUDError(f"Error deleting user: {str(e)}")

def get_system_statistics() -> Dict[str, Any]:
    """
    Get comprehensive system statistics
    
    Returns:
        Dictionary containing system statistics
    """
    try:
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(active=True).count()
        admin_users = User.query.filter_by(role='admin').count()
        
        # Activity statistics
        total_messages = Message.query.count()
        total_chats = Chat.query.count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = User.query.filter(User.created_at >= week_ago).count()
        messages_week = Message.query.filter(Message.timestamp >= week_ago).count()
        
        # Daily activity for last 7 days
        daily_stats = []
        for i in range(7):
            date = datetime.utcnow().date() - timedelta(days=i)
            start_date = datetime.combine(date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            daily_messages = Message.query.filter(
                Message.timestamp >= start_date,
                Message.timestamp < end_date
            ).count()
            
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'messages': daily_messages
            })
        
        # Most active users
        active_user_stats = db.session.query(
            User.name,
            User.email,
            func.count(Message.id).label('message_count')
        ).join(Message).group_by(User.id).order_by(
            desc('message_count')
        ).limit(10).all()
        
        # Persona usage statistics
        persona_stats = db.session.query(
            Message.persona,
            func.count(Message.id).label('count')
        ).group_by(Message.persona).order_by(desc('count')).all()
        
        return {
            'users': {
                'total': total_users,
                'active': active_users,
                'admins': admin_users,
                'inactive': total_users - active_users
            },
            'activity': {
                'total_messages': total_messages,
                'total_chats': total_chats,
                'new_users_week': new_users_week,
                'messages_week': messages_week
            },
            'daily_activity': list(reversed(daily_stats)),
            'top_users': [(u.name, u.email, u.message_count) for u in active_user_stats],
            'persona_usage': [(p.persona, p.count) for p in persona_stats]
        }
        
    except Exception as e:
        current_app.logger.error(f"Error getting system statistics: {str(e)}")
        return {}

def get_user_messages_admin(user_id: int, page: int = 1, per_page: int = 50, 
                           persona_filter: Optional[str] = None) -> Tuple[List[Message], int]:
    """
    Get user's messages for admin review
    
    Args:
        user_id: User's ID
        page: Page number
        per_page: Messages per page
        persona_filter: Filter by persona
    
    Returns:
        Tuple of (messages list, total count)
    """
    try:
        query = Message.query.filter_by(user_id=user_id)
        
        if persona_filter:
            query = query.filter_by(persona=persona_filter)
        
        total = query.count()
        messages = query.order_by(desc(Message.timestamp)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return messages, total
        
    except Exception as e:
        current_app.logger.error(f"Error getting user messages for admin: {str(e)}")
        return [], 0

def search_all_messages(search_term: str, limit: int = 100, 
                       user_filter: Optional[int] = None) -> List[Message]:
    """
    Search all messages in the system (admin only)
    
    Args:
        search_term: Term to search for
        limit: Maximum results
        user_filter: Filter by specific user ID
    
    Returns:
        List of matching messages
    """
    try:
        query = Message.query.filter(Message.content.contains(search_term))
        
        if user_filter:
            query = query.filter_by(user_id=user_filter)
        
        return query.order_by(desc(Message.timestamp)).limit(limit).all()
        
    except Exception as e:
        current_app.logger.error(f"Error searching messages: {str(e)}")
        return []

def get_all_messages(page: int = 1, per_page: int = 50, 
                    user_id: Optional[int] = None,
                    persona_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all messages with pagination and filtering (admin only)
    
    Args:
        page: Page number
        per_page: Messages per page
        user_id: Filter by specific user ID
        persona_filter: Filter by persona
    
    Returns:
        Dictionary with messages, pagination info, and filter options
    """
    try:
        query = Message.query.join(User)
        
        if user_id:
            query = query.filter(Message.user_id == user_id)
        
        if persona_filter:
            query = query.filter(Message.persona.contains(persona_filter))
        
        messages_pagination = query.order_by(desc(Message.timestamp)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get unique personas for filter
        personas_query = db.session.query(Message.persona).distinct()
        personas = [p[0] for p in personas_query.all() if p[0]]
        
        return {
            'messages': messages_pagination,
            'personas': personas,
            'user_filter': user_id,
            'persona_filter': persona_filter
        }
        
    except Exception as e:
        current_app.logger.error(f"Error getting all messages: {str(e)}")
        raise AdminCRUDError(f"Failed to retrieve messages: {str(e)}")

def bulk_user_action(user_ids: List[int], action: str, admin_id: int, **kwargs) -> Dict[str, Any]:
    """
    Perform bulk actions on multiple users
    
    Args:
        user_ids: List of user IDs
        action: Action to perform ('activate', 'deactivate', 'delete', 'update_role')
        admin_id: ID of admin performing the action
        **kwargs: Additional parameters for the action
    
    Returns:
        Dictionary with success/failure counts and messages
    """
    try:
        success_count = 0
        error_count = 0
        errors = []
        
        for user_id in user_ids:
            try:
                if action == 'activate':
                    admin_update_user(user_id, admin_id, active=True)
                elif action == 'deactivate':
                    if user_id != admin_id:  # Don't deactivate self
                        admin_update_user(user_id, admin_id, active=False)
                    else:
                        errors.append(f"Cannot deactivate your own account (ID: {user_id})")
                        error_count += 1
                        continue
                elif action == 'delete':
                    admin_delete_user(user_id, admin_id)
                elif action == 'update_role':
                    new_role = kwargs.get('role')
                    if new_role and user_id != admin_id:  # Don't change own role
                        admin_update_user(user_id, admin_id, role=new_role)
                    else:
                        errors.append(f"Cannot change your own role (ID: {user_id})")
                        error_count += 1
                        continue
                else:
                    errors.append(f"Unknown action: {action}")
                    error_count += 1
                    continue
                
                success_count += 1
                
            except (AdminCRUDError, Exception) as e:
                errors.append(f"User ID {user_id}: {str(e)}")
                error_count += 1
        
        current_app.logger.info(f"Admin {admin_id} performed bulk {action}: {success_count} success, {error_count} errors")
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors,
            'total_processed': len(user_ids)
        }
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk user action: {str(e)}")
        return {
            'success_count': 0,
            'error_count': len(user_ids),
            'errors': [f"Bulk operation failed: {str(e)}"],
            'total_processed': len(user_ids)
        }

def export_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Export all user data for admin purposes
    
    Args:
        user_id: User's ID
    
    Returns:
        Dictionary containing all user data
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Get all user data
        messages = Message.query.filter_by(user_id=user_id).order_by(asc(Message.timestamp)).all()
        chats = Chat.query.filter_by(user_id=user_id).order_by(asc(Chat.created_at)).all()
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        
        return {
            'user_info': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'active': user.active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'settings': {
                'current_persona': settings.current_persona if settings else None,
                'mode': settings.mode if settings else None,
                'tts_enabled': settings.tts_enabled if settings else None,
                'age_confirmed': settings.age_confirmed if settings else None,
                'show_ads': settings.show_ads if settings else None,
            } if settings else None,
            'messages': [
                {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'persona': msg.persona,
                    'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
                }
                for msg in messages
            ],
            'chats': [
                {
                    'id': chat.id,
                    'title': chat.title,
                    'persona': chat.persona,
                    'mode': chat.mode,
                    'created_at': chat.created_at.isoformat() if chat.created_at else None,
                    'updated_at': chat.updated_at.isoformat() if chat.updated_at else None
                }
                for chat in chats
            ],
            'export_timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        current_app.logger.error(f"Error exporting user data for {user_id}: {str(e)}")
        return None