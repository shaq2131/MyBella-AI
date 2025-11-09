"""
Age Verification & Feature Access Migration
Creates tables and seeds initial feature restrictions
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend import create_app
from backend.database.models.models import db
from backend.database.models.age_verification_models import (
    UserAgeVerification, FeatureAccess, UserFeatureOverride, PersonaAgeRestriction
)


def seed_feature_restrictions():
    """
    Seed initial feature access rules
    """
    print("🔒 Seeding age-restricted features...")
    
    features = [
        # TEEN-BLOCKED FEATURES (18+ only)
        {
            'feature_key': 'intimacy_mode',
            'feature_name': 'Intimacy / Time-Grown Relationship Mode',
            'feature_description': 'Depth-based affection and romantic relationship progression',
            'feature_category': 'romantic',
            'min_age_required': 18,
            'teen_accessible': False,
            'adult_only': True,
            'compliance_reason': 'Romantic/intimate content restricted for minors per App Store guidelines'
        },
        {
            'feature_key': 'whisper_talk',
            'feature_name': 'WhisperTalk™ Romantic Voice Modes',
            'feature_description': 'Voice chat with romantic/intimate tone variations',
            'feature_category': 'romantic',
            'min_age_required': 18,
            'teen_accessible': False,
            'adult_only': True,
            'compliance_reason': 'Romantic voice interactions restricted for minors'
        },
        {
            'feature_key': 'love_letters',
            'feature_name': 'Love Letters & Flirty Notes',
            'feature_description': 'Romantic daily messages and love letters from AI companion',
            'feature_category': 'romantic',
            'min_age_required': 18,
            'teen_accessible': False,
            'adult_only': True,
            'compliance_reason': 'Romantic content restricted for minors'
        },
        {
            'feature_key': 'romantic_avatars',
            'feature_name': 'Romantic Avatar Skins',
            'feature_description': 'Intimate or romantic persona appearances',
            'feature_category': 'romantic',
            'min_age_required': 18,
            'teen_accessible': False,
            'adult_only': True,
            'compliance_reason': 'Romantic imagery restricted for minors'
        },
        
        # TEEN-ACCESSIBLE FEATURES (16+)
        {
            'feature_key': 'mood_letters',
            'feature_name': 'Daily Mood Letters',
            'feature_description': 'Supportive wellness-focused daily messages',
            'feature_category': 'wellness',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Wellness content appropriate for teens'
        },
        {
            'feature_key': 'cbt_games',
            'feature_name': 'CBT Games (Reframe Puzzle, Mindful Match)',
            'feature_description': 'Cognitive behavioral therapy exercises and games',
            'feature_category': 'wellness',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Mental health tools appropriate for teens'
        },
        {
            'feature_key': 'secrets_vault',
            'feature_name': 'Secrets Vault (PIN-Protected)',
            'feature_description': 'Private journaling with PIN protection',
            'feature_category': 'wellness',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Privacy tools appropriate for teens with parental awareness'
        },
        {
            'feature_key': 'mood_timeline',
            'feature_name': 'Mood Timeline & Journaling',
            'feature_description': 'Emotional tracking and wellness journaling',
            'feature_category': 'wellness',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Mental health tracking appropriate for teens'
        },
        {
            'feature_key': 'wellness_avatars',
            'feature_name': 'Wellness Avatar Skins',
            'feature_description': 'Safe, supportive persona appearances',
            'feature_category': 'wellness',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Non-romantic avatars appropriate for all ages'
        },
        {
            'feature_key': 'study_companion',
            'feature_name': 'Study Companion Mode',
            'feature_description': 'Productivity and study assistance features',
            'feature_category': 'wellness',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Educational features appropriate for teens'
        },
        
        # PREMIUM FEATURES (Available to paying users of appropriate age)
        {
            'feature_key': 'voice_chat_basic',
            'feature_name': 'Basic Voice Chat',
            'feature_description': 'Non-romantic voice conversations',
            'feature_category': 'premium',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Voice chat with content filtering for teens'
        },
        {
            'feature_key': 'unlimited_messages',
            'feature_name': 'Unlimited Messages',
            'feature_description': 'Remove daily message limits',
            'feature_category': 'premium',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Message limits relaxed for subscribers'
        },
        {
            'feature_key': 'extra_cbt_packs',
            'feature_name': 'Extra CBT Exercise Packs',
            'feature_description': 'Additional cognitive behavioral therapy content',
            'feature_category': 'premium',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Mental health content appropriate for paying teen users'
        },
        {
            'feature_key': 'streak_rewards',
            'feature_name': 'Mood & Study Habit Streak Rewards',
            'feature_description': 'Gamified wellness tracking with achievements',
            'feature_category': 'premium',
            'min_age_required': 16,
            'teen_accessible': True,
            'adult_only': False,
            'compliance_reason': 'Motivational features appropriate for teens'
        }
    ]
    
    added_count = 0
    for feature_data in features:
        existing = FeatureAccess.query.filter_by(feature_key=feature_data['feature_key']).first()
        if not existing:
            feature = FeatureAccess(**feature_data)
            db.session.add(feature)
            added_count += 1
            print(f"  ✅ Added: {feature_data['feature_name']}")
    
    db.session.commit()
    print(f"\n✅ Added {added_count} feature restrictions")


def seed_persona_age_restrictions():
    """
    Seed age-appropriate behavior for default personas
    """
    print("\n👤 Configuring persona age-appropriate behaviors...")
    
    from backend.database.models.models import PersonaProfile
    
    persona_configs = [
        {
            'name': 'Isabella',
            'teen_tone': 'supportive_sister',
            'teen_system_prompt': """You are Isabella in supportive sister mode. You're here to listen, encourage, and help with wellness. 
            Be warm but professional. Focus on mental health, school stress, and personal growth. 
            NEVER use romantic, flirty, or intimate language. Your role is supportive friend/mentor only.""",
            'teen_forbidden_topics': '["romantic relationships", "dating advice", "intimacy", "flirting"]'
        },
        {
            'name': 'Luna',
            'teen_tone': 'friend_mode',
            'teen_system_prompt': """You are Luna in friend mode. You're a supportive peer who helps with wellness and creativity. 
            Be encouraging and relatable. Focus on mental health, creative expression, and positive habits. 
            NEVER use romantic or flirty language. Your role is friendly peer support only.""",
            'teen_forbidden_topics': '["romantic relationships", "dating", "intimacy", "attraction"]'
        },
        {
            'name': 'Sam',
            'teen_tone': 'maternal_coach',
            'teen_system_prompt': """You are Sam in nurturing coach mode. You're a maternal figure who provides guidance and emotional support. 
            Be caring, wise, and encouraging. Focus on wellness, self-care, and building healthy habits. 
            NEVER use romantic language. Your role is maternal mentor only.""",
            'teen_forbidden_topics': '["romantic relationships", "dating", "intimacy", "flirting"]'
        },
        {
            'name': 'Alex',
            'teen_tone': 'brotherly_coach',
            'teen_system_prompt': """You are Alex in brotherly motivational mode. You're an encouraging older brother figure. 
            Be supportive, motivational, and focused on wellness and productivity. 
            NEVER use romantic or intimate language. Your role is brotherly mentor only.""",
            'teen_forbidden_topics': '["romantic relationships", "dating", "intimacy", "flirting"]'
        }
    ]
    
    added_count = 0
    for config in persona_configs:
        persona = PersonaProfile.query.filter_by(name=config['name']).first()
        if persona:
            existing = PersonaAgeRestriction.query.filter_by(persona_id=persona.id).first()
            if not existing:
                restriction = PersonaAgeRestriction(
                    persona_id=persona.id,
                    teen_mode_enabled=True,
                    teen_tone=config['teen_tone'],
                    teen_system_prompt=config['teen_system_prompt'],
                    teen_forbidden_topics=config['teen_forbidden_topics'],
                    allow_romantic_dialogue=False,
                    allow_flirty_responses=False,
                    allow_intimacy_content=False,
                    wellness_focus_only=True
                )
                db.session.add(restriction)
                added_count += 1
                print(f"  ✅ Configured: {persona.name} → {config['teen_tone']}")
    
    db.session.commit()
    print(f"\n✅ Configured {added_count} persona age restrictions")


def run_migration():
    """
    Main migration execution
    """
    print("\n" + "="*60)
    print("🔒 AGE VERIFICATION & FEATURE ACCESS MIGRATION")
    print("="*60 + "\n")
    
    app, _ = create_app()
    
    with app.app_context():
        # Create tables
        print("📊 Creating database tables...\n")
        db.create_all()
        print("✅ Tables created successfully\n")
        
        # Seed data
        seed_feature_restrictions()
        seed_persona_age_restrictions()
        
        print("\n" + "="*60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n✨ Age-Gated Features Available:")
        print("1. ✅ User Age Verification (DOB collection)")
        print("2. ✅ Feature Access Control (14 features)")
        print("3. ✅ Persona Age Restrictions (4 personas)")
        print("4. ✅ Teen Mode (16-17): Wellness-only")
        print("5. ✅ Adult Mode (18+): Full features")
        
        print("\n📋 Next Steps:")
        print("1. Add DOB field to signup form")
        print("2. Create age verification service")
        print("3. Update chat service to check age restrictions")
        print("4. Add feature access middleware")
        print("5. Update persona prompts based on user age")
        
        print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    run_migration()
