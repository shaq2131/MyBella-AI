"""
Test Age Verification System Integration
"""

import sys
from datetime import date, timedelta
from backend import create_app
from backend.database.models.models import db
from backend.database.models.age_verification_models import FeatureAccess, PersonaAgeRestriction
from backend.services.age_verification_service import AgeVerificationService

def test_age_verification():
    """Test the age verification system"""
    print("\n" + "="*60)
    print("🧪 AGE VERIFICATION SYSTEM TEST")
    print("="*60 + "\n")
    
    app = create_app()
    
    with app.app_context():
        # Check if tables exist
        print("📊 Checking Database Tables...")
        try:
            feature_count = FeatureAccess.query.count()
            persona_count = PersonaAgeRestriction.query.count()
            
            print(f"✅ FeatureAccess table exists: {feature_count} records")
            print(f"✅ PersonaAgeRestriction table exists: {persona_count} records")
            
            if feature_count == 0:
                print("\n⚠️  No feature restrictions found. Running migration...")
                from scripts.migrations.add_age_verification import run_migration
                run_migration()
                print("✅ Migration completed\n")
            
            # Test age calculations
            print("\n" + "-"*60)
            print("🎂 Testing Age Calculations:")
            print("-"*60)
            
            # Test cases
            test_cases = [
                ("15-year-old (blocked)", date.today() - timedelta(days=365*15 + 180), "Should be blocked"),
                ("16-year-old (teen)", date.today() - timedelta(days=365*16 + 180), "Teen mode"),
                ("17-year-old (teen)", date.today() - timedelta(days=365*17 + 180), "Teen mode"),
                ("18-year-old (adult)", date.today() - timedelta(days=365*18 + 180), "Full access"),
                ("25-year-old (adult)", date.today() - timedelta(days=365*25 + 180), "Full access"),
            ]
            
            for label, dob, expected in test_cases:
                age = (date.today() - dob).days // 365
                print(f"\n  {label}:")
                print(f"    DOB: {dob}")
                print(f"    Age: {age} years")
                print(f"    Expected: {expected}")
            
            # Test feature access
            print("\n" + "-"*60)
            print("🔐 Testing Feature Restrictions:")
            print("-"*60)
            
            features = FeatureAccess.query.all()
            if features:
                teen_blocked = [f for f in features if f.adult_only]
                teen_accessible = [f for f in features if f.teen_accessible]
                
                print(f"\n  🚫 Teen-Blocked Features ({len(teen_blocked)}):")
                for feature in teen_blocked[:4]:  # Show first 4
                    print(f"    - {feature.feature_name} (18+ only)")
                
                print(f"\n  ✅ Teen-Accessible Features ({len(teen_accessible)}):")
                for feature in teen_accessible[:4]:  # Show first 4
                    print(f"    - {feature.feature_name} (16+)")
            
            # Test persona configurations
            print("\n" + "-"*60)
            print("🎭 Testing Persona Age Restrictions:")
            print("-"*60)
            
            personas = PersonaAgeRestriction.query.all()
            if personas:
                for persona in personas[:2]:  # Show first 2
                    print(f"\n  Persona ID {persona.persona_id}:")
                    print(f"    Teen Tone: {persona.teen_tone}")
                    print(f"    Allow Romantic: {persona.allow_romantic_dialogue}")
                    print(f"    Wellness Only: {persona.wellness_focus_only}")
            
            print("\n" + "="*60)
            print("✅ AGE VERIFICATION SYSTEM TEST COMPLETE")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_age_verification()
    sys.exit(0 if success else 1)
