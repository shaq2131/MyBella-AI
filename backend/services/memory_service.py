"""
Memory Service for MyBella
Manages conversation context, user preferences, and memory retrieval
AI-AGNOSTIC: Works with any AI provider (OpenAI, Claude, Gemini, etc.)
"""

from backend.database.models.models import db
from backend.database.models.memory_models import ConversationMemory, ChatMessage, UserPreference
from datetime import datetime, timedelta
from sqlalchemy import desc, func
import json


class MemoryService:
    """Service for managing conversation memory and context"""
    
    @staticmethod
    def save_message(user_id, role, content, persona=None, persona_id=None, session_id=None, model=None):
        """
        Save a chat message to history
        
        Args:
            user_id: User ID
            role: 'user' or 'assistant'
            content: Message content
            persona: Persona name (optional, legacy)
            persona_id: Persona ID for memory isolation (optional)
            session_id: Session identifier (optional)
            model: AI model used (optional)
        
        Returns:
            ChatMessage object
        """
        # Find or create conversation memory for this session
        memory = None
        if session_id:
            memory = ConversationMemory.query.filter_by(
                user_id=user_id,
                session_id=session_id
            ).first()
            
            if not memory:
                memory = ConversationMemory(
                    user_id=user_id,
                    persona=persona or 'Unknown',
                    persona_id=persona_id,
                    session_id=session_id
                )
                db.session.add(memory)
                db.session.flush()
        
        # Create message with persona_id for memory isolation
        message = ChatMessage(
            user_id=user_id,
            memory_id=memory.id if memory else None,
            role=role,
            content=content,
            persona=persona,
            persona_id=persona_id,  # NEW: Per-persona memory
            model=model
        )
        
        # Update memory metadata
        if memory:
            memory.message_count = (memory.message_count or 0) + 1
            memory.last_updated = datetime.utcnow()
        
        db.session.add(message)
        db.session.commit()
        
        return message
    
    @staticmethod
    def get_recent_context(user_id, persona=None, persona_id=None, limit=10):
        """
        Get recent conversation context for AI prompt (per-persona isolation)
        
        Args:
            user_id: User ID
            persona: Filter by persona name (optional, legacy)
            persona_id: Filter by persona ID (NEW - recommended)
            limit: Number of recent messages to retrieve
        
        Returns:
            List of message dicts suitable for AI context
        """
        query = ChatMessage.query.filter_by(user_id=user_id)
        
        # Prefer persona_id filtering for memory isolation
        if persona_id:
            query = query.filter_by(persona_id=persona_id)
        elif persona:
            query = query.filter_by(persona=persona)
        
        messages = query.order_by(desc(ChatMessage.timestamp)).limit(limit).all()
        
        # Reverse to chronological order
        messages.reverse()
        
        # Format for AI context
        context = []
        for msg in messages:
            context.append({
                'role': msg.role,
                'content': msg.content
            })
        
        return context
    
    @staticmethod
    def get_conversation_summary(user_id, persona=None, days=7):
        """
        Get summary of recent conversations
        
        Args:
            user_id: User ID
            persona: Filter by persona (optional)
            days: Number of days to look back
        
        Returns:
            Dict with conversation summary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = ConversationMemory.query.filter(
            ConversationMemory.user_id == user_id,
            ConversationMemory.last_updated >= cutoff_date
        )
        
        if persona:
            query = query.filter_by(persona=persona)
        
        memories = query.order_by(desc(ConversationMemory.last_updated)).all()
        
        # Aggregate summaries
        all_topics = []
        total_messages = 0
        recent_moods = []
        
        for memory in memories:
            if memory.key_topics:
                all_topics.extend(memory.key_topics.split(','))
            total_messages += memory.message_count or 0
            if memory.user_mood:
                recent_moods.append(memory.user_mood)
        
        # Get unique topics
        unique_topics = list(set([t.strip() for t in all_topics if t.strip()]))
        
        return {
            'conversation_count': len(memories),
            'total_messages': total_messages,
            'key_topics': unique_topics[:10],  # Top 10 topics
            'recent_moods': recent_moods[:5],  # Last 5 moods
            'time_period_days': days
        }
    
    @staticmethod
    def get_user_preferences(user_id, category=None):
        """
        Get learned user preferences
        
        Args:
            user_id: User ID
            category: Filter by category (optional)
        
        Returns:
            List of preference dicts
        """
        query = UserPreference.query.filter_by(user_id=user_id)
        
        if category:
            query = query.filter_by(category=category)
        
        preferences = query.order_by(desc(UserPreference.confidence)).all()
        
        return [p.to_dict() for p in preferences]
    
    @staticmethod
    def save_preference(user_id, category, key, value, confidence=1.0, learned_from='conversation'):
        """
        Save or update a user preference
        
        Args:
            user_id: User ID
            category: Preference category
            key: Preference key
            value: Preference value
            confidence: Confidence score (0-1)
            learned_from: Source of preference
        
        Returns:
            UserPreference object
        """
        # Check if preference exists
        preference = UserPreference.query.filter_by(
            user_id=user_id,
            category=category,
            key=key
        ).first()
        
        if preference:
            # Update existing
            preference.value = value
            preference.confidence = max(preference.confidence, confidence)
            preference.last_confirmed = datetime.utcnow()
            preference.times_observed += 1
        else:
            # Create new
            preference = UserPreference(
                user_id=user_id,
                category=category,
                key=key,
                value=value,
                confidence=confidence,
                learned_from=learned_from
            )
            db.session.add(preference)
        
        db.session.commit()
        return preference
    
    @staticmethod
    def build_ai_context(user_id, persona, include_preferences=True, include_summary=True):
        """
        Build complete context for AI prompt (AI-AGNOSTIC)
        
        This method prepares all context that YOU will pass to your chosen AI
        Works with OpenAI, Claude, Gemini, or any other AI API
        
        Args:
            user_id: User ID
            persona: Persona name
            include_preferences: Include user preferences
            include_summary: Include conversation summary
        
        Returns:
            Dict with complete context for AI
        """
        context = {
            'recent_messages': MemoryService.get_recent_context(user_id, persona, limit=10),
            'preferences': {},
            'conversation_summary': {}
        }
        
        if include_preferences:
            # Get all preferences
            prefs = MemoryService.get_user_preferences(user_id)
            
            # Organize by category
            for pref in prefs:
                category = pref['category']
                if category not in context['preferences']:
                    context['preferences'][category] = {}
                context['preferences'][category][pref['key']] = pref['value']
        
        if include_summary:
            context['conversation_summary'] = MemoryService.get_conversation_summary(
                user_id, persona, days=7
            )
        
        return context
    
    @staticmethod
    def format_context_for_prompt(context):
        """
        Format context into a text prompt snippet
        Can be prepended to your AI prompt
        
        Args:
            context: Context dict from build_ai_context()
        
        Returns:
            String formatted for AI prompt
        """
        prompt_parts = []
        
        # Add conversation summary
        if context.get('conversation_summary'):
            summary = context['conversation_summary']
            if summary.get('key_topics'):
                topics_str = ', '.join(summary['key_topics'])
                prompt_parts.append(f"Recent conversation topics: {topics_str}")
        
        # Add preferences
        if context.get('preferences'):
            pref_lines = []
            for category, prefs in context['preferences'].items():
                for key, value in prefs.items():
                    pref_lines.append(f"- {key}: {value}")
            
            if pref_lines:
                prompt_parts.append("User preferences:\n" + "\n".join(pref_lines))
        
        return "\n\n".join(prompt_parts)
    
    @staticmethod
    def search_conversations(user_id, search_query, limit=20):
        """
        Search through conversation history
        
        Args:
            user_id: User ID
            search_query: Search string
            limit: Max results
        
        Returns:
            List of matching messages
        """
        messages = ChatMessage.query.filter(
            ChatMessage.user_id == user_id,
            ChatMessage.content.ilike(f'%{search_query}%')
        ).order_by(desc(ChatMessage.timestamp)).limit(limit).all()
        
        return [msg.to_dict() for msg in messages]
    
    @staticmethod
    def get_conversation_stats(user_id):
        """
        Get statistics about user's conversations
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with statistics
        """
        total_messages = ChatMessage.query.filter_by(user_id=user_id).count()
        total_conversations = ConversationMemory.query.filter_by(user_id=user_id).count()
        
        # Get messages by persona
        persona_stats = db.session.query(
            ChatMessage.persona,
            func.count(ChatMessage.id).label('count')
        ).filter(
            ChatMessage.user_id == user_id
        ).group_by(ChatMessage.persona).all()
        
        # Get most active days
        recent_days = datetime.utcnow() - timedelta(days=30)
        daily_activity = db.session.query(
            func.date(ChatMessage.timestamp).label('date'),
            func.count(ChatMessage.id).label('count')
        ).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.timestamp >= recent_days
        ).group_by(func.date(ChatMessage.timestamp)).all()
        
        return {
            'total_messages': total_messages,
            'total_conversations': total_conversations,
            'persona_breakdown': {p: c for p, c in persona_stats},
            'daily_activity': [{'date': str(d), 'count': c} for d, c in daily_activity],
            'preferences_count': UserPreference.query.filter_by(user_id=user_id).count()
        }
