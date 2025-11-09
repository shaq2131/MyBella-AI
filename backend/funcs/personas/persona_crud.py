"""
Persona Profile CRUD Functions for MyBella
Database operations for managing persona profiles and avatars
"""

import os
from typing import Optional, List, Dict, Any
from flask import current_app
from werkzeug.utils import secure_filename
from backend.database.models.models import db, PersonaProfile
from backend.database.utils.utils import safe_filename, allowed_image_file
from sqlalchemy.exc import IntegrityError
from datetime import datetime

class PersonaCRUDError(Exception):
    """Custom exception for persona CRUD operations"""
    pass

def create_persona_profile(name: str, display_name: Optional[str] = None, 
                          description: Optional[str] = None) -> PersonaProfile:
    """
    Create a new persona profile
    
    Args:
        name: Persona name (unique identifier)
        display_name: Friendly display name
        description: Persona description
    
    Returns:
        PersonaProfile object
    
    Raises:
        PersonaCRUDError: If creation fails
    """
    try:
        # Check if persona already exists
        if PersonaProfile.query.filter_by(name=name).first():
            raise PersonaCRUDError(f"Persona {name} already exists")
        
        persona = PersonaProfile(
            name=name.strip(),
            display_name=display_name.strip() if display_name else None,
            description=description.strip() if description else None
        )
        
        db.session.add(persona)
        db.session.commit()
        
        current_app.logger.info(f"Created persona profile: {name}")
        return persona
        
    except IntegrityError as e:
        db.session.rollback()
        raise PersonaCRUDError(f"Database error: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise PersonaCRUDError(f"Error creating persona: {str(e)}")

def get_persona_profile(name: str) -> Optional[PersonaProfile]:
    """
    Get persona profile by name
    
    Args:
        name: Persona name
    
    Returns:
        PersonaProfile object or None
    """
    try:
        return PersonaProfile.query.filter_by(name=name).first()
    except Exception as e:
        current_app.logger.error(f"Error getting persona {name}: {str(e)}")
        return None

def get_all_personas() -> List[PersonaProfile]:
    """
    Get all active persona profiles
    
    Returns:
        List of PersonaProfile objects
    """
    try:
        return PersonaProfile.query.filter_by(is_active=True).order_by(PersonaProfile.name).all()
    except Exception as e:
        current_app.logger.error(f"Error getting all personas: {str(e)}")
        return []

def update_persona_profile_picture(name: str, file) -> Optional[str]:
    """
    Update persona's profile picture
    
    Args:
        name: Persona name
        file: Uploaded file object
    
    Returns:
        String path to saved file or None if failed
    
    Raises:
        PersonaCRUDError: If update fails
    """
    try:
        persona = PersonaProfile.query.filter_by(name=name).first()
        if not persona:
            raise PersonaCRUDError(f"Persona {name} not found")
        
        if not file or not getattr(file, 'filename', None):
            raise PersonaCRUDError("No file provided")
        
        filename = secure_filename(file.filename)
        if not allowed_image_file(filename):
            raise PersonaCRUDError("Invalid file type. Allowed: .jpg, .jpeg, .png, .gif, .webp")
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config.get('PERSONA_PICS_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        file_ext = os.path.splitext(filename)[1]
        new_filename = f"persona_{name.lower()}_{int(datetime.utcnow().timestamp())}{file_ext}"
        file_path = os.path.join(upload_folder, new_filename)
        
        # Delete old profile picture if exists
        if persona.profile_picture:
            old_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', ''), persona.profile_picture)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass  # Don't fail if old file can't be deleted
        
        # Save new file
        file.save(file_path)
        
        # Update database with relative path
        relative_path = f"persona_pics/{new_filename}"
        persona.profile_picture = relative_path
        persona.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"Updated profile picture for persona {name}")
        return relative_path
        
    except PersonaCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise PersonaCRUDError(f"Error updating persona profile picture: {str(e)}")

def get_persona_profile_picture_url(name: str) -> Optional[str]:
    """
    Get persona's profile picture URL
    
    Args:
        name: Persona name
    
    Returns:
        URL to profile picture or None
    """
    try:
        persona = PersonaProfile.query.filter_by(name=name).first()
        if persona and persona.profile_picture:
            return f"/uploads/{persona.profile_picture}"
        return None
    except Exception as e:
        current_app.logger.error(f"Error getting persona profile picture URL for {name}: {str(e)}")
        return None

def update_persona_profile(name: str, display_name: Optional[str] = None,
                          description: Optional[str] = None) -> bool:
    """
    Update persona profile information
    
    Args:
        name: Persona name
        display_name: New display name
        description: New description
    
    Returns:
        bool: True if successful
    
    Raises:
        PersonaCRUDError: If update fails
    """
    try:
        persona = PersonaProfile.query.filter_by(name=name).first()
        if not persona:
            raise PersonaCRUDError(f"Persona {name} not found")
        
        if display_name is not None:
            persona.display_name = display_name.strip() if display_name else None
        
        if description is not None:
            persona.description = description.strip() if description else None
        
        persona.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"Updated persona profile: {name}")
        return True
        
    except PersonaCRUDError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise PersonaCRUDError(f"Error updating persona: {str(e)}")

def get_persona_with_picture_info(name: str) -> Dict[str, Any]:
    """
    Get persona with profile picture information for chat display
    
    Args:
        name: Persona name
    
    Returns:
        Dictionary with persona info and picture URL
    """
    try:
        persona = PersonaProfile.query.filter_by(name=name).first()
        
        result = {
            'name': name,
            'display_name': persona.display_name if persona else name,
            'description': persona.description if persona else None,
            'profile_picture_url': None
        }
        
        if persona and persona.profile_picture:
            result['profile_picture_url'] = f"/uploads/{persona.profile_picture}"
        
        return result
        
    except Exception as e:
        current_app.logger.error(f"Error getting persona info for {name}: {str(e)}")
        return {
            'name': name,
            'display_name': name,
            'description': None,
            'profile_picture_url': None
        }