"""
Secrets Vault Service
PIN-protected private journaling with encryption simulation
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
from backend.database.models.models import db
from backend.database.models.wellness_models import SecretVaultEntry
import hashlib
import json


class SecretsVaultService:
    """Service for managing PIN-protected secret journal entries"""
    
    @staticmethod
    def verify_pin(user_id: int, pin: str) -> bool:
        """
        Verify user's vault PIN
        
        Args:
            user_id: User ID
            pin: 4-digit PIN to verify
            
        Returns:
            True if PIN matches, False otherwise
        """
        try:
            # Get user's PIN hash from first entry or settings
            entry = SecretVaultEntry.query.filter_by(user_id=user_id).first()
            
            if not entry:
                return False  # No vault set up yet
            
            pin_hash = SecretsVaultService._hash_pin(pin)
            return entry.pin_hash == pin_hash
            
        except Exception as e:
            current_app.logger.error(f"Error verifying PIN: {e}")
            return False
    
    @staticmethod
    def set_pin(user_id: int, pin: str) -> Dict[str, Any]:
        """
        Set or update vault PIN for user
        
        Args:
            user_id: User ID
            pin: 4-digit PIN
            
        Returns:
            Result dictionary
        """
        try:
            # Validate PIN format
            if not pin or len(pin) != 4 or not pin.isdigit():
                return {
                    'success': False,
                    'error': 'PIN must be exactly 4 digits'
                }
            
            pin_hash = SecretsVaultService._hash_pin(pin)
            
            # Update all user's entries with new PIN hash
            entries = SecretVaultEntry.query.filter_by(user_id=user_id).all()
            
            if entries:
                for entry in entries:
                    entry.pin_hash = pin_hash
            else:
                # Create initial entry to store PIN
                entry = SecretVaultEntry(
                    user_id=user_id,
                    title="Welcome to Your Vault",
                    content="This is your private space. Only you can access these entries with your PIN.",
                    pin_hash=pin_hash,
                    is_encrypted=True
                )
                db.session.add(entry)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'PIN set successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error setting PIN: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_entry(user_id: int, title: str, content: str, pin: str, 
                    tags: List[str] = None, mood: str = None) -> Dict[str, Any]:
        """
        Create new vault entry
        
        Args:
            user_id: User ID
            title: Entry title
            content: Entry content
            pin: PIN for verification
            tags: Optional tags
            mood: Optional mood rating
            
        Returns:
            Result with entry data
        """
        try:
            # Verify PIN
            if not SecretsVaultService.verify_pin(user_id, pin):
                return {
                    'success': False,
                    'error': 'Invalid PIN'
                }
            
            pin_hash = SecretsVaultService._hash_pin(pin)
            
            # Create entry
            entry = SecretVaultEntry(
                user_id=user_id,
                title=title,
                content=content,
                pin_hash=pin_hash,
                tags=json.dumps(tags) if tags else None,
                mood=mood,
                is_encrypted=True
            )
            
            db.session.add(entry)
            db.session.commit()
            
            return {
                'success': True,
                'entry': entry.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating vault entry: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_entries(user_id: int, pin: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get all vault entries for user
        
        Args:
            user_id: User ID
            pin: PIN for verification
            limit: Max number of entries
            
        Returns:
            Result with entries list
        """
        try:
            # Verify PIN
            if not SecretsVaultService.verify_pin(user_id, pin):
                return {
                    'success': False,
                    'error': 'Invalid PIN'
                }
            
            entries = SecretVaultEntry.query.filter_by(
                user_id=user_id
            ).order_by(
                SecretVaultEntry.created_at.desc()
            ).limit(limit).all()
            
            return {
                'success': True,
                'entries': [entry.to_dict() for entry in entries],
                'count': len(entries)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting vault entries: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_entry(user_id: int, entry_id: int, pin: str) -> Dict[str, Any]:
        """
        Get single vault entry
        
        Args:
            user_id: User ID
            entry_id: Entry ID
            pin: PIN for verification
            
        Returns:
            Result with entry data
        """
        try:
            # Verify PIN
            if not SecretsVaultService.verify_pin(user_id, pin):
                return {
                    'success': False,
                    'error': 'Invalid PIN'
                }
            
            entry = SecretVaultEntry.query.filter_by(
                id=entry_id,
                user_id=user_id
            ).first()
            
            if not entry:
                return {
                    'success': False,
                    'error': 'Entry not found'
                }
            
            return {
                'success': True,
                'entry': entry.to_dict()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting vault entry: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def update_entry(user_id: int, entry_id: int, pin: str,
                    title: str = None, content: str = None,
                    tags: List[str] = None, mood: str = None) -> Dict[str, Any]:
        """
        Update vault entry
        
        Args:
            user_id: User ID
            entry_id: Entry ID
            pin: PIN for verification
            title: New title (optional)
            content: New content (optional)
            tags: New tags (optional)
            mood: New mood (optional)
            
        Returns:
            Result with updated entry
        """
        try:
            # Verify PIN
            if not SecretsVaultService.verify_pin(user_id, pin):
                return {
                    'success': False,
                    'error': 'Invalid PIN'
                }
            
            entry = SecretVaultEntry.query.filter_by(
                id=entry_id,
                user_id=user_id
            ).first()
            
            if not entry:
                return {
                    'success': False,
                    'error': 'Entry not found'
                }
            
            # Update fields
            if title is not None:
                entry.title = title
            if content is not None:
                entry.content = content
            if tags is not None:
                entry.tags = json.dumps(tags)
            if mood is not None:
                entry.mood = mood
            
            entry.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'entry': entry.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating vault entry: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def delete_entry(user_id: int, entry_id: int, pin: str) -> Dict[str, Any]:
        """
        Delete vault entry
        
        Args:
            user_id: User ID
            entry_id: Entry ID
            pin: PIN for verification
            
        Returns:
            Result dictionary
        """
        try:
            # Verify PIN
            if not SecretsVaultService.verify_pin(user_id, pin):
                return {
                    'success': False,
                    'error': 'Invalid PIN'
                }
            
            entry = SecretVaultEntry.query.filter_by(
                id=entry_id,
                user_id=user_id
            ).first()
            
            if not entry:
                return {
                    'success': False,
                    'error': 'Entry not found'
                }
            
            db.session.delete(entry)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Entry deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting vault entry: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_stats(user_id: int, pin: str) -> Dict[str, Any]:
        """
        Get vault statistics
        
        Args:
            user_id: User ID
            pin: PIN for verification
            
        Returns:
            Statistics dictionary
        """
        try:
            # Verify PIN
            if not SecretsVaultService.verify_pin(user_id, pin):
                return {
                    'success': False,
                    'error': 'Invalid PIN'
                }
            
            entries = SecretVaultEntry.query.filter_by(user_id=user_id).all()
            
            if not entries:
                return {
                    'success': True,
                    'stats': {
                        'total_entries': 0,
                        'first_entry': None,
                        'last_entry': None,
                        'total_words': 0
                    }
                }
            
            total_words = sum(len(entry.content.split()) for entry in entries if entry.content)
            
            return {
                'success': True,
                'stats': {
                    'total_entries': len(entries),
                    'first_entry': min(entry.created_at for entry in entries).isoformat(),
                    'last_entry': max(entry.created_at for entry in entries).isoformat(),
                    'total_words': total_words
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting vault stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _hash_pin(pin: str) -> str:
        """Hash PIN using SHA-256"""
        return hashlib.sha256(pin.encode()).hexdigest()
    
    @staticmethod
    def has_vault(user_id: int) -> bool:
        """Check if user has set up vault"""
        return SecretVaultEntry.query.filter_by(user_id=user_id).count() > 0
