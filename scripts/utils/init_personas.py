#!/usr/bin/env python3
"""
Initialize personas for gender-based assignment
Run this script to create the enhanced persona profiles
"""

import sys
import os

# Add the current directory to sys.path to import backend modules
sys.path.insert(0, os.path.abspath('.'))

from flask import Flask
from backend.database.models.models import db
from backend.services.persona_init import initialize_default_personas

def create_app():
    """Create Flask app for persona initialization"""
    app = Flask(__name__)
    
    # Get the absolute path to the database
    db_path = os.path.join(os.path.abspath('.'), 'backend', 'database', 'instances', 'mybella.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def main():
    """Main initialization function"""
    print("🎭 Initializing Enhanced Personas for Gender-Based Assignment...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Initialize personas
            initialize_default_personas()
            print("✅ Personas initialized successfully!")
            
            # List created personas
            from backend.database.models.models import PersonaProfile
            personas = PersonaProfile.query.all()
            
            print(f"\n📋 Available Personas ({len(personas)} total):")
            for persona in personas:
                print(f"  • {persona.name} - {persona.description[:50]}...")
            
            print("\n🎯 Gender Assignment Rules:")
            print("  • Female users → Alex (male companion)")
            print("  • Male users → Isabella (female companion)")
            print("  • Other/Unspecified → Isabella (default)")
            
            print("\n🚀 System ready! Users can now:")
            print("  1. Register with gender selection")
            print("  2. Get assigned appropriate default companion")
            print("  3. Switch between all available personas")
            
        except Exception as e:
            print(f"❌ Error initializing personas: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)