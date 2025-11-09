"""
User CRUD Functions for MyBella
Database operations for user management from user perspective
"""

import os
from typing import Optional, List, Dict, Any
from flask import current_app
from werkzeug.utils import secure_filename
from backend.database.models.models import db, User, UserSettings, Message, Chat
from backend.database.utils.utils import safe_filename, allowed_image_file
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, desc
from datetime import datetime, timedelta

class UserCRUDError(Exception):
    """Custom exception for user CRUD operations"""
    pass

def create_user(name: str, email: str, password: str, role: str = 'user') -> User:
    """
    Create a new user account
    
    Args:
        name: User's full name
        email: User's email address
        password: User's password (will be hashed)
        role: User role ('user' or 'admin')
    
    Returns:
        User: The created user object
    
    Raises:
        UserCRUDError: If user creation fails
    """
    try:
        # Check if email already exists
        if User.query.filter_by(email=email.lower()).first():
            raise UserCRUDError(f"Email {email} is already registered")
        
        # Create new user
        user = User(
            name=name.strip(),
            email=email.lower().strip(),
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create default settings for user
        if role == 'user':
            settings = UserSettings(user_id=user.id)
            db.session.add(settings)
        
        db.session.commit()
        current_app.logger.info(f"Created new user: {email}")
        return user
        
    except IntegrityError as e:
        db.session.rollback()
        raise UserCRUDError(f"Database error: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise UserCRUDError(f"Error creating user: {str(e)}")

def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Get user by ID
    
    Args:
        user_id: User's ID
    
    Returns:
        User object or None if not found
    """
    try:
        return User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(f"Error getting user by ID {user_id}: {str(e)}")
        return None

def get_user_by_email(email: str) -> Optional[User]:
    """
    Get user by email address
    
    Args:
        email: User's email address
    
    Returns:
        User object or None if not found
    """
    try:
        return User.query.filter_by(email=email.lower().strip()).first()
    except Exception as e:
        current_app.logger.error(f"Error getting user by email {email}: {str(e)}")
        return None

def update_user_profile(user_id: int, name: Optional[str] = None, email: Optional[str] = None) -> bool:
    """
    Update user profile information
    
    Args:
        user_id: User's ID
        name: New name (optional)
        email: New email (optional)
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        UserCRUDError: If update fails
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise UserCRUDError("User not found")
        
        # Update name if provided
        if name:
            user.name = name.strip()
        
        # Update email if provided
        if email:
            email = email.lower().strip()
            # Check if email is taken by another user
            existing_user = User.query.filter(
                User.email == email,
                User.id != user_id
            ).first()
            if existing_user:
                raise UserCRUDError(f"Email {email} is already in use")
            user.email = email
        
        db.session.commit()
        current_app.logger.info(f"Updated user profile: {user.email}")
        return True
        
    except IntegrityError as e:
        db.session.rollback()
        raise UserCRUDError(f"Database error: {str(e)}")
    except UserCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise UserCRUDError(f"Error updating user: {str(e)}")

def change_user_password(user_id: int, current_password: str, new_password: str) -> bool:
    """
    Change user's password
    
    Args:
        user_id: User's ID
        current_password: Current password for verification
        new_password: New password to set
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        UserCRUDError: If password change fails
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise UserCRUDError("User not found")
        
        # Verify current password
        if not user.check_password(current_password):
            raise UserCRUDError("Current password is incorrect")
        
        # Set new password
        user.set_password(new_password)
        db.session.commit()
        
        current_app.logger.info(f"Password changed for user: {user.email}")
        return True
        
    except UserCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise UserCRUDError(f"Error changing password: {str(e)}")

def deactivate_user_account(user_id: int, password: str) -> bool:
    """
    Deactivate user account (soft delete)
    
    Args:
        user_id: User's ID
        password: User's password for verification
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        UserCRUDError: If deactivation fails
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise UserCRUDError("User not found")
        
        # Verify password
        if not user.check_password(password):
            raise UserCRUDError("Password is incorrect")
        
        # Deactivate account
        user.active = False
        db.session.commit()
        
        current_app.logger.info(f"Deactivated user account: {user.email}")
        return True
        
    except UserCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise UserCRUDError(f"Error deactivating account: {str(e)}")

def delete_user_account(user_id: int, password: str) -> bool:
    """
    Permanently delete user account and all associated data
    
    Args:
        user_id: User's ID
        password: User's password for verification
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        UserCRUDError: If deletion fails
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise UserCRUDError("User not found")
        
        # Verify password
        if not user.check_password(password):
            raise UserCRUDError("Password is incorrect")
        
        email = user.email  # Store for logging
        
        # Delete user (cascade will handle related data)
        db.session.delete(user)
        db.session.commit()
        
        current_app.logger.info(f"Permanently deleted user account: {email}")
        return True
        
    except UserCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise UserCRUDError(f"Error deleting account: {str(e)}")

def get_user_settings(user_id: int) -> Optional[UserSettings]:
    """
    Get user settings
    
    Args:
        user_id: User's ID
    
    Returns:
        UserSettings object or None if not found
    """
    try:
        return UserSettings.query.filter_by(user_id=user_id).first()
    except Exception as e:
        current_app.logger.error(f"Error getting user settings for {user_id}: {str(e)}")
        return None

def update_user_settings(user_id: int, settings_data: Dict[str, Any]) -> bool:
    """
    Update user settings
    
    Args:
        user_id: User's ID
        settings_data: Dictionary containing settings to update
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        UserCRUDError: If update fails
    """
    try:
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        if not settings:
            # Create settings if they don't exist
            settings = UserSettings(user_id=user_id)
            db.session.add(settings)
        
        # Update settings
        for key, value in settings_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        db.session.commit()
        current_app.logger.info(f"Updated settings for user {user_id}")
        return True
        
    except Exception as e:
        db.session.rollback()
        raise UserCRUDError(f"Error updating settings: {str(e)}")

def get_user_statistics(user_id: int) -> Dict[str, Any]:
    """
    Get user statistics
    
    Args:
        user_id: User's ID
    
    Returns:
        Dictionary containing user statistics
    """
    try:
        # Basic counts
        message_count = Message.query.filter_by(user_id=user_id).count()
        chat_count = Chat.query.filter_by(user_id=user_id).count()
        user_message_count = Message.query.filter_by(user_id=user_id, role='user').count()
        
        # Persona usage
        persona_stats = db.session.query(
            Message.persona,
            func.count(Message.id).label('count')
        ).filter_by(user_id=user_id).group_by(Message.persona).all()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_messages = Message.query.filter(
            Message.user_id == user_id,
            Message.timestamp >= week_ago
        ).count()
        
        # Most recent message
        last_message = Message.query.filter_by(user_id=user_id).order_by(
            desc(Message.timestamp)
        ).first()
        
        # Get voice minutes remaining
        try:
            from backend.database.models.models import UserSubscription
            subscription = UserSubscription.query.filter_by(user_id=user_id).first()
            voice_minutes_remaining = int(subscription.remaining_minutes) if subscription else 100
        except:
            voice_minutes_remaining = 100
        
        return {
            'total_messages': message_count,
            'user_messages': user_message_count,
            'chat_sessions': chat_count,
            'persona_usage': [(p.persona, p.count) for p in persona_stats],
            'recent_activity': recent_messages,
            'last_activity': last_message.timestamp if last_message else None,
            'voice_minutes_remaining': voice_minutes_remaining
        }
        
    except Exception as e:
        current_app.logger.error(f"Error getting user statistics for {user_id}: {str(e)}")
        return {}

def get_user_messages(user_id: int, limit: int = 50, offset: int = 0, persona_filter: Optional[str] = None) -> List[Message]:
    """
    Get user's messages with optional filtering
    
    Args:
        user_id: User's ID
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        persona_filter: Filter by specific persona (optional)
    
    Returns:
        List of Message objects
    """
    try:
        query = Message.query.filter_by(user_id=user_id)
        
        if persona_filter:
            query = query.filter_by(persona=persona_filter)
        
        return query.order_by(desc(Message.timestamp)).offset(offset).limit(limit).all()
        
    except Exception as e:
        current_app.logger.error(f"Error getting user messages for {user_id}: {str(e)}")
        return []

def search_user_messages(user_id: int, search_term: str, limit: int = 20) -> List[Message]:
    """
    Search user's messages by content
    
    Args:
        user_id: User's ID
        search_term: Term to search for in message content
        limit: Maximum number of results
    
    Returns:
        List of matching Message objects
    """
    try:
        return Message.query.filter(
            Message.user_id == user_id,
            Message.content.contains(search_term)
        ).order_by(desc(Message.timestamp)).limit(limit).all()
        
    except Exception as e:
        current_app.logger.error(f"Error searching user messages for {user_id}: {str(e)}")
        return []

def update_user_profile_picture(user_id: int, file) -> Optional[str]:
    """
    Update user's profile picture
    
    Args:
        user_id: User's ID
        file: Uploaded file object
    
    Returns:
        String path to saved file or None if failed
    
    Raises:
        UserCRUDError: If update fails
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise UserCRUDError("User not found")
        
        if not file or not getattr(file, 'filename', None):
            raise UserCRUDError("No file provided")
        
        filename = secure_filename(file.filename)
        if not allowed_image_file(filename):
            raise UserCRUDError("Invalid file type. Allowed: .jpg, .jpeg, .png, .gif, .webp")
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config.get('PROFILE_PICS_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        file_ext = os.path.splitext(filename)[1]
        new_filename = f"user_{user_id}_{int(datetime.utcnow().timestamp())}{file_ext}"
        file_path = os.path.join(upload_folder, new_filename)
        
        # Delete old profile picture if exists
        if user.profile_picture:
            old_path = os.path.join(current_app.config.get('UPLOAD_FOLDER'), user.profile_picture)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass  # Don't fail if old file can't be deleted
        
        # Save new file
        file.save(file_path)
        
        # Update database with relative path
        relative_path = f"profile_pics/{new_filename}"
        user.profile_picture = relative_path
        db.session.commit()
        
        current_app.logger.info(f"Updated profile picture for user {user_id}")
        return relative_path
        
    except UserCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise UserCRUDError(f"Error updating profile picture: {str(e)}")

def get_user_profile_picture_url(user_id: int) -> Optional[str]:
    """
    Get user's profile picture URL
    
    Args:
        user_id: User's ID
    
    Returns:
        URL to profile picture or None
    """
    try:
        user = User.query.get(user_id)
        if user and user.profile_picture:
            return f"/uploads/{user.profile_picture}"
        return None
    except Exception as e:
        current_app.logger.error(f"Error getting profile picture URL for {user_id}: {str(e)}")
        return None