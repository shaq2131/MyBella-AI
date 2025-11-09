"""
Default Persona Initialization
Creates default persona profiles for MyBella
"""

from sqlalchemy import inspect, text
from backend.database.models.models import db, PersonaProfile
from flask import current_app


def ensure_persona_schema() -> None:
    """Ensure persona_profiles table has latest columns."""
    inspector = inspect(db.engine)
    columns = {col["name"] for col in inspector.get_columns("persona_profiles")}
    statements = []

    if "communication_style" not in columns:
        statements.append(
            text(
                "ALTER TABLE persona_profiles ADD COLUMN communication_style VARCHAR(50) DEFAULT 'friendly'"
            )
        )
    if "tagline" not in columns:
        statements.append(text("ALTER TABLE persona_profiles ADD COLUMN tagline VARCHAR(150)"))

    for statement in statements:
        db.session.execute(statement)

    if statements:
        db.session.commit()


def initialize_default_personas() -> None:
    """Initialize default persona profiles with gender-based assignment."""
    ensure_persona_schema()

    default_personas = [
        {
            "name": "Isabella",
            "display_name": "Isabella",
            "description": "A warm, caring female companion who provides emotional support and meaningful conversations. Perfect for male users seeking a nurturing AI friend.",
            "personality_traits": "Empathetic, nurturing, supportive, great listener, emotionally intelligent",
            "voice_settings": "female_warm",
            "communication_style": "nurturing",
            "tagline": "Your gentle, heart-centered confidant."
        },
        {
            "name": "Alex",
            "display_name": "Alex",
            "description": "A confident, supportive male companion who offers practical advice and engaging discussions. Ideal for female users looking for a reliable AI partner.",
            "personality_traits": "Confident, supportive, practical, engaging, good conversationalist",
            "voice_settings": "male_friendly",
            "communication_style": "supportive",
            "tagline": "Always here with grounded, practical guidance."
        },
        {
            "name": "Luna",
            "display_name": "Luna",
            "description": "A creative, artistic female companion who loves discussing arts, literature, and imagination. Great for users who enjoy creative conversations.",
            "personality_traits": "Creative, artistic, imaginative, inspiring, thoughtful",
            "voice_settings": "female_gentle",
            "communication_style": "creative",
            "tagline": "Let's dream, create, and explore together."
        },
        {
            "name": "Maya",
            "display_name": "Maya",
            "description": "A wellness-focused female companion specializing in mindfulness, self-care, and mental health support. Perfect for holistic well-being conversations.",
            "personality_traits": "Mindful, calming, health-focused, wise, balanced",
            "voice_settings": "female_calm",
            "communication_style": "therapeutic",
            "tagline": "Grounded guidance for mind, body, and soul."
        },
        {
            "name": "Sam",
            "display_name": "Sam",
            "description": "An adventurous, energetic male companion who loves discussing sports, travel, and exciting activities. Great for users seeking dynamic conversations.",
            "personality_traits": "Adventurous, energetic, sporty, motivational, fun-loving",
            "voice_settings": "male_energetic",
            "communication_style": "enthusiastic",
            "tagline": "Your hype partner for life's adventures."
        },
        {
            "name": "Ethan",
            "display_name": "Ethan",
            "description": "A tech-savvy, intelligent male companion focused on innovation, problem-solving, and intellectual discussions. Perfect for users who love learning.",
            "personality_traits": "Intelligent, analytical, tech-savvy, curious, problem-solver",
            "voice_settings": "male_professional",
            "communication_style": "professional",
            "tagline": "Smart, analytical, and ready to deep-dive with you."
        }
    ]

    try:
        for persona_data in default_personas:
            existing = PersonaProfile.query.filter_by(name=persona_data["name"]).first()
            if not existing:
                persona = PersonaProfile()
                persona.name = persona_data["name"]
                persona.display_name = persona_data["display_name"]
                persona.description = persona_data["description"]
                persona.personality_traits = persona_data.get("personality_traits", "")
                persona.voice_settings = persona_data.get("voice_settings", "default")
                persona.communication_style = persona_data.get("communication_style", "friendly")
                persona.tagline = persona_data.get("tagline")
                persona.is_active = True
                db.session.add(persona)
            else:
                updated = False
                if not existing.personality_traits and persona_data.get("personality_traits"):
                    existing.personality_traits = persona_data["personality_traits"]
                    updated = True
                if not getattr(existing, "communication_style", None) and persona_data.get("communication_style"):
                    existing.communication_style = persona_data["communication_style"]
                    updated = True
                if not getattr(existing, "tagline", None) and persona_data.get("tagline"):
                    existing.tagline = persona_data["tagline"]
                    updated = True
                if updated:
                    db.session.add(existing)

        db.session.commit()
        current_app.logger.info("Default personas initialized")

    except Exception as exc:  # pragma: no cover - logged for debugging
        db.session.rollback()
        current_app.logger.error(f"Error initializing default personas: {exc}")