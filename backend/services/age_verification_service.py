"""
Age Verification Service
Handles age-gated feature access and compliance (COPPA, GDPR-K)
"""

from datetime import datetime, date
from typing import Dict, Optional, List, Any
from flask import request

from backend.database.models.models import db, User
from backend.database.models.age_verification_models import (
    UserAgeVerification, FeatureAccess, UserFeatureOverride, PersonaAgeRestriction
)


class AgeVerificationService:
    """
    Service for managing age verification and feature access control
    
    Features:
    - Age calculation from DOB
    - Age tier classification (minor/teen/adult)
    - Feature access checking
    - Persona behavior adaptation
    - Compliance tracking
    """
    
    @staticmethod
    def verify_age(user_id: int, date_of_birth: date, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """
        Verify user's age and create/update age verification record
        
        Args:
            user_id: User ID
            date_of_birth: User's date of birth
            ip_address: IP address for compliance logging
            user_agent: User agent for compliance logging
            
        Returns:
            Dictionary with verification status and age tier
        """
        # Check if verification already exists
        verification = UserAgeVerification.query.filter_by(user_id=user_id).first()
        
        if verification:
            # Update existing verification
            verification.date_of_birth = date_of_birth
            verification.ip_address = ip_address or request.remote_addr
            verification.user_agent = user_agent or request.headers.get('User-Agent')
            verification.update_age_tier()
        else:
            # Create new verification
            verification = UserAgeVerification(
                user_id=user_id,
                date_of_birth=date_of_birth,
                ip_address=ip_address or request.remote_addr,
                user_agent=user_agent or request.headers.get('User-Agent')
            )
            verification.update_age_tier()
            db.session.add(verification)
        
        db.session.commit()
        
        age = verification.calculate_age()
        
        return {
            'success': True,
            'age': age,
            'age_tier': verification.age_tier,
            'is_teen': verification.is_teen,
            'is_adult': verification.is_adult,
            'is_minor': verification.is_minor,
            'verified_at': verification.age_verified_at.isoformat()
        }
    
    @staticmethod
    def get_user_age_info(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get age verification information for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with age info or None if not verified
        """
        verification = UserAgeVerification.query.filter_by(user_id=user_id).first()
        
        if not verification:
            return None
        
        # Update age tier in case user had birthday
        verification.update_age_tier()
        db.session.commit()
        
        age = verification.calculate_age()
        
        return {
            'age': age,
            'age_tier': verification.age_tier,
            'is_teen': verification.is_teen,
            'is_adult': verification.is_adult,
            'is_minor': verification.is_minor,
            'date_of_birth': verification.date_of_birth.isoformat(),
            'verified_at': verification.age_verified_at.isoformat()
        }
    
    @staticmethod
    def check_feature_access(user_id: int, feature_key: str) -> Dict[str, Any]:
        """
        Check if user has access to a specific feature
        
        Args:
            user_id: User ID
            feature_key: Feature identifier (e.g., 'intimacy_mode')
            
        Returns:
            Dictionary with access status and reason
        """
        # Get user's age info
        age_info = AgeVerificationService.get_user_age_info(user_id)
        
        if not age_info:
            return {
                'accessible': False,
                'reason': 'Age verification required',
                'requires_verification': True
            }
        
        age = age_info['age']
        
        # Check for manual overrides first
        override = UserFeatureOverride.query.filter_by(
            user_id=user_id,
            feature_key=feature_key
        ).first()
        
        if override and override.is_active():
            if override.override_type == 'grant':
                return {
                    'accessible': True,
                    'reason': 'Manual override granted',
                    'override': True
                }
            else:
                return {
                    'accessible': False,
                    'reason': override.reason or 'Access manually denied',
                    'override': True
                }
        
        # Check feature access rules
        feature = FeatureAccess.query.filter_by(feature_key=feature_key, is_active=True).first()
        
        if not feature:
            return {
                'accessible': True,  # Feature not restricted
                'reason': 'Feature not in access control system'
            }
        
        # Check age requirements
        accessible = feature.is_accessible_for_age(age)
        
        if not accessible:
            if age < feature.min_age_required:
                reason = f'Minimum age {feature.min_age_required} required'
            elif feature.adult_only and age < 18:
                reason = 'This feature is only available for users 18+'
            elif age_info['is_teen'] and not feature.teen_accessible:
                reason = 'This feature is not available in Teen Mode (16-17)'
            else:
                reason = 'Access restricted based on age'
            
            return {
                'accessible': False,
                'reason': reason,
                'min_age_required': feature.min_age_required,
                'compliance_reason': feature.compliance_reason
            }
        
        return {
            'accessible': True,
            'reason': 'Age requirements met'
        }
    
    @staticmethod
    def get_accessible_features(user_id: int) -> List[str]:
        """
        Get list of features accessible to user based on age
        
        Args:
            user_id: User ID
            
        Returns:
            List of accessible feature keys
        """
        age_info = AgeVerificationService.get_user_age_info(user_id)
        
        if not age_info:
            return []
        
        age = age_info['age']
        
        # Get all active features
        features = FeatureAccess.query.filter_by(is_active=True).all()
        
        accessible = []
        for feature in features:
            if feature.is_accessible_for_age(age):
                accessible.append(feature.feature_key)
        
        # Add any manual overrides
        overrides = UserFeatureOverride.query.filter_by(user_id=user_id).all()
        for override in overrides:
            if override.is_active() and override.override_type == 'grant':
                if override.feature_key not in accessible:
                    accessible.append(override.feature_key)
        
        return accessible
    
    @staticmethod
    def get_restricted_features(user_id: int) -> List[Dict[str, Any]]:
        """
        Get list of features NOT accessible to user (with reasons)
        
        Args:
            user_id: User ID
            
        Returns:
            List of restricted feature dictionaries
        """
        age_info = AgeVerificationService.get_user_age_info(user_id)
        
        if not age_info:
            return []
        
        age = age_info['age']
        
        # Get all active features
        features = FeatureAccess.query.filter_by(is_active=True).all()
        
        restricted = []
        for feature in features:
            if not feature.is_accessible_for_age(age):
                restricted.append({
                    'feature_key': feature.feature_key,
                    'feature_name': feature.feature_name,
                    'min_age_required': feature.min_age_required,
                    'reason': feature.compliance_reason,
                    'years_until_access': max(0, feature.min_age_required - age)
                })
        
        return restricted
    
    @staticmethod
    def get_persona_behavior(persona_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get age-appropriate persona behavior settings
        
        Args:
            persona_id: Persona ID
            user_id: User ID
            
        Returns:
            Dictionary with persona behavior settings
        """
        age_info = AgeVerificationService.get_user_age_info(user_id)
        
        if not age_info:
            # Default safe behavior
            return {
                'tone': 'supportive',
                'system_prompt': 'You are a supportive, wellness-focused AI companion.',
                'allow_romantic': False,
                'allow_flirty': False,
                'allow_intimacy': False,
                'wellness_only': True
            }
        
        age = age_info['age']
        
        # Get persona age restrictions
        restriction = PersonaAgeRestriction.query.filter_by(persona_id=persona_id).first()
        
        if not restriction:
            # No specific restrictions, use age-based defaults
            if age_info['is_teen']:
                return {
                    'tone': 'supportive',
                    'system_prompt': 'You are a supportive, wellness-focused AI companion. Be encouraging and professional.',
                    'allow_romantic': False,
                    'allow_flirty': False,
                    'allow_intimacy': False,
                    'wellness_only': True
                }
            else:
                return {
                    'tone': 'conversational',
                    'system_prompt': '',
                    'allow_romantic': True,
                    'allow_flirty': True,
                    'allow_intimacy': True,
                    'wellness_only': False
                }
        
        # Use configured restrictions
        if age_info['is_teen']:
            return {
                'tone': restriction.teen_tone,
                'system_prompt': restriction.teen_system_prompt,
                'allow_romantic': False,
                'allow_flirty': False,
                'allow_intimacy': False,
                'wellness_only': restriction.wellness_focus_only
            }
        else:
            return {
                'tone': restriction.adult_tone or 'conversational',
                'system_prompt': restriction.adult_system_prompt or '',
                'allow_romantic': restriction.allow_romantic_dialogue,
                'allow_flirty': restriction.allow_flirty_responses,
                'allow_intimacy': restriction.allow_intimacy_content,
                'wellness_only': False
            }
    
    @staticmethod
    def requires_age_verification(user_id: int) -> bool:
        """
        Check if user needs to verify their age
        
        Args:
            user_id: User ID
            
        Returns:
            True if verification required, False otherwise
        """
        verification = UserAgeVerification.query.filter_by(user_id=user_id).first()
        return verification is None
    
    @staticmethod
    def get_age_gate_message(user_id: int) -> Optional[str]:
        """
        Get age-appropriate feature restriction message
        
        Args:
            user_id: User ID
            
        Returns:
            Message to display or None if unrestricted
        """
        age_info = AgeVerificationService.get_user_age_info(user_id)
        
        if not age_info:
            return None
        
        if age_info['is_minor']:
            return "MyBella requires users to be at least 16 years old. Please contact support for more information."
        
        if age_info['is_teen']:
            return "You're using MyBella in Teen Mode (16-17). Romantic features are disabled, but you have full access to wellness, CBT, and study tools!"
        
        return None  # Adult, no restrictions
