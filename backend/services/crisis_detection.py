"""
Crisis Detection Service for MyBella AI Wellness Companion
Monitors user messages for crisis indicators and provides immediate support resources
"""

import re
from typing import Dict, List, Tuple

# Crisis keywords and phrases (comprehensive list)
CRISIS_KEYWORDS = [
    # Suicide ideation
    'kill myself', 'end my life', 'suicide', 'suicidal', 'want to die', 
    'better off dead', 'no reason to live', 'can\'t go on', 'end it all',
    'take my own life', 'don\'t want to be alive', 'wish i was dead',
    
    # Self-harm
    'cut myself', 'hurt myself', 'self harm', 'self-harm', 'cutting',
    'burning myself', 'punish myself',
    
    # Severe distress
    'nobody cares', 'everyone hates me', 'worthless', 'hopeless',
    'can\'t take it anymore', 'give up', 'no hope', 'pointless',
    
    # Planning indicators
    'goodbye forever', 'final goodbye', 'won\'t be here', 'last time',
    'made my decision', 'planning to', 'going to end',
    
    # Abuse indicators
    'being abused', 'hurting me', 'afraid for my life', 'threatening me',
    'domestic violence', 'sexual abuse',
]

# Regex patterns for more complex detection
CRISIS_PATTERNS = [
    r'\b(want|going|plan)\s+(to\s+)?(die|kill\s+myself|end\s+it)\b',
    r'\b(no\s+)?(point|reason)\s+(in|to)\s+(living|live|continue)\b',
    r'\bcan\'?t\s+(take|handle|deal)\s+.+\s+anymore\b',
    r'\bgoodbye\s+(cruel\s+)?world\b',
    r'\bfinal\s+(message|goodbye|words)\b',
]

# Support resources
CRISIS_RESOURCES = {
    'hotlines': [
        {
            'name': '988 Suicide & Crisis Lifeline',
            'number': '988',
            'description': 'Free, confidential support 24/7 for people in distress',
            'availability': '24/7',
            'languages': 'English & Spanish'
        },
        {
            'name': 'Crisis Text Line',
            'number': 'Text HOME to 741741',
            'description': 'Free, 24/7 crisis support via text message',
            'availability': '24/7',
            'languages': 'English & Spanish'
        },
        {
            'name': 'National Domestic Violence Hotline',
            'number': '1-800-799-7233',
            'description': 'Support for domestic violence situations',
            'availability': '24/7',
            'languages': 'Multiple languages'
        },
        {
            'name': 'SAMHSA National Helpline',
            'number': '1-800-662-4357',
            'description': 'Treatment referral and information service',
            'availability': '24/7',
            'languages': 'English & Spanish'
        },
        {
            'name': 'Veterans Crisis Line',
            'number': '1-800-273-8255 (Press 1)',
            'description': 'Support for veterans and their families',
            'availability': '24/7',
            'languages': 'Multiple languages'
        }
    ],
    'online_resources': [
        {
            'name': 'International Association for Suicide Prevention',
            'url': 'https://www.iasp.info/resources/Crisis_Centres/',
            'description': 'Crisis centers worldwide directory'
        },
        {
            'name': 'NAMI (National Alliance on Mental Illness)',
            'url': 'https://www.nami.org/help',
            'description': 'Mental health resources and support'
        }
    ]
}


def detect_crisis(message: str) -> Tuple[bool, str, List[str]]:
    """
    Analyze user message for crisis indicators.
    
    Args:
        message: User's message text
        
    Returns:
        Tuple of (is_crisis, severity_level, matched_keywords)
        - is_crisis: Boolean indicating if crisis detected
        - severity_level: 'high', 'medium', 'low'
        - matched_keywords: List of matched crisis indicators
    """
    if not message:
        return False, 'none', []
    
    message_lower = message.lower().strip()
    matched_keywords = []
    
    # Check for direct keyword matches
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            matched_keywords.append(keyword)
    
    # Check regex patterns
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            matched_keywords.append(f"pattern:{pattern[:30]}")
    
    # Determine if crisis detected
    is_crisis = len(matched_keywords) > 0
    
    # Determine severity
    severity = 'none'
    if is_crisis:
        # High severity keywords
        high_severity = ['kill myself', 'suicide', 'end my life', 'want to die', 
                        'final goodbye', 'made my decision', 'going to end']
        
        if any(kw in message_lower for kw in high_severity):
            severity = 'high'
        elif len(matched_keywords) >= 2:
            severity = 'high'
        elif len(matched_keywords) == 1:
            # Check if it's a strong indicator
            strong_indicators = ['suicidal', 'self harm', 'cut myself', 'hurt myself']
            if any(kw in message_lower for kw in strong_indicators):
                severity = 'medium'
            else:
                severity = 'low'
    
    return is_crisis, severity, matched_keywords


def get_crisis_response(severity: str = 'medium') -> Dict:
    """
    Get appropriate crisis response based on severity.
    
    Args:
        severity: Crisis severity level ('high', 'medium', 'low')
        
    Returns:
        Dictionary with response message and resources
    """
    responses = {
        'high': {
            'message': (
                "🆘 I'm deeply concerned about what you've shared. Your safety is the most important thing right now.\n\n"
                "**Please reach out for immediate help:**\n"
                "• Call 988 (Suicide & Crisis Lifeline) - Available 24/7\n"
                "• Text HOME to 741741 (Crisis Text Line)\n"
                "• If you're in immediate danger, please call 911\n\n"
                "You don't have to face this alone. These trained professionals are here to help you through this moment."
            ),
            'show_resources': True,
            'alert_level': 'critical'
        },
        'medium': {
            'message': (
                "I hear that you're going through a really difficult time right now, and I'm concerned about you.\n\n"
                "**Support is available:**\n"
                "• 988 Suicide & Crisis Lifeline (24/7)\n"
                "• Crisis Text Line: Text HOME to 741741\n\n"
                "Talking to someone who specializes in crisis support can make a real difference. "
                "Would you like to see more resources?"
            ),
            'show_resources': True,
            'alert_level': 'warning'
        },
        'low': {
            'message': (
                "It sounds like you're dealing with some difficult feelings. I want you to know that support is available.\n\n"
                "If things feel overwhelming, please consider reaching out:\n"
                "• 988 Suicide & Crisis Lifeline\n"
                "• Crisis Text Line: Text HOME to 741741\n\n"
                "I'm here to listen, but professional crisis counselors are specially trained to help."
            ),
            'show_resources': False,
            'alert_level': 'info'
        }
    }
    
    return responses.get(severity, responses['medium'])


def get_all_crisis_resources() -> Dict:
    """
    Get comprehensive crisis resources.
    
    Returns:
        Dictionary with all available crisis resources
    """
    return CRISIS_RESOURCES


def log_crisis_event(user_id: int, message: str, severity: str, matched_keywords: List[str]):
    """
    Log crisis detection event for monitoring and follow-up.
    This should be implemented to store in database for admin review.
    
    Args:
        user_id: ID of the user
        message: The message that triggered detection
        severity: Crisis severity level
        matched_keywords: List of matched crisis indicators
    """
    # TODO: Implement database logging
    # This is critical for:
    # 1. Admin monitoring and intervention
    # 2. Follow-up with users
    # 3. System improvement
    # 4. Legal compliance
    
    import datetime
    log_entry = {
        'user_id': user_id,
        'timestamp': datetime.datetime.now(),
        'severity': severity,
        'matched_keywords': matched_keywords,
        'message_preview': message[:100] if len(message) > 100 else message
    }
    
    # For now, print to console (should be stored in database)
    print(f"CRISIS EVENT LOGGED: {log_entry}")
    
    return log_entry


def should_block_ai_response(severity: str) -> bool:
    """
    Determine if AI response should be blocked/modified in crisis situations.
    
    Args:
        severity: Crisis severity level
        
    Returns:
        Boolean indicating if normal AI response should be blocked
    """
    # Block AI response for high severity to prioritize crisis resources
    return severity == 'high'
