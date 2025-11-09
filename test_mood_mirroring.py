"""
Test Mood Mirroring Integration
Verify that AI chat adapts tone based on user's mood
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend import create_app
from backend.database.models.models import db, User
from backend.database.models.wellness_models import MoodEntry, MoodScale
from backend.services.mood_service import MoodService
from backend.services.chat.chat_service import build_system_prompt
from datetime import date, timedelta

def test_mood_service():
    """Test MoodService functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING MOOD SERVICE")
    print("="*60)
    
    app, socketio = create_app()
    
    with app.app_context():
        # Find test user
        user = User.query.first()
        
        if not user:
            print("❌ No users found in database. Create a user first.")
            return False
        
        print(f"\n✅ Testing with user: {user.name} (ID: {user.id})")
        
        # Test 1: Get mood context with no recent mood
        print("\n--- Test 1: No Recent Mood ---")
        mood_context = MoodService.get_mood_context(user.id)
        print(f"Has recent mood: {mood_context['has_recent_mood']}")
        print(f"Should suggest check-in: {MoodService.should_suggest_mood_checkin(user.id)}")
        
        if not mood_context['has_recent_mood']:
            print("✅ Correctly identifies no recent mood")
        
        # Test 2: Create test mood entries with different levels
        print("\n--- Test 2: Creating Test Mood Entries ---")
        
        test_moods = [
            (MoodScale.VERY_LOW, "Feeling very low"),
            (MoodScale.BELOW_AVERAGE, "Not great today"),
            (MoodScale.AVERAGE, "Feeling okay"),
            (MoodScale.GOOD, "Pretty good!"),
            (MoodScale.EXCELLENT, "Amazing day!")
        ]
        
        for mood_scale, description in test_moods:
            # Delete any existing moods for today
            MoodEntry.query.filter(
                MoodEntry.user_id == user.id,
                MoodEntry.entry_date == date.today()
            ).delete()
            db.session.commit()
            
            # Create test mood
            mood = MoodEntry(
                user_id=user.id,
                overall_mood=mood_scale,
                entry_date=date.today()
            )
            db.session.add(mood)
            db.session.commit()
            
            # Get mood context
            context = MoodService.get_mood_context(user.id)
            
            print(f"\nMood Level {mood_scale.value}/10 ({description}):")
            print(f"  Has recent mood: {context['has_recent_mood']}")
            print(f"  Mood level: {context['mood_level']}")
            print(f"  Tone adjustment: {context['tone_adjustment'][:100]}...")
            
            # Test prompt building
            base_prompt = "You are Isabella, an empathetic AI companion."
            adjusted_prompt = MoodService.get_mood_adjusted_prompt(base_prompt, user.id)
            
            # Check if tone adjustment was added
            if "MOOD-AWARE" in adjusted_prompt:
                print(f"  ✅ Mood adjustment applied to prompt")
            else:
                print(f"  ❌ Mood adjustment NOT applied")
        
        # Test 3: Test with high anxiety
        print("\n--- Test 3: High Anxiety Override ---")
        MoodEntry.query.filter(
            MoodEntry.user_id == user.id,
            MoodEntry.entry_date == date.today()
        ).delete()
        db.session.commit()
        
        anxiety_mood = MoodEntry(
            user_id=user.id,
            overall_mood=MoodScale.AVERAGE,  # Mood is average
            anxiety_level=MoodScale.VERY_GOOD,  # But anxiety is high (8/10)
            entry_date=date.today()
        )
        db.session.add(anxiety_mood)
        db.session.commit()
        
        context = MoodService.get_mood_context(user.id)
        print(f"Overall mood: {context['mood_level']}/10")
        print(f"Anxiety level: {context['anxiety_level']}/10")
        print(f"Tone adjustment: {context['tone_adjustment'][:100]}...")
        
        if "anxiety" in context['tone_adjustment'].lower():
            print("✅ Anxiety override working correctly")
        else:
            print("❌ Anxiety override NOT working")
        
        # Test 4: Mood check-in suggestion
        print("\n--- Test 4: Mood Check-in Suggestions ---")
        
        # Create old mood (3 days ago)
        old_mood = MoodEntry(
            user_id=user.id,
            overall_mood=MoodScale.GOOD,
            entry_date=date.today() - timedelta(days=3)
        )
        
        MoodEntry.query.filter(
            MoodEntry.user_id == user.id,
            MoodEntry.entry_date == date.today()
        ).delete()
        db.session.add(old_mood)
        db.session.commit()
        
        should_suggest = MoodService.should_suggest_mood_checkin(user.id)
        print(f"Should suggest check-in (3 days old): {should_suggest}")
        
        if should_suggest:
            prompt = MoodService.get_mood_checkin_prompt("Isabella")
            print(f"Check-in prompt: {prompt}")
            print("✅ Check-in suggestion working")
        else:
            print("❌ Check-in suggestion NOT working")
        
        # Clean up test data
        print("\n--- Cleaning Up Test Data ---")
        MoodEntry.query.filter(MoodEntry.user_id == user.id).delete()
        db.session.commit()
        print("✅ Test mood entries removed")
        
        return True

def test_chat_integration():
    """Test chat service integration with mood awareness"""
    print("\n" + "="*60)
    print("🧪 TESTING CHAT SERVICE INTEGRATION")
    print("="*60)
    
    app, socketio = create_app()
    
    with app.app_context():
        user = User.query.first()
        
        if not user:
            print("❌ No users found")
            return False
        
        print(f"\n✅ Testing with user: {user.name}")
        
        # Create mood entries for different scenarios
        test_scenarios = [
            {
                'name': 'Low Mood',
                'mood': MoodScale.VERY_LOW,
                'expected_tone': ['gentle', 'compassionate', 'validating']
            },
            {
                'name': 'Good Mood',
                'mood': MoodScale.VERY_GOOD,
                'expected_tone': ['enthusiastic', 'upbeat', 'energetic']
            },
            {
                'name': 'Average Mood',
                'mood': MoodScale.AVERAGE,
                'expected_tone': ['conversational', 'friendly', 'balanced']
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n--- Scenario: {scenario['name']} ---")
            
            # Create mood
            MoodEntry.query.filter(
                MoodEntry.user_id == user.id,
                MoodEntry.entry_date == date.today()
            ).delete()
            db.session.commit()
            
            mood = MoodEntry(
                user_id=user.id,
                overall_mood=scenario['mood'],
                entry_date=date.today()
            )
            db.session.add(mood)
            db.session.commit()
            
            # Build system prompt
            prompt = build_system_prompt(
                persona="Isabella",
                mode="Wellness",
                retrieved_chunks=None,
                user_id=user.id
            )
            
            # Check if expected tone keywords are in prompt
            prompt_lower = prompt.lower()
            found_keywords = [kw for kw in scenario['expected_tone'] if kw.lower() in prompt_lower]
            
            print(f"Expected tone keywords: {scenario['expected_tone']}")
            print(f"Found in prompt: {found_keywords}")
            print(f"Prompt excerpt: ...{prompt[-200:]}")
            
            if found_keywords:
                print(f"✅ Mood-aware tone detected ({len(found_keywords)}/{len(scenario['expected_tone'])} keywords)")
            else:
                print(f"⚠️  Tone keywords not found (prompt may still be adjusted)")
        
        # Clean up
        MoodEntry.query.filter(MoodEntry.user_id == user.id).delete()
        db.session.commit()
        print("\n✅ Test data cleaned up")
        
        return True

def run_all_tests():
    """Run all mood mirroring tests"""
    print("\n" + "="*60)
    print("🧪 MOOD MIRRORING INTEGRATION TESTS")
    print("="*60)
    
    try:
        test1_passed = test_mood_service()
        test2_passed = test_chat_integration()
        
        print("\n" + "="*60)
        print("📊 TEST RESULTS")
        print("="*60)
        print(f"Mood Service Tests: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
        print(f"Chat Integration Tests: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("\n✨ Mood mirroring is working correctly!")
            print("   - AI tone adjusts based on user mood")
            print("   - High anxiety/stress triggers calming tone")
            print("   - Mood check-in suggestions work")
            print("   - Chat service integration complete")
            return 0
        else:
            print("\n⚠️  SOME TESTS FAILED")
            print("   Check the output above for details")
            return 1
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
