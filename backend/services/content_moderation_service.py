"""
Content Moderation Service - MyBella
Real-time content filtering and safety guardrails
"""

from backend.database.models.models import db
from backend.database.models.onboarding_models import ContentModerationLog
from flask import current_app
from datetime import datetime
import re
from typing import Dict, List, Tuple, Optional


class ContentModerationService:
    """Service for moderating user and AI content"""
    
    # Profanity and inappropriate language (with word boundaries)
    PROFANITY_PATTERNS = [
        r'\bf+u+c+k',
        r'\bs+h+i+t',
        r'a+s+s+h+o+l+e',
        r'\bb+i+t+c+h',
        r'\bd+a+m+n',
        r'\bc+r+a+p',
        r'\bh+e+l+l\b',  # Word boundary to avoid matching "hello"
        r'\bp+i+s+s',
        r'\bc+o+c+k\b',
        r'\bd+i+c+k\b',
        r'p+u+s+s+y',
        r's+l+u+t',
        r'w+h+o+r+e',
        r'c+u+n+t',
        r'\bf+a+g\b',
        r'n+i+g+g',
        r'r+e+t+a+r+d',
    ]
    
    # Sexual content patterns
    SEXUAL_PATTERNS = [
        r'\bsex\b',
        r'\bsexual\b',
        r'\bporn\b',
        r'\bxxx\b',
        r'\bnaked\b',
        r'\bnude\b',
        r'\bmasturbat',
        r'\borgasm\b',
        r'\bhorny\b',
        r'\barouse',
        r'\berotic\b',
        r'\bintercourse\b',
        r'\bforeplay\b',
        r'\bfetish\b',
    ]
    
    # Violence patterns
    VIOLENCE_PATTERNS = [
        r'\bkill\b',
        r'\bmurder\b',
        r'\bstab\b',
        r'\bshoot\b',
        r'\bgun\b',
        r'\bweapon\b',
        r'\battack\b',
        r'\bhurt\b',
        r'\bbeat\b',
        r'\bviolent',
        r'\bblood\b',
        r'\btorture\b',
        r'\babuse\b',
    ]
    
    # Harassment patterns
    HARASSMENT_PATTERNS = [
        r'\bhate you\b',
        r'\bkill yourself\b',
        r'\bdie\b',
        r'\bstupid\b',
        r'\bidiot\b',
        r'\bloser\b',
        r'\bpathetic\b',
        r'\bworthless\b',
        r'\bugly\b',
        r'\bfat\b',
        r'\bdumb\b',
    ]
    
    # Underage/minor protection (for 18+ features)
    UNDERAGE_PATTERNS = [
        r'\bchild\b',
        r'\bkid\b',
        r'\bminor\b',
        r'\bunderage\b',
        r'\bteen\b',
        r'\byoung\b',
        r'\blittle\b',
        r'\bschool\b',
    ]
    
    # Replacement words for profanity
    PROFANITY_REPLACEMENTS = {
        'fuck': '****',
        'shit': '****',
        'asshole': '*******',
        'bitch': '*****',
        'damn': '****',
        'crap': '****',
        'hell': '****',
        'piss': '****',
        'cock': '****',
        'dick': '****',
        'pussy': '*****',
        'slut': '****',
        'whore': '*****',
        'cunt': '****',
    }
    
    @staticmethod
    def moderate_content(
        content: str,
        user_id: int,
        content_type: str = 'message',
        content_id: Optional[int] = None,
        strict_mode: bool = False,
        age_tier: str = 'adult'
    ) -> Dict:
        """
        Moderate content for inappropriate material
        
        Args:
            content: Text to moderate
            user_id: User ID
            content_type: Type of content ('message', 'profile', 'persona_creation')
            content_id: Reference ID to actual content
            strict_mode: If True, block on any flags (default: False)
            age_tier: 'teen' or 'adult' (stricter for teens)
        
        Returns:
            {
                'allowed': bool,
                'filtered_content': str (cleaned version),
                'flags': list of flag reasons,
                'severity': str ('none', 'low', 'medium', 'high', 'critical'),
                'action': str ('pass', 'filter', 'block', 'warn')
            }
        """
        
        if not content or not content.strip():
            return {
                'allowed': True,
                'filtered_content': content,
                'flags': [],
                'severity': 'none',
                'action': 'pass'
            }
        
        content_lower = content.lower()
        flags = []
        severity = 'none'
        max_severity_score = 0
        
        # Check profanity
        profanity_matches = []
        for pattern in ContentModerationService.PROFANITY_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                profanity_matches.append(pattern)
        
        if profanity_matches:
            flags.append('profanity')
            max_severity_score = max(max_severity_score, 2)  # medium
        
        # Check sexual content
        sexual_matches = []
        for pattern in ContentModerationService.SEXUAL_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                sexual_matches.append(pattern)
        
        if sexual_matches:
            flags.append('sexual_content')
            # More severe for teen users
            if age_tier == 'teen':
                max_severity_score = max(max_severity_score, 4)  # critical
            else:
                max_severity_score = max(max_severity_score, 3)  # high
        
        # Check violence
        violence_matches = []
        for pattern in ContentModerationService.VIOLENCE_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                violence_matches.append(pattern)
        
        if violence_matches:
            flags.append('violence')
            max_severity_score = max(max_severity_score, 3)  # high
        
        # Check harassment
        harassment_matches = []
        for pattern in ContentModerationService.HARASSMENT_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                harassment_matches.append(pattern)
        
        if harassment_matches:
            flags.append('harassment')
            max_severity_score = max(max_severity_score, 3)  # high
        
        # Check underage content (critical for 18+ features)
        underage_matches = []
        if content_type in ['intimacy_mode', 'romantic']:
            for pattern in ContentModerationService.UNDERAGE_PATTERNS:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    underage_matches.append(pattern)
            
            if underage_matches:
                flags.append('underage_reference')
                max_severity_score = max(max_severity_score, 5)  # critical+
        
        # Convert severity score to label
        if max_severity_score == 0:
            severity = 'none'
        elif max_severity_score == 1:
            severity = 'low'
        elif max_severity_score == 2:
            severity = 'medium'
        elif max_severity_score == 3:
            severity = 'high'
        else:
            severity = 'critical'
        
        # Determine action
        action = 'pass'
        allowed = True
        filtered_content = content
        
        if severity == 'critical':
            # Block critical content
            action = 'block'
            allowed = False
            filtered_content = "[Content blocked due to policy violation]"
        
        elif severity == 'high':
            if strict_mode or age_tier == 'teen':
                # Block high severity in strict mode or for teens
                action = 'block'
                allowed = False
                filtered_content = "[Content blocked due to policy violation]"
            else:
                # Filter for adults in normal mode
                action = 'filter'
                allowed = True
                filtered_content = ContentModerationService._filter_content(content)
        
        elif severity == 'medium':
            # Filter medium severity content
            action = 'filter'
            allowed = True
            filtered_content = ContentModerationService._filter_content(content)
        
        elif severity == 'low':
            # Warn but allow
            action = 'warn'
            allowed = True
            filtered_content = content
        
        # Log moderation event
        ContentModerationService._log_moderation(
            user_id=user_id,
            content_type=content_type,
            content_id=content_id,
            content_excerpt=content[:500] if len(content) > 500 else content,
            flagged=(len(flags) > 0),
            flag_reason=', '.join(flags) if flags else None,
            severity=severity,
            action=action,
            automated=True,
            moderation_engine='regex_patterns',
            confidence_score=0.9 if flags else 1.0
        )
        
        return {
            'allowed': allowed,
            'filtered_content': filtered_content,
            'flags': flags,
            'severity': severity,
            'action': action
        }
    
    @staticmethod
    def _filter_content(content: str) -> str:
        """Replace profanity and inappropriate content with asterisks"""
        filtered = content
        
        # Replace profanity
        for word, replacement in ContentModerationService.PROFANITY_REPLACEMENTS.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            filtered = pattern.sub(replacement, filtered)
        
        return filtered
    
    @staticmethod
    def _log_moderation(
        user_id: int,
        content_type: str,
        content_id: Optional[int],
        content_excerpt: str,
        flagged: bool,
        flag_reason: Optional[str],
        severity: str,
        action: str,
        automated: bool,
        moderation_engine: str,
        confidence_score: float
    ):
        """Log moderation event to database"""
        try:
            log_entry = ContentModerationLog(
                user_id=user_id,
                content_type=content_type,
                content_id=content_id,
                content_excerpt=content_excerpt,
                flagged=flagged,
                flag_reason=flag_reason,
                severity=severity,
                action=action,
                automated=automated,
                moderation_engine=moderation_engine,
                confidence_score=confidence_score
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to log moderation event: {e}")
            db.session.rollback()
    
    @staticmethod
    def check_user_content(user_id: int, content: str, age_tier: str = 'adult') -> Dict:
        """
        Check user-generated content (messages, posts, etc.)
        More lenient than AI content
        """
        return ContentModerationService.moderate_content(
            content=content,
            user_id=user_id,
            content_type='message',
            strict_mode=False,
            age_tier=age_tier
        )
    
    @staticmethod
    def check_ai_response(user_id: int, response: str, age_tier: str = 'adult') -> Dict:
        """
        Check AI-generated responses
        Stricter to prevent harmful AI outputs
        """
        return ContentModerationService.moderate_content(
            content=response,
            user_id=user_id,
            content_type='ai_response',
            strict_mode=True,
            age_tier=age_tier
        )
    
    @staticmethod
    def get_safe_fallback_response(context: str = 'general') -> str:
        """
        Get a safe fallback response when content is blocked
        """
        fallbacks = {
            'general': "I want to keep our conversation positive and supportive. Let's talk about something else - how are you feeling today?",
            'profanity': "I noticed some language that might not be constructive. Let's keep our conversation respectful. What's on your mind?",
            'sexual': "I'm here to support your wellness and mental health. Let's keep our conversation appropriate. How can I help you today?",
            'violence': "I'm concerned about the direction of our conversation. I'm here to support you in healthy ways. Would you like to talk about what's troubling you?",
            'harassment': "I care about you and want to maintain a supportive space. Let's communicate with kindness. What's really going on?",
            'teen_blocked': "This topic isn't appropriate for our conversation right now. I'm here to support your wellness journey. What would you like to talk about?",
        }
        return fallbacks.get(context, fallbacks['general'])
    
    @staticmethod
    def get_user_moderation_stats(user_id: int, days: int = 30) -> Dict:
        """
        Get moderation statistics for a user
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total flags
        total_flags = ContentModerationLog.query.filter(
            ContentModerationLog.user_id == user_id,
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.flagged == True
        ).count()
        
        # Flags by severity
        critical_flags = ContentModerationLog.query.filter(
            ContentModerationLog.user_id == user_id,
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.severity == 'critical'
        ).count()
        
        high_flags = ContentModerationLog.query.filter(
            ContentModerationLog.user_id == user_id,
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.severity == 'high'
        ).count()
        
        # Actions taken
        blocks = ContentModerationLog.query.filter(
            ContentModerationLog.user_id == user_id,
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.action == 'block'
        ).count()
        
        filters = ContentModerationLog.query.filter(
            ContentModerationLog.user_id == user_id,
            ContentModerationLog.created_at >= cutoff_date,
            ContentModerationLog.action == 'filter'
        ).count()
        
        return {
            'total_flags': total_flags,
            'critical_flags': critical_flags,
            'high_flags': high_flags,
            'blocks': blocks,
            'filters': filters,
            'period_days': days
        }
    
    @staticmethod
    def is_teen_safe(content: str) -> bool:
        """
        Quick check if content is safe for teen users
        """
        result = ContentModerationService.moderate_content(
            content=content,
            user_id=0,  # System check
            content_type='teen_check',
            age_tier='teen',
            strict_mode=True
        )
        
        return result['allowed'] and result['severity'] in ['none', 'low']
    
    @staticmethod
    def sanitize_for_display(content: str) -> str:
        """
        Sanitize content for display (remove profanity, keep context)
        """
        return ContentModerationService._filter_content(content)
