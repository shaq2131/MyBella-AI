"""
Add Per-Persona Memory Isolation
- Adds persona_id foreign keys to chat_messages and conversation_memories
- Adds user_id foreign key to persona_profiles for custom personas
- Migrates existing persona name strings to persona_id references
- Preserves all existing data
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend import create_app
from backend.database.models.models import db, PersonaProfile, UserSettings
from backend.database.models.memory_models import ChatMessage, ConversationMemory, UserPreference
from sqlalchemy import text

def migrate_persona_isolation():
    """Add persona_id columns and migrate existing data"""
    app, socketio = create_app()
    
    with app.app_context():
        print("\n=== Adding Per-Persona Memory Isolation ===\n")
        
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            
            # 1. Add persona_id column to chat_messages if it doesn't exist
            chat_messages_cols = [col['name'] for col in inspector.get_columns('chat_messages')]
            if 'persona_id' not in chat_messages_cols:
                print("📝 Adding persona_id to chat_messages...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE chat_messages ADD COLUMN persona_id INTEGER'))
                    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_chat_messages_persona ON chat_messages(persona_id)'))
                    conn.commit()
                print("✅ Added persona_id to chat_messages")
            else:
                print("ℹ️  persona_id already exists in chat_messages")
            
            # 2. Add persona_id column to conversation_memories if it doesn't exist
            memory_cols = [col['name'] for col in inspector.get_columns('conversation_memories')]
            if 'persona_id' not in memory_cols:
                print("📝 Adding persona_id to conversation_memories...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE conversation_memories ADD COLUMN persona_id INTEGER'))
                    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_conversation_memories_persona ON conversation_memories(persona_id)'))
                    conn.commit()
                print("✅ Added persona_id to conversation_memories")
            else:
                print("ℹ️  persona_id already exists in conversation_memories")
            
            # 3. Add persona_id column to user_preferences if it doesn't exist
            prefs_cols = [col['name'] for col in inspector.get_columns('user_preferences')]
            if 'persona_id' not in prefs_cols:
                print("📝 Adding persona_id to user_preferences...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE user_preferences ADD COLUMN persona_id INTEGER'))
                    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_user_preferences_persona ON user_preferences(persona_id)'))
                    conn.commit()
                print("✅ Added persona_id to user_preferences")
            else:
                print("ℹ️  persona_id already exists in user_preferences")
            
            # 4. Add user_id column to persona_profiles for custom personas (if not exists)
            persona_cols = [col['name'] for col in inspector.get_columns('persona_profiles')]
            if 'user_id' not in persona_cols:
                print("📝 Adding user_id to persona_profiles for custom personas...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE persona_profiles ADD COLUMN user_id INTEGER'))
                    conn.execute(text('ALTER TABLE persona_profiles ADD COLUMN is_custom BOOLEAN DEFAULT 0'))
                    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_persona_profiles_user ON persona_profiles(user_id)'))
                    conn.commit()
                print("✅ Added user_id and is_custom to persona_profiles")
            else:
                print("ℹ️  user_id already exists in persona_profiles")
            
            # 5. Add current_persona_id to user_settings if it doesn't exist
            settings_cols = [col['name'] for col in inspector.get_columns('user_settings')]
            if 'current_persona_id' not in settings_cols:
                print("📝 Adding current_persona_id to user_settings...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE user_settings ADD COLUMN current_persona_id INTEGER'))
                    conn.commit()
                print("✅ Added current_persona_id to user_settings")
            else:
                print("ℹ️  current_persona_id already exists in user_settings")
            
            # 6. Add voice_id column to persona_profiles if it doesn't exist
            if 'voice_id' not in persona_cols:
                print("📝 Adding voice_id to persona_profiles...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE persona_profiles ADD COLUMN voice_id VARCHAR(100)'))
                    conn.execute(text('ALTER TABLE persona_profiles ADD COLUMN custom_voice_url TEXT'))
                    conn.commit()
                print("✅ Added voice_id and custom_voice_url to persona_profiles")
            else:
                print("ℹ️  voice_id already exists in persona_profiles")
            
            print("\n=== Migrating Existing Data ===\n")
            
            # 7. Migrate existing persona names to persona_ids in chat_messages
            print("📊 Migrating chat_messages persona names to IDs...")
            messages = ChatMessage.query.filter(ChatMessage.persona_id == None).all()
            migrated_messages = 0
            
            for message in messages:
                if message.persona:
                    persona = PersonaProfile.query.filter_by(name=message.persona).first()
                    if persona:
                        message.persona_id = persona.id
                        migrated_messages += 1
            
            if migrated_messages > 0:
                db.session.commit()
                print(f"✅ Migrated {migrated_messages} chat messages")
            else:
                print("ℹ️  No chat messages to migrate")
            
            # 8. Migrate conversation_memories
            print("📊 Migrating conversation_memories persona names to IDs...")
            memories = ConversationMemory.query.filter(ConversationMemory.persona_id == None).all()
            migrated_memories = 0
            
            for memory in memories:
                if memory.persona:
                    persona = PersonaProfile.query.filter_by(name=memory.persona).first()
                    if persona:
                        memory.persona_id = persona.id
                        migrated_memories += 1
            
            if migrated_memories > 0:
                db.session.commit()
                print(f"✅ Migrated {migrated_memories} conversation memories")
            else:
                print("ℹ️  No conversation memories to migrate")
            
            # 9. Migrate user_settings current_persona to current_persona_id
            print("📊 Migrating user_settings current_persona to IDs...")
            settings = UserSettings.query.filter(UserSettings.current_persona_id == None).all()
            migrated_settings = 0
            
            for setting in settings:
                if setting.current_persona:
                    persona = PersonaProfile.query.filter_by(name=setting.current_persona).first()
                    if persona:
                        setting.current_persona_id = persona.id
                        migrated_settings += 1
            
            if migrated_settings > 0:
                db.session.commit()
                print(f"✅ Migrated {migrated_settings} user settings")
            else:
                print("ℹ️  No user settings to migrate")
            
            print("\n=== Migration Complete ===\n")
            print("✅ Per-persona memory isolation is now active!")
            print("✅ Each persona will have its own conversation history")
            print("✅ Custom persona creation is now supported")
            print("✅ Voice customization per persona is enabled")
            
        except Exception as e:
            print(f"\n❌ Error during migration: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_persona_isolation()
