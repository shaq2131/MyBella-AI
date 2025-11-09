"""
Create conversation memory tables
Run this once to add memory system support to MyBella
"""

from backend import create_app
from backend.database.models.models import db
from backend.database.models.memory_models import ConversationMemory, ChatMessage, UserPreference

def create_memory_tables():
    """Create memory tables in database"""
    app, _ = create_app()
    
    with app.app_context():
        print("Creating conversation memory tables...")
        
        # Create tables
        db.create_all()
        
        print("Memory tables created successfully!")
        print("\nCreated tables:")
        print("  - conversation_memories (stores conversation summaries)")
        print("  - chat_messages (stores individual messages)")
        print("  - user_preferences (stores learned preferences)")
        print("\nMemory system is ready!")
        print("\nNOTE: The memory system is AI-AGNOSTIC.")
        print("It will work with whatever AI provider you integrate:")
        print("  - OpenAI GPT")
        print("  - Anthropic Claude")
        print("  - Google Gemini")
        print("  - Any other AI API")
        print("\nTo use in your AI integration:")
        print("  1. Call /memory/api/context to get conversation context")
        print("  2. Include the context in your AI prompt")
        print("  3. Call /memory/api/save-message to save responses")


if __name__ == '__main__':
    create_memory_tables()
